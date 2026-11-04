"""Lê o arquivo 'Tema 12 - Saúde Mental' (PeNSE 2019, IBGE, tabelas agregadas) e gera um CSV tidy.

Layout verificado nas 21 abas (12.1.1 ... 12.7.3): coluna 0 = rótulo da linha; a partir da coluna 1,
cinco blocos de 3 colunas (estimativa, limite inferior, limite superior do IC95%) para:
Total, Homem, Mulher, Pública, Privada. Valores em %.
Aba .1 = grupos de idade x Grandes Regiões; .2 = Regiões e UFs; .3 = Municípios das capitais.
"""
import sys

import pandas as pd

INDICADORES = {
    "12.1": "Sem amigos próximos", "12.2": "Muito preocupado(a)", "12.3": "Triste",
    "12.4": "Ninguém se preocupa comigo", "12.5": "Irritado(a)/nervoso(a)",
    "12.6": "Vida não vale a pena", "12.7": "Autoavaliação negativa",
}
GRUPOS = ["Total", "Homem", "Mulher", "Pública", "Privada"]
REGIOES = {"Norte", "Nordeste", "Sudeste", "Sul", "Centro-Oeste"}
NIVEL = {"1": "regiao_idade", "2": "uf", "3": "capital"}


def ler(caminho: str) -> pd.DataFrame:
    x = pd.ExcelFile(caminho)
    linhas = []
    for aba in x.sheet_names:
        ind, nivel = INDICADORES[aba[:4]], NIVEL[aba[-1]]
        d = x.parse(aba, header=None)
        faixa = "13 a 17 anos"
        for _, r in d.iterrows():
            rot = r.iloc[0]
            if not isinstance(rot, str) or rot.startswith("Fonte"):
                continue
            rot = rot.strip()
            est = pd.to_numeric(r.iloc[1], errors="coerce")
            if pd.isna(est):
                if rot.endswith("anos"):
                    faixa = rot
                continue
            for k, g in enumerate(GRUPOS):
                p, lo, hi = (pd.to_numeric(r.iloc[1 + 3 * k + j], errors="coerce") for j in range(3))
                linhas.append({"indicador": ind, "nivel": nivel, "faixa_idade": faixa if nivel == "regiao_idade" else "13 a 17 anos",
                               "local": rot, "eh_regiao": rot in REGIOES, "grupo": g,
                               "p": p, "ic_inf": lo, "ic_sup": hi})
    return pd.DataFrame(linhas)


if __name__ == "__main__":
    df = ler(sys.argv[1])
    df.to_csv(sys.argv[2], index=False)
    print(len(df), "linhas;", df["p"].isna().sum(), "estimativas ausentes")
