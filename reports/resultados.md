# Resultados da execução

Gerado automaticamente pelo experimento; não editar os valores manualmente.

- Modelo selecionado: **XGBoost calibrado**.
- Origem: https://doi.org/10.24432/C55S3H (CC BY 4.0).
- SHA-256: `56c885f84457f6680f8438f02bfcdac9579323d8a94465ee5f26e32baa727602`.
- Registros: 30,000; inadimplentes: 6,636.
- Perfis repetidos após a primeira ocorrência: 817. Permaneceram agrupados, sem exclusão.

## Partições

| Partição | Clientes | Inadimplentes | Prevalência |
|---|---:|---:|---:|
| treino | 18004 | 3984 | 22.13% |
| validacao | 5998 | 1326 | 22.11% |
| teste | 5998 | 1326 | 22.11% |

## Comparação na validação

| Modelo | Brier ↓ | ROC AUC ↑ | AP ↑ |
|---|---:|---:|---:|
| XGBoost calibrado | 0.1409 | 0.7633 | 0.5211 |
| Regressao Logistica | 0.1419 | 0.7493 | 0.5045 |
| Referencia | 0.1722 | 0.5000 | 0.2211 |

## Avaliação final no teste

Limiar de alerta escolhido na validação: **0.255**.

| Métrica | Resultado |
|---|---:|
| roc_auc | 0.7934 |
| average_precision | 0.5757 |
| brier | 0.1318 |
| log_loss | 0.4226 |
| ks | 0.4587 |
| gini | 0.5867 |
| precision | 0.5401 |
| recall | 0.5588 |
| f1 | 0.5493 |
| tn | 4041 |
| fp | 631 |
| fn | 585 |
| tp | 741 |

## Cenários fixos no teste

| Corte PD | Elegíveis | Elegibilidade | Inadimplência entre elegíveis |
|---|---:|---:|---:|
| 10% | 1405 | 23.42% | 5.05% |
| 20% | 4216 | 70.29% | 11.22% |
| 30% | 4867 | 81.14% | 13.64% |
| 40% | 5098 | 84.99% | 14.71% |

Os cortes são ilustrativos e não foram otimizados pelo teste. Não há conclusão sobre rentabilidade ou política ideal.

PSI entre validação e teste: **0.00440**. É uma comparação entre amostras da mesma fotografia, não evidência de monitoramento temporal.

Consulte a metodologia e as limitações no README antes de interpretar estes resultados.
