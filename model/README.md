# Excel models

**Use the historical workbook to explain results; use the quarterly workbook to test assumptions.**

| Model | Open | What to inspect |
|---|---|---|
| Historical financial analysis | [PG_1_Analysis.xlsx](../outputs/PG_1_Analysis.xlsx) | Reported statements → profit bridge → checks → drivers. |
| Quarterly scenarios | [PG_Financial_Scenarios.xlsx](https://github.com/hoichengit/Portfolio-Guide/blob/codex/financial-scenarios/outputs/PG_Financial_Scenarios.xlsx) | Editable assumptions → scenario model → frozen forecast comparison. |

## Historical workbook

| Sheet | Purpose |
|---|---|
| PG_1_Analysis | Revenue, costs, margins and the $703m profit bridge. |
| PG_2_Analysis | Statement connections and disclosed rounding residuals. |
| PG_3_Analysis | Sales drivers and segment contribution. |
| PG_4_Analysis | Gross-margin and SG&A explanations. |
| Reported Earnings / Balance / Cash / Drivers | Source inputs kept apart from calculations. |

## Quarterly workbook

1. Open **Assumptions** and use the yellow case selector.
2. Edit blue inputs to test a different assumption.
3. Read **Scenario Model** for recalculated earnings and cash.
4. Use **Forecast Comparison** to inspect the original frozen forecasts. Editing the model does not rewrite that forecast record.

**Calculation:** Sales × gross margin − sales × SG&A ratio = operating income. Add net non-operating income, deduct tax and noncontrolling income to obtain attributable earnings.

Operating cash flow uses an assumed earnings-conversion ratio. Free cash flow is operating cash flow less capex. This simplified cash schedule does not model every working-capital and financing account.

[Scenario questions](../analysis/09_scenarios.md) · [Sensitivity analysis](../analysis/11_sensitivity.md) · [Checks](../qa/README.md) · [← Project home](../README.md)
