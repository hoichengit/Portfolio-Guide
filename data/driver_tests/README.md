# Driver and policy tests | Data and rerun guide

**Purpose:** preserve the information available at each forecast date and test a fixed set of candidate improvements.

| Files | Contents |
|---|---|
| `sources/` | Original SEC page tables for four added 2021 quarters, collected from the rendered reports. |
| `added_source_rows.csv` | Exact source table, row, excerpt, URL and file hash for those quarters. |
| `pg_quarterly.csv` / `.json` | 21 quarters and seven company/segment rows per quarter; five reporting segments are modelled. |
| `raw/` | 144 original ALFRED CSV downloads, four series × 36 dates. |
| `market_manifest.json` | Requested dates, hashes and outcomes, including 108 unsuccessful downloads for three excluded series. |
| `checkpoints.csv` / `.json` | Quarter start, prior-quarter report publication and day before target earnings, for 12 target quarters. |
| `training.csv` | Historical company-market pairs used by each fit. Join `fit_id` to `fits.csv` for its information cutoff. |
| `fits.csv` / `.json` | Training totals, coefficients and target features for 1,576 fits. |
| `forecasts.csv` / `.json` | 2,992 forecasts, calibration-row IDs and actuals attached for scoring. |
| `scores.csv` / `.json` | RMSE, MAE, bias and matching-sample benchmarks. |
| `validation.json` | Publication-date and target-outcome checks. |

## Reproduce

From the project root, with Python and NumPy installed:

```bash
python src/test_driver_models.py
```

This uses the preserved downloads and needs no market API key. To recollect the dated inputs, run `python src/extend_driver_inputs.py`; original SEC tables are preserved in `sources/`. The earlier 2022–2026 company history is in `data/history_rebuild/`.

To rebuild Excel, run `node src/build_driver_tests.mjs` in the provided artifact-tool environment. Python outputs are portable; the workbook builder additionally requires `@oai/artifact-tool`. Excel opens independently of that tool.

## Definitions and limits

- Company quarters are calendar quarters, regardless of P&G's fiscal-year labels.
- Price contribution and forecast errors are in percentage points. Volume and organic-sales growth are year-on-year percent changes, represented as 2 for 2%.
- Monthly market levels are aggregated to quarters before calculating year-on-year growth. Unknown months follow the previous-year monthly pattern adjusted by the latest three available monthly growth rates.
- Single-variable fits need eight observations; the two-variable Beauty candidate needs twelve. Own-history models use the lag available at the checkpoint.
- Full and half bias corrections use the last four completed, published, same-stage broad-model errors. They are not fitted using the future test outcome.
- Product CPI is US-only, partially matched and not a measure of P&G's realised price. Company reported drivers are rounded approximations.
- This extension compares three checkpoints per quarter. The earlier PG_5 release-by-release replay remains available; this run does not claim to replay every release for all new candidates.
- These are retrospectively inspected periods, not an untouched holdout. No April–June 2026 P&G actual is used.
- The policy calculator is an explicitly hypothetical cost sensitivity. Its published P&G inputs are cited in the workbook and analysis page; it is not a fitted policy coefficient.
