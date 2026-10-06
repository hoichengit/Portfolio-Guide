# P&G | From Company Guidance to an Independent Forecast

**Can P&G deliver its outlook, and what would change our view?**

- 📅 **Start:** the January–March results released on 24 April 2026.
- 🎯 **Forecast:** April–June 2026 as one quarter; add nine-month actuals to show the full year. No monthly split.
- 🔎 **Method:** separate company guidance, our assumptions and actual results.

![From guidance to forecast review](architecture/april_workflow.svg)

## 1. Understand the company's outlook

**P&G guided to 1%–5% full-year sales growth. The midpoint is a reference, not our forecast.**

- [**1. Company guidance:** What did P&G expect?](analysis/01_management_guidance.md)
- [**2. Quarterly sales target:** What sales are needed in April–June?](analysis/02_quarter_sales_target.md)

💡 **The 3% annual midpoint requires only 0.45% growth in April–June.** Open question 2 to see why.

## 2. Test market evidence before adjusting the scenarios

**Five years of history help us test market signals, forecast corrections and policy timing before changing the forecast.**

- **Company history:** 21 quarters, January 2021–March 2026, across five reporting segments.
- **Product research:** 11 categories mapped to available market data; missing product-level amounts stay missing.
- **Historical tests:** 18 exploratory company–market comparisons.
- **Release-aware backtest:** 122 archived market versions; five forecasting methods tested over eight quarters. Grooming pricing improved, while several demand models failed to beat simple rules.
- **Competitors:** optional checks for industry performance and market share; no peer coefficient enters this model.
- **Latest extension:** 12 test quarters, product-price and company-history challengers, chronological bias correction and a separate tariff-timing calculator. Correction helped Beauty but worsened Grooming.

👉 **[New: first test the market relationship, then predict missing months](analysis/07_two_stage_forecast.md)** · [Download the two-stage Excel analysis](outputs/two_stage/PG_7_Two_Stage_Forecast.xlsx)

Six early candidates were tested on seven later target quarters. Some helped; better monthly market estimates did not always improve P&G forecasts.

👉 **[Which model changes helped, and why policy timing matters](analysis/06_driver_policy_tests.md)** · [Download the new Excel analysis](outputs/driver_tests/PG_6_Driver_and_Policy_Tests.xlsx)

👉 [See the release-aware backtest and data-gap remedies](analysis/05_release_backtest.md) · [Read the questions and answers](analysis/03_scenario_adjustment.md) · [Expand original-report and Excel evidence](analysis/04_historical_matching.md) · [Download the historical analysis](outputs/history_review/PG_4_Historical_Market_Analysis.xlsx)

This historical reconstruction separates what was known on 24 April from what was known on 15 May. The previous unsupported blanket reductions have been withdrawn from the active argument. A new calibrated downside/base/upside forecast remains unfinished.

## 3. Compare the 24 April forecast with actual results

**Sales were $219.48m above the guidance midpoint reference. Across six independent metric tests, the four-quarter average beat our selected forecasting methods.**

👉 [**Did the forecast work? See predictions, actuals and error explanations**](analysis/08_april24_forecast_vs_actual.md) · [**Download the Excel comparison**](outputs/april24_forecast/PG_8_April24_Forecast_vs_Actual.xlsx)

👉 [**Why did the forecast miss? Business evidence and Monte Carlo outcomes**](analysis/09_variance_causes_and_risk.md) · [**Download the causes and simulation analysis**](outputs/variance_causes/PG_9_Variance_Causes_and_Monte_Carlo.xlsx)

👉 [**Can we improve the forecast? Revised methods, historical tests and Monte Carlo**](analysis/11_forecast_improvement.md) · [**Open the revised Excel analysis**](outputs/forecast_improvement/PG_11_Forecast_Improvement.xlsx)

The dated point forecasts are now evaluated. A 100,000-draw simulation explores six separate metrics with assumption sensitivities. A reconciled company-wide downside/base/upside model remains unfinished; these metric predictions must not be added together.

👉 [**Was the model reliable before results? January–March replay and leakage audit**](analysis/12_jan_mar_replay.md) · [**Open the January–March Excel**](outputs/jan_mar_replay/PG_12_Jan_Mar_Replay.xlsx)

The January–March replay missed by 2.50pp initially and 2.85pp at the pre-release update. It does not establish reliable forecasting or calibrated risk probabilities.

## 🧰 Skills demonstrated so far

| Skill | Evidence |
|---|---|
| Financial research | Locate the actual guidance and preserve its date and definition. |
| Excel | Build linked sales calculations and reconcile annual totals to quarterly targets. |
| Market analysis | Align monthly indicators with quarterly company results; test associations and stability. |
| Analytical judgement | Separate annual from quarterly growth, and company guidance from our own scenarios. |
| Forecast evaluation | Freeze dated predictions, compare actuals with simple benchmarks, and separate market-input errors from relationship errors. |

[📊 Download the Excel sample](outputs/april_guidance_sample/PG_1_Management_Guidance.xlsx) · [🔎 Read the analysis](analysis/01_management_guidance.md)

<details>
<summary>Project version</summary>

This version uses the April-start forecast framing. Earlier models remain in repository history and supporting files. The current Monte Carlo is a retrospective uncertainty illustration with explicit assumptions, not a validated probability model.

</details>
