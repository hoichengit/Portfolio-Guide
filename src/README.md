# Reproduce the valuation

**Purpose:** rebuild the published financial calculation using the frozen public inputs.

1. Download this project branch.
2. Decompress `PG_companyfacts.json.gz` into the same `raw_data` directory.
3. From the project root, run:

```bash
python3 src/finance.py PG
```

Python uses only its standard library. The output is `processed_data/valuations.json`, with selected facts in `processed_data/sec_provenance.json`.

The existing Excel workbook recalculates in Microsoft Excel. Its blue inputs are editable; the scenario selector controls one shared forecast model. The Power BI file embeds the published results; pressing Refresh does not import arbitrary Excel edits. To publish revised assumptions, regenerate the model data and update the report's tables.

## Calculation chain

```text
Revenue = prior revenue × (1 + growth)
Operating profit = revenue × operating margin
Operating working capital = receivables + inventory − payables
Unlevered cash flow = EBIT × (1 − tax) + D&A − capex − change in working capital
Enterprise value = discounted forecast cash flows + discounted terminal value
Equity value = enterprise value + cash + investments − debt − noncontrolling interest
Per-share value = equity value / diluted-share proxy
```

The source-code assumptions are deliberately visible in `CONFIG`. Forecast inputs are judgement calls. No later filing or realised return is used to select the scenarios.
