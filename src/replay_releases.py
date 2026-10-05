"""Replay frozen market vintages and published P&G facts, then score separately.

Model definitions are fixed for this run. This is retrospective model development,
not an independent prospective test or a causal identification exercise.
"""
from pathlib import Path
from datetime import date,timedelta
import calendar,csv,json,math,statistics
ROOT=Path(__file__).resolve().parents[1];P=ROOT/'data/release_backtest'
mean=statistics.mean
def dump(name,rows):
    (P/(name+'.json')).write_text(json.dumps(rows,indent=2))
    if rows:
        with (P/(name+'.csv')).open('w') as f:
            w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def previous_month(s,n=1):
    k=int(s[:4])*12+int(s[5:7])-1-n
    return f'{k//12}-{k%12+1:02d}-01'
def months(q):
    m=int(q[5:7]);return[f'{q[:4]}-{i:02d}-01' for i in range(m-2,m+1)]
def prior_quarter(q):
    s=previous_month(q,3);y,m=int(s[:4]),int(s[5:7]);return f'{y}-{m:02d}-{calendar.monthrange(y,m)[1]}'
def fit(x,y):
    sx=sum(x);sy=sum(y);sxx=sum(t*t for t in x);sxy=sum(a*b for a,b in zip(x,y));n=len(x)
    if n<8 or abs(sxx-sx*sx/n)<1e-12:return None
    b=(sxy-sx*sy/n)/(sxx-sx*sx/n);return dict(n=n,sx=sx,sy=sy,sxx=sxx,sxy=sxy,beta=b,intercept=mean(y)-b*mean(x))
def quarterly(data,q,agg):
    ms=months(q);prev=[str(int(s[:4])-1)+s[4:] for s in ms]
    if not all(m in data for m in ms+prev):return None
    fn=sum if agg=='sum' else mean
    return 100*(fn([data[m] for m in ms])/fn([data[m] for m in prev])-1)
def estimate_market(data,q,agg):
    # Fill unknown target months with the mean YoY rate of the latest three
    # observed months, preserving prior-year monthly seasonality. No future levels.
    ms=months(q);eligible=[m for m in sorted(data) if m<=ms[-1] and str(int(m[:4])-1)+m[4:] in data]
    if len(eligible)<3:return None
    recent=eligible[-3:];g=mean([data[m]/data[str(int(m[:4])-1)+m[4:]]-1 for m in recent])
    filled=dict(data);detail=[]
    for m in ms:
        py=str(int(m[:4])-1)+m[4:]
        if py not in data:return None
        observed=m in data;v=data[m] if observed else data[py]*(1+g);filled[m]=v
        detail.append(dict(month=m,observed=observed,value=v,prior_year=data[py],carry_yoy_pct=g*100))
    return quarterly(filled,q,agg),detail
