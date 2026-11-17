"""Observatório Estatístico de Saúde Mental e Vulnerabilidades Psicossociais (protótipo, FMU TECH Inovação 2026.2).

Interface Streamlit. Toda a conta é feita em src/painel.py (testado em tests/test_painel.py), que
usa os estimadores de src/estatistica.py (validados contra 2.760 números oficiais do IBGE).
Rodar localmente: `streamlit run app/app.py`.
Verificação no ambiente de desenvolvimento: todas as páginas foram executadas com Streamlit/Plotly
simulados (as bibliotecas não puderam ser instaladas lá), conferindo cálculos e colunas dos gráficos.
O visual final deve ser conferido com `streamlit run` antes da apresentação.

Ferramenta de exploração estatística AGREGADA: não faz diagnóstico individual nem prova causalidade.
"""
import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))
import painel as pn  # noqa: E402

# Cores: vermelho da identidade do projeto para série única; azul/laranja para 2 grupos;
# cinza neutro para "sem diferença". Texto sempre na cor padrão (identidade vem da legenda).
VERMELHO, AZUL, LARANJA, CINZA = "#7A1020", "#2a78d6", "#eb6834", "#9a9890"
CORES_SITUACAO = {"Acima do Brasil": VERMELHO, "Abaixo do Brasil": AZUL,
                  "Sem diferença significativa": CINZA}
BASE_PADRAO = RAIZ / "data" / "processed" / "analitica_pense2019.csv.gz"
MODELOS_CSV = RAIZ / "docs" / "resultados_modelos.csv"
COV_PADRAO = ["sem_amigos", "feminino", "idade_16_17", "escola_privada", "pais_raramente_entendem",
              "agressao_familia", "bullying_sofrido", "cyberbullying"]
NOME_MODELO = {"M0 bruto": "M0 · sem ajuste", "M1 +sexo/idade/escola": "M1 · + sexo, idade, escola",
               "M2 +família": "M2 · + família", "M3 completo": "M3 · + bullying (completo)",
               "S2 composto >= 3": "Composto com ≥3 itens", "S2 composto >= 5": "Composto com 5 itens",
               "S3 só meninas": "Só meninas", "S3 só meninos": "Só meninos",
               "S4 +escolaridade da mãe": "+ escolaridade da mãe"}
AVISO = ("Estimativas para **grupos** de alunos (dados agregados e anônimos). "
         "Não é diagnóstico individual e associação não significa causa.")

PAGINAS = ["Início", "Panorama", "Comparar grupos", "Acúmulo de vulnerabilidades",
           "Priorização por UF", "Fatores associados", "Metodologia e glossário"]

st.set_page_config(page_title="Observatório de Saúde Mental", layout="wide")
st.markdown(f"<style>h1,h2,h3{{color:{VERMELHO}}}</style>", unsafe_allow_html=True)


# ----------------------------------------------------------------------------- dados e cache
@st.cache_data(show_spinner="Carregando a base…")
def carregar(arq):
    return pd.read_csv(arq)


with st.sidebar:
    st.markdown(f"### {pn.TITULO}")
    pag = st.radio("Navegação", PAGINAS, label_visibility="collapsed")
    st.caption("Fonte: PeNSE 2019 (IBGE/Ministério da Saúde), alunos de 13 a 17 anos.")
    with st.expander("Avançado: carregar outra base"):
        arq = st.file_uploader("Base analítica (CSV ou CSV.GZ)", type=["csv", "gz"])
    st.info("Precisa conversar com alguém? **CVV – 188** (ligação gratuita, 24 horas) ou cvv.org.br.")

if arq is not None:
    df, CHAVE = carregar(arq), f"upload:{arq.name}:{arq.size}"
elif BASE_PADRAO.exists():
    df, CHAVE = carregar(BASE_PADRAO), "padrao"
else:
    df, CHAVE = None, None
if df is not None and "SINTETICO" in df.columns:
    st.error("DADOS SINTÉTICOS DE TESTE. Nenhum número abaixo é resultado científico.")

# O "_" no início do argumento diz ao Streamlit para não tentar comparar o DataFrame inteiro;
# o cache é identificado pela CHAVE da base + parâmetros.
SPIN = "Calculando com o desenho amostral (pesos, estratos e escolas)…"


