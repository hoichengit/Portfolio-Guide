"""Collect public ALFRED revision dates and date-frozen CSVs; no API key required."""
from pathlib import Path
import concurrent.futures, csv, hashlib, io, json, re, subprocess
ROOT=Path(__file__).resolve().parents[1]/'data/release_backtest'
CODES=['PCENDC96','RSHPCS','CUUR0000SEGB']
EXTRA=['2024-04-01','2024-07-01','2024-10-01','2025-01-01','2025-04-01','2025-07-01','2025-10-01','2026-01-01','2026-04-01','2026-04-24','2026-05-15']
def request(url):
    return subprocess.check_output(['curl','-fsSL','--retry','2','--max-time','45',url])
def main():
    (ROOT/'raw').mkdir(parents=True,exist_ok=True); jobs=[];calendar=[]
    for code in CODES:
        url='https://alfred.stlouisfed.org/series/downloaddata?seid='+code
        page=request(url);(ROOT/'raw'/f'{code}_vintage_dates.html').write_bytes(page)
        block=re.search(r'<select[^>]*id="form_selected_vintage_dates".*?</select>',page.decode(),re.S).group()
        dates=sorted(set(re.findall(r'value="(\d{4}-\d{2}-\d{2})"',block)))
        dates=[d for d in dates if '2023-12-01'<=d<='2026-05-15']
        calendar.extend(dict(series=code,date=d,source_url=url,date_type='ALFRED vintage / revision date') for d in dates)
        jobs.extend((code,d,d in dates) for d in sorted(set(dates+EXTRA)))
    (ROOT/'release_calendar.json').write_text(json.dumps(calendar,indent=2))
    def collect(job):
        code,date,event=job;f=ROOT/'raw'/f'{code}_{date}.csv'
        url=f'https://alfred.stlouisfed.org/graph/alfredgraph.csv?id={code}&cosd=2021-01-01&coed=2026-04-01&vintage_date={date}'
        r=dict(series=code,vintage=date,is_release_event=event,source_url=url,file='raw/'+f.name)
        try:
            b=f.read_bytes() if f.exists() else request(url)
            rows=list(csv.reader(io.StringIO(b.decode())))
            assert rows[0]==['observation_date',code+'_'+date.replace('-','')]
            valid=[x for x in rows[1:] if x[1] not in ['', '.']]
            assert valid and max(x[0] for x in valid)<=date
            f.write_bytes(b);r.update(status='downloaded',observations=len(valid),latest_month=valid[-1][0],sha256=hashlib.sha256(b).hexdigest())
        except Exception as e:r.update(status='failed',reason=str(e))
        return r
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:
        results=list(pool.map(collect,jobs))
    (ROOT/'vintage_manifest.json').write_text(json.dumps(results,indent=2))
    print(json.dumps(dict(downloaded=sum(r['status']=='downloaded' for r in results),failed=[r for r in results if r['status']=='failed'],release_events=len(calendar))))
if __name__=='__main__':main()
