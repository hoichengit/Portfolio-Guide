# Analysis outputs — NIKE

- [Excel analysis](NKE_Three_Statement_Analysis.xlsx): Summary, nine question-specific worksheets and Reported inputs.
- [Calculated results](analysis_results.csv): reusable numeric output. Monetary figures are USD millions. Ratio levels are decimals; changes in percentage ratios are percentage points.
- [Validation results](validation.json): source comparisons, accounting reconciliations and workbook checks.

## How to read the workbook

1. Start with **Summary** for the financial conclusion.
2. Open **NKE_1_Analysis** to **NKE_9_Analysis** for the corresponding GitHub question.
3. Follow a formula to **Reported inputs** to find the source number and PDF page.

The workbook is our analysis, created from public filings. It is not a company-supplied Excel model. Key evidence is highlighted red. Other linked inputs are green, original numeric inputs are blue and calculations are black. Red emphasis identifies important evidence; it does not always mean a negative result.

## Definitions

| Measure | Calculation / scope |
|---|---|
| Gross margin | (Revenue − cost of sales) / revenue |
| Operating profit | Revenue − cost of sales − SG&A; excludes other income; NIKE-defined EBIT includes it |
| Current ratio | Current assets / current liabilities |
| Operating working capital | Receivables + inventory − payables |
| Receivable days | Average opening/closing receivables / total revenue × 365; credit-sales proxy |
| Inventory days | Average opening/closing inventory / COGS × 365 |
| Payable days | Average opening/closing payables / COGS × 365; purchases proxy |
| Cash conversion cycle | Receivable days + inventory days − payable days |
| Net debt | Current debt + long-term debt − cash − separately reported short-term investments; excludes leases |
| Free cash flow | Reported CFO − cash capex; no company-specific adjustments |
| CFO conversion | CFO / consolidated net income |

Rounding differences are retained and shown. Stock balances do not mechanically equal cash-flow changes because of currency, timing and noncash effects. NIKE's tariff-adjusted AR ratio removes the closing refund receivable from the two-point average; it is not a daily weighted trade DSO. A change in a ratio is not a percentage growth rate.

[Back to analysis](../README.md)
