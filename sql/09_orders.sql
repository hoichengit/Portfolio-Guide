WITH ordered AS (
 SELECT OrderID,SUM(Quantity*UnitPrice) AS ordered_ex_tax FROM Sales_OrderLines GROUP BY OrderID
), billed AS (
 SELECT i.OrderID,SUM(l.ExtendedPrice-l.TaxAmount) AS invoiced_ex_tax
 FROM Sales_Invoices i JOIN Sales_InvoiceLines l ON i.InvoiceID=l.InvoiceID GROUP BY i.OrderID
)
SELECT o.OrderID,o.OrderDate,o.BackorderOrderID,r.ordered_ex_tax,
 COALESCE(b.invoiced_ex_tax,0) AS invoiced_ex_tax,
 r.ordered_ex_tax-COALESCE(b.invoiced_ex_tax,0) AS unmatched_order_value
FROM Sales_Orders o JOIN ordered r ON o.OrderID=r.OrderID
LEFT JOIN billed b ON o.OrderID=b.OrderID
WHERE ABS(r.ordered_ex_tax-COALESCE(b.invoiced_ex_tax,0))>0.02
ORDER BY o.OrderDate DESC;
