# QA Agent

**Purpose:** Find inconsistencies before a financial claim is published.

[Skills](skills.md#qa) · [Executable role instructions](https://github.com/hoichengit/Portfolio-Guide/blob/codex/financial-scenarios/agents/qa.md) · [Actual structured output](https://github.com/hoichengit/Portfolio-Guide/blob/codex/financial-scenarios/outputs/runs/PG_mid_market/qa/output.json) · [All roles](README.md)

## Questions this role handles

| Area | Example |
|---|---|
| Source agreement, dates, units, reconciliation and output validation. | [Cash and earnings links](#worked-example) |

<a id="worked-example"></a>
## Cash and earnings links: What did the role establish?

**Answer:** Annual earnings and cash links agree; source rounding remains visible.

[Read the full financial question](../analysis/04_reconciliation.md)
<details>
<summary>🔎 Compare source and Excel</summary>

**Original report**

<img src="../evidence/q4_earnings_source.png" width="850" alt="Original source evidence">

**Excel output**

<img src="../evidence/q4_excel.png" width="850" alt="Actual Excel evidence">

Red marks identify the relevant amounts. Use the full question for the period, units and reconciliation details.

</details>

## Handoff

Return explicit findings. Rejected runs and subsequent reviews remain in the record before assumptions are frozen.

[← Agent workflow](README.md) · [Project home](../README.md)
