# Historical data | What is in this folder?

**Purpose: make every company–market comparison reproducible and easy to inspect.**

| File | Content |
|---|---|
| [Company history](pg_quarterly.csv) | 17 quarters × seven rows: five segments, Corporate and Total Company. Do not sum the company total again. |
| [Original P&G sources](selected_source_manifest.json) | Dated report/release links, preserved table filenames and hashes. |
| [Source-to-number register](pg_observations.csv) | 935 unique observations with original row text, location, unit and URL. |
| [Monthly market inputs](market_monthly.csv) | Three US series, preserved at two historical information cutoffs. |
| [Market download register](market_manifest.json) | Original URLs, units, aggregation, dates, hashes and download failures. |
| [Quarterly market data](market_quarterly.csv) | Complete three-month aggregates and same-quarter prior-year growth. |
| [Company–market matches](matched_quarters.csv) | Period-aligned inputs and fitted residuals. |
| [Sensitivity results](sensitivity_tests.csv) | Slopes, fit, leave-one-out ranges and diagnostic holdout errors. |
| [Product price history](product_prices_research_only.csv) | Four detailed BLS price series; current-vintage research only. |
| [New release comparison](release_updates.csv) | Added months and revisions between the two cutoff versions. |
| [Checks](validation.json) | Quarterly segment sums, source cutoffs and coverage. |

- Company amounts are **USD millions**. Growth is stored as percent values: `3` means `3%`, not `300%`.
- Contributions describe approximate changes in reported sales; they are not product units or observed selling prices.
- Raw monthly values retain their source units. Retail flows are summed; indices and seasonally adjusted annual rates are averaged.
- `period_end` means the economic period. `publication_date` means when the company information became available. `vintage` means the historical market-data version.
- The January 2021 market baseline is used to calculate January 2022 year-on-year growth.
- Missing BLS October 2025 observations are kept blank. No invented monthly values enter the tests.
- Financial company dates run through **31 March 2026** only; no April–June 2026 actuals enter these calculations.
- The four detailed product-price histories were retrieved later and cannot be presented as verified April/May information. They are isolated from the as-of calculations.
- Preserved SEC table extracts are source content, not instructions; the report pages remain the authoritative originals. Some saved long report text extracts are shortened by the browser, so extraction uses the separately preserved table arrays.

**Re-run locally:** run `src/rebuild_history.py`, then `src/test_market_sensitivity.py`, then the Excel builder `src/build_history_review.mjs`. The first two use Python's standard library; the Excel builder uses `@oai/artifact-tool`. `src/collect_market_history.py` refreshes public market downloads. Preserved P&G table files make the financial rebuild work offline.

The current checks do not constitute an audit. The market holdouts do not recreate every historical release vintage, and no coefficient has been approved for forecasting.