@st.cache_data(show_spinner=SPIN)
def c_panorama(chave, indicadores, por, _df):
    return pn.panorama(_df, list(indicadores), por)


@st.cache_data(show_spinner=SPIN)
def c_comparar(chave, y, g, _df):
    return pn.comparar(_df, y, g)


@st.cache_data(show_spinner=SPIN)
def c_ranking(chave, y, _df):
    return pn.ranking_uf(_df, y)


@st.cache_data(show_spinner=SPIN)
def c_gradiente(chave, y, _df):
    return pn.gradiente_vulnerabilidades(_df, y)


@st.cache_data(show_spinner="Ajustando a regressão logística com desenho amostral…")
def c_modelo(chave, y, X, _df):
    return pn.modelo(_df, y, list(X))


# ----------------------------------------------------------------------------- utilidades
def com_erros(t, eixo="%"):
    t = t.copy()
    t["_mais"] = t["IC95% sup"] - t[eixo]
    t["_menos"] = t[eixo] - t["IC95% inf"]
    return t


def estilo(fig, altura=420, titulo_x=None, titulo_y=None):
    fig.update_layout(height=altura, margin=dict(l=10, r=10, t=30, b=10), plot_bgcolor="rgba(0,0,0,0)",
                      legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0, title=None))
    fig.update_xaxes(title=titulo_x, gridcolor="rgba(128,128,128,0.2)", zeroline=False)
    fig.update_yaxes(title=titulo_y, gridcolor="rgba(128,128,128,0.2)", zeroline=False)
    return fig


def mostrar_tabela(t, nome_arquivo, colunas):
    """Tabela arredondada + botão para baixar em CSV que abre direto no Excel em português."""
    vis = t[colunas].copy()
    st.dataframe(vis.round(1), hide_index=True)
    st.download_button("Baixar tabela (CSV)", vis.to_csv(index=False, sep=";", decimal=",").encode("utf-8-sig"),
                       file_name=nome_arquivo, mime="text/csv", key=f"dl_{nome_arquivo}")


def pct(x):
    return f"{pn.br(x)}%"


# ----------------------------------------------------------------------------- páginas
def pagina_inicio():
    st.title(pn.TITULO)
    st.caption(pn.SUBTITULO)
    st.markdown(
        "**O problema (ODS 3 – Saúde e Bem-Estar).** Quase 1 em cada 5 estudantes brasileiros de 13 a 17 "
        "anos relata sofrimento psicológico frequente. Escolas e secretarias de educação precisam saber "
        "**quais grupos estão mais expostos** e **quais fatores do dia a dia escolar e familiar** acompanham "
        "esse sofrimento, para priorizar ações de prevenção.")
    if df is None:
        st.info("Base de dados não encontrada. Use *Avançado: carregar outra base* na barra lateral.")
        return
    tot = c_panorama(CHAVE, ("autoavaliacao_neg",), None, df).iloc[0]
    sexo = c_panorama(CHAVE, ("autoavaliacao_neg",), "feminino", df).set_index("Grupo")
    grad = c_gradiente(CHAVE, "autoavaliacao_neg", df)
    alto = grad.iloc[3:]                                   # 3 ou mais vulnerabilidades
    rob = pn.robustez_sem_amigos(MODELOS_CSV).set_index("modelo") if MODELOS_CSV.exists() else None

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Autoavaliação negativa", pct(tot["%"]),
              help="% de alunos que, nos últimos 30 dias, relataram ao menos 4 de 5 sentimentos negativos "
                   "na maioria das vezes ou sempre (tristeza, preocupação, irritação, ninguém se importa, "
                   "vida não vale a pena).")
    c2.metric("Meninas × meninos", f"{pct(sexo.loc['Feminino', '%'])} × {pct(sexo.loc['Masculino', '%'])}",
              help="Mesma medida, por sexo.")
    c3.metric("Com 3+ vulnerabilidades", pct(alto["% dos alunos"].sum()),
              help="Alunos com 3 ou mais destes 5 fatores: sem amigos próximos, bullying, cyberbullying, "
                   "pais que raramente entendem seus problemas, agressão por familiar.")
    if rob is not None:
        c4.metric("Sem amigos próximos", f"chance {pn.br(rob.loc['M3 completo', 'OR'], 2)}×",
                  help="Razão de chances ajustada (modelo completo): mesmo comparando alunos de mesmo sexo, "
                       "idade, tipo de escola, contexto familiar e exposição a bullying.")

    st.markdown("#### O que os dados mostram")
    st.markdown(
        f"- Entre quem tem **3 ou mais vulnerabilidades**, a autoavaliação negativa chega a "
        f"**{pct(grad.iloc[3]['%'])}** (3) e **{pct(grad.iloc[4]['%'])}** (4 ou mais), contra "
        f"**{pct(grad.iloc[0]['%'])}** de quem não tem nenhuma.\n"
        "- Além do sexo (meninas relatam muito mais sofrimento), os fatores mais fortes no modelo ajustado são "
        "**pais que raramente entendem os problemas do filho** e **cyberbullying**: fatores sobre os quais "
        "escola e família conseguem agir.\n"
        "- Não ter amigos próximos continua associado ao sofrimento mesmo depois de descontar todos os "
        "outros fatores.")
    st.markdown("#### Para quem é esta ferramenta")
    st.markdown(
        "- **Secretarias de educação e gestores escolares:** priorizar onde e para quem direcionar "
        "programas de convivência, combate ao bullying e aproximação com famílias.\n"
        "- **Equipes pedagógicas e psicólogos escolares:** argumentos baseados em dados para planejar ações.\n"
        "- **Pesquisadores e estudantes:** estimativas oficiais reproduzíveis, com margem de erro correta.")
    st.markdown("#### Como navegar")
    st.markdown(
        "**Panorama** → tamanho do problema · **Comparar grupos** → quem está mais exposto · "
        "**Acúmulo de vulnerabilidades** → como os fatores se somam · **Priorização por UF** → onde agir · "
        "**Fatores associados** → o que pesa mais, ajustando pelos demais · **Metodologia** → como ler os números.")
    st.caption(AVISO)


