WITH inputs AS (
 SELECT 2.0 AS ar_days_reduction, 0.01 AS stock_reduction
), annual_sales AS (
 SELECT SUM(l.ExtendedPrice-l.TaxAmount) AS revenue
 FROM Sales_InvoiceLines l JOIN Sales_Invoices i ON i.InvoiceID=l.InvoiceID
 WHERE i.InvoiceDate>='2015-06-01' AND i.InvoiceDate<'2016-06-01'
), balances AS (
 SELECT (SELECT SUM(OutstandingBalance) FROM Sales_CustomerTransactions) AS ar,
 (SELECT SUM(QuantityOnHand*LastCostPrice) FROM Warehouse_StockItemHoldings) AS stock
)
SELECT ar_days_reduction,stock_reduction,
 MIN(revenue/365.0*ar_days_reduction,ar) AS capped_ar_release,
 stock*stock_reduction AS stock_release_at_cost,
 MIN(revenue/365.0*ar_days_reduction,ar)+stock*stock_reduction AS illustrative_total
FROM inputs CROSS JOIN annual_sales CROSS JOIN balances;
