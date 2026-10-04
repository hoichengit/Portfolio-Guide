# Processed data and calculations

**Our outputs preserve the reported amounts and add clearly identified calculations.**

| File | What it contains | Format |
|---|---|---|
| [Income history](../../processed_data/financial_history.csv) | 45 values with metric, year, unit and source row. | One metric/year per row; numeric value. |
| [Balance and cash inputs](../../processed_data/three_statement_inputs.csv) | 154 values with statement, year and source location. | Numeric amounts in USD millions. |
| [Business drivers](../../processed_data/extended_history.json) | Sales drivers, segment revenue and margin effects. | Ratios, dollar amounts and basis points remain distinct. |
| [Historical analysis workbook](../../outputs/PG_1_Analysis.xlsx) | Reported inputs, calculations and checks. | Editable Excel formulas. |

<details>
<summary>🔎 See how source revenue becomes an Excel input</summary>

**Original source**

<img src="../../evidence/q1_source.png" width="850" alt="Original revenue by year">

**Our Excel worksheet**

<img src="../../evidence/q1_excel.png" width="850" alt="Matching revenue values in Excel">

The year order changes; the reported amounts do not. New fields in the CSV identify the unit, classification and source row so the extraction can be checked.

</details>

[Workbook guide](../../model/README.md) · [Data manifest](../DATA_MANIFEST.md) · [← Project home](../../README.md)
