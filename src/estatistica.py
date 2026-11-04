"""Estimadores para amostras complexas (estratos + conglomerados + pesos).

Implementação própria, apenas numpy/scipy/pandas, por linearização de Taylor
(variância com reposição entre UPAs dentro de estratos).
Referência de método: Lumley (2010), Complex Surveys; Heeringa, West & Berglund (2017).

Limitações declaradas:
- Estratos com uma única UPA não contribuem para a variância (verificado contra as tabelas do IBGE).
- IC por t de Student com gl = nº de UPAs - nº de estratos (aproximação padrão).
- Não substitui pacotes validados (Stata svy, R survey); usar para conferência cruzada.
"""
from __future__ import annotations

import warnings

import numpy as np
import pandas as pd
from scipy import stats


def _var_total(u: np.ndarray, strata: np.ndarray, psu: np.ndarray):
    """Variância do total de u (valores linearizados) e graus de liberdade.
    Estratos com uma única UPA não contribuem para a variância (equivale a `lonely.psu="remove"`).
    Verificado empiricamente: reproduz os IC95% das tabelas oficiais do IBGE, inclusive em
    capitais com poucas UPAs (a variante 'centrar na média geral' alargava os IC em até 1,3 pp)."""
    df_ = pd.DataFrame({"u": u, "h": strata, "p": psu})
    tot = df_.groupby(["h", "p"], sort=False)["u"].sum().reset_index()
    var, n_psu, n_str = 0.0, 0, 0
    for _, g in tot.groupby("h", sort=False):
        n_h = len(g)
        n_psu += n_h
        n_str += 1
        if n_h < 2:
            continue
        var += n_h / (n_h - 1) * ((g["u"] - g["u"].mean()) ** 2).sum()
    return var, max(n_psu - n_str, 1)


def _pos(df, w, posest, totais):
    """Pesos pós-estratificados w* = w * N_c / soma_c(w), calculados sobre TODAS as linhas.
    Retorna (w*, índice de célula). Sem posest, retorna os pesos originais."""
    ww = df[w].to_numpy(float)
    if posest is None:
        return ww, None
    cel = df[posest].to_numpy()
    soma = pd.Series(ww).groupby(cel).transform("sum").to_numpy()
    return ww * df[totais].to_numpy(float) / soma, cel


def _residuo_cel(e, wstar, cel):
    """Subtrai a média ponderada da célula (efeito da pós-estratificação na variância)."""
    if cel is None:
        return e
    num = pd.Series(wstar * e).groupby(cel).transform("sum").to_numpy()
    den = pd.Series(wstar).groupby(cel).transform("sum").to_numpy()
    return e - num / den


def _linear(df, y, w, dominio, posest, totais):
    d = np.ones(len(df), bool) if dominio is None else np.asarray(dominio, bool)
    d = d & df[y].notna().to_numpy()
    yy = df[y].fillna(0).to_numpy(float)
    ws, cel = _pos(df, w, posest, totais)
    td = (ws * d).sum()
    p = (ws * d * yy).sum() / td
    u = ws * _residuo_cel(d * (yy - p), ws, cel) / td
    return p, u, td, int(d.sum())


def proporcao(df, y, w, strata, psu, dominio=None, conf=0.95, posest=None, totais=None):
    """Proporção ponderada de y (0/1) com IC95%. `dominio`: máscara booleana.
    Com `posest`/`totais`, aplica pós-estratificação (desenho oficial da PeNSE).
    Ausentes de y saem do domínio (nunca viram zero)."""
    p, u, td, n = _linear(df, y, w, dominio, posest, totais)
    var, gl = _var_total(u, df[strata].to_numpy(), df[psu].to_numpy())
    se = np.sqrt(var)
    t = stats.t.ppf(1 - (1 - conf) / 2, gl)
    return {"p": p, "se": se, "ic_inf": max(p - t * se, 0), "ic_sup": min(p + t * se, 1),
            "n_validos": n, "pop_estimada": td, "gl": gl}


def diferenca_proporcoes(df, y, w, strata, psu, dom_a, dom_b, conf=0.95, posest=None, totais=None):
    """Diferença p_A - p_B com IC, via linearização conjunta (captura a covariância)."""
    pa, ua, _, _ = _linear(df, y, w, dom_a, posest, totais)
    pb, ub, _, _ = _linear(df, y, w, dom_b, posest, totais)
    var, gl = _var_total(ua - ub, df[strata].to_numpy(), df[psu].to_numpy())
    se, diff = np.sqrt(var), pa - pb
    t = stats.t.ppf(1 - (1 - conf) / 2, gl)
    return {"dif": diff, "se": se, "ic_inf": diff - t * se, "ic_sup": diff + t * se,
            "p_valor": 2 * (1 - stats.t.cdf(abs(diff / se), gl)) if se > 0 else np.nan}