def pagina_panorama():
    st.header("Panorama: quantos alunos relatam cada sentimento")
    opcoes = {"Nenhuma (Brasil)": None, "Sexo": "feminino", "Tipo de escola": "escola_privada",
              "Faixa etária": "idade_16_17"}
    escolha = st.radio("Quebrar por", list(opcoes), horizontal=True)
    por = opcoes[escolha]
    t = com_erros(c_panorama(CHAVE, tuple(pn.ROTULOS), por, df))
    ordem = list(pn.ROTULOS.values())[::-1]
    if por is None:
        fig = px.bar(t, x="%", y="Indicador", orientation="h", error_x="_mais", error_x_minus="_menos",
                     color_discrete_sequence=[VERMELHO], category_orders={"Indicador": ordem},
                     hover_data={"_mais": False, "_menos": False, "n": True})
        st.plotly_chart(estilo(fig, 420, "% dos alunos (com IC95%)"))
        cols = ["Indicador", "%", "IC95% inf", "IC95% sup", "n"]
    else:
        fig = px.bar(t, x="%", y="Indicador", color="Grupo", barmode="group", orientation="h",
                     error_x="_mais", error_x_minus="_menos", color_discrete_sequence=[AZUL, LARANJA],
                     category_orders={"Indicador": ordem}, hover_data={"_mais": False, "_menos": False})
        st.plotly_chart(estilo(fig, 520, "% dos alunos (com IC95%)"))
        cols = ["Indicador", "Grupo", "%", "IC95% inf", "IC95% sup", "n"]
    st.caption("Últimos 30 dias, 'na maioria das vezes' ou 'sempre'. Barras de erro = intervalo de confiança "
               "de 95% considerando o desenho amostral. " + AVISO)
    mostrar_tabela(t, "panorama.csv", cols)