def main():
    financial=json.loads((ROOT/'data/history_rebuild/pg_quarterly.json').read_text())
    manifest=json.loads((P/'vintage_manifest.json').read_text())
    assert all(r['status']=='downloaded' for r in manifest),'Missing downloads; resolve before scoring'
    vintages={};market={}
    for r in manifest:
        key=(r['series'],r['vintage']);vintages.setdefault(r['series'],[]).append(r)
        market[key]={d:float(v) for d,v in list(csv.reader((P/r['file']).open()))[1:] if v not in ['', '.']}
    for v in vintages.values():v.sort(key=lambda r:r['vintage'])
    segments=['Beauty','Grooming','Health Care','Fabric & Home Care','Baby, Feminine & Family Care']
    pairs=[(s,'organic_volume_growth','PCENDC96') for s in segments]+[(s,'price_contribution','CUUR0000SEGB') for s in ['Beauty','Grooming']]+[(s,'organic_sales_growth','RSHPCS') for s in ['Beauty','Health Care']]
    targets=sorted({r['period_end'] for r in financial if '2024-06-30'<=r['period_end']<='2026-03-31'})
    source_dates={r['period_end']:r['publication_date'] for r in financial}
    rows=[];training=[];month_detail=[];checks=[]
    for target in targets+['2026-06-30']:
        start=months(target)[0];end=(date.fromisoformat(source_dates[target])-timedelta(days=1)).isoformat() if target in source_dates else '2026-05-15'
        for seg,metric,code in pairs:
            events=sorted(set([start,end]+[r['vintage'] for r in vintages[code] if r['is_release_event'] and start<=r['vintage']<=end]+[r['publication_date'] for r in financial if start<=r['publication_date']<=end]+(['2026-04-24'] if target=='2026-06-30' else [])))
            agg='sum' if code=='RSHPCS' else 'mean'
            for cutoff in events:
                source=max((r for r in vintages[code] if r['vintage']<=cutoff),key=lambda r:r['vintage'])
                data=market[(code,source['vintage'])]
                known=sorted([r for r in financial if r['segment']==seg and r['period_end']<target and r['publication_date']<=cutoff],key=lambda r:r['period_end'])
                assert known and all(r['publication_date']<=cutoff for r in known)
                baseline=mean([r[metric] for r in known[-4:]]);last=known[-1][metric]
                base=dict(segment=seg,metric=metric,series=code,target_quarter=target,cutoff=cutoff,market_vintage=source['vintage'],market_url=source['source_url'],latest_market_month=max(data),latest_company_quarter=known[-1]['period_end'],latest_company_publication=known[-1]['publication_date'],baseline=baseline,last_actual=last)
                est=estimate_market(data,target,agg);assert est is not None
                targetx,detail=est
                observed=sum(d['observed'] for d in detail)
                pid=len(rows)+1
                for d in detail:month_detail.append(dict(prediction_id=pid,**d))
                models={}
                for method in ['bridge','lagged']:
                    train=[]
                    for f in known:
                        x=quarterly(data,f['period_end'] if method=='bridge' else prior_quarter(f['period_end']),agg)
                        if x is not None:train.append((f,x))
                    coef=fit([x for f,x in train],[f[metric] for f,x in train]);tx=targetx if method=='bridge' else quarterly(data,prior_quarter(target),agg)
                    for f,x in train:training.append(dict(prediction_id=pid,method=method,company_quarter=f['period_end'],company_published=f['publication_date'],market_growth=x,company_growth=f[metric]))
                    pred=coef['intercept']+coef['beta']*tx if coef and tx is not None else None
                    models[method]=pred
                    for k in ['n','sx','sy','sxx','sxy','beta','intercept']:base[method+'_'+k]=coef[k] if coef else None
                    base[method+'_x']=tx
                r=dict(prediction_id=pid,**base,months_observed=observed,bridge=models['bridge'],lagged=models['lagged'],blend=(baseline+models['bridge'])/2 if models['bridge'] is not None else None)
                rows.append(r)
                checks.append(source['vintage']<=cutoff and max(data)<=cutoff and all(f['publication_date']<=cutoff and f['period_end']<target for f in known))
    dump('predictions',rows);dump('training_pairs',training);dump('target_months',month_detail)
    # Outcomes are joined only after all predictions have been built.
    actual={(r['segment'],r['period_end']):r for r in financial}
    scored=[]
    for seg,metric,code in pairs:
        for target in targets:
            rs=[r for r in rows if r['segment']==seg and r['metric']==metric and r['target_quarter']==target]
            stages={'Origin':rs[0],'Pre-earnings':rs[-1]}
            for count,label in [(1,'First month'),(2,'Second month')]:
                eligible=[r for r in rs if r['months_observed']>=count]
                if eligible:stages[label]=eligible[0]
            for stage,r in stages.items():
                y=actual[(seg,target)][metric]
                for method in ['baseline','last_actual','bridge','lagged','blend']:
                    if r[method] is None:continue
                    scored.append(dict(prediction_id=r['prediction_id'],segment=seg,metric=metric,series=code,target_quarter=target,stage=stage,cutoff=r['cutoff'],method=method,prediction=r[method],actual=y,error=r[method]-y,squared_error=(r[method]-y)**2,baseline_error=r['baseline']-y,last_actual_error=r['last_actual']-y,months_observed=r['months_observed']))
    dump('scored_predictions',scored)
    scores=[]
    for seg,metric,code in pairs:
        for stage in ['Origin','First month','Second month','Pre-earnings']:
            for method in ['baseline','last_actual','bridge','lagged','blend']:
                rs=[r for r in scored if (r['segment'],r['metric'],r['stage'],r['method'])==(seg,metric,stage,method)]
                if not rs:continue
                rm=lambda k:math.sqrt(mean([r[k]**2 for r in rs]))
                scores.append(dict(segment=seg,metric=metric,series=code,stage=stage,method=method,quarters=len(rs),rmse=rm('error'),baseline_rmse=rm('baseline_error'),last_actual_rmse=rm('last_actual_error'),mae=mean([abs(r['error']) for r in rs]),bias=mean([r['error'] for r in rs]),wins_vs_baseline=sum(abs(r['error'])<abs(r['baseline_error']) for r in rs)))
    dump('scores',scores)
    validation=dict(predictions=len(rows),release_vintages=len(manifest),test_quarters=len(targets),no_future_inputs=all(checks),actuals_joined_after_predictions=True,target_april_june_actuals_used=False,minimum_training_pairs=8,methods='four-quarter mean; last actual; same-quarter bridge; previous-quarter market; fixed 50/50 mean-bridge blend',unknown_month_rule='Latest three available monthly YoY rates averaged; apply to matching prior-year levels',timing='End-of-day ALFRED vintage events plus P&G publication dates; not an intraday execution record',selection='Retrospective model development; these periods were examined earlier, so not an untouched confirmation sample')
    (P/'validation.json').write_text(json.dumps(validation,indent=2))
    print(json.dumps(validation));print(json.dumps([r for r in scores if r['stage']=='Pre-earnings' and r['method']=='bridge'],indent=2))
if __name__=='__main__':main()
