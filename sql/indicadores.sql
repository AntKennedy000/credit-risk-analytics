-- Fonte: somente o conjunto de teste; valores monetários em NT$, não reais.
-- LIMIT_BAL é limite concedido, não saldo devedor nem exposição em default.
SELECT faixa_risco,
       COUNT(*) AS clientes,
       SUM(inadimplente) AS inadimplentes,
       AVG(inadimplente * 1.0) AS taxa_inadimplencia,
       AVG(pd_estimada) AS pd_media,
       AVG(limite_ntd) AS limite_medio_ntd
FROM carteira_teste
GROUP BY faixa_risco
ORDER BY pd_media;
