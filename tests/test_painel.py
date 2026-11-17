"""Testes da lógica do painel (src/painel.py) com dados sintéticos de verdade conhecida."""
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
import painel as pn  # noqa: E402


def _base(seed=0, n_uf=4, escolas=6, alunos=60):
    """Base no formato da base analítica, com UFs que diferem de propósito."""
    rng = np.random.default_rng(seed)
    linhas = []
    for i, uf in enumerate([11, 21, 35, 43][:n_uf]):
        p_uf = [0.10, 0.10, 0.10, 0.40][i]          # só a UF 43 é bem diferente
        for e in range(escolas):
            for _ in range(alunos):
                v = rng.binomial(1, [0.05, 0.2, 0.1, 0.15, 0.1])
                y = rng.binomial(1, min(0.95, p_uf + 0.1 * v.sum()))
                linhas.append([uf * 100 + e % 2, uf * 1000 + e, rng.uniform(1, 3), uf, uf // 10,
                               rng.binomial(1, 0.5), y, *v])
    df = pd.DataFrame(linhas, columns=["estrato", "upa", "peso", "uf", "regiao", "feminino",
                                       "autoavaliacao_neg", *pn.VULNERABILIDADES]).astype(float)
    df["dom"] = True
    df["posest"] = "c" + df.uf.astype(int).astype(str)
    df["totais"] = df.groupby("posest").peso.transform("sum") * 10
    return df


def test_br_formata_padrao_brasileiro():
    assert pn.br(1234.567, 1) == "1.234,6"
    assert pn.br(0.5, 2) == "0,50"
    assert pn.br(float("nan")) == "—"


def test_holm_manual():
    # p ordenados: 0,01 (x3) 0,02 (x2) 0,03 (x1) -> 0,03; 0,04; 0,04 (monotonia)
    aj = pn.holm([0.03, 0.01, 0.02])
    assert np.allclose(aj, [0.04, 0.03, 0.04])
    assert (pn.holm([0.5, 0.9]) <= 1).all()


def test_n_vulnerabilidades_nao_conta_ausente_como_zero():
    df = pd.DataFrame({c: [1.0, 0.0, np.nan] for c in pn.VULNERABILIDADES})
    k = pn.n_vulnerabilidades(df, teto=4)
    assert k.iloc[0] == 4 and k.iloc[1] == 0 and np.isnan(k.iloc[2])


def test_gradiente_cresce_e_distribuicao_soma_100():
    g = pn.gradiente_vulnerabilidades(_base())
    assert abs(g["% dos alunos"].sum() - 100) < 1e-6
    assert g["%"].iloc[0] < g["%"].iloc[2]          # verdade conhecida: risco sobe com vulnerabilidades


def test_ranking_uf_identifica_uf_diferente():
    t, brasil = pn.ranking_uf(_base(), "autoavaliacao_neg")
    assert len(t) == 4 and t["%"].is_monotonic_decreasing
    assert t.iloc[0]["cod_uf"] == 43 and t.iloc[0]["Situação"] == "Acima do Brasil"
    assert (t.p_holm >= t.p_valor - 1e-12).all()
    assert 0 < brasil["p"] < 1


def test_comparar_binario_traz_diferenca_coerente():
    df = _base()
    tab, dif = pn.comparar(df, "autoavaliacao_neg", "cyberbullying")
    p1 = tab.loc[tab.valor == 1, "%"].item()
    p0 = tab.loc[tab.valor == 0, "%"].item()
    assert abs(dif["dif_pp"] - (p1 - p0)) < 1e-9 and dif["ic_inf"] < dif["dif_pp"] < dif["ic_sup"]
    _, dif_reg = pn.comparar(df, "autoavaliacao_neg", "regiao")
    assert dif_reg is None                            # grupo não binário: só a tabela


def test_interpretar_or():
    assert "Sem evidência" in pn.interpretar_or(1.1, 0.9, 1.3, 0.3)
    assert "2,00 vezes" in pn.interpretar_or(2.0, 1.5, 2.6, 0.001)
    assert "20% menor" in pn.interpretar_or(0.8, 0.7, 0.9, 0.001)


def test_robustez_le_resultados_reais():
    caminho = os.path.join(os.path.dirname(__file__), "..", "docs", "resultados_modelos.csv")
    r = pn.robustez_sem_amigos(caminho).set_index("modelo")
    assert abs(r.loc["M3 completo", "OR"] - 1.77) < 0.01
