# Resultados (PeNSE 2019, alunos frequentes de 13 a 17 anos; estimativas com desenho amostral)

Todos os números vêm de `docs/resultados_modelos.csv` e `docs/validacao_microdados_vs_tabelas_ibge.csv` (reprodutíveis com `src/modelos.py` e `src/validacao_ibge.py`).

## Hipótese confirmatória (H1): sem amigos próximos × autoavaliação negativa
- Prevalência de autoavaliação negativa: **31,5%** entre quem não tem amigos próximos e **17,1%** entre quem tem.
- OR bruta (M0) **2,23** (IC95% 1,95–2,55). Ajustada por sexo, idade e escola (M1) 2,46 (2,13–2,83); + entendimento dos pais e agressão familiar (M2) 2,01 (1,70–2,38); modelo completo com bullying e cyberbullying (M3) **1,77 (1,48–2,12)**. H0 rejeitada em todos os modelos.
- Interpretação: associação positiva e robusta, que diminui ao ajustar por experiências familiares e de pares (parte do efeito bruto é compartilhada com esses fatores). Não permite concluir causalidade nem direção.

## Modelo completo (M3), OR (IC95%)
Sexo feminino 3,93 (3,66–4,23); pais raramente entendem seus problemas 3,20 (2,99–3,41); cyberbullying 2,45 (2,22–2,69); bullying sofrido 2,04 (1,90–2,19); agressão por familiares 1,38 (1,28–1,49); 16 e 17 anos 1,26 (1,18–1,35); escola privada 0,93 (0,87–0,98); sem amigos próximos 1,77 (1,48–2,12). VIF máximo 1,07.

## Sensibilidade (OR de "sem amigos" no modelo completo)
Composto >= 3 itens: 1,87 (1,56–2,25). Composto = 5 itens: 1,74 (1,41–2,14). Só meninas: 1,57 (1,27–1,95). Só meninos: 2,14 (1,70–2,68). Com escolaridade da mãe (n menor): 1,81 (1,51–2,17).
Itens isolados: tristeza 1,87; ninguém se preocupa 1,93; vida não vale a pena 1,78; irritação 1,28; **preocupação 0,78 (0,69–0,89)**, sentido oposto. Esta última é exploratória e merece cautela (a preocupação com tarefas escolares pode ser menor em quem tem menos vínculos).

## Padrão ecológico
Entre as 27 UFs, "sem amigos próximos" não acompanha a autoavaliação negativa (Spearman 0,02), mas entre estudantes a associação é forte. Exemplo de por que correlações entre estados não valem para indivíduos.

## Replicação das tabelas oficiais do IBGE
2.760 estimativas: 49% a menos de 0,01 p.p., 82% a menos de 0,05, 93% a menos de 0,1; máximo 0,38 p.p. (pontos) e 0,54 p.p. (limites de IC, capitais com poucas escolas).
