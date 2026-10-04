# Analytical choices and decision log

**The record below explains choices visible in the delivered model and review files. It does not attribute unrecorded approvals to the portfolio author.**

| Issue | Choice in the delivered work | Why | Evidence |
|---|---|---|---|
| Reported vs calculated profit | Label gross profit as derived. | It is sales less product costs, not a separate row on the source page. | [Historical review](../agents/review.md) |
| Source rounding | Retain ±$1m residuals. | Forcing a zero would alter the source. | [Statement checks](../analysis/04_reconciliation.md) |
| Forecast comparison | Match the research run to its history-only cutoff. | Separate new financial information from research. | [Scenario design](../analysis/09_scenarios.md) |
| Overlapping cost evidence | Use one bounded margin adjustment. | Avoid stacking related macro signals. | [Market analysis](../analysis/08_market_research.md) |
| May base gross margin | 49.0% → 48.6%; other base drivers unchanged. | Updated cost evidence changes the margin case. | [Scenario output](https://github.com/hoichengit/Portfolio-Guide/blob/codex/financial-scenarios/outputs/runs/PG_mid_market/scenario/output.json) |
| Rejected QA | Preserve the initial rejection and supplemental review. | Make the review history visible. | [Freeze lineage](https://github.com/hoichengit/Portfolio-Guide/blob/codex/financial-scenarios/outputs/runs/PG_mid_market/freeze.json) |
| Forecast miss | Prioritise SG&A and non-operating income. | They dominate the remaining earnings bridge. | [Actual comparison](../analysis/10_forecast_review.md) |

## Analyst review checkpoint

Before adopting a new forecast, record the proposed assumption, the challenge, the final value, supporting evidence and the reviewer. No example “I rejected +3% and chose +1%” is presented as a real decision unless that event is documented.

[Final analytical conclusion](final_recommendation.md) · [← Project home](../README.md)
