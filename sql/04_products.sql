SELECT s.StockItemID,s.StockItemName,SUM(l.Quantity) AS units,
 SUM(l.ExtendedPrice-l.TaxAmount) AS sales,SUM(l.LineProfit) AS gross_profit,
 1.0*SUM(l.LineProfit)/NULLIF(SUM(l.ExtendedPrice-l.TaxAmount),0) AS gross_margin
FROM Sales_InvoiceLines l JOIN Sales_Invoices i ON l.InvoiceID=i.InvoiceID
JOIN Warehouse_StockItems s ON l.StockItemID=s.StockItemID
WHERE i.InvoiceDate>='2015-06-01' AND i.InvoiceDate<'2016-06-01'
GROUP BY s.StockItemID,s.StockItemName ORDER BY gross_profit DESC;
