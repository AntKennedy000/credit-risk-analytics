# Metodologia e decisões

## Escopo

Risco comportamental de clientes existentes de cartão, com desfecho binário no mês seguinte. Não confundir com score de originação, modelo regulatório de 12 meses ou decisão automatizada de concessão.

## Separação dos dados

São criados cinco grupos de partições com `StratifiedGroupKFold`, semente 42. O primeiro é teste, o segundo validação e os outros três treino. O agrupamento é o hash dos atributos usados pelo modelo: registros com entradas idênticas ficam sempre juntos, mesmo que tenham IDs ou desfechos diferentes. Nenhuma linha é removida por essa repetição.

A estratificação busca aproximar prevalências, mas restrições de grupos podem impedir tamanhos e proporções exatos. Os números reais constam no JSON. ID não é interpretado como data. Não há claim de validação temporal.

## Ajuste e calibração

A Regressão Logística padroniza atributos numéricos e usa one-hot para códigos de pagamento, preservando categorias como -2 e 0 sem inventar significados ausentes na documentação resumida da fonte.

O XGBoost usa 180 árvores, profundidade 3, learning rate 0,05, amostragem 0,85 e regularização L2 de 5. Uma calibração sigmoide em três folds internos ao treino ajusta as probabilidades; a saída final é a média dos classificadores calibrados. Os grupos internos também são disjuntos.

Modelos são comparados pelo Brier da validação (menor é melhor). Não são ajustados hiperparâmetros no teste. O modelo selecionado não é retreinado com validação antes da avaliação final, preservando a compatibilidade com o limiar escolhido.

## Limiar e cenários

O limiar de alerta maximiza F1 na grade 0,05–0,80, passo 0,005, somente na validação. Empates usam o menor valor encontrado. F1 não incorpora custos financeiros; o limiar não representa uma política ótima de crédito.

Os cortes de elegibilidade (PD ≤ 10%, 20%, 30%, 40%) são fixados a priori e apenas descritos em validação e teste. Não escolhemos o melhor corte olhando o teste. A inadimplência do grupo elegível é observada retrospectivamente, não prevista como efeito de uma nova política.

## Estabilidade e interpretação

O PSI usa dez intervalos fixos de probabilidade e suavização de 0,5 na contagem de cada intervalo. Compara validação e teste; ambos pertencem à mesma fotografia histórica. Não aplicamos regras automáticas de semáforo ou conclusões de deriva em produção.

A importância por permutação usa três repetições na validação. As barras de dispersão representam variação das permutações, não intervalos de confiança da população. Correlação e atributos derivados limitam a interpretação isolada.

## O que não pode ser inferido

- Desempenho futuro, brasileiro ou em outros produtos;
- Ganhos de rentabilidade, redução comprovada de perdas ou causalidade;
- Cumprimento regulatório, provisão contábil ou validade comercial;
- Ausência de discriminação por excluir colunas demográficas;
- Validade de PD em uma população com prevalência diferente.
