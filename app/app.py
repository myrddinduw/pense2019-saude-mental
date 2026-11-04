"""Observatório Estatístico de Saúde Mental e Vulnerabilidades Psicossociais (protótipo).

STATUS: a lógica estatística chamada aqui (src/estatistica.py) está testada e validada contra as
tabelas do IBGE. A interface em si NÃO foi executada no ambiente de desenvolvimento (streamlit e
plotly não puderam ser instalados lá). Testar localmente: `streamlit run app/app.py`.
Ferramenta de exploração estatística; não realiza diagnóstico individual nem sugere causalidade.
"""
import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))
import estatistica as es  # noqa: E402

VERMELHO = "#7A1020"
D = dict(w="peso", strata="estrato", psu="upa", posest="posest", totais="totais")
ROTULOS = {"sem_amigos": "Sem amigos próximos", "preocupado": "Muito preocupado(a)",
           "triste": "Triste", "ninguem_se_importa": "Sente que ninguém se importa",
           "irritado": "Irritado(a)/nervoso(a)", "vida_nao_vale": "Vida não vale a pena",
           "autoavaliacao_neg": "Autoavaliação negativa (>=4 de 5)"}
GRUPOS = {"feminino": "Sexo", "escola_privada": "Dependência administrativa",
          "idade_16_17": "Faixa etária", "regiao": "Região", "uf": "UF",
          "bullying_sofrido": "Sofreu bullying (colegas)", "cyberbullying": "Sofreu cyberbullying",
          "pais_raramente_entendem": "Entendimento dos pais", "agressao_familia": "Agressão familiar (12m)",
          "mae_ate_fund_incompleto": "Escolaridade da mãe"}
REGIAO_NOMES = {1: "Norte", 2: "Nordeste", 3: "Sudeste", 4: "Sul", 5: "Centro-Oeste"}
UF_NOMES = {11: "RO", 12: "AC", 13: "AM", 14: "RR", 15: "PA", 16: "AP", 17: "TO", 21: "MA",
            22: "PI", 23: "CE", 24: "RN", 25: "PB", 26: "PE", 27: "AL", 28: "SE", 29: "BA",
            31: "MG", 32: "ES", 33: "RJ", 35: "SP", 41: "PR", 42: "SC", 43: "RS",
            50: "MS", 51: "MT", 52: "GO", 53: "DF"}
BIN_LABELS = {
    "feminino": {0.0: "Masculino", 1.0: "Feminino"},
    "escola_privada": {0.0: "Pública", 1.0: "Privada"},
    "idade_16_17": {0.0: "13 a 15 anos", 1.0: "16 ou 17 anos"},
    "bullying_sofrido": {0.0: "Não sofreu", 1.0: "Sofreu"},
    "cyberbullying": {0.0: "Não sofreu", 1.0: "Sofreu"},
    "pais_raramente_entendem": {0.0: "Entendem", 1.0: "Raramente/nunca entendem"},
    "agressao_familia": {0.0: "Não sofreu", 1.0: "Sofreu"},
    "mae_ate_fund_incompleto": {0.0: "Fund. completo ou mais", 1.0: "Fund. incompleto ou menos"},
}


def rotulo_grupo(g, val):
    if g == "regiao":
        return REGIAO_NOMES.get(int(val), str(val))
    if g == "uf":
        return UF_NOMES.get(int(val), str(val))
    return BIN_LABELS.get(g, {}).get(val, str(val))
PAGINAS = ["1. Pesquisa", "2. Panorama", "3. Comparações", "4. Resultados", "5. Metodologia"]

st.set_page_config(page_title="Observatório de Saúde Mental", layout="wide")
st.markdown(f"<style>h1,h2,h3{{color:{VERMELHO}}}</style>", unsafe_allow_html=True)
pag = st.sidebar.radio("Navegação", PAGINAS)


@st.cache_data
def carregar(arq):
    return pd.read_csv(arq)


padrao = RAIZ / "data" / "processed" / "analitica_pense2019.csv.gz"
arq = st.sidebar.file_uploader("Base analítica (CSV ou CSV.GZ)", type=["csv", "gz"])
df = carregar(arq) if arq else (carregar(padrao) if padrao.exists() else None)
if df is not None and "SINTETICO" in df.columns:
    st.error("DADOS SINTÉTICOS DE TESTE. Nenhum número abaixo é resultado científico.")


def prop(y, dom):
    return es.proporcao(df, y, dominio=dom, **D)


