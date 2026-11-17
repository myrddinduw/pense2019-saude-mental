"""Lógica do painel (sem Streamlit): tudo o que o app calcula está aqui, para ser testável.

O app (app/app.py) só desenha a interface; os números saem destas funções, que por sua vez
chamam os estimadores validados de src/estatistica.py (desenho amostral completo: estrato,
escola/UPA, peso e pós-estratificação).

Nada aqui faz diagnóstico individual: todas as saídas são estimativas para GRUPOS de alunos.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

import estatistica as es

# Desenho amostral da base analítica (nomes das colunas em data/processed/analitica_pense2019.csv.gz)
D = dict(w="peso", strata="estrato", psu="upa", posest="posest", totais="totais")

TITULO = "Observatório Estatístico de Saúde Mental e Vulnerabilidades Psicossociais"
SUBTITULO = "Escolares brasileiros de 13 a 17 anos · PeNSE 2019 (IBGE/Ministério da Saúde)"

ROTULOS = {"autoavaliacao_neg": "Autoavaliação negativa (≥4 de 5 itens)",
           "triste": "Triste", "ninguem_se_importa": "Sente que ninguém se importa",
           "vida_nao_vale": "Vida não vale a pena", "irritado": "Irritado(a)/nervoso(a)",
           "preocupado": "Muito preocupado(a)", "sem_amigos": "Sem amigos próximos"}

GRUPOS = {"feminino": "Sexo", "escola_privada": "Tipo de escola", "idade_16_17": "Faixa etária",
          "regiao": "Região", "uf": "UF",
          "bullying_sofrido": "Sofreu bullying (colegas, 30 dias)",
          "cyberbullying": "Sofreu cyberbullying (30 dias)",
          "pais_raramente_entendem": "Pais entendem seus problemas?",
          "agressao_familia": "Agressão física por familiar (12 meses)",
          "mae_ate_fund_incompleto": "Escolaridade da mãe",
          "sem_amigos": "Amigos próximos"}

BIN_LABELS = {
    "feminino": {0.0: "Masculino", 1.0: "Feminino"},
    "escola_privada": {0.0: "Pública", 1.0: "Privada"},
    "idade_16_17": {0.0: "13 a 15 anos", 1.0: "16 ou 17 anos"},
    "bullying_sofrido": {0.0: "Não sofreu", 1.0: "Sofreu"},
    "cyberbullying": {0.0: "Não sofreu", 1.0: "Sofreu"},
    "pais_raramente_entendem": {0.0: "Entendem", 1.0: "Raramente/nunca entendem"},
    "agressao_familia": {0.0: "Não sofreu", 1.0: "Sofreu"},
    "mae_ate_fund_incompleto": {0.0: "Fund. completo ou mais", 1.0: "Fund. incompleto ou menos"},
    "sem_amigos": {0.0: "Tem 1 ou mais", 1.0: "Nenhum"},
}

# Rótulos dos preditores na regressão (o "1" de cada variável 0/1)
ROTULO_PREDITOR = {"sem_amigos": "Não tem amigos próximos (vs. tem)", "feminino": "Sexo feminino (vs. masculino)",
                   "idade_16_17": "Ter 16 ou 17 anos (vs. 13-15)",
                   "escola_privada": "Escola privada (vs. pública)",
                   "pais_raramente_entendem": "Pais raramente entendem seus problemas",
                   "agressao_familia": "Agressão física por familiar",
                   "bullying_sofrido": "Sofreu bullying", "cyberbullying": "Sofreu cyberbullying",
                   "mae_ate_fund_incompleto": "Mãe com fundamental incompleto ou menos"}
PREDITORES = list(ROTULO_PREDITOR)

REGIAO_NOMES = {1: "Norte", 2: "Nordeste", 3: "Sudeste", 4: "Sul", 5: "Centro-Oeste"}
UF_NOMES = {11: "Rondônia", 12: "Acre", 13: "Amazonas", 14: "Roraima", 15: "Pará", 16: "Amapá",
            17: "Tocantins", 21: "Maranhão", 22: "Piauí", 23: "Ceará", 24: "Rio Grande do Norte",
            25: "Paraíba", 26: "Pernambuco", 27: "Alagoas", 28: "Sergipe", 29: "Bahia",
            31: "Minas Gerais", 32: "Espírito Santo", 33: "Rio de Janeiro", 35: "São Paulo",
            41: "Paraná", 42: "Santa Catarina", 43: "Rio Grande do Sul", 50: "Mato Grosso do Sul",
            51: "Mato Grosso", 52: "Goiás", 53: "Distrito Federal"}

# Vulnerabilidades psicossociais somadas no "índice de acúmulo" (todas 0/1 e autorrelatadas).
# Análise EXPLORATÓRIA (não estava no protocolo confirmatório).
VULNERABILIDADES = ["sem_amigos", "bullying_sofrido", "cyberbullying",
                    "pais_raramente_entendem", "agressao_familia"]


# ----------------------------------------------------------------------------- formatação
def br(x: float, casas: int = 1) -> str:
    """Número no padrão brasileiro (vírgula decimal, ponto de milhar)."""
    if x is None or (isinstance(x, float) and np.isnan(x)):
        return "—"
    s = f"{x:,.{casas}f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")


def rotulo_grupo(g: str, val) -> str:
    if g == "regiao":
        return REGIAO_NOMES.get(int(val), str(val))
    if g == "uf":
        return UF_NOMES.get(int(val), str(val))
    return BIN_LABELS.get(g, {}).get(float(val), str(val))


def _linha(r: dict, **extra) -> dict:
    return {**extra, "%": 100 * r["p"], "IC95% inf": 100 * r["ic_inf"],
            "IC95% sup": 100 * r["ic_sup"], "n": int(r["n_validos"])}


# ----------------------------------------------------------------------------- descritivas
def proporcao(df, y, dominio):
    return es.proporcao(df, y, dominio=np.asarray(dominio, bool), **D)


def panorama(df: pd.DataFrame, indicadores=None, por: str | None = None) -> pd.DataFrame:
    """Prevalência ponderada (%) com IC95% de cada indicador, no total ou quebrada por um grupo."""
    indicadores = list(ROTULOS) if indicadores is None else indicadores
    dom = df["dom"].to_numpy(bool)
    linhas = []
    for y in indicadores:
        if por is None:
            linhas.append(_linha(proporcao(df, y, dom), Indicador=ROTULOS.get(y, y), codigo=y))
            continue
        for val in sorted(df[por].dropna().unique()):
            m = dom & (df[por] == val).to_numpy()
            linhas.append(_linha(proporcao(df, y, m), Indicador=ROTULOS.get(y, y), codigo=y,
                                 Grupo=rotulo_grupo(por, val)))
    return pd.DataFrame(linhas)


def comparar(df: pd.DataFrame, y: str, g: str):
    """Prevalência de y em cada categoria de g. Se g é 0/1, também devolve a diferença
    (categoria 1 menos categoria 0) em pontos percentuais com IC95% e p-valor, estimada por
    linearização conjunta (leva em conta que os grupos dividem as mesmas escolas)."""
    dom = df["dom"].to_numpy(bool)
    valores = sorted(df[g].dropna().unique())
    tab = pd.DataFrame([_linha(proporcao(df, y, dom & (df[g] == v).to_numpy()),
                               Grupo=rotulo_grupo(g, v), valor=v) for v in valores])
    dif = None
    if set(valores) <= {0.0, 1.0} and len(valores) == 2:
        r = es.diferenca_proporcoes(df, y, dom_a=dom & (df[g] == 1).to_numpy(),
                                    dom_b=dom & (df[g] == 0).to_numpy(), **D)
        dif = {"dif_pp": 100 * r["dif"], "ic_inf": 100 * r["ic_inf"], "ic_sup": 100 * r["ic_sup"],
               "p_valor": r["p_valor"], "grupo_1": rotulo_grupo(g, 1.0), "grupo_0": rotulo_grupo(g, 0.0)}
    return tab, dif


def holm(pvals) -> np.ndarray:
    """Correção de Holm-Bonferroni para comparações múltiplas (controla o erro tipo I global)."""
    p = np.asarray(pvals, float)
    m = len(p)
    ordem = np.argsort(p)
    aj = np.empty(m)
    acum = 0.0
    for i, idx in enumerate(ordem):
        acum = max(acum, min(1.0, (m - i) * p[idx]))
        aj[idx] = acum
    return aj


def ranking_uf(df: pd.DataFrame, y: str, alfa: float = 0.05):
    """Prevalência de y em cada UF e diferença em relação ao Brasil (UF − Brasil), com IC95%,
    p-valor bruto e ajustado por Holm (27 testes). Classifica cada UF em
    'Acima do Brasil', 'Abaixo do Brasil' ou 'Sem diferença significativa' pelo p ajustado.
    Devolve (tabela ordenada da maior para a menor prevalência, estimativa do Brasil)."""
    dom = df["dom"].to_numpy(bool)
    brasil = proporcao(df, y, dom)
    linhas = []
    for uf in sorted(df["uf"].dropna().unique()):
        m = dom & (df["uf"] == uf).to_numpy()
        r = proporcao(df, y, m)
        d = es.diferenca_proporcoes(df, y, dom_a=m, dom_b=dom, **D)
        linhas.append(_linha(r, UF=rotulo_grupo("uf", uf), cod_uf=int(uf),
                             Região=REGIAO_NOMES.get(int(uf) // 10, "")) |
                      {"dif_pp": 100 * d["dif"], "p_valor": d["p_valor"]})
    t = pd.DataFrame(linhas)
    t["p_holm"] = holm(t["p_valor"].fillna(1).to_numpy())
    t["Situação"] = np.where(t.p_holm >= alfa, "Sem diferença significativa",
                             np.where(t.dif_pp > 0, "Acima do Brasil", "Abaixo do Brasil"))
    return t.sort_values("%", ascending=False).reset_index(drop=True), brasil


def n_vulnerabilidades(df: pd.DataFrame, cols=VULNERABILIDADES, teto: int = 4) -> pd.Series:
    """Quantas vulnerabilidades o aluno relatou (0 a `teto`, com `teto` = 'teto ou mais').
    Ausente se faltar resposta em qualquer item (nunca conta ausente como zero)."""
    completo = df[cols].notna().all(axis=1)
    return df[cols].sum(axis=1).clip(upper=teto).where(completo)


def gradiente_vulnerabilidades(df: pd.DataFrame, y: str = "autoavaliacao_neg", teto: int = 4):
    """Prevalência de y segundo o nº de vulnerabilidades acumuladas, e a % de alunos em cada faixa."""
    dom = df["dom"].to_numpy(bool)
    k = n_vulnerabilidades(df, teto=teto)
    aux = df.assign(_k=k)
    linhas = []
    for v in range(teto + 1):
        rot = f"{v} ou mais" if v == teto else str(v)
        r = proporcao(df, y, dom & (k == v).to_numpy())
        aux["_faixa"] = (k == v).astype(float).where(k.notna())
        dist = proporcao(aux, "_faixa", dom)
        linhas.append(_linha(r, Vulnerabilidades=rot) | {"% dos alunos": 100 * dist["p"]})
    return pd.DataFrame(linhas)


# ----------------------------------------------------------------------------- modelos
def modelo(df: pd.DataFrame, y: str, X: list[str]) -> pd.DataFrame:
    """Regressão logística com desenho amostral; devolve uma linha por preditor (sem intercepto)."""
    r = es.logistica_ponderada(df, y, X, dominio=df["dom"].to_numpy(bool), **D)
    n = r.attrs["n_usados"]
    r = r[r.termo != "(Intercepto)"].copy()
    r["Fator"] = r.termo.map(lambda t: ROTULO_PREDITOR.get(t, t))
    r["Leitura"] = [interpretar_or(*a) for a in r[["OR", "ic_inf", "ic_sup", "p_valor"]].to_numpy()]
    r["n_usados"] = n
    return r.sort_values("OR", ascending=False).reset_index(drop=True)


def interpretar_or(OR: float, ic_inf: float, ic_sup: float, p: float) -> str:
    """Frase em linguagem simples para uma razão de chances ajustada."""
    ic = f"(IC95% {br(ic_inf, 2)} a {br(ic_sup, 2)})"
    if ic_inf <= 1 <= ic_sup:
        return f"Sem evidência de associação após o ajuste {ic}."
    if OR > 1:
        return f"Chance {br(OR, 2)} vezes a do grupo de comparação {ic}."
    return f"Chance {br(100 * (1 - OR), 0)}% menor que a do grupo de comparação {ic}."


def robustez_sem_amigos(caminho_csv) -> pd.DataFrame:
    """OR de 'sem amigos próximos' em cada modelo pré-calculado (docs/resultados_modelos.csv)."""
    R = pd.read_csv(caminho_csv)
    R = R[R.termo == "sem_amigos"][["modelo", "desfecho", "OR", "ic_inf", "ic_sup", "p_valor", "n_usados"]]
    return R.reset_index(drop=True)
