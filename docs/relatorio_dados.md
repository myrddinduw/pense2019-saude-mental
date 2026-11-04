# Relatório de seleção de bases

**Atualização (3 nov. 2026):** o usuário forneceu as tabelas oficiais do IBGE 'Tema 12 – Saúde Mental' (21 abas, indicadores por idade/região, UF e capitais, com sexo e dependência administrativa, IC95%). Foram lidas e conferidas; os totais do Brasil coincidem com Antunes et al. (2022). Elas permitem análises descritivas, mas **não** modelo individual.

**Atualização 2 (3 nov. 2026):** o usuário forneceu também os **microdados** (CSV, SAS, XLSX) e o **dicionário oficial** da PeNSE 2019. Variáveis e códigos agora estão VERIFICADOS (ver dicionario_variaveis.md) e as 2.760 estimativas das tabelas foram replicadas (docs/validacao_microdados_vs_tabelas_ibge.csv).

**Limite da etapa anterior (superado).** O ambiente de desenvolvimento não alcança `ftp.ibge.gov.br` (bloqueio de rede, HTTP 403 do proxy). Portanto: **nenhum microdado foi baixado ou analisado**. Variáveis abaixo foram verificadas apenas pela **redação das perguntas em artigos revisados por pares**, não pelo dicionário oficial. Os códigos das colunas continuam pendentes.

## Bases avaliadas

| Base | Instituição | Acesso | Verificado |
|---|---|---|---|
| PeNSE 2019 | IBGE / Ministério da Saúde | Microdados e dicionário no portal do IBGE (pesquisa PeNSE) | Amostra em 2 estágios (escolas, turmas), 4.242 escolas, 6.612 turmas, 159.245 questionários válidos, 13–17 anos, abr.–set. 2019, questionário autoaplicado em smartphone, dados calibrados por pesos |
| PeNSE 2015 | IBGE / MS | Idem | 9º ano, n = 102.301 (artigo 3); variável escola = UPA e variáveis de estrato foram incluídas nos microdados (nota do IBGE) |
| PNS 2019 | IBGE / MS | https://www.ibge.gov.br/estatisticas/sociais/saude/9160-pesquisa-nacional-de-saude.html | PHQ-9 em 88.531 adultos (≥18); população-alvo ≥15 anos |
| SIDRA / DATASUS | IBGE / MS | Tabelas agregadas | Não avaliados em profundidade; só contexto, sem prevalência individual |

## Matriz de decisão (0–5; julgamento da equipe, a revisar com o orientador)

| Critério | PeNSE 2019 | PeNSE 2015 | PNS 2019 |
|---|---|---|---|
| Relevância para a pergunta | 4 (sofrimento + amigos + bullying) | 4 (solidão + insônia diretas) | 2 (depressão em adultos; sem ansiedade social) |
| Validade dos indicadores | 3 (itens únicos, não escalas) | 3 | 4 (PHQ-9 validado) |
| Representatividade | 4 (escolares; exclui fora da escola) | 4 | 5 (domiciliar) |
| Documentação | 4 | 4 | 4 |
| Microdados disponíveis | 4 (com supressão parcial, nota técnica 01/2022) | 4 | 4 |
| Possibilidade estatística | 5 (n grande, pesos, UPA) | 5 | 5 |
| Viabilidade técnica / prazo | 4 | 4 | 3 (muitos módulos) |
| **Total (/35)** | **28** | **28** | **27** |

**Recomendação:** PeNSE 2019 como base principal (mais recente; bloco de saúde mental e cyberbullying). PeNSE 2015 como análise de sensibilidade para solidão e insônia, **se** o dicionário confirmar essas variáveis. Empate técnico: a decisão se apoia na atualidade e no tema do edital (jovens/escolares).

## Resposta à distinção científica obrigatória
Nenhuma das bases avaliadas mede **ansiedade social** com instrumento específico. Recorte alternativo mais defensável:
**"Fatores psicossociais associados a indicadores de sofrimento psicológico em escolares brasileiros (PeNSE 2019)"**, mantendo a conexão teórica com ansiedade social via solidão percebida e relações interpessoais.

## Variáveis candidatas (redação verificada em artigo; código e coluna A CONFIRMAR)
Sem amigos próximos; preocupação; tristeza; "ninguém se preocupa" (proxy de solidão); irritação; "vida não vale a pena"; autoavaliação negativa (≥4 de 5); sexo; idade; dependência administrativa; cyberbullying. Escolaridade materna, apoio familiar e acesso a serviços **não foram verificadas**.

## Limitações documentadas
Exclusão de adolescentes fora da escola; autorrelato; viés de memória (30 dias); desenho transversal; supressão parcial de variáveis para confidencialidade (ex.: 1,9% em cor/raça tornou-se "sem resposta").