def pagina_comparar():
    st.header("Comparar grupos: quem está mais exposto")
    c1, c2 = st.columns(2)
    y = c1.selectbox("Indicador", list(pn.ROTULOS), format_func=pn.ROTULOS.get)
    grupos = [g for g in pn.GRUPOS if g != y]
    g = c2.selectbox("Comparar por", grupos, format_func=pn.GRUPOS.get)
    t, dif = c_comparar(CHAVE, y, g, df)
    t = com_erros(t)
    if dif is not None:
        sinal = "mais" if dif["dif_pp"] > 0 else "menos"
        signif = dif["ic_inf"] > 0 or dif["ic_sup"] < 0
        st.metric(f"{dif['grupo_1']} − {dif['grupo_0']}", f"{pn.br(dif['dif_pp'])} p.p.",
                  help="Diferença em pontos percentuais, com IC95% por linearização conjunta.")
        st.markdown(
            f"No grupo **{dif['grupo_1']}**, a prevalência é **{pn.br(abs(dif['dif_pp']))} pontos percentuais "
            f"{sinal}** que no grupo **{dif['grupo_0']}** (IC95% {pn.br(dif['ic_inf'])} a {pn.br(dif['ic_sup'])}). "
            + ("A diferença é estatisticamente significativa." if signif
               else "A diferença **não** é estatisticamente significativa."))
    fig = px.bar(t, x="Grupo", y="%", error_y="_mais", error_y_minus="_menos",
                 color_discrete_sequence=[VERMELHO], hover_data={"_mais": False, "_menos": False, "n": True})
    if g in ("regiao", "uf"):
        br_ = c_panorama(CHAVE, (y,), None, df).iloc[0]["%"]
        fig.add_hline(y=br_, line_dash="dash", line_color=CINZA, annotation_text=f"Brasil {pct(br_)}")
        if g == "uf":
            fig.update_xaxes(categoryorder="total descending")
    st.plotly_chart(estilo(fig, 420, None, f"% — {pn.ROTULOS[y]}"))
    st.caption("Diferenças descritivas (sem ajuste por outros fatores). Para comparar descontando os demais "
               "fatores, veja **Fatores associados**. " + AVISO)
    mostrar_tabela(t, f"comparacao_{y}_{g}.csv", ["Grupo", "%", "IC95% inf", "IC95% sup", "n"])


def pagina_acumulo():
    st.header("Acúmulo de vulnerabilidades: os fatores se somam")
    st.markdown("Contamos quantos destes **5 fatores** cada aluno relatou: sem amigos próximos · sofreu bullying "
                "· sofreu cyberbullying · pais raramente entendem seus problemas · agressão física por familiar.")
    y = st.selectbox("Desfecho", [c for c in pn.ROTULOS if c != "sem_amigos"], format_func=pn.ROTULOS.get)
    t = com_erros(c_gradiente(CHAVE, y, df))
    t["rótulo"] = t["%"].map(pct)
    fig = px.bar(t, x="Vulnerabilidades", y="%", error_y="_mais", error_y_minus="_menos", text="rótulo",
                 color_discrete_sequence=[VERMELHO],
                 hover_data={"_mais": False, "_menos": False, "rótulo": False, "% dos alunos": ":.1f"})
    fig.update_traces(textposition="inside", insidetextanchor="end")
    st.plotly_chart(estilo(fig, 420, "Nº de vulnerabilidades relatadas", f"% — {pn.ROTULOS[y]}"))
    c1, c2 = st.columns(2)
    c1.metric("Alunos com 3 ou mais", pct(t.iloc[3:]["% dos alunos"].sum()))
    c2.metric("Alunos sem nenhuma", pct(t.iloc[0]["% dos alunos"]))
    st.markdown("**Leitura para gestão:** o sofrimento se concentra em quem acumula fatores. Ações que reduzem "
                "um fator (ex.: programa contra bullying, aproximação com famílias) tendem a alcançar justamente "
                "esse grupo de maior risco.")
    st.caption("Análise exploratória (não fazia parte da hipótese confirmatória). Casos com algum dos 5 fatores "
               "sem resposta ficam de fora (≈1,6% do domínio). " + AVISO)
    mostrar_tabela(t, f"acumulo_{y}.csv", ["Vulnerabilidades", "%", "IC95% inf", "IC95% sup", "n", "% dos alunos"])


