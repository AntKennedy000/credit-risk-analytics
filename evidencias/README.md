# Evidências da execução

As imagens são gráficos gerados pelo código com os resultados reais do experimento, não capturas ilustrativas de ferramentas.

| Arquivo | Origem |
|---|---|
| 01-avaliacao-modelo.png | Previsões do modelo selecionado sobre o teste reservado. |
| 02-carteira-cenarios.png | Agregados SQL por faixa e quatro cortes fixos de elegibilidade. |
| 03-importancia-validacao.png | Importância por permutação, três repetições, sobre a validação. |

Para regenerar somente os gráficos e o painel, preservando o modelo e as previsões salvas:

```powershell
.\.venv\Scripts\python.exe -m src.report
```

`reports/verificacao.txt` registra os 12 testes executados localmente após o treino, todos aprovados.

A [execução no GitHub Actions em 23/09/2026](https://github.com/AntKennedy000/credit-risk-analytics/actions/runs/35852845403) também foi concluída com sucesso: oito testes executados e aprovados; quatro testes de integração ignorados porque dependem dos artefatos gerados pelo treinamento local. Isso não representa um novo treinamento na nuvem. O workflow possui apenas permissão de leitura e não grava alterações no repositório.

O painel foi aberto no navegador e o cenário de 20% foi conferido: 4.216 elegíveis, 70,3% de elegibilidade e 11,2% de inadimplência observada entre elegíveis. Esses números correspondem ao CSV de cenários, com arredondamento de exibição.
