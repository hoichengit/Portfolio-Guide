# Procter & Gamble — Stock Valuation

![Project overview](evidence/banner.svg)

**🎯 Goal:** assess what the business could be worth, and identify the assumptions needed to support its share price.

- **Data:** five fiscal years of SEC financial statements, business-segment disclosures, two peers and dated market inputs.
- **Work:** build a linked financial forecast, value future cash flows, test sensitivities and reverse-engineer market expectations.
- **Result:** Base value **$125.94**, versus **$145.12** on 31 August 2026; the model implies **-13.2%**.

[📗 Excel model](processed_data/PG_Financial_Analysis.xlsx) · [📂 Raw data](raw_data/README.md) · [🔎 Analysis outputs](processed_data/README.md)

> Historical valuation exercise, reconstructed with filings available by **31 August 2026**. The scenarios are analyst assumptions, not company guidance or a claim of forecasting accuracy.

## Analysis questions

| Question | What I tested |
|---|---|
| [1. Revenue sources](#1-revenue-sources) | Where does the company earn its revenue? |
| [2. Profitability](#2-profitability) | How has operating profitability changed? |
| [3. Cash conversion](#3-cash-conversion) | Do accounting profits turn into cash? |
| [4. Five-year forecast](#4-five-year-forecast) | What do the three scenarios assume? |
| [5. DCF valuation](#5-dcf-valuation) | What is each scenario worth per share? |
| [6. Peer comparison](#6-peer-comparison) | Does the peer comparison support the valuation? |
| [7. Reverse DCF](#7-reverse-dcf) | What growth does the market price require? |

**What matters:** P&G needs more growth than the 3% Base assumption to support the observed price, if the other Base inputs stay fixed.

```mermaid
flowchart LR
 A[Official reports] --> B[Historical financials]
 B --> C[Bear / Base / Bull]
 C --> D[Cash-flow valuation]
 D --> E[Peers and sensitivity]
 E --> F[Decision and risks]
```

<a id="1-revenue-sources"></a>

## 1. Revenue sources: Where does the company earn its revenue?

**Answer:** **Fabric & Home Care** is the largest disclosed component at **$30,314m**, or **34.8%** of company revenue. Total FY2026 revenue was **$87,032m**.

**How:** Read the segment note, retain corporate reconciliation items, and divide each component by reported total revenue. P&G's rounded segment figures differ from the total by $1m.

<details>
<summary>📸 Open the evidence</summary>

**Original income statement — key figures outlined in red**

![Original income statement — key figures outlined in red](evidence/Original_report.png)

**Actual Excel worksheet — revenue highlighted in red**

![Actual Excel worksheet — revenue highlighted in red](evidence/Native_excel_income.png)

**Revenue by business / geography**

![Revenue by business / geography](evidence/Segments.png)

</details>

<a id="2-profitability"></a>

## 2. Profitability: How has operating profitability changed?

**Answer:** Operating margin moved from **24.3%** to **22.7%**; revenue changed **+3.3%**. This separates growth from the profit kept on each sales dollar.

**How:** Use reported operating income divided by revenue. Keep reported results; do not silently remove restructuring or impairment costs.

<details>
<summary>📸 Open the evidence</summary>

**Original income statement**

![Original income statement](evidence/Original_report.png)

**Actual Excel worksheet — income statement, FY2022 to FY2026**

![Actual Excel worksheet — income statement, FY2022 to FY2026](evidence/Native_excel_income.png)

**Historical financials — complete analysis**

![Historical financials — complete analysis](evidence/Historical.png)

</details>

<a id="3-cash-conversion"></a>

## 3. Cash conversion: Do accounting profits turn into cash?

**Answer:** Cash from operations was **$19,556m** against parent net income of **$16,046m**. After **$4,409m** of capex, cash flow was **$15,147m**.

**How:** Compare operating cash flow with earnings, then subtract capital spending. This CFO-minus-capex measure includes working-capital and cash-tax effects; it is not the same as unlevered DCF cash flow.

<details>
<summary>📸 Open the evidence</summary>

**Original cash-flow statement**

![Original cash-flow statement](evidence/Original_cash.png)

**Excel cash-flow figures — FY2022 to FY2026, left to right**

![Excel cash-flow figures — FY2022 to FY2026, left to right](evidence/Cash_history.png)

</details>

<a id="4-five-year-forecast"></a>

## 4. Five-year forecast: What do the three scenarios assume?

**Answer:** The Base case grows FY2031 revenue to **$100,894m**, with a **23.5%** operating margin. The workbook uses one active scenario selector, so the statements and DCF change together.

**How:** Apply growth and margin assumptions to the latest annual base. Keep receivable, inventory and payable days at their FY2026 levels; link cash flow to the balance sheet and verify that assets equal liabilities plus equity.

| Scenario | Revenue growth: FY2027 → FY2031 | Operating margin: FY2027 → FY2031 |
|---|---|---|
| Bear | 1% → 1% → 1% → 1% → 1% | 21.5% → 21.5% → 21.5% → 21.5% → 21.5% |
| Base | 3% → 3% → 3% → 3% → 3% | 22.7% → 23.0% → 23.2% → 23.4% → 23.5% |
| Bull | 5% → 5% → 5% → 5% → 5% | 23.5% → 24.0% → 24.5% → 25.0% → 25.0% |

<details>
<summary>📸 Open the evidence</summary>

**Five-year linked forecast**

![Five-year linked forecast](evidence/Forecast.png)

</details>

<a id="5-dcf-valuation"></a>

## 5. DCF valuation: What is each scenario worth per share?

**Answer:** The three model values are **$103.09 / $125.94 / $148.80** for Bear / Base / Bull. Base WACC is **7.30%**, with **2.5%** terminal growth.

**How:** Discount forecast unlevered free cash flow; add discounted terminal value, then cash and investments; subtract debt and noncontrolling interests. Divide by the diluted-share proxy. The remaining first fiscal year is prorated from the valuation date.

**Key risk:** terminal value contributes **80.6%** of enterprise value. Small changes in WACC or long-run growth can change the conclusion.

<details>
<summary>📸 Open the evidence</summary>

**Value per share calculation**

![Value per share calculation](evidence/Valuation.png)

**WACC and terminal-growth sensitivity**

![WACC and terminal-growth sensitivity](evidence/Sensitivity.png)

</details>

<a id="6-peer-comparison"></a>

## 6. Peer comparison: Does the peer comparison support the valuation?

**Answer:** The two peers trade at **35.1×** and **18.4×** GAAP earnings, versus **21.0×** for PG. This is a plausibility check; it is not a substitute for the cash-flow model.

**How:** Rebuild each peer's trailing twelve months as latest full year + current year-to-date − prior comparable year-to-date. Divide market capitalisation by GAAP parent earnings; keep each company's period and share-count date visible.

| Peer | TTM through | Share count dated | GAAP P/E |
|---|---|---|---|
| CL | 2026-06-30 | 2026-06-30 | 35.1× |
| KMB | 2026-06-30 | 2026-07-28 | 18.4× |

The small peer set differs in business mix and growth. GAAP earnings retain exceptional items; KMB also requires care around business disposals. No unjustified "normalised" adjustment is inserted.

<details>
<summary>📸 Open the evidence</summary>

**Peer calculations and period dates**

![Peer calculations and period dates](evidence/Peers.png)

</details>

<a id="7-reverse-dcf"></a>

## 7. Reverse DCF: What growth does the market price require?

**Answer:** Holding the Base margin path and other assumptions fixed, approximately **5.90% annual revenue growth** produces **$145.12 per share**. This is one conditional solution, not a forecast of what investors believe.

**How:** Use the same DCF engine and search for a constant revenue-growth rate that makes model value equal the dated market price. In Excel, switch Drivers B26 to 1 and use the prefilled growth in B27 to reproduce the result.

<details>
<summary>📸 Open the evidence</summary>

**Reverse DCF result and replay inputs**

![Reverse DCF result and replay inputs](evidence/Sensitivity.png)

</details>

## What this project demonstrates

| Skill | Evidence |
|---|---|
| Financial-statement analysis | Five annual periods; revenue, margins, cash and capital structure |
| Financial modelling | Linked forecast with scenario selector and balance checks |
| Valuation | DCF, market-price comparison, peer check and reverse DCF |
| Model risk | Timing, dilution, terminal value and assumption sensitivities |
| Communication | Short answers with expandable source and worksheet evidence |

## Model boundaries

- Revenue is forecast at company level. The segment analysis explains exposure; it is not a separate segment forecast.
- Growth, margins, beta, equity premium and debt cost are analyst assumptions, not statistically estimated coefficients.
- SG&A / revenue stays at the latest historical ratio. The chosen operating-margin path is achieved through gross-margin change; this is a simplification, especially for NIKE's recovery case.
- Working capital uses receivables + inventory − payables. Other operating balances stay fixed; no acquisitions, buybacks, FX cash effects or new borrowing are forecast.
- Latest fiscal-year-end cash and debt stand in for valuation-date balances. First-year cash flow is prorated uniformly, which ignores seasonality.
- The share denominator combines latest disclosed common shares with conversion / annual dilution proxies. It is not an exact valuation-date diluted share count.
- Stock compensation remains an operating cost in the DCF. Operating leases stay in operating expenses and are excluded from the debt bridge.

[Reproduce the model](src/README.md) · [Sources and definitions](raw_data/README.md) · [Back to portfolio](https://github.com/hoichengit/Portfolio-Guide)

**Power BI status:** the five-page report is undergoing final Desktop verification. The verified Excel model and supporting analysis are available above.
