# Estratégia de apresentação (banca FMU TECH Inovação 2026.2, 7-8/dez)

Banca mista: professor da Escola TECH + membro externo de mercado (não é banca 100% de
estatística). Critérios de nota: impacto, inovação, qualidade técnica, aplicação. A estrutura
abaixo cobre os 5 pontos exigidos pelo edital (problema, público, bases, título, solução) e usa
o app Streamlit como demonstração viva, não só slides.

## Estrutura sugerida (ajuste ao tempo real alocado; proporções abaixo somam ~12 min)

| # | Bloco | Tempo | Conteúdo |
|---|---|---|---|
| 1 | Gancho + problema | 1 min | ODS 3. Frase de abertura concreta: "escolares sem amigos próximos têm quase o dobro de chance de autoavaliação negativa sobre a própria vida — mesmo depois de descontar sexo, idade, escola, família e bullying." Não abrir com metodologia. |
| 2 | Pergunta, público e título | 1 min | Pergunta de pesquisa (protocolo_pesquisa.md). Público: escolares 13-17 anos, rede pública e privada, Brasil. Título oficial do projeto. |
| 3 | Base de dados (rápido, credibilidade) | 1,5 min | PeNSE 2019/IBGE, 124.898 alunos no domínio, desenho amostral complexo (escola/estrato/peso). Uma frase sobre por que isso importa: "sem o peso certo, a margem de erro sai errada". Citar validação: 2.760 estimativas replicadas das tabelas oficiais do IBGE, 93% com erro < 0,1 ponto percentual — é isso que dá confiança nos números que vêm a seguir. |
| 4 | DEMO EM VIVO do app | 4 min | Abrir o Streamlit direto (não print). Ordem: Panorama (prevalências com IC95%) → Comparações (escolher "sem amigos" × sexo/escola, deixar a banca pedir um grupo) → Resultados (OR ajustada). Deixar 1 interação ser pedida pela banca ao vivo (dá sensação de sistema funcional de verdade). |
| 5 | Resultado principal (H1) | 2 min | OR bruta 2,23 → ajustada completa 1,77 (IC95% 1,48–2,12): associação robusta, diminui ao controlar família/pares, mas não desaparece. H0 rejeitada. |
| 6 | Achado honesto/contraintuitivo | 1 min | "Preocupação" teve OR 0,78 (sentido invertido) — mostrar que não se escondeu um resultado que não bateu com a expectativa; isso é o que dá credibilidade científica diante da banca. |
| 7 | Limitações, sem rodeio | 1 min | Transversal (sem causalidade), autorrelato, exclui quem está fora da escola. Dizer isso ANTES que perguntem — mostra maturidade, não fragilidade. |
| 8 | Solução/aplicação prática + fechamento | 0,5 min | Para quem serve: gestores escolares/secretarias de educação priorizando apoio psicossocial por grupo de risco (agregado), não diagnóstico individual. Encerrar com a frase de abertura, fechando o círculo. |

## Papéis (se apresentação em grupo)
Dividir por função real do projeto, não por slide: quem fala de **dados/desenho amostral**
(credibilidade estatística), quem conduz a **demo do app** (mouse/teclado com uma pessoa só,
evita travar a transição), quem fala de **aplicação/impacto** (fala direto com o membro de
mercado da banca). O orientador/estatística pode assumir perguntas técnicas na Q&A.

## Risco técnico do dia
- Ter **print de cada página do app** como slide de backup (Wi-Fi/projetor podem falhar).
- Testar o `streamlit run app/app.py` no notebook/sala real antes, não só aqui.
- Base padrão (`data/processed/analitica_pense2019.csv.gz`) já carrega sem upload manual —
  não depender de internet para subir arquivo.

## Perguntas prováveis da banca (preparar resposta curta)
- *"Isso prevê ou diagnostica um aluno específico?"* → Não. Estatística agregada/exploratória,
  nunca diagnóstico individual (deixar isso explícito e repetido).
- *"Por que peso amostral complexo, dá pra simplificar?"* → Sem ele os IC e p-valores saem
  errados; validamos contra 2.760 números oficiais do IBGE para garantir isso.
- *"Causa ou correlação?"* → Correlação; desenho transversal não permite causalidade, direção
  reversa é plausível (quem já sofre pode se isolar mais, não só o contrário).
- *"Por que 2019 e não um ano mais recente?"* → Única edição com bloco completo de bullying/
  cyberbullying e dicionário oficial verificado disponível para esta análise.
- *"Qual o uso de mercado/impacto real?"* → Painel de priorização para redes escolares/políticas
  públicas (ODS 3), não produto clínico.

## O que NÃO fazer
- Não abrir com metodologia/desenho amostral — perde o membro de mercado nos primeiros 30s.
- Não esconder o resultado contraintuitivo da "preocupação" — citá-lo fortalece a banca.
- Não prometer causalidade nem uso clínico/diagnóstico em nenhum momento.
