"""Download public, date-frozen market inputs. Reject non-CSV error pages."""
from pathlib import Path
import csv, io, json, urllib.request, hashlib, sys

ROOT = Path(__file__).resolve().parents[1] / 'data/history_rebuild'
SERIES = {
    'RSHPCS': ('US health and personal care store sales', 'USD million, monthly flow, seasonally adjusted', 'sum'),
    'PCENDC96': ('US real nondurable consumption', 'USD billion, chained 2017, seasonally adjusted annual rate', 'mean'),
    'CUUR0000SEGB': ('US personal care products CPI', 'Index 1982-84=100, not seasonally adjusted', 'mean'),
    'CUUR0000SEHN01': ('US household cleaning products CPI', 'Index, not seasonally adjusted', 'mean'),
    'CUUR0000SEHN02': ('US household paper products CPI', 'Index, not seasonally adjusted', 'mean'),
}

def main():
    folder=ROOT/'market'; folder.mkdir(parents=True,exist_ok=True)
    manifest=[]
    for code,(label,unit,aggregation) in SERIES.items():
        for vintage in ['2026-04-24','2026-05-15']:
            url=f'https://alfred.stlouisfed.org/graph/alfredgraph.csv?id={code}&cosd=2021-01-01&coed=2026-04-01&vintage_date={vintage}'
            row=dict(series=code,label=label,unit=unit,aggregation=aggregation,vintage=vintage,url=url)
            try:
                data=urllib.request.urlopen(url,timeout=30).read()
                parsed=list(csv.reader(io.StringIO(data.decode())))
                assert parsed[0]==['observation_date',code+'_'+vintage.replace('-','')],str(parsed[0])[:100]
                valid=[r for r in parsed[1:] if r[1] not in ['', '.']]
                assert valid
                file=f'{code}_{vintage}.csv'; (folder/file).write_bytes(data)
                row.update(status='downloaded',file='market/'+file,observations=len(valid),first=valid[0][0],last=valid[-1][0],sha256=hashlib.sha256(data).hexdigest())
            except Exception as exc:
                row.update(status='unavailable',reason=str(exc)[:200])
            manifest.append(row); print(code,vintage,row['status'],row.get('last',''),flush=True)
    (ROOT/'market_manifest.json').write_text(json.dumps(manifest,indent=2))

def product_prices(source=None):
    codes={'CUUR0000SEHN01':'Household cleaning products','CUUR0000SEHN02':'Household paper products','CUUR0000SEGB01':'Hair, dental, shaving and miscellaneous personal care products','CUUR0000SEGB02':'Cosmetics, perfume, bath, nail preparations and implements'}
    request=dict(seriesid=list(codes),startyear='2021',endyear='2026')
    url='https://api.bls.gov/publicAPI/v2/timeseries/data/'
    j=json.loads(Path(source).read_text()) if source else json.load(urllib.request.urlopen(urllib.request.Request(url,data=json.dumps(request).encode(),headers={'Content-Type':'application/json'}),timeout=30))
    assert j['status']=='REQUEST_SUCCEEDED'
    rows=[]
    for s in j['Results']['series']:
        for r in s['data']:
            if r['period']=='M13':continue
            date=r['year']+'-'+r['period'][1:]+'-01'
            if date>'2026-04-01':continue
            rows.append(dict(series=s['seriesID'],category=codes[s['seriesID']],month=date,value=float(r['value']) if r['value'] not in ['-','.',''] else None,vintage='Retrieved 2026-10-05; historical vintage not verified',forecast_eligible=False,source_url=url))
    rows.sort(key=lambda r:(r['series'],r['month']))
    (ROOT/'product_prices_research_only.json').write_text(json.dumps(rows,indent=2))
    with (ROOT/'product_prices_research_only.csv').open('w') as f:
        w=csv.DictWriter(f,fieldnames=rows[0]);w.writeheader();w.writerows(rows)
    (ROOT/'product_price_request.json').write_text(json.dumps(dict(url=url,request=request,scope='Current-vintage research only; not an as-of forecast input'),indent=2))
    print('Product-price observations',len(rows),'missing',sum(r['value'] is None for r in rows))

if __name__=='__main__':
    if len(sys.argv)>1:product_prices(sys.argv[1])
    else:main();product_prices()
