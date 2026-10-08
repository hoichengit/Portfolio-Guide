WITH usage AS (
 SELECT l.StockItemID,SUM(l.Quantity) AS units_90d
 FROM Sales_InvoiceLines l JOIN Sales_Invoices i ON l.InvoiceID=i.InvoiceID
 WHERE i.InvoiceDate BETWEEN '2016-03-03' AND '2016-05-31' GROUP BY l.StockItemID
)
SELECT s.StockItemName,h.StockItemID,h.QuantityOnHand,h.LastCostPrice,
 h.QuantityOnHand*h.LastCostPrice AS value_at_last_cost,
 COALESCE(u.units_90d,0) AS units_90d,
 90.0*h.QuantityOnHand/NULLIF(u.units_90d,0) AS days_cover,
 CASE WHEN h.QuantityOnHand>h.TargetStockLevel THEN (h.QuantityOnHand-h.TargetStockLevel)*h.LastCostPrice ELSE 0 END AS excess_vs_target
FROM Warehouse_StockItemHoldings h JOIN Warehouse_StockItems s ON h.StockItemID=s.StockItemID
LEFT JOIN usage u ON h.StockItemID=u.StockItemID ORDER BY value_at_last_cost DESC;