if pag == PAGINAS[0]:
    st.title("Saúde mental de escolares: fatores psicossociais associados")
    st.write("**Pergunta:** ter poucos amigos próximos e outras vulnerabilidades psicossociais se associam "
             "a maior sofrimento psicológico em escolares de 13 a 17 anos, após ajuste por sexo, idade e tipo de escola?")
    st.write("**Fonte:** PeNSE 2019 (IBGE/Ministério da Saúde), microdados públicos. A PeNSE não mede "
             "ansiedade social; os desfechos são indicadores de sofrimento psicológico autorrelatado.")
elif df is None:
    st.info("Carregue a base analítica na barra lateral para ver as páginas 2 a 4.")
elif pag == PAGINAS[1]:
    st.header("Panorama (alunos frequentes de 13 a 17 anos, Brasil)")
    linhas = []
    for c, rot in ROTULOS.items():
        r = prop(c, df["dom"])
        linhas.append({"Indicador": rot, "%": 100 * r["p"], "IC95% inf": 100 * r["ic_inf"],
                       "IC95% sup": 100 * r["ic_sup"], "n válidos": r["n_validos"]})
    t = pd.DataFrame(linhas)
    st.dataframe(t.round(1), hide_index=True)
    st.plotly_chart(px.bar(t, x="%", y="Indicador", orientation="h",
                           color_discrete_sequence=[VERMELHO]), use_container_width=True)
    st.caption("Estimativas ponderadas com pós-estratificação, estratos e escolas (UPA). "
               "Ausências excluídas (casos completos por indicador).")
elif pag == PAGINAS[2]:
    st.header("Comparações entre grupos")
    y = st.selectbox("Indicador", list(ROTULOS), format_func=ROTULOS.get)
    g = st.selectbox("Grupo", list(GRUPOS), format_func=GRUPOS.get)
    linhas = []
    for val in sorted(df[g].dropna().unique(), key=lambda v: rotulo_grupo(g, v)):
        r = prop(y, df["dom"] & (df[g] == val))
        linhas.append({"Grupo": rotulo_grupo(g, val), "%": 100 * r["p"], "IC95% inf": 100 * r["ic_inf"],
                       "IC95% sup": 100 * r["ic_sup"], "n": r["n_validos"]})
    st.dataframe(pd.DataFrame(linhas).round(1), hide_index=True)
    st.caption("Diferenças descritivas; associação não implica causalidade.")
elif pag == PAGINAS[3]:
    st.header("Razões de chances ajustadas (regressão logística com desenho amostral)")
    y = st.selectbox("Desfecho", [c for c in ROTULOS if c != "sem_amigos"], format_func=ROTULOS.get)
    cand = ["sem_amigos", "feminino", "idade_16_17", "escola_privada", "pais_raramente_entendem",
            "agressao_familia", "bullying_sofrido", "cyberbullying"]
    X = st.multiselect("Preditores (0/1)", cand, default=cand)
    if y == "autoavaliacao_neg" and "ninguem_se_importa" in X:
        st.warning("'Ninguém se importa' é item do desfecho composto: associação circular.")
    if X:
        try:
            res = es.logistica_ponderada(df, y, X, dominio=df["dom"], **D)
            res = res[res.termo != "(Intercepto)"]
            st.dataframe(res[["termo", "OR", "ic_inf", "ic_sup", "p_valor"]].round(3), hide_index=True)
            st.caption(f"Casos completos no domínio: n={res.attrs['n_usados']}. OR = razão de chances; "
                       "estudo transversal, sem causalidade.")
        except Exception as e:  # noqa: BLE001
            st.warning(f"Modelo não pôde ser ajustado: {e}")
else:
    st.header("Metodologia e limitações")
    st.markdown("""
- Dados: microdados da PeNSE 2019 (IBGE). Domínio: alunos frequentes (IND_EXPANSAO = 1) de 13 a 17 anos.
- Desenho: escola = UPA dentro de estrato, peso inicial, pós-estratificação (POSEST) como no exemplo oficial do IBGE.
- Validação: 2.760 estimativas replicadas contra as tabelas oficiais (93% a menos de 0,1 p.p.).
- Delineamento transversal: associações, não causas. Autorrelato; viés de memória (30 dias).
- Exclui adolescentes fora da escola (possivelmente mais vulneráveis).
- Indicadores de item único e um composto; **não são diagnóstico** de ansiedade, depressão ou fobia social.
- Casos completos; ausências nunca foram trocadas por zero nas análises.
""")
