# Observatório Estatístico de Saúde Mental e Vulnerabilidades Psicossociais

Projeto FMU TECH Inovação 2026.2 (Bacharelado em Estatística, ODS 3), apresentação em
7-8/dez/2026. Este README é o ponto de partida para o grupo: explica a pesquisa, a
estrutura do repositório e como rodar tudo na sua máquina.

> Ferramenta de **exploração estatística agregada**. Não faz diagnóstico individual nem
> prova causalidade — ver seção [Limitações](#7-limitações-e-cuidados).

## Sumário
1. [A pesquisa, em uma frase](#1-a-pesquisa-em-uma-frase)
2. [Fonte de dados](#2-fonte-de-dados)
3. [Estrutura do repositório](#3-estrutura-do-repositório)
4. [Como rodar na sua máquina](#4-como-rodar-na-sua-máquina)
5. [Como o projeto funciona por dentro (pipeline)](#5-como-o-projeto-funciona-por-dentro-pipeline)
6. [Principais resultados](#6-principais-resultados)
7. [Limitações e cuidados](#7-limitações-e-cuidados)
8. [Onde encontrar mais detalhes](#8-onde-encontrar-mais-detalhes)
9. [Status e pendências](#9-status-e-pendências)

## 1. A pesquisa, em uma frase

**Pergunta:** entre escolares de 13 a 17 anos, a ausência de amigos próximos se associa a
maior sofrimento psicológico, mesmo depois de ajustar por sexo, idade, escola, família e
bullying?

**Resposta (resumida):** sim — quem não tem amigos próximos tem OR ajustada de **1,77**
(IC95% 1,48–2,12) para autoavaliação negativa sobre a própria vida, no modelo mais
completo. Isso é só um corte dos resultados; ver seção 6 e `docs/resultados.md`.

**Base de dados:** PeNSE 2019 (IBGE/Ministério da Saúde), microdados oficiais —
124.898 alunos no domínio de análise (13-17 anos, frequentes), com desenho amostral
complexo (escola dentro de estrato, pesos, pós-estratificação).

## 2. Fonte de dados

Os **microdados brutos da PeNSE não estão neste repositório** (termos de uso do IBGE
pedem para não redistribuir). Isso é proposital — só a base já processada
(`data/processed/analitica_pense2019.csv.gz`) está versionada, e ela é suficiente para
rodar o app e os testes.

Se precisar reprocessar do zero (não é necessário para rodar o app):
1. Baixe em https://www.ibge.gov.br → pesquisa **PeNSE 2019** → microdados (CSV) e
   dicionário (`Dicionario_PENSE2019_Microdados.xls`).
2. Coloque o CSV em `data/raw/` (pasta já existe, vazia por padrão).
3. Veja o passo "Reprocessar os dados brutos" na seção 4.

## 3. Estrutura do repositório

```
app/
  app.py                   # Dashboard Streamlit (o "sistema funcional" do projeto)
src/
  preparar_dados.py        # Microdados brutos -> base analítica (limpeza, códigos de ausente)
  estatistica.py           # Estimadores próprios para amostra complexa (proporção, diferença, regressão logística ponderada)
  modelos.py                # Roda todos os modelos de regressão (confirmatório + sensibilidade)
  ler_tabelas_ibge.py       # Lê as tabelas oficiais do IBGE (Tema 12) para um CSV "tidy"
  validacao_ibge.py         # Compara nossos números com as tabelas oficiais (validação externa)
  analise_tabelas.py        # Análises descritivas extras a partir das tabelas oficiais
  dados_sinteticos.py       # Gera dados FALSOS só para testar código (nunca usar como resultado)
data/
  raw/                      # Microdados brutos (vazio no repo, ver seção 2)
  processed/                # Base pronta para análise (versionada, já inclusa)
docs/
  protocolo_pesquisa.md         # Pergunta, hipóteses, plano de análise (definido ANTES dos resultados)
  dicionario_variaveis.md       # De onde vem cada coluna (código oficial do IBGE)
  metodologia.md                 # Desenho amostral, estimadores, validação
  resultados.md                  # Resultados numéricos (OR, IC95%, sensibilidade)
  resultados_modelos.csv         # Saída bruta de src/modelos.py
  relatorio_dados.md             # Como e por que escolhemos a PeNSE 2019 (vs. outras bases)
  revisao_literatura.md          # Revisão exploratória (não sistemática) de artigos relacionados
  validacao_microdados_vs_tabelas_ibge.csv  # 2.760 comparações número a número com o IBGE
  estrategia_apresentacao.md     # Roteiro sugerido para a apresentação de banca
tests/
  test_estatistica.py       # Testa src/estatistica.py com dados sintéticos de verdade conhecida
  test_tabelas_ibge.py      # Testa a leitura das tabelas do IBGE
requirements.txt
```

## 4. Como rodar na sua máquina

Pré-requisito: Python 3.11+ (testado com 3.12).

```bash
# 1. Clonar e entrar na pasta
git clone <url-do-repositorio>
cd projeto-saude-mental

# 2. Ambiente virtual
python3 -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate

# 3. Instalar dependências
pip install -r requirements.txt

# 4. Rodar os testes (confere se tudo está funcionando)
pytest tests -q

# 5. Rodar o dashboard
streamlit run app/app.py
```

Abra `http://localhost:8501`. O app já carrega sozinho a base
`data/processed/analitica_pense2019.csv.gz` — não precisa subir nenhum arquivo manualmente.

### Reprocessar os dados brutos (opcional, só se mexer no ETL)
```bash
# Roda os modelos de regressão a partir do CSV bruto do IBGE
python src/modelos.py data/raw/PENSE2019_MICRODADOS.csv docs/resultados_modelos.csv

# Confere nossos números contra as tabelas oficiais do IBGE (demora ~6 min)
python src/validacao_ibge.py data/raw/PENSE2019_MICRODADOS.csv \
    data/processed/pense2019_tema12_tidy.csv saida_validacao.csv
```

## 5. Como o projeto funciona por dentro (pipeline)

```
microdados PeNSE 2019 (CSV do IBGE)
        │  src/preparar_dados.py
        │  (limpa códigos de ausente, cria colunas 0/1 como "sem_amigos", "feminino"...)
        ▼
base analítica (data/processed/analitica_pense2019.csv.gz)
        │
        ├── src/estatistica.py ──► proporções/IC95%, diferenças entre grupos,
        │                          regressão logística ponderada (tudo respeitando
        │                          o desenho amostral: estrato + escola + peso)
        │
        ├── src/modelos.py ──────► roda a bateria de modelos (bruto, ajustado,
        │                          sensibilidade) e salva docs/resultados_modelos.csv
        │
        └── app/app.py ──────────► dashboard Streamlit, chama estatistica.py
                                    em tempo real conforme o usuário escolhe
                                    indicador/grupo na interface
```

A validação externa (`src/validacao_ibge.py`) é um caminho paralelo: pega as mesmas
funções de `estatistica.py` e confere se reproduzem as tabelas **já publicadas** pelo
IBGE — é isso que dá confiança de que o estimador próprio (feito do zero, sem usar R
`survey` ou Stata `svy`) está correto.

## 6. Principais resultados

(Números completos e todos os modelos de sensibilidade em `docs/resultados.md`.)

- **Hipótese confirmatória:** sem amigos próximos × autoavaliação negativa. OR bruta
  **2,23** (IC95% 1,95–2,55) → OR ajustada completa (sexo, idade, escola, família,
  bullying, cyberbullying) **1,77** (1,48–2,12). H0 rejeitada em todos os modelos.
- No modelo completo, os maiores efeitos foram sexo feminino (OR 3,93) e pais que
  raramente entendem os problemas do filho (OR 3,20).
- Achado contraintuitivo, registrado sem esconder: o item "muito preocupado(a)" teve OR
  **0,78** (sentido invertido) — ver nota de cautela em `docs/resultados.md`.
- **Validação externa:** 2.760 estimativas replicadas das tabelas oficiais do IBGE, 93%
  com diferença menor que 0,1 ponto percentual.

## 7. Limitações e cuidados

- **Transversal**: mostra associação, não causa (a direção pode ser inversa).
- **Autorrelato** com janela de 30 dias (viés de memória possível).
- Exclui adolescentes **fora da escola** (grupo possivelmente mais vulnerável).
- Indicadores de **item único** (exceto o composto de autoavaliação); não são
  instrumentos diagnósticos validados.
- `src/estatistica.py` é implementação própria da variância para amostra complexa — foi
  validada contra o IBGE, mas não substitui pacotes consolidados (R `survey`, Stata
  `svy`) em um artigo formal.
- Nunca usar `src/dados_sinteticos.py` como se fosse resultado real — ele gera dados
  falsos só para testar código (toda saída tem a coluna `SINTETICO=1`).

## 8. Onde encontrar mais detalhes

| Dúvida | Arquivo |
|---|---|
| Qual é exatamente a pergunta e as hipóteses? | `docs/protocolo_pesquisa.md` |
| De onde vem cada coluna/variável? | `docs/dicionario_variaveis.md` |
| Como o desenho amostral foi tratado estatisticamente? | `docs/metodologia.md` |
| Quais os números de cada modelo? | `docs/resultados.md`, `docs/resultados_modelos.csv` |
| Por que escolhemos a PeNSE 2019 e não outra base? | `docs/relatorio_dados.md` |
| Que outros estudos existem sobre o tema? | `docs/revisao_literatura.md` |
| Como estruturar a fala na banca? | `docs/estrategia_apresentacao.md` |

## 9. Status e pendências

- Estimadores validados, modelos ajustados, 11 testes passando, app funcional (testado
  localmente com `streamlit run`).
- Pendente: validar com o orientador a regra de corte do "sofrimento frequente"; buscar
  literatura adicional com busca booleana formal (PubMed/SciELO/BVS); revisar a
  navegação do app para equilibrar rigor técnico com clareza para a banca (que tem um
  membro de mercado, não só acadêmico).
