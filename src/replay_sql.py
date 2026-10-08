"""Run packaged SQL queries against a portable SQLite extract. Python standard library only."""
import sqlite3,csv,json,sys
from pathlib import Path
root=Path(__file__).resolve().parents[1]
db_path=Path(sys.argv[1]) if len(sys.argv)>1 else root/'processed_data/wwi.sqlite'
queries=root/'sql' if (root/'sql').exists() else root/'outputs/WWI/sql'
out=root/'replayed_results';out.mkdir(exist_ok=True)
c=sqlite3.connect(db_path);c.row_factory=sqlite3.Row
for path in sorted(queries.glob('*.sql')):
 rows=[dict(r) for r in c.execute(path.read_text())]
 with (out/(path.stem+'.csv')).open('w') as f:
  if rows:w=csv.DictWriter(f,fieldnames=rows[0]);w.writeheader();w.writerows(rows)
 if path.stem=='01_quality':assert all(r['failures']==0 for r in rows)
 print(path.name,len(rows),'rows')
