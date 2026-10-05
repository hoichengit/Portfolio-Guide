"""Rebuild quarterly financial history from preserved, dated source tables."""
from pathlib import Path
import csv, json, re, hashlib
ROOT=Path(__file__).resolve().parents[1]
P=ROOT/'data/history_rebuild'
SEGMENTS=['Beauty','Grooming','Health Care','Fabric & Home Care','Baby, Feminine & Family Care','Corporate','Total Company']

def numbers(cells):
    out=[]
    for c in cells:
        c=c.strip().replace('$','').replace('%','').replace(',','').replace('\xa0','').strip()
        if c in ['—','–','-']: out.append(0.0)
        elif re.fullmatch(r'\(?-?\d+(?:\.\d+)?\)?',c): out.append(float(c.replace('(','-').replace(')','')))
    return out

def save(name,rows):
    (P/(name+'.json')).write_text(json.dumps(rows,indent=2))
    with (P/(name+'.csv')).open('w') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

def main():
    sources=json.loads((P/'filings.json').read_text())
    sources=[dict(s,file='sources/pg_'+s['period']+'_tables.json') for s in sources if s['form']=='10-Q']
    for s in json.loads((P/'extra_releases.json').read_text()):
        sources.append(dict(s,form='Earnings release',file='sources/release_'+s['period']+'_tables.json'))
    s=dict(period_end='2025-06-30',publication_date='2025-07-29',url='https://www.pginvestor.com/news/news-details/2025/PG-Announces-Fourth-Quarter-and-Fiscal-Year-2025-Results/default.aspx')
    file='sources/release_2025-06-30_tables.json'
    sources.append(dict(period=s['period_end'],date=s['publication_date'],url=s['url'],form='Earnings release',file=file))
    observations=[]; bykey={}
    for s in sorted(sources,key=lambda s:s['period']):
        assert s['date']<='2026-04-24' and s['period']<='2026-03-31'
        tables=json.loads((P/s['file']).read_text())
        for ti,t in enumerate(tables):
            # Some filings append the YTD table below the quarterly table.
            stop=next((i for i,row in enumerate(t) if i>5 and any('Six Months Ended' in c or 'Nine Months Ended' in c for c in row)),len(t))
            t=t[:stop]
            flat=re.sub(r'\s+',' ',' '.join(' '.join(row) for row in t))
            quarter=('Three Months Ended' in flat or ('April' in flat and 'June' in flat)) and not ('Nine Months Ended' in flat or 'Six Months Ended' in flat)
            if not quarter or 'Beauty' not in flat:continue
            kind=''
            if 'Volume with Acquisitions' in flat and 'Volume Excluding' in flat:kind='drivers'
            elif 'Organic Volume' in flat and 'Organic Sales' in flat:kind='release_drivers'
            elif '% Change Versus Year Ago' in flat and 'Net Sales' in flat:kind='sales'
            elif 'Organic Sales Growth' in flat and 'Net Sales Growth' in flat:kind='organic'
            if not kind:continue
            for ri,row in enumerate(t):
                row=[x.strip() for x in row if x.strip()]
                if not row:continue
                seg='Total Company' if row[0] in ['Total P&G','TOTAL COMPANY','TOTAL'] else row[0]
                if seg not in SEGMENTS:continue
                ns=numbers(row[1:]); metrics={}
                if kind=='drivers' and len(ns)==7:
                    metrics=dict(zip(['reported_volume_growth','organic_volume_growth','fx_contribution','price_contribution','mix_contribution','other_contribution','reported_sales_growth'],ns))
                elif kind=='release_drivers' and len(ns)==8:
                    metrics=dict(zip(['reported_volume_growth','fx_contribution','price_contribution','mix_contribution','other_contribution','reported_sales_growth','organic_volume_growth','organic_sales_growth'],ns))
                elif kind=='organic' and len(ns)==4:metrics={'organic_sales_growth':ns[-1]}
                elif kind=='sales' and ns:metrics={'net_sales':ns[0]}
                for metric,value in metrics.items():
                    r=dict(period_end=s['period'],segment=seg,metric=metric,value=value,unit='USD million' if metric=='net_sales' else 'percent / percentage-point contribution',publication_date=s['date'],source_url=s['url'],source_file=s['file'],locator=f'table {ti}, row {ri} (zero-based)',excerpt=' | '.join(row))
                    key=(s['period'],seg,metric)
                    if key in bykey:assert bykey[key]['value']==value,(key,bykey[key]['value'],value)
                    else:bykey[key]=r;observations.append(r)
    wide=[]
    periods=sorted(set(r['period_end'] for r in observations))
    metrics=['net_sales','reported_sales_growth','organic_sales_growth','reported_volume_growth','organic_volume_growth','price_contribution','mix_contribution','fx_contribution','other_contribution']
    for date in periods:
        for seg in SEGMENTS:
            d=dict(period_end=date,segment=seg)
            for metric in metrics:d[metric]=bykey.get((date,seg,metric),{}).get('value')
            assert d['net_sales'] is not None,(date,seg,'missing sales')
            if seg!='Corporate':assert all(d[x] is not None for x in metrics),(date,seg,d)
            d['publication_date']=next(r['publication_date'] for r in observations if r['period_end']==date)
            wide.append(d)
    checks=[]
    for date in periods:
        rs=[r for r in wide if r['period_end']==date]
        diff=sum(r['net_sales'] for r in rs if r['segment']!='Total Company')-next(r['net_sales'] for r in rs if r['segment']=='Total Company')
        assert abs(diff)<=3,(date,diff)
        checks.append(dict(period=date,segment_sum_difference_usdm=diff,tolerance_usdm=3))
    save('pg_observations',observations);save('pg_quarterly',wide)
    (P/'validation.json').write_text(json.dumps(dict(quarters=len(periods),segments=5,first=periods[0],last=periods[-1],quarterly_reconciliations=checks,all_sources_before_cutoff=True),indent=2))
    for s in sources:s['sha256']=hashlib.sha256((P/s['file']).read_bytes()).hexdigest()
    (P/'selected_source_manifest.json').write_text(json.dumps(sources,indent=2))
    print('Extracted',len(periods),'quarters,',len(wide),'quarter/segment rows,',len(observations),'traceable observations')

if __name__=='__main__':main()
