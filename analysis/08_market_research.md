# 8. Market evidence: What should change in the model?

**Answer:** Use company guidance, demand indicators and competitor results to challenge assumptions. Translate overlapping cost signals into one bounded adjustment.

## 🔍 Three research questions

| Question | Evidence used | Model implication |
|---|---|---|
| Is demand stronger in real terms? | BEA consumption and BLS inflation releases. | Challenge volume growth; nominal spending is not unit demand. |
| Can pricing hold? | P&G disclosures and Unilever's first-quarter update. | Test price and volume together; peer growth does not prove P&G share loss. |
| When do higher costs reach earnings? | Company commodity/tariff outlook and producer-cost evidence. | Adjust the quarterly gross-margin case without assigning a full annual cost change to one quarter. |

[Primary company evidence: P&G’s 24 April 2026 results and annual cost guidance](https://www.pginvestor.com/news/news-details/2026/PG-Announces-Fiscal-Year-2026-Third-Quarter-Results/default.aspx).

## What actually changed?

**May research lowered base gross margin from 49.0% to 48.6%.** The other base assumptions stayed unchanged. Model earnings fell by **$69.1m**.

The bear margin moved from **47.5% to 46.7%** and the bull from **50.5% to 50.3%**. These are scenario judgments, not a measured conversion of each source into basis points.

<details>
<summary>🔎 Open the dated research and model evidence</summary>

**Original sources**

- [Market evidence register: publication dates, source URLs and interpretation](https://github.com/hoichengit/Portfolio-Guide/blob/codex/financial-scenarios/data/research/market_evidence.json)
- [Historical-source register](https://github.com/hoichengit/Portfolio-Guide/blob/codex/financial-scenarios/data/history/source_manifest.json)

**Workbook evidence**

![Research changes](https://github.com/hoichengit/Portfolio-Guide/blob/codex/financial-scenarios/outputs/screenshots/PG/Research_Changes.png)

This is a render of the delivered quarterly workbook, not a native Excel application capture. Open [the workbook](https://github.com/hoichengit/Portfolio-Guide/blob/codex/financial-scenarios/outputs/PG_Financial_Scenarios.xlsx) to inspect the cells.

**Actual agent output:** [Research role](https://github.com/hoichengit/Portfolio-Guide/blob/codex/financial-scenarios/outputs/runs/PG_mid_market/research/output.json) → [Scenario assumptions](https://github.com/hoichengit/Portfolio-Guide/blob/codex/financial-scenarios/outputs/runs/PG_mid_market/scenario/output.json).

</details>

## Why this matters

Counting CPI, PPI, freight and company guidance as separate full cost shocks can double-count the same pressure. Keep one explanation of what changed, its period and the model input it affects.

**Time control:** March uses sources published by 31 March 2026. May uses sources published by 15 May 2026. Later results belong to evaluation only.

[Next: scenario design →](09_scenarios.md)


[← Project home](../README.md) · [All questions](README.md)