def pagina_uf():
    st.header("Priorização por UF: onde a situação é pior que a média do país")
    y = st.selectbox("Indicador", list(pn.ROTULOS), format_func=pn.ROTULOS.get)
    t, brasil = c_ranking(CHAVE, y, df)
    t = com_erros(t)
    acima, abaixo = (t.Situação == "Acima do Brasil").sum(), (t.Situação == "Abaixo do Brasil").sum()
    c1, c2, c3 = st.columns(3)
    c1.metric("Brasil", pct(100 * brasil["p"]))
    c2.metric("UFs acima do Brasil", int(acima))
    c3.metric("UFs abaixo do Brasil", int(abaixo))
    fig = px.bar(t, x="%", y="UF", orientation="h", color="Situação", color_discrete_map=CORES_SITUACAO,
                 error_x="_mais", error_x_minus="_menos",
                 hover_data={"_mais": False, "_menos": False, "Região": True, "dif_pp": ":.1f", "p_holm": ":.3f"})
    fig.update_yaxes(categoryorder="total ascending")
    fig.add_vline(x=100 * brasil["p"], line_dash="dash", line_color=CINZA,
                  annotation_text=f"Brasil {pct(100 * brasil['p'])}")
    st.plotly_chart(estilo(fig, 760, "% dos alunos (com IC95%)"))
    st.markdown(
        "**Como ler:** a cor indica se a UF difere do Brasil **depois da correção de Holm** para 27 comparações "
        "simultâneas. Sem essa correção, ao testar 27 UFs a 5% esperaríamos ~1 'diferença' só por acaso. "
        "Ranking com intervalos sobrepostos não deve ser lido como ordem exata.")
    st.caption("Diferença UF − Brasil estimada por linearização conjunta (a UF faz parte do Brasil). " + AVISO)
    t = t.rename(columns={"dif_pp": "Dif. (p.p.)", "p_holm": "p ajustado (Holm)"})
    mostrar_tabela(t, f"ranking_uf_{y}.csv",
                   ["UF", "Região", "%", "IC95% inf", "IC95% sup", "Dif. (p.p.)", "p ajustado (Holm)", "Situação", "n"])


def pagina_fatores():
    st.header("Fatores associados, descontando os demais")
    aba1, aba2 = st.tabs(["Modelo interativo", "Robustez do resultado principal"])
    with aba1:
        _aba_modelo()
    with aba2:
        _aba_robustez()


def _aba_modelo():
    c1, c2 = st.columns([1, 2])
    y = c1.selectbox("Desfecho", [c for c in pn.ROTULOS if c != "sem_amigos"], format_func=pn.ROTULOS.get)
    X = c2.multiselect("Fatores no modelo", pn.PREDITORES, default=COV_PADRAO,
                       format_func=pn.ROTULO_PREDITOR.get)
    if not X:
        st.info("Escolha ao menos um fator.")
        return
    try:
        m = c_modelo(CHAVE, y, tuple(X), df)
    except Exception as e:  # noqa: BLE001
        st.warning(f"O modelo não pôde ser ajustado: {e}")
        return
    m = com_erros(m.rename(columns={"ic_inf": "IC95% inf", "ic_sup": "IC95% sup"}), "OR")
    fig = px.scatter(m, x="OR", y="Fator", error_x="_mais", error_x_minus="_menos", log_x=True,
                     color_discrete_sequence=[VERMELHO], hover_data={"_mais": False, "_menos": False})
    fig.update_traces(marker=dict(size=11))
    fig.add_vline(x=1, line_dash="dash", line_color=CINZA, annotation_text="sem associação")
    fig.update_yaxes(categoryorder="array", categoryarray=m.sort_values("OR").Fator.tolist())
    st.plotly_chart(estilo(fig, 90 + 45 * len(m), "Razão de chances ajustada (escala log, IC95%)"))
    st.markdown("**Em linguagem simples** (mantendo os outros fatores do modelo iguais):")
    for _, r in m.iterrows():
        st.markdown(f"- **{r.Fator}:** {r.Leitura}")
    st.caption(f"Regressão logística com pesos, estratos e escolas; casos completos (n = {pn.br(m['n_usados'].iloc[0], 0)}). "
               "Estudo transversal: associação, não causa. " + AVISO)
    mostrar_tabela(m.rename(columns={"OR": "Razão de chances", "p_valor": "p-valor"}), f"modelo_{y}.csv",
                   ["Fator", "Razão de chances", "IC95% inf", "IC95% sup", "p-valor"])


