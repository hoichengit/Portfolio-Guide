# Raw data — WideWorldImporters

**Purpose:** retain the original transaction values and explain how the tables connect.

- [Download the 14 raw tables](WWI_raw_tables.zip): CSV extracts plus the original column metadata. No financial rows are filtered out of these tables.
- [Original Microsoft BACPAC](https://github.com/microsoft/sql-server-samples/releases/download/wide-world-importers-v1.0/WideWorldImporters-Standard.bacpac): complete SQL Server source archive, also retained in the local project package.
- [Source manifest](source_manifest.json): download URL, file size and SHA-256 fingerprint.
- [Microsoft sample repository](https://github.com/microsoft/sql-server-samples/tree/master/samples/databases/wide-world-importers): sample documentation and licensing.

The BACPAC uses SQL Server native records. The extraction script reads the schema and decodes all stored rows; stream boundaries are checked. The portable analysis imports the selected raw tables into SQLite. Computed SQL Server columns are not stored in the BCP stream. In CSV, blank nullable text can represent either an empty string or NULL; the BACPAC remains the authoritative source for that distinction.

Dates use ISO format; monetary values retain decimal amounts; quantities are numeric; IDs are keys, not measures. Table names replace `.` with `_` in SQLite. **ExtendedPrice includes tax**; revenue uses ExtendedPrice minus TaxAmount. **LineProfit is gross profit**, not net income.

### Original values

![Original database values](../evidence/Raw%20sample.png)

## Table and column dictionary

<details>
<summary>Sales.InvoiceLines — 13 stored columns</summary>

| Column | Original SQL Server type | Nullable |
|---|---|---|
| InvoiceLineID | int | No |
| InvoiceID | int | No |
| StockItemID | int | No |
| Description | nvarchar | No |
| PackageTypeID | int | No |
| Quantity | int | No |
| UnitPrice | decimal | Yes |
| TaxRate | decimal | No |
| TaxAmount | decimal | No |
| LineProfit | decimal | No |
| ExtendedPrice | decimal | No |
| LastEditedBy | int | No |
| LastEditedWhen | datetime2 | No |

</details>

<details>
<summary>Sales.Invoices — 23 stored columns</summary>

| Column | Original SQL Server type | Nullable |
|---|---|---|
| InvoiceID | int | No |
| CustomerID | int | No |
| BillToCustomerID | int | No |
| OrderID | int | Yes |
| DeliveryMethodID | int | No |
| ContactPersonID | int | No |
| AccountsPersonID | int | No |
| SalespersonPersonID | int | No |
| PackedByPersonID | int | No |
| InvoiceDate | date | No |
| CustomerPurchaseOrderNumber | nvarchar | Yes |
| IsCreditNote | bit | No |
| CreditNoteReason | nvarchar(max) | Yes |
| Comments | nvarchar(max) | Yes |
| DeliveryInstructions | nvarchar(max) | Yes |
| InternalComments | nvarchar(max) | Yes |
| TotalDryItems | int | No |
| TotalChillerItems | int | No |
| DeliveryRun | nvarchar | Yes |
| RunPosition | nvarchar | Yes |
| ReturnedDeliveryData | nvarchar(max) | Yes |
| LastEditedBy | int | No |
| LastEditedWhen | datetime2 | No |

</details>

<details>
<summary>Sales.CustomerTransactions — 13 stored columns</summary>

| Column | Original SQL Server type | Nullable |
|---|---|---|
| CustomerTransactionID | int | No |
| CustomerID | int | No |
| TransactionTypeID | int | No |
| InvoiceID | int | Yes |
| PaymentMethodID | int | Yes |
| TransactionDate | date | No |
| AmountExcludingTax | decimal | No |
| TaxAmount | decimal | No |
| TransactionAmount | decimal | No |
| OutstandingBalance | decimal | No |
| FinalizationDate | date | Yes |
| LastEditedBy | int | No |
| LastEditedWhen | datetime2 | No |

</details>

<details>
<summary>Sales.Customers — 31 stored columns</summary>

| Column | Original SQL Server type | Nullable |
|---|---|---|
| CustomerID | int | No |
| CustomerName | nvarchar | No |
| BillToCustomerID | int | No |
| CustomerCategoryID | int | No |
| BuyingGroupID | int | Yes |
| PrimaryContactPersonID | int | No |
| AlternateContactPersonID | int | Yes |
| DeliveryMethodID | int | No |
| DeliveryCityID | int | No |
| PostalCityID | int | No |
| CreditLimit | decimal | Yes |
| AccountOpenedDate | date | No |
| StandardDiscountPercentage | decimal | No |
| IsStatementSent | bit | No |
| IsOnCreditHold | bit | No |
| PaymentDays | int | No |
| PhoneNumber | nvarchar | No |
| FaxNumber | nvarchar | No |
| DeliveryRun | nvarchar | Yes |
| RunPosition | nvarchar | Yes |
| WebsiteURL | nvarchar | No |
| DeliveryAddressLine1 | nvarchar | No |
| DeliveryAddressLine2 | nvarchar | Yes |
| DeliveryPostalCode | nvarchar | No |
| DeliveryLocation | geography | Yes |
| PostalAddressLine1 | nvarchar | No |
| PostalAddressLine2 | nvarchar | Yes |
| PostalPostalCode | nvarchar | No |
| LastEditedBy | int | No |
| ValidFrom | datetime2 | No |
| ValidTo | datetime2 | No |

</details>

<details>
<summary>Sales.Orders — 16 stored columns</summary>

| Column | Original SQL Server type | Nullable |
|---|---|---|
| OrderID | int | No |
| CustomerID | int | No |
| SalespersonPersonID | int | No |
| PickedByPersonID | int | Yes |
| ContactPersonID | int | No |
| BackorderOrderID | int | Yes |
| OrderDate | date | No |
| ExpectedDeliveryDate | date | No |
| CustomerPurchaseOrderNumber | nvarchar | Yes |
| IsUndersupplyBackordered | bit | No |
| Comments | nvarchar(max) | Yes |
| DeliveryInstructions | nvarchar(max) | Yes |
| InternalComments | nvarchar(max) | Yes |
| PickingCompletedWhen | datetime2 | Yes |
| LastEditedBy | int | No |
| LastEditedWhen | datetime2 | No |

</details>

<details>
<summary>Sales.OrderLines — 12 stored columns</summary>

| Column | Original SQL Server type | Nullable |
|---|---|---|
| OrderLineID | int | No |
| OrderID | int | No |
| StockItemID | int | No |
| Description | nvarchar | No |
| PackageTypeID | int | No |
| Quantity | int | No |
| UnitPrice | decimal | Yes |
| TaxRate | decimal | No |
| PickedQuantity | int | No |
| PickingCompletedWhen | datetime2 | Yes |
| LastEditedBy | int | No |
| LastEditedWhen | datetime2 | No |

</details>

<details>
<summary>Purchasing.SupplierTransactions — 14 stored columns</summary>

| Column | Original SQL Server type | Nullable |
|---|---|---|
| SupplierTransactionID | int | No |
| SupplierID | int | No |
| TransactionTypeID | int | No |
| PurchaseOrderID | int | Yes |
| PaymentMethodID | int | Yes |
| SupplierInvoiceNumber | nvarchar | Yes |
| TransactionDate | date | No |
| AmountExcludingTax | decimal | No |
| TaxAmount | decimal | No |
| TransactionAmount | decimal | No |
| OutstandingBalance | decimal | No |
| FinalizationDate | date | Yes |
| LastEditedBy | int | No |
| LastEditedWhen | datetime2 | No |

</details>

<details>
<summary>Purchasing.Suppliers — 29 stored columns</summary>

| Column | Original SQL Server type | Nullable |
|---|---|---|
| SupplierID | int | No |
| SupplierName | nvarchar | No |
| SupplierCategoryID | int | No |
| PrimaryContactPersonID | int | No |
| AlternateContactPersonID | int | No |
| DeliveryMethodID | int | Yes |
| DeliveryCityID | int | No |
| PostalCityID | int | No |
| SupplierReference | nvarchar | Yes |
| BankAccountName | nvarchar | Yes |
| BankAccountBranch | nvarchar | Yes |
| BankAccountCode | nvarchar | Yes |
| BankAccountNumber | nvarchar | Yes |
| BankInternationalCode | nvarchar | Yes |
| PaymentDays | int | No |
| InternalComments | nvarchar(max) | Yes |
| PhoneNumber | nvarchar | No |
| FaxNumber | nvarchar | No |
| WebsiteURL | nvarchar | No |
| DeliveryAddressLine1 | nvarchar | No |
| DeliveryAddressLine2 | nvarchar | Yes |
| DeliveryPostalCode | nvarchar | No |
| DeliveryLocation | geography | Yes |
| PostalAddressLine1 | nvarchar | No |
| PostalAddressLine2 | nvarchar | Yes |
| PostalPostalCode | nvarchar | No |
| LastEditedBy | int | No |
| ValidFrom | datetime2 | No |
| ValidTo | datetime2 | No |

</details>

<details>
<summary>Purchasing.PurchaseOrders — 12 stored columns</summary>

| Column | Original SQL Server type | Nullable |
|---|---|---|
| PurchaseOrderID | int | No |
| SupplierID | int | No |
| OrderDate | date | No |
| DeliveryMethodID | int | No |
| ContactPersonID | int | No |
| ExpectedDeliveryDate | date | Yes |
| SupplierReference | nvarchar | Yes |
| IsOrderFinalized | bit | No |
| Comments | nvarchar(max) | Yes |
| InternalComments | nvarchar(max) | Yes |
| LastEditedBy | int | No |
| LastEditedWhen | datetime2 | No |

</details>

<details>
<summary>Purchasing.PurchaseOrderLines — 12 stored columns</summary>

| Column | Original SQL Server type | Nullable |
|---|---|---|
| PurchaseOrderLineID | int | No |
| PurchaseOrderID | int | No |
| StockItemID | int | No |
| OrderedOuters | int | No |
| Description | nvarchar | No |
| ReceivedOuters | int | No |
| PackageTypeID | int | No |
| ExpectedUnitPricePerOuter | decimal | Yes |
| LastReceiptDate | date | Yes |
| IsOrderLineFinalized | bit | No |
| LastEditedBy | int | No |
| LastEditedWhen | datetime2 | No |

</details>

<details>
<summary>Warehouse.StockItems — 23 stored columns</summary>

| Column | Original SQL Server type | Nullable |
|---|---|---|
| StockItemID | int | No |
| StockItemName | nvarchar | No |
| SupplierID | int | No |
| ColorID | int | Yes |
| UnitPackageID | int | No |
| OuterPackageID | int | No |
| Brand | nvarchar | Yes |
| Size | nvarchar | Yes |
| LeadTimeDays | int | No |
| QuantityPerOuter | int | No |
| IsChillerStock | bit | No |
| Barcode | nvarchar | Yes |
| TaxRate | decimal | No |
| UnitPrice | decimal | No |
| RecommendedRetailPrice | decimal | Yes |
| TypicalWeightPerUnit | decimal | No |
| MarketingComments | nvarchar(max) | Yes |
| InternalComments | nvarchar(max) | Yes |
| Photo | varbinary(max) | Yes |
| CustomFields | nvarchar(max) | Yes |
| LastEditedBy | int | No |
| ValidFrom | datetime2 | No |
| ValidTo | datetime2 | No |

</details>

<details>
<summary>Warehouse.StockItemHoldings — 9 stored columns</summary>

| Column | Original SQL Server type | Nullable |
|---|---|---|
| StockItemID | int | No |
| QuantityOnHand | int | No |
| BinLocation | nvarchar | No |
| LastStocktakeQuantity | int | No |
| LastCostPrice | decimal | No |
| ReorderLevel | int | No |
| TargetStockLevel | int | No |
| LastEditedBy | int | No |
| LastEditedWhen | datetime2 | No |

</details>

<details>
<summary>Warehouse.StockItemTransactions — 11 stored columns</summary>

| Column | Original SQL Server type | Nullable |
|---|---|---|
| StockItemTransactionID | int | No |
| StockItemID | int | No |
| TransactionTypeID | int | No |
| CustomerID | int | Yes |
| InvoiceID | int | Yes |
| SupplierID | int | Yes |
| PurchaseOrderID | int | Yes |
| TransactionOccurredWhen | datetime2 | No |
| Quantity | decimal | No |
| LastEditedBy | int | No |
| LastEditedWhen | datetime2 | No |

</details>

<details>
<summary>Application.TransactionTypes — 5 stored columns</summary>

| Column | Original SQL Server type | Nullable |
|---|---|---|
| TransactionTypeID | int | No |
| TransactionTypeName | nvarchar | No |
| LastEditedBy | int | No |
| ValidFrom | datetime2 | No |
| ValidTo | datetime2 | No |

</details>
