# Historical financial review

## Financial review

A separate Financial review agent checked P&G's official FY2026 annual report and independently returned these findings:

- FY2026 revenue growth: **3.2604%**.
- FY2026 operating-income growth: **−3.4375%**.
- Profit bridge: **+$2,748m revenue − $2,198m product costs − $1,253m SG&A = −$703m**.
- FY2024 impairment: **$1,341m**, relevant to historical comparability.
- Gross profit of **$43,670m** is derived from the annual statement's rounded line items; it is not a separately reported row on that page.

Source: 2026 Annual Report, printed p.37 / PDF p.49. These results agree with the project's calculations.

## Independent QA

A separate QA agent performed a read-only review without running the builder or changing files.

- All **45 inputs** match the original company spreadsheet, CSV and Reported Earnings sheet.
- Year order, negative interest expense, impairment zeros and EPS units agree.
- Formula references and cached results agree with independent calculations.
- Revenue change **+$2,748m**, operating-income change **−$703m**, and bridge difference **$0m**.
- The FY2024 **$1,341m** impairment caveat is included.

**Result:** No numerical issues found in this income-statement sample. Full three-statement analysis and the five-agent platform were not part of this check.

## Expanded historical analysis review

A fresh Financial review independently checked the original annual-report pages and company Excel. It identified the source rounding residuals, confirmed the company’s approximate volume/price/FX disclosures and distinguished management’s rounded margin explanation from calculated ratios.

A separate read-only QA review then checked the expanded workbook:

- **199 of 199 statement inputs** agree with the original company Excel: 45 income, 64 balance-sheet and 90 cash-flow values.
- **150 formulas** were independently evaluated against their stored results; no Excel error cells were found.
- Eight nonzero statement residuals of **±$1m** are retained. FY2024 balance-sheet checks remain unavailable because this source has no FY2024 balance sheet.
- Segment increases total **$2,748m**; displayed segment revenue totals are $1m below consolidated sales in each year.
- Beauty contributes **$1,059m / 38.5%** of the increase.
- Approximate company sales drivers total **3%**, compared with **3.2604%** calculated growth. No exact dollar attribution is claimed.
- The company gross-margin explanation totals **−100 bps**, compared with **−98.34 bps** calculated from rounded statement amounts.
- Six new worksheet previews were checked for readability and clipping.

**Result:** No numerical or material preview-layout issues were found. This review covers historical statements and disclosed business drivers, not forecasts, valuation or an audit opinion. The workbook was subsequently opened and saved in Microsoft Excel and its displayed worksheets captured as evidence.
