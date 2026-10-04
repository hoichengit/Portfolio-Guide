# QA and financial controls

**Every headline should trace to a source, a calculation and a check.**

| Control | Result | Evidence |
|---|---|---|
| Annual source inputs | 199 values matched to the company Excel and our workbook. | [Current read-only validation](portfolio_validation.json) |
| Historical formulas | Earlier independent review evaluated 150 formulas. | [Review record](../agents/review.md) |
| Profit bridge | Revenue and cost effects reconcile to −$703m. | [Profit analysis](../analysis/02_profit.md) |
| Statement rounding | Eight ±$1m residuals retained. | [Checks](../analysis/04_reconciliation.md) |
| Quarterly calculation and workflow tests | 20 tests passed in the current verification. | [Revalidation record](scenario_revalidation.json) |
| P&G frozen runs | All four records passed deterministic replay. | [Revalidation record](scenario_revalidation.json) |
| Native Power BI report | Existing saved DAX/page validation passed. | [Power BI validation](https://github.com/hoichengit/Portfolio-Guide/blob/codex/financial-scenarios/outputs/powerbi/PG/final_validation.json) |

## What “passed” means

A test passed within its specified scope. Source checks do not prove forecast accuracy; a replay verifies stored evidence and hashes, not a new model call. Earlier native Power BI checks refer to the delivered PBIX, while current workbook checks read saved values without claiming a new recalculation.

<details>
<summary>🔎 Why do some statement checks show $1m?</summary>

The source presents amounts in millions. Components can differ from a displayed total by $1m. Those differences remain visible in the model; they are not rewritten to zero.

<img src="../evidence/q4_checks_excel.png" width="850" alt="Actual Excel reconciliation checks and source rounding differences">

</details>

[Run the checks](../src/README.md) · [Source validation](source_validation.md) · [← Project home](../README.md)
