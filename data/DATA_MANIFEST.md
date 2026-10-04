# Data manifest

**Keep original sources, transformed inputs and assumptions separate.**

| Dataset | Coverage | Original or prepared? | Location |
|---|---|---|---|
| P&G annual report | FY2026 report; comparative FY2024–FY2026 statements | Company original | [Source register](../raw_data/source_manifest.json) |
| Company financial Excel | Income, balance sheet and cash flow | Company original | [Download](../raw_data/PG_2026_Company_Financials.xlsx) |
| Financial history | 45 income-statement values | Prepared extraction | [CSV](../processed_data/financial_history.csv) |
| Balance and cash inputs | 154 values | Prepared extraction | [CSV](../processed_data/three_statement_inputs.csv) |
| Business drivers | Sales contributions, segment sales and margin effects | Reviewed transcription | [JSON](../processed_data/extended_history.json) |
| Quarterly historical data | Publication-dated observations | Prepared extraction | [Quarterly history](https://github.com/hoichengit/Portfolio-Guide/blob/codex/financial-scenarios/data/history/history_tidy.csv) |
| Market evidence | Dated macro, company and peer evidence | Research register | [Market register](https://github.com/hoichengit/Portfolio-Guide/blob/codex/financial-scenarios/data/research/market_evidence.json) |
| Frozen quarterly scenarios | Four information sets; three cases each | Agent assumptions and model outputs | [Run records](https://github.com/hoichengit/Portfolio-Guide/blob/codex/financial-scenarios/outputs/runs/PG_mid_market/freeze.json) |
| Actual quarterly results | April–June 2026 | Evaluation inputs | [Analysis data](https://github.com/hoichengit/Portfolio-Guide/blob/codex/financial-scenarios/outputs/analysis.json) |

**Units:** Statement money is USD millions; EPS is USD/share. Ratios use decimals in calculation files. Fiscal years end 30 June.

**Transformations:** Reorder years chronologically; convert reported dashes to zero; retain signs, source row identifiers and rounding residuals. Source file hashes are in the original register.

[Source data](raw/README.md) · [Prepared data](processed/README.md) · [← Project home](../README.md)
