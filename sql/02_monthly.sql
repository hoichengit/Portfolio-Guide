WITH sales AS (
 SELECT substr(i.InvoiceDate,1,7) AS month,
 SUM(l.ExtendedPrice-l.TaxAmount) AS sales_ex_tax,
 SUM(l.TaxAmount) AS sales_tax, SUM(l.LineProfit) AS gross_profit
 FROM Sales_Invoices i JOIN Sales_InvoiceLines l ON i.InvoiceID=l.InvoiceID
 GROUP BY 1
), cash AS (
 SELECT substr(TransactionDate,1,7) AS month,
 -SUM(CASE WHEN TransactionTypeID=3 THEN TransactionAmount ELSE 0 END) AS receipts_inc_tax
 FROM Sales_CustomerTransactions GROUP BY 1
)
SELECT s.*, c.receipts_inc_tax,
 1.0*gross_profit/NULLIF(sales_ex_tax,0) AS gross_margin,
 1.0*sales_ex_tax/NULLIF(LAG(sales_ex_tax,12) OVER(ORDER BY s.month),0)-1 AS sales_yoy
FROM sales s LEFT JOIN cash c ON s.month=c.month ORDER BY s.month;