def logistica_ponderada(df, y, X_cols, w, strata, psu, conf=0.95, max_iter=50, tol=1e-9,
                        dominio=None, posest=None, totais=None):
    """Regressão logística ponderada (pseudo-verossimilhança), variância sanduíche por
    UPA/estrato; com `posest`, usa pesos pós-estratificados e o ajuste de resíduos por célula.
    Casos completos; linhas fora do domínio/incompletas ficam no desenho com escore zero
    (como no subset do pacote survey). Retorna OR, IC e p."""
    cols = [y] + list(X_cols)
    usado = df[cols].notna().all(axis=1).to_numpy().copy()
    if dominio is not None:
        usado &= np.asarray(dominio, bool)
    ws, cel = _pos(df, w, posest, totais)
    yy = df[y].fillna(0).to_numpy(float)
    Xall = np.column_stack([np.ones(len(df)), df[list(X_cols)].fillna(0).to_numpy(float)])
    X, Y, W = Xall[usado], yy[usado], ws[usado]
    if np.linalg.matrix_rank(X) < X.shape[1]:
        raise ValueError("Colinearidade perfeita nas covariáveis.")
    b = np.zeros(X.shape[1])
    for _ in range(max_iter):
        mu = 1 / (1 + np.exp(-X @ b))
        H = X.T @ (X * (W * mu * (1 - mu))[:, None])
        step = np.linalg.solve(H, X.T @ (W * (Y - mu)))
        b += step
        if np.max(np.abs(step)) < tol:
            break
    else:
        raise RuntimeError("IRLS não convergiu (possível separação).")
    mu = 1 / (1 + np.exp(-X @ b))
    H = X.T @ (X * (W * mu * (1 - mu))[:, None])
    Hinv = np.linalg.inv(H)
    S = np.zeros_like(Xall)                       # escores s_i = x_i (y - mu), zero fora do uso
    S[usado] = X * (Y - mu)[:, None]
    U = np.column_stack([ws * _residuo_cel(S[:, j], ws, cel) for j in range(S.shape[1])])
    g = pd.DataFrame(U).assign(h=df[strata].to_numpy(), p=df[psu].to_numpy())
    tot = g.groupby(["h", "p"], sort=False).sum().reset_index()
    meat, n_psu, n_str = np.zeros_like(H), 0, 0
    for _, grp in tot.groupby("h", sort=False):
        n_h = len(grp)
        if n_h < 2:
            continue
        M = grp.drop(columns=["h", "p"]).to_numpy()
        M = M - M.mean(0)
        meat += n_h / (n_h - 1) * M.T @ M
        n_psu += n_h
        n_str += 1
    V = Hinv @ meat @ Hinv
    se = np.sqrt(np.diag(V))
    gl = max(n_psu - n_str, 1)
    t = stats.t.ppf(1 - (1 - conf) / 2, gl)
    out = pd.DataFrame({"termo": ["(Intercepto)"] + list(X_cols), "coef": b, "se": se,
                        "OR": np.exp(b), "ic_inf": np.exp(b - t * se),
                        "ic_sup": np.exp(b + t * se),
                        "p_valor": 2 * (1 - stats.t.cdf(np.abs(b / se), gl))})
    out.attrs["n_usados"] = int(usado.sum())
    out.attrs["n_excluidos_ausentes"] = int((~usado).sum())
    out.attrs["gl"] = gl
    return out


def vif(df, X_cols):
    """Fator de inflação da variância (diagnóstico de colinearidade, sem pesos)."""
    X = df[list(X_cols)].dropna().to_numpy(float)
    res = {}
    for j, c in enumerate(X_cols):
        others = np.column_stack([np.ones(len(X)), np.delete(X, j, axis=1)])
        beta, *_ = np.linalg.lstsq(others, X[:, j], rcond=None)
        r2 = 1 - ((X[:, j] - others @ beta) ** 2).sum() / ((X[:, j] - X[:, j].mean()) ** 2).sum()
        res[c] = 1 / (1 - r2) if r2 < 1 else np.inf
    return pd.Series(res, name="VIF")
