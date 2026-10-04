# Power BI report

**Explore the quarterly forecast, research adjustments and actual results across six pages.**

### [⬇️ Download P&G Financial Scenarios.pbix](https://github.com/hoichengit/Portfolio-Guide/blob/codex/financial-scenarios/outputs/PG_Financial_Scenarios.pbix)

Open in Power BI Desktop. The file contains native visuals and slicers. A public Power BI Service link is not available for this case.

| Page | Question |
|---|---|
| 01 Financial perspective | What did the forecast say and where did actuals land? |
| 02 The operating engine | How do sales and costs generate earnings? |
| 03 Three possible paths | How wide are the bear, base and bull cases? |
| 04 What research changed | Which assumptions changed at each cutoff? |
| 05 Forecast vs actual | Which drivers explain the earnings miss? |
| 06 Evidence & discipline | Which sources and checks support the results? |

![P&G report in Power BI Desktop](https://github.com/hoichengit/Portfolio-Guide/blob/codex/financial-scenarios/outputs/powerbi/PG/screenshots/01.png)

## A useful review path

1. Select **May + research**, then **Base**.
2. Compare forecast earnings **$3,624.5m** with actual **$3,044.0m**.
3. Open **Forecast vs actual** and inspect SG&A and non-operating income.
4. Switch to **May history** to isolate the research effect.

<details>
<summary>🔎 Inspect the recorded Power BI checks</summary>

[Native DAX and page validation](https://github.com/hoichengit/Portfolio-Guide/blob/codex/financial-scenarios/outputs/powerbi/PG/final_validation.json)

The saved validation record reports passing metric comparisons and no errors on six pages. It relates to the delivered PBIX. The GitHub page is a report guide, not a substitute for opening the interactive file.

[Editable Power BI project](https://github.com/hoichengit/Portfolio-Guide/tree/codex/financial-scenarios/outputs/powerbi/PG)

</details>

**Refresh:** The delivered report uses a prepared scenario snapshot. A normal Power BI refresh does not invoke agents. Rerun the workflow and rebuild the report to include a new forecast.

[Excel model](../model/README.md) · [Forecast review](../analysis/10_forecast_review.md) · [← Project home](../README.md)
