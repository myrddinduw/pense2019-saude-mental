# Protocolo de pesquisa (versão preliminar)

**Título proposto:** Sofrimento psicológico e vulnerabilidades psicossociais em escolares brasileiros: análise estatística da PeNSE 2019.
(O título provisório sobre ansiedade social foi reformulado porque a base não a mede; ver relatorio_dados.md.)

**Pergunta.** Entre escolares de 13 a 17 anos, a ausência de amigos próximos e a percepção de que ninguém se importa associam-se a maior prevalência de sofrimento psicológico, após ajuste por sexo, idade e dependência administrativa da escola?

**Objetivo geral.** Estimar prevalências e associações ajustadas, respeitando o desenho amostral da PeNSE 2019.
**Objetivos específicos.** (1) estimar prevalências ponderadas com IC95%; (2) comparar por sexo e tipo de escola; (3) ajustar regressão logística; (4) apresentar tudo em protótipo interativo.

**População / unidade.** Escolares de 13–17 anos (PeNSE 2019); unidade = estudante.
**Desfecho principal (confirmatório).** Autoavaliação negativa (≥4 de 5 itens "na maioria das vezes/sempre").
**Desfechos secundários.** Tristeza, preocupação, irritação, "vida não vale a pena".
**Exposições.** Sem amigos próximos; ninguém se importa. **Confundidores.** Sexo, idade, dependência administrativa; outros conforme o dicionário.

## Hipóteses (confirmatória definida antes de ver os resultados dos modelos)
- H₀: OR ajustada de sem amigos próximos = 1 para autoavaliação negativa; H₁: OR ≠ 1.
- **Alteração ao protocolo (registrada):** a segunda hipótese prevista ("ninguém se importa" × autoavaliação) foi retirada porque esse item compõe o desfecho (associação circular). Ele é analisado apenas como desfecho de item único.
Demais comparações (sexo, escola, UF, itens, entendimento dos pais, bullying) são **exploratórias**.

## Plano de análise
1. Descritiva ponderada (proporções, IC95% por t com gl = UPAs − estratos).
2. Diferenças entre grupos por linearização conjunta.
3. Regressão logística ponderada, variância sanduíche por UPA/estrato; OR com IC95%.
4. Diagnósticos: VIF; casos completos com relato da exclusão; sensibilidade (categorizações alternativas do desfecho, com/sem cada preditor).
5. Sem causalidade, sem diagnóstico individual.

## Limitações previstas
Transversal; autorrelato; indicadores únicos; exclusão de não matriculados; ausentes por casos completos; implementação própria de variância (conferir com Stata/R).
