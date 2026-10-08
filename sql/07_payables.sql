SELECT s.SupplierName,t.SupplierTransactionID,t.TransactionDate,
 date(t.TransactionDate,'+'||s.PaymentDays||' days') AS due_date,
 t.OutstandingBalance AS balance,
 CASE WHEN date(t.TransactionDate,'+'||s.PaymentDays||' days')<'2016-05-31' THEN 'Overdue' ELSE 'Current' END AS status
FROM Purchasing_SupplierTransactions t JOIN Purchasing_Suppliers s ON t.SupplierID=s.SupplierID
WHERE t.OutstandingBalance<>0 ORDER BY due_date,balance DESC;
