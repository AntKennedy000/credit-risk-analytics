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

`reports/verificacao.txt` registra os 12 testes executados localmente após o treino. A automação de GitHub Actions está configurada, mas não foi executada remotamente nesta entrega; testes dependentes dos artefatos são ignorados em ambientes que ainda não rodaram o treino.

O painel foi aberto no navegador e o cenário de 20% foi conferido: 4.216 elegíveis, 70,3% de elegibilidade e 11,2% de inadimplência observada entre elegíveis. Esses números correspondem ao CSV de cenários, com arredondamento de exibição.
