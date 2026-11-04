"""Pipeline: microdados PeNSE 2019 (IBGE) -> base analítica.

Nomes de colunas e códigos VERIFICADOS no 'Dicionario_PENSE2019_Microdados.xls' (IBGE, 2022):
  sexo B01001A (1 Homem, 2 Mulher) | idade B01003 (2 = 13-15, 3 = 16-17) | cor B01002
  escolaridade da mãe B01008B | pais entendem problemas B07004 | bullying B07007A | cyberbullying B07013
  agressão por mãe/pai/responsável B09003A
  amigos próximos B12003 (1 = nenhum) | B12004 preocupado | B12005 triste | B12006 ninguém se preocupa
  B12007 irritado | B12008 vida não vale a pena  (4 = na maioria das vezes, 5 = sempre)
  códigos de não resposta: -2 (abandono) e 9 (sem resposta); vazio = registro sem questionário.
Desenho (exemplo oficial em R/SAS do IBGE): UPA = ESCOLA aninhada em ESTRATO; peso = PESO_INICIAL;
pós-estratificação por POSEST com totais TOTAIS_POSEST; domínio de estimação IND_EXPANSAO == 1.
"""
from __future__ import annotations

import pandas as pd

COLUNAS = ["REGIAO", "UF", "MUNICIPIO_CAP", "TIPO_MUNIC", "SITUACAO", "DEP_ADMIN", "ESCOLA",
           "ANO_TURMA", "B01001A", "B01003", "B01002", "B01008B", "B07002", "B07004", "B07007A",
           "B07013", "B09003A", "B12003", "B12004", "B12005", "B12006", "B12007", "B12008",
           "ESTRATO", "IND_EXPANSAO", "PESO_INICIAL", "PESO_ALUNO_FREQ", "POSEST", "TOTAIS_POSEST"]
FREQ = {"preocupado": "B12004", "triste": "B12005", "ninguem_se_importa": "B12006",
        "irritado": "B12007", "vida_nao_vale": "B12008"}
AUSENTE = (-2, 9)


def _limpa(s: pd.Series) -> pd.Series:
    """Códigos de não resposta -> NaN (nunca zero)."""
    return s.where(~s.isin(AUSENTE))


def construir_base(bruto: pd.DataFrame, limite_autoavaliacao: int = 4, relatorio: list | None = None,
                   convencao_ibge: bool = False):
    """convencao_ibge=False (padrão, usada nas análises): 'sem resposta' (9) e abandono (-2) viram NaN
    (casos completos). convencao_ibge=True (apenas para REPLICAR as tabelas do IBGE): o IBGE exclui
    abandono (-2) do denominador e mantém 'sem resposta' (9) no denominador como não-positivo
    (verificado: reproduz as tabelas a menos de 0,01 ponto percentual)."""
    rel = relatorio if relatorio is not None else []
    df = bruto[COLUNAS].copy()
    rel.append(f"Registros brutos: {len(df)} (IND_EXPANSAO=1: {(df.IND_EXPANSAO == 1).sum()})")
    out = pd.DataFrame({"estrato": df.ESTRATO, "upa": df.ESCOLA, "peso": df.PESO_INICIAL,
                        "posest": df.POSEST, "totais": df.TOTAIS_POSEST,
                        "uf": df.UF, "regiao": df.REGIAO, "dep_admin": df.DEP_ADMIN})
    # Domínio: alunos frequentes (IND_EXPANSAO = 1) de 13 a 17 anos. NÃO se descartam linhas:
    # o domínio é aplicado na estimação, como manda o desenho amostral.
    out["dom"] = (df.IND_EXPANSAO == 1) & df.B01003.isin([2, 3])
    rel.append(f"Domínio 13-17 anos frequentes: {int(out.dom.sum())} registros")
    sexo = _limpa(df.B01001A)
    out["feminino"] = (sexo == 2).where(sexo.notna())
    out["idade_16_17"] = (df.B01003 == 3).where(df.B01003.isin([2, 3]))
    out["escola_privada"] = (df.DEP_ADMIN == 2).astype(float)
    def _bin(col, pos):
        x = df[col]
        valido = x.notna() & (x != -2) if convencao_ibge else _limpa(x).notna()
        return x.isin(pos).where(valido)
    out["sem_amigos"] = _bin("B12003", [1])
    for nome, col in FREQ.items():
        out[nome] = _bin(col, [4, 5])
    npos = out[list(FREQ)].sum(axis=1)
    # Indicador composto: exige as 5 respostas válidas (9 e -2 excluem), em ambas as convenções
    # (verificado: reproduz o IBGE a menos de 0,01 pp).
    completo = pd.concat([_limpa(df[c]).notna() for c in FREQ.values()], axis=1).all(axis=1)
    out["autoavaliacao_neg"] = (npos >= limite_autoavaliacao).where(completo)
    mae = _limpa(df.B01008B)
    out["mae_ate_fund_incompleto"] = mae.isin([1, 2]).where(mae.notna() & (mae != 8))
    ent = _limpa(df.B07004)
    out["pais_raramente_entendem"] = ent.isin([1, 2]).where(ent.notna())
    bu = _limpa(df.B07007A)
    out["bullying_sofrido"] = (bu >= 2).where(bu.notna())
    cy = _limpa(df.B07013)
    out["cyberbullying"] = (cy == 1).where(cy.notna())
    ag = _limpa(df.B09003A)
    out["agressao_familia"] = (ag >= 2).where(ag.notna())
    for c in ["sem_amigos"] + list(FREQ) + ["autoavaliacao_neg"]:
        rel.append(f"{c}: {int(out.loc[out.dom, c].isna().sum())} ausentes no domínio (não respondidos)")
    out = out.astype({c: "float" for c in out.columns if out[c].dtype == object or out[c].dtype == bool and c != "dom"})
    if (out.peso <= 0).any() or out.peso.isna().any():
        raise ValueError("Pesos inválidos.")
    return out


def carregar(caminho_csv: str, **kw) -> pd.DataFrame:
    return construir_base(pd.read_csv(caminho_csv, usecols=COLUNAS), **kw)
