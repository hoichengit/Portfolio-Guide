# P&G Financial Analysis & Agentic Scenario Planning

**Can P&G protect profit and cash flow when demand, costs and currencies change?**

[📊 Financial model](outputs/PG_1_Analysis.xlsx) · [📁 Source data](raw_data/README.md) · [🔎 Evidence](#evidence) · [⚙️ Workflow](#workflow)

## In 30 seconds

**Sales grew. Operating profit fell. Higher costs absorbed the growth.**

![FY2026 sales and profit summary](architecture/summary.svg)

- **What we found:** Sales rose 3.3%, but operating profit fell 3.4%.
- **Why it matters:** Revenue growth alone overstates the improvement in performance.
- **What to test next:** Whether pricing and productivity can protect margins under weaker demand.

*Historical analysis is available. Market research, scenarios, valuation and a final recommendation are the next stages of this project.*

## 🧭 Choose a question

| Start here | What you will learn |
|---|---|
| [Why did profit fall?](#profit) | Trace the $703m decline to revenue and costs. |
| [Can I trust the numbers?](#evidence) | Compare the annual report with the Excel calculation. |
| [Read all seven historical questions](investment/01_financial_statements.md) | Explore statement checks, sales drivers and margins. |
| [How do the agents help?](#workflow) | See the roles, calculations and review steps. |

<a id="profit"></a>
## 1. Revenue vs profit: Why did profit fall when sales grew?

**Answer:** Additional revenue of **$2,748m** was smaller than the **$3,451m** increase in product costs and selling, general and administrative expenses (SG&A).

![Operating profit bridge](architecture/profit_bridge.svg)

**The calculation:** $2,748m − $2,198m − $1,253m = **−$703m**.

**Analyst interpretation:** Growth did not translate into higher operating profit. The next step is to separate cost pressure from investment and temporary charges before forecasting margins.

<a id="evidence"></a>
<details>
<summary>🔎 Show the evidence — original report → Excel</summary>

**Original annual report · FY2024–FY2026 · USD millions**

<a href="evidence/q2_source.png"><img src="evidence/q2_source.png" alt="Original income statement: sales and operating income highlighted in red" width="850"></a>

**Our Excel analysis · Same reported amounts, plus the profit calculation**

<a href="evidence/q2_excel.png"><img src="evidence/q2_excel.png" alt="Actual Excel screenshot: revenue, operating costs and the profit bridge" width="850"></a>

Follow the red revenue and operating-profit figures. The years appear in a different order; match the year labels. Red highlights identify evidence, not whether a result is good or bad.

[Open the source report, page 37](https://s204.q4cdn.com/332108499/files/doc_financials/2026/ar/2026_annual_report.pdf#page=49) · [Open our Excel workbook](outputs/PG_1_Analysis.xlsx)

</details>

<details>
<summary>🧮 Show the method and checks</summary>

1. Copy sales, product costs, SG&A and operating income from the report.
2. Subtract FY2025 from FY2026 for each line.
3. Add the revenue increase and subtract the cost increases.
4. Check that the result equals $19,748m − $20,451m = −$703m.

**Periods:** Years ended 30 June. **Units:** USD millions. **Source:** Consolidated Statements of Earnings.

FY2024 included a $1,341m impairment charge; FY2025 and FY2026 did not. This bridge compares FY2026 with FY2025.

[Review the existing QA record](agents/review.md)

</details>

<a id="workflow"></a>
## ⚙️ How the work gets done

**Agents organise evidence and challenge assumptions. Excel calculates. The analyst reviews the recommendation.**

![Target workflow, with current and planned roles distinguished](architecture/workflow.svg)

<details>
<summary>See the five roles and their outputs</summary>

| Role | One job | Output | Status |
|---|---|---|---|
| Financial | Extract and check the statements. | Financial history | Existing review and data |
| Business Driver | Explain changes in sales and margins. | Business-driver table | Analysis exists; separate agent planned |
| Market Research | Connect outside evidence to model drivers. | Market evidence and implications | Planned for this project |
| Scenario | Propose base, upside and downside assumptions. | Assumption table | Planned for this project |
| QA | Compare source, model and dashboard. | Reconciliation report | Source and Excel review exists; dashboard checks later |

[Current agents](agents/README.md) · [Current financial history](processed_data/financial_history.csv)

</details>

## 🗂️ Where the project is going

**Data → Analysis → Model → Decision**

<details>
<summary>See the proposed repository structure</summary>

| Folder | What belongs here |
|---|---|
| `data/raw/` and `data/processed/` | Original sources and cleaned inputs, with a data manifest. |
| `analysis/` | Historical, business-driver, market and valuation analysis. |
| `agents/` and `architecture/` | Responsibilities, skills, example outputs and workflow diagrams. |
| `model/` and `dashboard/` | Excel calculations, scenario outputs and Power BI. |
| `decisions/` | Assumption challenges, reasons for revisions and the final recommendation. |
| `reports/` and `qa/` | Short investment memo, executive summary and validation checks. |

This is the target organisation; existing files remain accessible while the project is reorganised. Decision entries will record actual analyst decisions; example decisions will be labelled as examples.

</details>
