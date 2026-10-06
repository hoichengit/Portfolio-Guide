"""Extend P&G history and download frozen, common-checkpoint market inputs."""
from pathlib import Path
from datetime import date,timedelta
import csv,io,json,hashlib,concurrent.futures,subprocess
from rebuild_history import numbers,SEGMENTS
from replay_releases import months,prior_quarter
ROOT=Path(__file__).resolve().parents[1]; P=ROOT/'data/driver_tests'
SOURCES=[
 ('2021-03-31','2021-04-20','https://www.sec.gov/Archives/edgar/data/80424/000008042421000056/fy2021q3jfm8-kexhibit991.htm',2,4,None),
 ('2021-06-30','2021-07-30','https://www.sec.gov/Archives/edgar/data/80424/000008042421000083/fy2021q4amj8-kexhibit991.htm',3,5,None),
 ('2021-09-30','2021-10-19','https://www.sec.gov/Archives/edgar/data/80424/000008042421000129/pg-20210930.htm',30,31,32),
 ('2021-12-31','2022-01-19','https://www.sec.gov/Archives/edgar/data/80424/000008042422000016/pg-20211231.htm',32,35,37)]
CODES=['PCENDC96','RSHPCS','CUUR0000SEGB','CUUR0000SEGB01','CUUR0000SEGB02','CUUR0000SEHN01','CUUR0000SEHN02']
def save(name,rows):
 (P/(name+'.json')).write_text(json.dumps(rows,indent=2))
 if rows:
  with (P/(name+'.csv')).open('w') as f:
   w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def main():
 P.mkdir(exist_ok=True);(P/'raw').mkdir(exist_ok=True)
 original=json.loads((ROOT/'data/history_rebuild/pg_quarterly.json').read_text()); facts=[];evidence=[]
 for q,pub,url,dt,st,ot in SOURCES:
  path=P/'sources'/f'pg_{q}_tables.json';tables=json.loads(path.read_text())
  driver={};sales={};organic={}
  for ti,dest in [(dt,driver),(st,sales)]+([(ot,organic)] if ot is not None else []):
   for ri,row in enumerate(tables[ti]):
    row=[c.strip() for c in row if c.strip()];seg=row[0] if row else ''
    seg='Total Company' if seg in ['Total P&G','TOTAL COMPANY'] else seg
    if seg not in SEGMENTS:continue
    ns=numbers(row[1:]);dest[seg]=ns
    evidence.append(dict(period_end=q,publication_date=pub,segment=seg,table=ti,row=ri,excerpt=' | '.join(row),source_url=url,source_file=str(path.relative_to(P)),sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
  for seg in SEGMENTS:
   d=dict(period_end=q,segment=seg,net_sales=sales[seg][0],reported_sales_growth=None,organic_sales_growth=None,reported_volume_growth=None,organic_volume_growth=None,price_contribution=None,mix_contribution=None,fx_contribution=None,other_contribution=None,publication_date=pub)
   if seg!='Corporate':
    ns=driver[seg]
    keys=['reported_volume_growth','fx_contribution','price_contribution','mix_contribution','other_contribution','reported_sales_growth','organic_volume_growth','organic_sales_growth'] if ot is None else ['reported_volume_growth','organic_volume_growth','fx_contribution','price_contribution','mix_contribution','other_contribution','reported_sales_growth']
    assert len(ns)==len(keys),(q,seg,ns)
    d.update(zip(keys,ns))
    if ot is not None:d['organic_sales_growth']=organic[seg][-1]
   facts.append(d)
  rs=[r for r in facts if r['period_end']==q];assert abs(sum(r['net_sales'] for r in rs if r['segment']!='Total Company')-next(r['net_sales'] for r in rs if r['segment']=='Total Company'))<=3
 facts+=original;save('pg_quarterly',facts);save('added_source_rows',evidence)
 dates={r['period_end']:r['publication_date'] for r in facts}
 checkpoints=[]
 for q in sorted(dates):
  if not '2023-06-30'<=q<='2026-03-31':continue
  for stage,cut in [('Origin',months(q)[0]),('Prior report',dates[prior_quarter(q)]),('Pre-earnings',(date.fromisoformat(dates[q])-timedelta(days=1)).isoformat())]:
   checkpoints.append(dict(target_quarter=q,stage=stage,cutoff=cut))
 save('checkpoints',checkpoints)
 jobs=[(c,d) for c in CODES for d in sorted({r['cutoff'] for r in checkpoints})]
 def fetch(job):
  c,d=job;f=P/'raw'/f'{c}_{d}.csv';url=f'https://alfred.stlouisfed.org/graph/alfredgraph.csv?id={c}&cosd=2020-01-01&coed=2026-03-01&vintage_date={d}'
  r=dict(series=c,vintage=d,source_url=url,file=str(f.relative_to(P)))
  try:
   b=f.read_bytes() if f.exists() else subprocess.check_output(['curl','-fsSL','--retry','2','--max-time','35',url],stderr=subprocess.DEVNULL)
   rows=list(csv.reader(io.StringIO(b.decode())));assert rows[0]==['observation_date',c+'_'+d.replace('-','')]
   valid=[x for x in rows[1:] if x[1] not in ['', '.']];assert valid and max(x[0] for x in valid)<=d
   f.write_bytes(b);r.update(status='downloaded',observations=len(valid),latest_month=valid[-1][0],sha256=hashlib.sha256(b).hexdigest())
  except Exception as e:r.update(status='failed',observations=0,latest_month='',sha256='',reason=str(e))
  return r
 with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:rs=list(pool.map(fetch,jobs))
 (P/'market_manifest.json').write_text(json.dumps(rs,indent=2))
 print(json.dumps(dict(quarters=len(dates),checkpoints=len(checkpoints),downloads=sum(r['status']=='downloaded' for r in rs),failed=[r for r in rs if r['status']!='downloaded'])))
if __name__=='__main__':main()
