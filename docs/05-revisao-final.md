# Revisão final — 23/09/2026

## Escopo verificado

- Contrato da fonte, criação de atributos e separação por grupos;
- Ajuste do preparo e calibração dentro do treino;
- Seleção do modelo e do limiar na validação, com teste reservado;
- Reprodução das probabilidades pelo modelo salvo;
- Consistência da matriz de confusão, partições e indicadores SQL;
- Correspondência entre métricas, tabelas, gráficos e documentação;
- Limites declarados: risco comportamental, base histórica, sem validação temporal ou Power BI executado;
- Links locais e execução dos testes.

## Correção realizada

Quando um dos cortes não selecionava nenhum cliente, o pandas podia representar a taxa de inadimplência como `NaN`. A serialização estrita do painel falhava nesse caso; o relatório Markdown podia exibir `nan%` ou falhar ao formatar `None`. O gráfico também tentava posicionar rótulos sem uma taxa válida.

O painel agora utiliza `null`, o relatório informa **Sem elegíveis**, e o gráfico omite pontos sem taxa observada. Se todos os cortes ficarem vazios, o gráfico apresenta uma mensagem explicativa. Taxa ausente permanece distinta de taxa zero.

Foram incluídos três testes com cenários parcialmente vazios e totalmente vazios, abrangendo a serialização HTML, a tabela Markdown e a geração completa dos gráficos. Os testes específicos reproduziram a falha antes da correção e passaram depois dela.

## Validação

**15 testes locais aprovados**, incluindo os quatro testes de integração com os artefatos já treinados. O registro está em [verificacao.txt](../reports/verificacao.txt).

Os relatórios foram regenerados a partir das previsões salvas. Gráficos, tabelas de resultados e métricas do experimento publicado permaneceram iguais; não foi necessário treinar ou ajustar novamente o modelo.

O README passou a orientar uma segunda execução dos testes após treinar, para que os testes de integração também sejam executados. No CI, esses quatro testes continuam sendo ignorados quando os artefatos locais não existem.

## Avaliação

A primeira versão está consistente para apresentação como projeto autoral educacional de portfólio. O escopo demonstrado é Python, SQL/SQLite, avaliação de modelos, calibração e comunicação de resultados em HTML.

Power BI permanece uma evolução documentada, sem `.pbix` validado. Auditoria de equidade, validação temporal e externa, intervalos de confiança e avaliação financeira não integram esta versão. A revisão não constitui validação para uso em decisões reais de crédito.
