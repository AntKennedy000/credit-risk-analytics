# Guia para apresentar e defender o projeto

## Explicação em um minuto

O projeto usa uma base pública de clientes que já possuem cartão para estimar inadimplência no mês seguinte. Foram comparadas uma referência de prevalência, Regressão Logística e XGBoost calibrado. A escolha foi feita na validação pelo Brier, e o teste ficou reservado para medir o resultado final. As probabilidades alimentam consultas SQL, faixas de risco e um painel que compara quatro cortes ilustrativos de elegibilidade.

## Perguntas que você precisa saber responder

**Por que Brier?** Porque queremos avaliar probabilidades, não apenas a classificação. Ele calcula o erro quadrático entre a probabilidade estimada e o resultado binário. Valores menores são melhores, mas devem ser comparados dentro do mesmo contexto de dados.

**Por que também AUC e KS?** Eles complementam a avaliação da capacidade de ordenar clientes por risco. Um bom ranking não garante que as probabilidades estejam calibradas.

**Por que separar validação e teste?** A validação orienta escolhas; o teste mede o resultado depois dessas escolhas. Se o teste também orientar ajustes, sua avaliação deixa de ser independente.

**Por que agrupar perfis repetidos?** Para evitar que as mesmas entradas apareçam nos dois lados da avaliação. Não apagamos registros apenas porque possuem o mesmo perfil.

**Por que não aprovamos clientes reais?** Porque é uma base histórica de outra população, com clientes existentes e sem validação comercial. O seletor apenas descreve quais registros teriam PD abaixo de um corte.

**Qual é a relação com sua experiência?** O problema aproxima crédito, inadimplência e análise de dados. A interpretação deve reconhecer as diferenças entre concessão, acompanhamento da carteira e recuperação, sem atribuir ao projeto conhecimentos não demonstrados.

**Por que não há perda esperada?** Faltam informações validadas de LGD e exposição em default. Usar o limite do cartão como se fosse exposição real geraria uma conclusão financeira inadequada.

**Qual seria o próximo passo?** Validar o painel no Power BI e, para evoluir o modelo, encontrar uma base longitudinal que permita testar períodos futuros. Azure pode ser uma etapa posterior de engenharia, sem mudar a metodologia.

## Antes de colocar no currículo

Execute o exemplo, confira a diferença entre modelo e política, leia as limitações e consiga explicar os três gráficos. Descreva o que foi executado: Python, SQL/SQLite, modelos de classificação, calibração e painel HTML. Acrescente Power BI somente quando essa etapa estiver implementada e validada.
