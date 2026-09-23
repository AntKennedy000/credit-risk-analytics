# Power BI — roteiro de evolução

**Status: preparado para implementação; não executado.** O painel concluído desta versão é HTML. Não há `.pbix` neste repositório.

Após executar `python -m src.train`, importe `data/processed/carteira_teste.csv` como tabela `Carteira`. Use localidade **Inglês (Estados Unidos)** ao interpretar números com ponto decimal. Defina `id`, `inadimplente` e `alerta` como números inteiros; `pd_estimada` e `limite_ntd` como decimais; `faixa_risco` como texto.

Crie as medidas de `medidas.dax`, uma por vez. Os cálculos são definidos em relação ao contexto de filtros e usam exclusivamente a partição de teste.

Página sugerida:

1. Cartões: clientes, inadimplência observada, PD média e limite total (NT$).
2. Colunas agrupadas: PD média e inadimplência por faixa.
3. Tabela: faixa, clientes, inadimplentes e limite médio.
4. Filtro: faixa de risco.
5. Rodapé: fonte, horizonte de um mês, Taiwan/2005 e uso educacional.

Não rotular limite total como carteira em aberto, EAD ou desembolso. Não criar série temporal com ID ou datas inventadas. Para ordenar as faixas, crie uma coluna `OrdemFaixa` com 1 Baixo, 2 Moderado, 3 Alto e 4 Muito alto; configure classificação de `faixa_risco` por essa coluna.

Validação ao concluir: conferir totais e taxas com `reports/faixas_risco.csv`, registrar capturas reais em `evidencias/` e atualizar o status desta pasta. As medidas abaixo ainda precisam ser validadas no Power BI.
