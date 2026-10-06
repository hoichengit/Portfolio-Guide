# Inputs and outputs for the variance investigation

- **Original reports and market releases:** [source register](research.json). Each source records its period, publication timing and limits.
- **Unchanged forecast inputs:** [24 April frozen predictions](../april24_forecast/frozen_forecast.csv), [raw market vintages](../april24_forecast/raw/), [actual quarterly tables](../april24_forecast/actual_tables.json).
- **Prepared analysis:** [financial changes](financials.csv), [cost drivers](cost_drivers.csv), [market comparison](market_comparison.csv), [Beauty history](beauty_price_history.csv).
- **Simulation inputs:** [configuration](simulation_config.json), [historical errors](historical_errors.csv), [six common quarterly errors](common_errors.csv).
- **Simulation output:** [probabilities](probabilities.csv), [counts from 100,000 draws](counts.csv), [assumption sensitivities](sensitivity.csv), [1,000-draw preview sample](simulation_sample.csv).

Errors and company growth contributions are stored in percentage points. Probability values are proportions, so 0.57943 means 57.943%. Financial amounts are USD millions. Annual advertising figures are not quarterly spend.

## Rerun

From this project directory, use Python with NumPy and Matplotlib:

```sh
python src/analyze_variance_causes.py
```

Then use Node.js with `@oai/artifact-tool` available:

```sh
node src/build_variance_causes.mjs
```

Change the simulation settings in `simulation_config.json` before rerunning. The original April forecast is read, never overwritten. Numerical outputs refresh; the explanatory GitHub prose is a reviewed report of the delivered settings and should be reviewed if settings change.

The simulation uses fixed random draws for reproducibility. It does not estimate causal probabilities or produce a reconciled total-company sales distribution. Six historical quarters remain six observations even after 100,000 simulated draws.
