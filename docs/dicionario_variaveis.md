# Dicionário de variáveis (VERIFICADO no Dicionario_PENSE2019_Microdados.xls, IBGE, 2022)

| Variável analítica | Coluna IBGE | Definição | Códigos |
|---|---|---|---|
| estrato | ESTRATO | Estrato de seleção | 2 primeiras posições = UF |
| upa | ESCOLA | Unidade primária (escola), aninhada em ESTRATO | 1 a 69 |
| peso | PESO_INICIAL | Peso antes da pós-estratificação (base da variância) | — |
| posest, totais | POSEST, TOTAIS_POSEST | Domínio de pós-estratificação e total de matriculados (Censo Escolar) | — |
| dom | IND_EXPANSAO = 1 e B01003 em {2,3} | Alunos frequentes de 13 a 17 anos | — |
| feminino | B01001A | Sexo | 1 Homem, 2 Mulher, 9 sem resposta |
| idade_16_17 | B01003 | Idade | 2 = 13 a 15, 3 = 16 ou 17 |
| escola_privada | DEP_ADMIN | Dependência administrativa | 1 Pública, 2 Privada |
| sem_amigos | B12003 | Quantos amigos próximos | 1 = nenhum |
| preocupado | B12004 | Muito preocupado com coisas do dia a dia, 30 dias | 4, 5 = positivo |
| triste | B12005 | Triste | 4, 5 |
| ninguem_se_importa | B12006 | Sentiu que ninguém se preocupa com você | 4, 5 |
| irritado | B12007 | Irritado/nervoso/mal-humorado | 4, 5 |
| vida_nao_vale | B12008 | Sentiu que a vida não vale a pena | 4, 5 |
| autoavaliacao_neg | B12004 a B12008 | >= 4 dos 5 itens positivos, com os 5 válidos | reproduz o IBGE a menos de 0,01 p.p. |
| pais_raramente_entendem | B07004 | Mãe/pai/responsável entendeu seus problemas | 1 Nunca, 2 Raramente = positivo |
| agressao_familia | B09003A | Agressão física por mãe/pai/responsável, 12 meses | 2 a 4 (>= 1 vez) = positivo |
| bullying_sofrido | B07007A | Zoado/intimidado por colegas, 30 dias | 2, 3 (>= 1 vez) = positivo |
| cyberbullying | B07013 | Ameaçado/humilhado em redes sociais, 30 dias | 1 = Sim |
| mae_ate_fund_incompleto | B01008B | Escolaridade da mãe | 1, 2 = positivo; 8 ("não sei") e 9 = ausente |

Não resposta: **-2** (abandono do questionário) e **9** (sem resposta); linhas com IND_EXPANSAO = 0 não têm questionário (vazio).

## Convenção do IBGE (descoberta na validação)
Para os indicadores de item único, o IBGE exclui -2 do denominador e **mantém 9 no denominador** como não-positivo. Para o composto, exclui qualquer ausente. Nas análises deste projeto usamos **casos completos** (9 e -2 viram ausente) para os itens. A diferença é de 0,1 a 0,3 p.p. e está documentada em `docs/validacao_microdados_vs_tabelas_ibge.csv` (opção `convencao_ibge=True`).

## Variáveis NÃO usadas
Ansiedade social não existe na base. Apoio social amplo e acesso a serviços de saúde mental não foram verificados como indicadores adequados e ficaram fora do escopo.
