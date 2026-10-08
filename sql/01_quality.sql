WITH lines AS (
 SELECT InvoiceID, SUM(ExtendedPrice) AS line_total
 FROM Sales_InvoiceLines GROUP BY InvoiceID
), ledger AS (
 SELECT InvoiceID, SUM(TransactionAmount) AS ledger_total
 FROM Sales_CustomerTransactions WHERE TransactionTypeID IN (1,2)
 GROUP BY InvoiceID
)
SELECT 'Invoice-to-ledger mismatches' AS check_name, COUNT(*) AS failures
FROM lines l LEFT JOIN ledger t ON l.InvoiceID=t.InvoiceID
WHERE t.InvoiceID IS NULL OR ABS(l.line_total-t.ledger_total)>0.02
UNION ALL
SELECT 'Line arithmetic mismatches',COUNT(*) FROM Sales_InvoiceLines
WHERE ABS(Quantity*UnitPrice+TaxAmount-ExtendedPrice)>0.02
UNION ALL
SELECT 'Orphan invoice lines',COUNT(*) FROM Sales_InvoiceLines l
LEFT JOIN Sales_Invoices i ON l.InvoiceID=i.InvoiceID WHERE i.InvoiceID IS NULL
UNION ALL
SELECT 'Duplicate invoice IDs',COUNT(*)-COUNT(DISTINCT InvoiceID) FROM Sales_Invoices;
