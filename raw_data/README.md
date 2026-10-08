# Raw data — Procter & Gamble

**Purpose:** show where the historical numbers and market inputs came from.

- [Official FY2026 annual report](PG_2026_Annual_Report.pdf): income statement, balance sheet, cash flows and segment notes.
- [Original SEC filing HTML](PG_2026_10K.html): searchable source with tagged facts.
- [PG SEC Company Facts](PG_companyfacts.json.gz): unmodified SEC JSON, compressed for download. It contains several reporting periods and filing versions; the model keeps only filings available by 31 August 2026.
- Peer company facts: [CL](CL_companyfacts.json.gz) · [KMB](KMB_companyfacts.json.gz).
- [Official Treasury table](treasury_aug2026.html): 31 August 2026 10-year par yield **4.75%**.
- Historical US-listed closing prices: [PG](https://finance.yahoo.com/quote/PG/history/) · [CL](https://finance.yahoo.com/quote/CL/history/) · [KMB](https://finance.yahoo.com/quote/KMB/history/). Prices are manually captured secondary market data; they are not SEC financial facts.

## Field guide

| Field | Format | Why it matters |
|---|---|---|
| `start`, `end` | ISO date | Financial period covered |
| `filed` | ISO date | Whether the information was available by the cutoff |
| `val` | Number in the tagged unit | Original reported amount |
| `units` | USD / shares / USD per share | Prevents mixing millions, shares and per-share data |
| `accn` | SEC filing identifier | Traces the amount to its filing |
| `form` | 10-K or 10-Q | Annual versus interim disclosure |
| XBRL tag | Text | Financial-statement concept |

Source values remain unchanged. The analysis converts dollar amounts and share counts to millions. [Every selected fact and its filing date](../processed_data/sec_provenance.json) remains available.

### Original report excerpt

Red outlines identify the figures used in the analysis. They are annotations; source text is unchanged.

![Original financial statement](../evidence/Original_report.png)

[Back to the analysis](../README.md)
