# January–March 2026 forecast reconstruction

Two end-of-day cutoffs: 22 January and 23 April 2026. Actuals released 24 April are scored after both forecast records are saved. Model design remains retrospective.

- `unscored_forecasts.json`: predictions and method-selection evidence without target actuals.
- `release_inputs.csv`: company dates, market vintage dates, observed months and paths to preserved raw market files.
- `training_pairs.csv`: every permitted company/market pair.
- `rolling_forecasts.json`: historical candidate forecasts, actuals and selection scores.
- `comparison.csv`: target forecasts joined to later actuals.
- `calibration_errors.csv`, `probabilities.csv`, `interval_tests.csv`: risk calibration and assessment.
- `config.json`, `validation.json`: assumptions, date correction and leakage checks.

Rerun from repository root: `python3 src/forecast_jan_mar.py`, then `node src/build_jan_mar.mjs`. Python needs numpy and matplotlib; workbook generation uses @oai/artifact-tool. Existing raw data archives and src/replay_releases.py / src/test_two_stage.py are dependencies. Calculated Excel errors update when saved input numbers change; changing cells does not rerun the statistical model.

Company source: https://www.pginvestor.com/news/news-details/2026/PG-Announces-Fiscal-Year-2026-Third-Quarter-Results/default.aspx . The prior release date is corrected to 22 January using the official second-quarter release. Historical company archive restatement vintages have not been fully audited.
