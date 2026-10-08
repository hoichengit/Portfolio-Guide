# Re-run the SQL analysis

**Purpose:** let another analyst reproduce the results without a SQL Server installation.

Download this project branch and keep its folders together. Python 3 includes SQLite; no paid software is needed.

```bash
# Import the original CSV values into a local SQLite database.
python3 src/import_csv.py

# Run every published SQL query and write result CSV files.
python3 src/replay_sql.py
```

Queries use SQLite syntax. `substr`, `date` and `julianday` are the main date functions. For SQL Server, replace these with equivalent T-SQL date expressions; do not paste the queries unchanged and claim they ran in SQL Server.

## Functions used

| SQL feature | What it does here |
|---|---|
| `WITH` / CTE | Keeps each calculation step readable |
| `JOIN` / `LEFT JOIN` | Connects invoices, customers, products and balances |
| `SUM`, `GROUP BY` | Builds financial totals at the intended level |
| `CASE` | Separates transaction types and aging buckets |
| `COALESCE` | Replaces a missing joined numeric amount with zero where appropriate |
| `NULLIF` | Prevents division by zero without inventing a ratio |
| `LAG(...,12)` | Compares a month with the same month a year earlier |
| `ROW_NUMBER` | Ranks customer profitability |
| `SUM(...) OVER()` | Calculates share of total without collapsing rows |
| `date`, `julianday` | Calculates due dates and days overdue |
| `MIN` | Caps the illustrative AR release at the current balance |

Every use is visible in the SQL code on the question page. The original BACPAC decoder is included for inspection; the CSV importer is the simpler reproducibility route.

The Power BI report embeds saved query outputs. Re-running SQL does not silently modify the existing PBIX; update its model tables to publish new results.
