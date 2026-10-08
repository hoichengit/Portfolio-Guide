WITH p AS (
 SELECT l.StockItemID,
 SUM(CASE WHEN substr(i.InvoiceDate,1,7)='2015-05' THEN l.Quantity ELSE 0 END) AS q0,
 SUM(CASE WHEN substr(i.InvoiceDate,1,7)='2016-05' THEN l.Quantity ELSE 0 END) AS q1,
 SUM(CASE WHEN substr(i.InvoiceDate,1,7)='2015-05' THEN l.ExtendedPrice-l.TaxAmount ELSE 0 END) AS r0,
 SUM(CASE WHEN substr(i.InvoiceDate,1,7)='2016-05' THEN l.ExtendedPrice-l.TaxAmount ELSE 0 END) AS r1
 FROM Sales_InvoiceLines l JOIN Sales_Invoices i ON l.InvoiceID=i.InvoiceID
 WHERE substr(i.InvoiceDate,1,7) IN ('2015-05','2016-05') GROUP BY l.StockItemID
)
SELECT 'Volume at prior price (common products)' AS driver,SUM((q1-q0)*1.0*r0/q0) AS impact
FROM p WHERE q0>0 AND q1>0
UNION ALL SELECT 'Realised price / within-product mix',SUM(q1*(1.0*r1/q1-1.0*r0/q0)) FROM p WHERE q0>0 AND q1>0
UNION ALL SELECT 'New or discontinued products',SUM(r1-r0) FROM p WHERE q0=0 OR q1=0
UNION ALL SELECT 'Total sales change',SUM(r1-r0) FROM p;