def _aba_robustez():
    if not MODELOS_CSV.exists():
        st.info("Arquivo docs/resultados_modelos.csv não encontrado.")
        return
    r = pn.robustez_sem_amigos(MODELOS_CSV)
    r["Modelo"] = [NOME_MODELO.get(mo, "Item: " + pn.ROTULOS.get(mo.replace("S1 item: ", ""), mo))
                   for mo in r.modelo]
    r["Tipo"] = ["Principal (M0 → M3)" if mo.startswith("M") else "Sensibilidade" for mo in r.modelo]
    r = com_erros(r.rename(columns={"ic_inf": "IC95% inf", "ic_sup": "IC95% sup"}), "OR")
    fig = px.scatter(r, x="OR", y="Modelo", color="Tipo", error_x="_mais", error_x_minus="_menos", log_x=True,
                     color_discrete_sequence=[VERMELHO, AZUL], hover_data={"_mais": False, "_menos": False})
    fig.update_traces(marker=dict(size=11))
    fig.update_yaxes(categoryorder="array", categoryarray=r.Modelo.tolist()[::-1])
    fig.add_vline(x=1, line_dash="dash", line_color=CINZA)
    st.plotly_chart(estilo(fig, 560, "Razão de chances de 'sem amigos próximos' (escala log, IC95%)"))
    st.markdown(
        "**Hipótese confirmatória (definida antes de ver os resultados):** não ter amigos próximos se associa "
        "à autoavaliação negativa. A razão de chances cai de 2,23 (sem ajuste) para 1,77 (modelo completo), "
        "mas **não desaparece** em nenhuma especificação. A exceção é o item *preocupação* (sentido oposto), "
        "registrado e discutido em vez de escondido.")


def pagina_metodologia():
    st.header("Metodologia e glossário")
    st.markdown("""
#### Como ler os números
- **Prevalência (%)**: porcentagem estimada de alunos (de todo o Brasil, não só da amostra) com aquela resposta.
- **IC95% (intervalo de confiança)**: faixa onde o valor verdadeiro deve estar, com 95% de confiança. Intervalos
  que não se sobrepõem indicam diferença clara; sobreposição pede cautela.
- **p.p. (pontos percentuais)**: diferença entre duas porcentagens (ex.: 27% − 8% = 19 p.p.).
- **Razão de chances (OR)**: quantas vezes a chance do desfecho é maior (OR > 1) ou menor (OR < 1) num grupo,
  comparado ao grupo de referência, **mantidos iguais os outros fatores do modelo**. OR = 1: sem associação.
- **p-valor / correção de Holm**: probabilidade de ver uma diferença tão grande só por acaso. Quando fazemos
  muitos testes ao mesmo tempo (27 UFs), a correção de Holm evita "achados" por acaso.
- **Peso amostral**: cada aluno entrevistado representa vários alunos do país; sem os pesos e o sorteio por
  escola/estrato, porcentagens e margens de erro sairiam erradas.

#### Dados e desenho
- Microdados públicos da **PeNSE 2019** (IBGE/Ministério da Saúde). Domínio: alunos frequentes de 13 a 17 anos
  (124.898 questionários).
- Desenho: escola = UPA dentro de estrato, peso inicial e pós-estratificação, como no exemplo oficial do IBGE.
- **Validação**: 2.760 estimativas das tabelas oficiais do IBGE replicadas; 93% com diferença menor que 0,1 p.p.

#### Limitações
- Estudo **transversal**: mostra associação, não causa (a direção pode ser inversa).
- **Autorrelato** com janela de 30 dias (viés de memória possível); itens únicos, **não são diagnóstico**
  de ansiedade ou depressão.
- Não inclui adolescentes **fora da escola**, possivelmente os mais vulneráveis.
- Casos completos: respostas ausentes nunca foram tratadas como "não".

#### Ética e privacidade
Dados públicos e anonimizados pelo IBGE; nenhum dado pessoal é coletado pela ferramenta. Resultados são sempre
apresentados para grupos, nunca para indivíduos.
""")


# ----------------------------------------------------------------------------- roteamento
ROTA = {PAGINAS[0]: pagina_inicio, PAGINAS[1]: pagina_panorama, PAGINAS[2]: pagina_comparar,
        PAGINAS[3]: pagina_acumulo, PAGINAS[4]: pagina_uf, PAGINAS[5]: pagina_fatores,
        PAGINAS[6]: pagina_metodologia}

if df is None and pag not in (PAGINAS[0], PAGINAS[6]):
    st.info("Carregue a base analítica na barra lateral (Avançado) para ver esta página.")
else:
    try:
        ROTA[pag]()
    except KeyError as e:
        st.error(f"A base carregada não tem a coluna {e}. Use a base analítica gerada por src/preparar_dados.py.")
