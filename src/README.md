# Reproduce and verify the project

**Two workflows support this report: annual financial extraction and quarterly scenario modelling.**

## 1. Verify the annual workbook

Requires Python 3.11+ and `openpyxl`:

```sh
python3 -m pip install openpyxl
python3 src/verify_portfolio.py
```

This compares all 199 reported inputs with the company source and the saved workbook, checks headline results and scans report links. It writes `qa/portfolio_validation.json`. It does not alter the workbook or claim to recalculate Excel formulas.

## 2. Rebuild annual data and Excel

Download the report and company spreadsheet from [the source register](../raw_data/source_manifest.json), preserving their filenames in `raw_data/`.

```sh
python3 -m pip install openpyxl pdfplumber pypdf
python3 src/extract.py
python3 src/extend_data.py
node src/build.mjs
```

`extend_data.py` also uses Poppler's `pdftoppm` to render source pages. The workbook builder requires the Codex artifact runtime providing `@oai/artifact-tool`; it is not a standalone public npm dependency. The delivered Excel file opens independently of that authoring runtime.

The builder imports `extend_workbook.mjs` to build the full eight-sheet workbook. Driver transcriptions are tied to the cited FY2026 report and must be reviewed when changing years. After rebuilding, open Excel and refresh the corresponding screenshots.

## 3. Replay the quarterly workflow

Use a separate checkout of the existing scenario branch:

```sh
git clone --branch codex/financial-scenarios --single-branch https://github.com/hoichengit/Portfolio-Guide.git pg-scenarios
cd pg-scenarios
python3 src/workflow.py replay --run outputs/runs/PG_pre_history
python3 src/workflow.py replay --run outputs/runs/PG_pre_market
python3 src/workflow.py replay --run outputs/runs/PG_mid_history
python3 src/workflow.py replay --run outputs/runs/PG_mid_market
python3 -m unittest discover -s tests -p '*test.py'
```

Replay verifies frozen inputs and outputs without calling a model. For a fresh agent run, follow the [scenario repository instructions](https://github.com/hoichengit/Portfolio-Guide/blob/codex/financial-scenarios/README.md) with your own authenticated Codex CLI. Fresh runs may produce different assumptions; write to a new run directory.

[Actual execution records](https://github.com/hoichengit/Portfolio-Guide/blob/codex/financial-scenarios/docs/agents-execution.md) · [Role instructions](../agents/README.md) · [Current verification](../qa/README.md)
