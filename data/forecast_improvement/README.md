# Forecast improvement inputs and outputs

- **Original company data:** [quarterly results](../driver_tests/pg_quarterly.json), [original frozen forecasts](../april24_forecast/frozen_forecast.csv) and [actual results](../april24_forecast/variance.csv).
- **Dated inputs:** [market vintage and financial release dates](release_inputs.csv). The referenced raw files remain in the existing market archives.
- **Calculations:** [training pairs](training_pairs.csv), [candidate and selected predictions](rolling_forecasts.csv), [method selection audit](selection_log.json).
- **Results:** [historical errors](historical_scores.csv), [April–June comparison](target_comparison.csv), [simulation probabilities](probabilities.csv), [interval coverage tests](interval_tests.csv).
- **Assumptions:** [configuration](config.json), [sensitivity tests](sensitivity.csv), [summary and limitations](summary.json), [validation checks](validation.json).

Growth rates and errors use numeric percentage-point units: `1.5` means 1.5%, or a 1.5pp pricing contribution as indicated by the metric. Simulation counts divided by `draws` give probabilities. A growth range and its probability are different quantities.

## Reproduce

Run `python src/improve_forecast.py` with NumPy and Matplotlib available. It reads the preserved market archives and existing monthly estimator, creates candidate forecasts, selects methods using earlier outcomes, saves the unscored June forecasts, then joins June actuals for evaluation. It also performs a future-actual injection check.

Run `node src/build_forecast_improvement.mjs` with `@oai/artifact-tool` available to regenerate the Excel report. The workbook calculates errors and probabilities from saved simulation counts; it does not regenerate 100,000 draws when a cell changes.

The Python file defines the fixed configuration and writes `config.json` as a record. Change the configuration in that file to run a new experiment; preserve a separate record of any changed specification. Reviewed prose and native Excel screenshots do not update automatically.

This is retrospective development after the target outcome was inspected. Calendar controls prevent direct future inputs in each forecast; they cannot remove hindsight from the research design. Six measures are overlapping company indicators, not six independent businesses.
