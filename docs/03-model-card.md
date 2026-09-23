# Ficha do modelo

**Uso pretendido:** estudo de risco comportamental e comunicação de indicadores de crédito.

**População de desenvolvimento:** clientes existentes de cartão de Taiwan em 2005. Fonte e licença registradas no README.

**Horizonte:** desfecho de inadimplência no mês seguinte, conforme a UCI. Não é PD regulatória de 12 meses.

**Modelo publicado localmente:** definido por menor Brier na validação; nome, métricas, versões e hash constam em `reports/resumo.json`. O arquivo treinado é regenerável e não integra o Git.

**Entradas:** 19 atributos financeiros/históricos originais e quatro derivados. Identificador e atributos demográficos não entram no modelo.

**Saídas:** probabilidade, faixa ilustrativa e alerta por limiar. Não há recomendação de taxa de juros, limite ou decisão comercial.

**Validação:** grupos de entradas idênticas separados entre treino, validação e teste; avaliação final do modelo selecionado apenas no teste.

**Vieses e lacunas:** sem avaliação temporal ou externa, sem auditoria de equidade, sem intervalos de confiança, com possíveis variáveis proxy. Resultado não transferível automaticamente a outras populações.

**Interpretação:** importância por permutação global na validação. Não há explicação individual validada ou causalidade.

**Operação:** inferência local em lote; não há implantação, monitoramento contínuo ou integração bancária. O PSI apresentado é uma demonstração entre partições.

**Restrições:** uso educacional. Não utilizar para decisões que afetem pessoas reais.
