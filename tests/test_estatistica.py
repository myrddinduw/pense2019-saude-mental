import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
import estatistica as es  # noqa: E402
from dados_sinteticos import gerar  # noqa: E402


def test_proporcao_reduz_a_srs():
    """Pesos iguais, cada obs. = 1 UPA, 1 estrato: SE deve ser sqrt(p(1-p)/n) * sqrt(n/(n-1))."""
    rng = np.random.default_rng(0)
    n = 400
    df = pd.DataFrame({"y": rng.binomial(1, 0.3, n), "w": 1.0, "h": 1, "p": range(n)})
    r = es.proporcao(df, "y", "w", "h", "p")
    p = df.y.mean()
    esperado = np.sqrt(p * (1 - p) / n * n / (n - 1))
    assert abs(r["p"] - p) < 1e-12
    assert abs(r["se"] - esperado) < 1e-10


def test_proporcao_ponderada_manual():
    df = pd.DataFrame({"y": [1, 0, 1, 0], "w": [10, 10, 30, 50.0],
                       "h": [1, 1, 2, 2], "p": [1, 2, 3, 4]})
    r = es.proporcao(df, "y", "w", "h", "p")
    assert abs(r["p"] - 0.4) < 1e-12  # (10+30)/100


def test_ausentes_nao_viram_zero():
    df = pd.DataFrame({"y": [1, np.nan, 0, 1], "w": 1.0, "h": 1, "p": range(4)})
    r = es.proporcao(df, "y", "w", "h", "p")
    assert r["n_validos"] == 3 and abs(r["p"] - 2 / 3) < 1e-12


def test_logistica_recupera_verdade_conhecida():
    beta = (-1.2, 0.8, 0.5)
    df = gerar(n_estratos=60, psu_por_estrato=8, alunos_por_psu=40, seed=1, beta=beta)
    r = es.logistica_ponderada(df, "sofrimento", ["sem_amigos", "feminino"],
                               "peso", "estrato", "upa").set_index("termo")
    assert abs(r.loc["feminino", "coef"] - 0.5) < 0.15
    assert abs(r.loc["sem_amigos", "coef"] - 0.8) < 0.35
    assert (r["ic_inf"] < r["OR"]).all() and (r["OR"] < r["ic_sup"]).all()


def test_logistica_contra_solucao_analitica_2x2():
    """Com um preditor binário e pesos iguais, OR = razão de chances da tabela 2x2."""
    rng = np.random.default_rng(3)
    n = 2000
    x = rng.binomial(1, 0.4, n)
    y = rng.binomial(1, np.where(x == 1, 0.35, 0.2))
    df = pd.DataFrame({"y": y, "x": x, "w": 1.0, "h": 1, "p": range(n)})
    r = es.logistica_ponderada(df, "y", ["x"], "w", "h", "p").set_index("termo")
    a, b = ((x == 1) & (y == 1)).sum(), ((x == 1) & (y == 0)).sum()
    c, d = ((x == 0) & (y == 1)).sum(), ((x == 0) & (y == 0)).sum()
    assert abs(r.loc["x", "OR"] - (a * d) / (b * c)) < 1e-6


def test_diferenca_simetrica():
    df = gerar(seed=5)
    fem = df.feminino == 1
    a = es.diferenca_proporcoes(df, "sofrimento", "peso", "estrato", "upa", fem, ~fem)
    b = es.diferenca_proporcoes(df, "sofrimento", "peso", "estrato", "upa", ~fem, fem)
    assert abs(a["dif"] + b["dif"]) < 1e-12 and abs(a["se"] - b["se"]) < 1e-12


def test_posestratificacao_ponto_manual():
    """Estimador pós-estratificado = soma_c N_c * media_ponderada_c(y) / soma N_c."""
    df = pd.DataFrame({"y": [1, 0, 1, 1, 0, 0], "w": [1.0, 3, 2, 2, 5, 1],
                       "h": [1, 1, 1, 2, 2, 2], "p": [1, 2, 3, 4, 5, 6],
                       "cel": ["a", "a", "a", "b", "b", "b"], "N": [100, 100, 100, 50, 50, 50]})
    r = es.proporcao(df, "y", "w", "h", "p", posest="cel", totais="N")
    ma = (1 * 1 + 0 * 3 + 1 * 2) / 6
    mb = (1 * 2 + 0 * 5 + 0 * 1) / 8
    assert abs(r["p"] - (100 * ma + 50 * mb) / 150) < 1e-12


def test_logistica_com_posest_igual_or_2x2():
    rng = np.random.default_rng(11)
    n = 3000
    df = pd.DataFrame({"x": rng.binomial(1, 0.3, n), "w": rng.uniform(1, 5, n),
                       "h": rng.integers(0, 10, n), "cel": rng.integers(0, 4, n)})
    df["p"] = df.h * 100 + rng.integers(0, 8, n)
    df["y"] = rng.binomial(1, np.where(df.x == 1, 0.4, 0.25))
    df["N"] = df.cel.map({0: 4000, 1: 6000, 2: 5000, 3: 3000})
    r = es.logistica_ponderada(df, "y", ["x"], "w", "h", "p", posest="cel", totais="N").set_index("termo")
    ws = df.w * df.N / df.groupby("cel").w.transform("sum")
    t = lambda x, y: (ws * (df.x == x) * (df.y == y)).sum()
    assert abs(r.loc["x", "OR"] - (t(1, 1) * t(0, 0)) / (t(1, 0) * t(0, 1))) < 1e-6


def test_validacao_contra_tabelas_ibge_se_disponivel():
    caminho = os.path.join(os.path.dirname(__file__), "..", "docs", "validacao_microdados_vs_tabelas_ibge.csv")
    if not os.path.exists(caminho):
        return
    R = pd.read_csv(caminho)
    assert len(R) == 2760 and (R.d_p.abs() < 0.1).mean() > 0.9 and R.d_p.abs().max() < 0.5
