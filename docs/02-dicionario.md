# Dicionário de dados

Origem: [UCI / Yeh](https://doi.org/10.24432/C55S3H), CC BY 4.0. Valores financeiros em NT$.

| Campo | Tratamento |
|---|---|
| ID | Identificador de origem, excluído dos atributos do modelo. |
| LIMIT_BAL | Limite concedido; precisa ser positivo. Não é EAD nem saldo devedor. |
| PAY_0, PAY_2…PAY_6 | Estados mensais de pagamento, do mais recente para o mais antigo. Os códigos originais são preservados. Valores positivos representam meses de atraso segundo a fonte. |
| BILL_AMT1…6 | Valores das faturas mensais, de setembro a abril de 2005. Valores não positivos são preservados. |
| PAY_AMT1…6 | Valores pagos nos meses correspondentes, conforme a nomenclatura da fonte. |
| SEX, EDUCATION, MARRIAGE, AGE | Excluídos do modelo nesta versão. |
| default payment next month | Alvo binário: 1 inadimplente, 0 não inadimplente, conforme definição original. |
| utilizacao_limite | BILL_AMT1 / LIMIT_BAL; pode exceder 1 ou ser negativa. |
| pagamento_sobre_fatura | PAY_AMT1 / BILL_AMT1 quando a fatura é positiva; caso contrário 0 por convenção explícita. Não é taxa de recuperação. |
| meses_com_atraso | Número de códigos PAY maiores que zero no histórico. |
| maior_atraso | Máximo dos códigos PAY, limitados inferiormente a zero. |

## Saída de teste

| Campo | Definição |
|---|---|
| id | ID público de origem, para rastrear partição. |
| pd_estimada | Probabilidade do desfecho no horizonte original da base. |
| inadimplente | Resultado observado, 0 ou 1. |
| faixa_risco | Baixo ≤ 10%; Moderado > 10% e ≤ 20%; Alto > 20% e ≤ 40%; Muito alto > 40%. |
| limite_ntd | Limite original em NT$. |
| alerta | 1 quando PD ≥ limiar escolhido na validação. |

## Indicadores

- Taxa de inadimplência: soma do alvo / quantidade de clientes do grupo.
- PD média: média das probabilidades do grupo.
- Elegibilidade: PD menor ou igual ao corte ilustrativo.
- Taxa de elegibilidade: elegíveis / total da partição.
- Inadimplência entre elegíveis: inadimplentes elegíveis / elegíveis. Sem elegíveis, a taxa fica ausente, não zero.
