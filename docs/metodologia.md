# Metodologia

## Dados
Microdados públicos da PeNSE 2019 (IBGE, versão com controle de confidencialidade da nota técnica 01/2022, que suprime parcialmente algumas variáveis, p.ex. 1,9% em cor/raça). 165.838 registros; 159.245 alunos frequentes (IND_EXPANSAO = 1) em 4.242 escolas e 321 estratos; 124.898 com 13 a 17 anos no domínio de análise.

## Desenho amostral (exemplo oficial do IBGE em R)
UPA = escola aninhada em estrato; peso = PESO_INICIAL; pós-estratificação por POSEST com TOTAIS_POSEST; domínio IND_EXPANSAO = 1. Os pesos pós-estratificados que calculamos reproduzem PESO_ALUNO_FREQ do IBGE (diferença máxima 1e-7).

## Estimação (src/estatistica.py)
- Proporção: razão de totais ponderados; variância por linearização de Taylor com ajuste de resíduos por célula de pós-estratificação, entre UPAs dentro de estratos; IC95% por t (gl = UPAs − estratos).
- Domínios (sexo, escola, UF...) mantêm toda a amostra no desenho, como `subset` do pacote survey.
- Estratos com uma única UPA (18) não contribuem para a variância. Validado: reproduz os IC do IBGE, inclusive capitais com poucas UPAs.
- Regressão logística: pseudo-verossimilhança com pesos pós-estratificados, variância sanduíche por UPA/estrato com o mesmo ajuste. Conferida contra o OR ponderado 2×2 e a variância por linearização direta (idênticos até a 4ª casa).

## Validação externa
2.760 estimativas das 21 tabelas do IBGE (Brasil, regiões × idade, UFs, capitais; 7 indicadores; total, sexo, escola) replicadas: 49% a menos de 0,01 p.p., 82% a menos de 0,05, 93% a menos de 0,1; máximo 0,38 p.p. nas estimativas e 0,54 p.p. nos limites do IC (capitais com poucas escolas). A diferença residual é compatível com a supressão parcial de variáveis nos microdados públicos.

## Modelos
Desfecho principal: autoavaliação negativa. Exposição confirmatória: sem amigos próximos. Cobertura: M0 bruto; M1 + sexo, idade, escola; M2 + entendimento dos pais e agressão familiar; M3 + bullying e cyberbullying. Sensibilidade: S1 desfechos de item único; S2 limiares 3 e 5 do composto; S3 estratos por sexo; S4 + escolaridade da mãe. Diagnóstico: VIF máximo 1,07.

## Limitações
Transversal (associação, não causa; direção reversa plausível); autorrelato com janela de 30 dias; itens únicos; população limitada a alunos frequentes; casos completos (1,1% a 2,3% do domínio excluídos nos modelos principais; 17,5% no S4, que inclui escolaridade da mãe); preditores e desfechos autorrelatados na mesma ocasião podem compartilhar viés de resposta; implementação própria da variância, validada, mas sem substituir R survey/Stata svy.
