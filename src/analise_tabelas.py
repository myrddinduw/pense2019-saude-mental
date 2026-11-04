"""Análise descritiva a partir das tabelas oficiais do IBGE (PeNSE 2019, Tema 12).

Limite: são estimativas JÁ publicadas (com IC95%). Diferenças entre domínios usam
EP = (IC_sup - IC_inf) / (2*1,96) e assumem independência entre os domínios
(aproximação; os domínios compartilham escolas, então o EP real da diferença tende a ser
menor que o calculado, ou seja, o teste é conservador). Correlações entre UFs são
ECOLÓGICAS e não valem para indivíduos.
"""
import sys

import numpy as np
import pandas as pd
from scipy import stats

Z = 1.959964


def _se(r):
    return (r.ic_sup - r.ic_inf) / (2 * Z)


def tabela_brasil(d):
    b = d[(d.nivel == "regiao_idade") & (d.local == "Brasil") & (d.faixa_idade == "13 a 17 anos")]
    return b


def diferenca(d, g1, g2, nivel="regiao_idade", local="Brasil", faixa="13 a 17 anos"):
    """Diferença g1 - g2 (pontos percentuais), z aproximado, por indicador."""
    base = d[(d.nivel == nivel) & (d.local == local) & (d.faixa_idade == faixa)]
    out = []
    for ind, g in base.groupby("indicador"):
        a, b = g[g.grupo == g1].iloc[0], g[g.grupo == g2].iloc[0]
        dif = a.p - b.p
        se = np.hypot(_se(a), _se(b))
        out.append({"indicador": ind, f"{g1}": a.p, f"{g2}": b.p, "dif_pp": dif,
                    "ic_inf": dif - Z * se, "ic_sup": dif + Z * se,
                    "razao": a.p / b.p, "p_aprox": 2 * (1 - stats.norm.cdf(abs(dif / se)))})
    return pd.DataFrame(out).set_index("indicador")


def idade(d):
    out = []
    for ind, g in d[(d.nivel == "regiao_idade") & (d.local == "Brasil") & (d.grupo == "Total")].groupby("indicador"):
        a, b = g[g.faixa_idade == "16 e 17 anos"].iloc[0], g[g.faixa_idade == "13 a 15 anos"].iloc[0]
        dif, se = a.p - b.p, np.hypot(_se(a), _se(b))
        out.append({"indicador": ind, "13_15": b.p, "16_17": a.p, "dif_pp": dif,
                    "ic_inf": dif - Z * se, "ic_sup": dif + Z * se,
                    "p_aprox": 2 * (1 - stats.norm.cdf(abs(dif / se)))})
    return pd.DataFrame(out).set_index("indicador")


def ufs(d):
    u = d[(d.nivel == "uf") & (~d.eh_regiao) & (d.local != "Brasil") & (d.grupo == "Total")].copy()
    u["local"] = u["local"].str.strip()
    return u


def extremos(d):
    """Maior e menor UF por indicador e se os IC95% se sobrepõem."""
    u = ufs(d)
    out = []
    for ind, g in u.groupby("indicador"):
        g = g.sort_values("p")
        lo, hi = g.iloc[0], g.iloc[-1]
        out.append({"indicador": ind, "menor_UF": lo.local, "menor_p": lo.p, "maior_UF": hi.local,
                    "maior_p": hi.p, "ICs_nao_se_sobrepoem": bool(hi.ic_inf > lo.ic_sup)})
    return pd.DataFrame(out).set_index("indicador")


def correlacao_ecologica(d):
    u = ufs(d).pivot(index="local", columns="indicador", values="p")
    rho = u.corr(method="spearman")
    n = len(u)
    return rho, n


def regioes(d, indicador="Autoavaliação negativa"):
    r = d[(d.nivel == "regiao_idade") & (d.faixa_idade == "13 a 17 anos") & (d.grupo == "Total")
          & (d.indicador == indicador)]
    return r[["local", "p", "ic_inf", "ic_sup"]].set_index("local")


if __name__ == "__main__":
    d = pd.read_csv(sys.argv[1])
    pd.set_option("display.width", 200)
    print("== Mulher - Homem (pp) =="); print(diferenca(d, "Mulher", "Homem").round(3))
    print("== Pública - Privada (pp) =="); print(diferenca(d, "Pública", "Privada").round(3))
    print("== 16-17 vs 13-15 =="); print(idade(d).round(3))
    print("== Extremos entre UFs =="); print(extremos(d).round(1))
    rho, n = correlacao_ecologica(d); print(f"== Spearman entre UFs (n={n}) =="); print(rho.round(2))
    print("== Regiões, autoavaliação negativa =="); print(regioes(d).round(1))
