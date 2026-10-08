WITH overdue AS (
 SELECT t.CustomerTransactionID,c.CustomerName,t.InvoiceID,t.TransactionDate,
 date(t.TransactionDate,'+'||c.PaymentDays||' days') AS due_date,
 t.OutstandingBalance AS balance,
 CAST(julianday('2016-05-31')-julianday(t.TransactionDate)-c.PaymentDays AS INTEGER) AS days_overdue
 FROM Sales_CustomerTransactions t JOIN Sales_Customers c ON t.CustomerID=c.CustomerID
 WHERE t.OutstandingBalance<>0
)
SELECT *, CASE WHEN days_overdue<=0 THEN 'Current' WHEN days_overdue<=30 THEN '1-30 days'
 WHEN days_overdue<=60 THEN '31-60 days' ELSE '61+ days' END AS aging_bucket
FROM overdue ORDER BY days_overdue DESC,balance DESC;
