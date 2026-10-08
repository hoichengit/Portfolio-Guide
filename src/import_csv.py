"""Rebuild the analysis database from the bundled raw table ZIP, without SQL Server."""
from pathlib import Path
import sqlite3,zipfile,csv,io,json
R=Path(__file__).resolve().parents[1];z=zipfile.ZipFile(R/'raw_data/WWI_raw_tables.zip');schema=json.loads(z.read('schema.json'));(R/'processed_data').mkdir(exist_ok=True);db=sqlite3.connect(R/'processed_data/wwi.sqlite')
for table,cols in schema.items():
 name=table.replace('.','_');types=['INTEGER' if c['type'] in ['int','bigint','smallint','tinyint','bit'] else 'NUMERIC' if c['type'] in ['decimal','numeric','float'] else 'TEXT' for c in cols]
 db.execute(f'DROP TABLE IF EXISTS "{name}"');db.execute(f'CREATE TABLE "{name}" ('+', '.join('"'+c['name']+'" '+t for c,t in zip(cols,types))+')')
 reader=csv.reader(io.StringIO(z.read(name+'.csv').decode()));assert next(reader)==[c['name'] for c in cols]
 db.executemany(f'INSERT INTO "{name}" VALUES ('+','.join('?' for c in cols)+')',([None if v=='' and c['nullable'] else v for v,c in zip(row,cols)] for row in reader));db.commit();print(name,db.execute(f'SELECT COUNT(*) FROM "{name}"').fetchone()[0])
