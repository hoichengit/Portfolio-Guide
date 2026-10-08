WITH c AS (
 SELECT i.CustomerID, SUM(l.ExtendedPrice-l.TaxAmount) AS sales,
 SUM(l.LineProfit) AS gross_profit, COUNT(DISTINCT i.InvoiceID) AS invoices
 FROM Sales_Invoices i JOIN Sales_InvoiceLines l ON i.InvoiceID=l.InvoiceID
 WHERE i.InvoiceDate>='2015-06-01' AND i.InvoiceDate<'2016-06-01'
 GROUP BY i.CustomerID
)
SELECT ROW_NUMBER() OVER(ORDER BY c.gross_profit DESC) AS profit_rank,
 n.CustomerName,c.*,1.0*c.gross_profit/NULLIF(c.sales,0) AS gross_margin,
 1.0*c.sales/SUM(c.sales) OVER() AS revenue_share
FROM c JOIN Sales_Customers n ON c.CustomerID=n.CustomerID ORDER BY profit_rank;
