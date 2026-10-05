# Release-aware backtest data

**Purpose: preserve what the model could know at each date, separately from the actuals used to score it.**

- **Original market data:** [raw CSV versions](raw/) and [version register](vintage_manifest.json). Dates and URLs come from the public ALFRED download pages; the preserved HTML includes their vintage-date lists.
- **Original company data:** [P&G source register](../history_rebuild/selected_source_manifest.json) and [quarterly facts](../history_rebuild/pg_quarterly.csv).
- **Prepared model inputs and outputs:** [forecast log](predictions.csv), [training pairs](training_pairs.csv), [observed/estimated target months](target_months.csv), [scored forecasts](scored_predictions.csv) and [model scores](scores.csv).
- **Checks:** [availability and scope](validation.json).

## How to read the files

| Field | Meaning |
|---|---|
| `prediction_id` | A stable row identifier within this generated run. Joins the forecast, training inputs and target-month estimates. |
| `target_quarter` | P&G calendar quarter being predicted; not its fiscal-quarter label. |
| `cutoff` | End-of-day information cutoff for that forecast. |
| `market_vintage` | Latest preserved market version at or before the cutoff. |
| `company_published` / `latest_company_publication` | Publication date used to restrict training facts. |
| `months_observed` | Number of target-quarter market observations already available: 0–3. |
| `observed` | Distinguishes a real published market value from an explicit estimate. |
| `bridge` | Same-quarter market model, with unknown target months estimated. |
| `lagged` | Previous-quarter market model. Blank when the required input or eight training pairs are unavailable. |
| `baseline` | Mean of the last four published company observations. |
| `last_actual` | Latest published company observation. |
| `blend` | Fixed 50/50 average of bridge and baseline. |
| `error` | Prediction minus actual, in percentage points. |

Growth values are stored in percent units: `3` means 3%, or 3pp for a disclosed pricing contribution. Monetary market levels retain source units: PCENDC96 is chained-dollar billions at a seasonally adjusted annual rate; RSHPCS is monthly USD millions, seasonally adjusted; CUUR0000SEGB is an unadjusted price index.

Training starts with January–March 2022 company results. Scores cover April–June 2024 through January–March 2026, eight quarters. Forecasts through 15 May 2026 for April–June are experimental outputs with no target-quarter actual joined.

## Reproduce

1. Run `src/collect_release_vintages.py` to download/copy-cache the public historical versions.
2. Run `src/replay_releases.py` to reproduce forecasts and separately score them. The Python analysis uses the standard library; the downloader uses curl.
3. Open the delivered Excel to inspect and recalculate coefficients, forecasts and errors. The optional authoring script `src/build_release_backtest.mjs` requires the artifact-tool runtime used to create it; it is not a standard Excel dependency.

The Python process owns source retrieval and publication-date alignment. Adding releases or changing the model definition requires rerunning that process; Excel cell edits do not download new history. Target-month carry-forward rates and market training pairs are prepared inputs; Excel formulas recalculate the downstream model from them.

ALFRED dates reflect archived availability and may differ from exact publication minutes. No intraday execution claim is made. The same historical periods informed model development, and repeated forecasts of one quarter are not independent outcomes.
