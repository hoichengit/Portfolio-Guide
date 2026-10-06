"""Screen completed-quarter relationships, then test missing-month forecasts.

All comparisons are retrospective development. The selection date separates
screening from evaluation chronologically; it does not undo earlier inspection.
"""
from pathlib import Path
from datetime import date,timedelta
import json,csv,math,statistics,sys
from replay_releases import quarterly,months,previous_month,fit,prior_quarter

ROOT=Path(__file__).resolve().parents[1];P=ROOT/'data/two_stage';P.mkdir(exist_ok=True)
mean=statistics.mean
SELECTION='2024-07-01'
METHODS=['YoY carry','Flat level','Recent trend','Seasonal step']
SEGMENTS=['Beauty','Grooming','Health Care','Fabric & Home Care','Baby, Feminine & Family Care']
PAIRS=[(s,'organic_volume_growth','PCENDC96') for s in SEGMENTS]+[(s,'price_contribution','CUUR0000SEGB') for s in ['Beauty','Grooming','Health Care']]+[(s,'organic_sales_growth','RSHPCS') for s in ['Beauty','Health Care']]+[('Beauty','price_contribution','CUUR0000SEGB02')]

def save(n,rows):
 (P/(n+'.json')).write_text(json.dumps(rows,indent=2))
 if rows:
  with (P/(n+'.csv')).open('w') as f:
   w=csv.DictWriter(f,fieldnames=list(dict.fromkeys(k for r in rows for k in r)));w.writeheader();w.writerows(rows)
def rm(es):return math.sqrt(mean(e*e for e in es))
def load():
 entries={}
 for folder,name in [('release_backtest','vintage_manifest'),('driver_tests','market_manifest')]:
  for r in json.loads((ROOT/f'data/{folder}/{name}.json').read_text()):
   if r['status']!='downloaded':continue
   d={m:float(v) for m,v in list(csv.reader((ROOT/f'data/{folder}'/r['file']).open()))[1:] if v not in ['', '.']}
   key=r['series'],r['vintage']
   if key not in entries or len(d)>len(entries[key]['data']):entries[key]=dict(r,data=d,path=f'data/{folder}/'+r['file'])
 return entries
E=load()
FACTS=json.loads((ROOT/'data/driver_tests/pg_quarterly.json').read_text())
def version(code,cut):
 return max((v for (c,d),v in E.items() if c==code and d<=cut),key=lambda r:r['vintage'])
def agg(code):return 'sum' if code=='RSHPCS' else 'mean'
def pair_id(seg,metric,code):return seg+' | '+metric+' | '+code

def screen():
 rows=[];summary=[]
 for seg,metric,code in PAIRS:
  v=version(code,SELECTION);d=v['data'];facts=sorted([f for f in FACTS if f['segment']==seg and f['publication_date']<=SELECTION],key=lambda f:f['period_end'])
  for window in ['Expanding','Last eight']:
   rr=[]
   for f in facts:
    q=f['period_end']
    if not '2023-06-30'<=q<='2024-03-31':continue
    known=[z for z in facts if z['period_end']<q]
    tr=[(z,quarterly(d,z['period_end'],agg(code))) for z in known];tr=[(z,x) for z,x in tr if x is not None]
    if window=='Last eight':tr=tr[-8:]
    c=fit([x for z,x in tr],[z[metric] for z,x in tr]);x=quarterly(d,q,agg(code))
    if c is None or x is None:continue
    prediction=c['intercept']+c['beta']*x;last=known[-1][metric];four=mean(z[metric] for z in known[-4:])
    r=dict(pair=pair_id(seg,metric,code),segment=seg,metric=metric,series=code,window=window,quarter=q,selection_date=SELECTION,market_vintage=v['vintage'],market_growth=x,n=c['n'],intercept=c['intercept'],beta=c['beta'],prediction=prediction,actual=f[metric],last=last,four_mean=four,error=prediction-f[metric],last_error=last-f[metric],mean_error=four-f[metric]);rr.append(r);rows.append(r)
   if len(rr)==4:summary.append(dict(pair=pair_id(seg,metric,code),segment=seg,metric=metric,series=code,window=window,quarters=4,rmse=rm([r['error'] for r in rr]),last_rmse=rm([r['last_error'] for r in rr]),mean_rmse=rm([r['mean_error'] for r in rr])))
 selected=[]
 for seg,metric in sorted({(s,m) for s,m,c in PAIRS}):
  candidates=[r for r in summary if r['segment']==seg and r['metric']==metric];best=min(candidates,key=lambda r:r['rmse'])
  if best['rmse']<min(best['last_rmse'],best['mean_rmse']):selected.append(best)
 for r in summary:r['selected']=r in selected
 save('relationship_tests',rows);save('relationship_scores',summary);save('selected_relationships',selected)
 return selected

def estimate(d,q,method):
 target=months(q);latest=max(m for m in d if m<=target[-1]);missing=[m for m in target if m not in d]
 if any(m<latest for m in missing):return None # no extrapolation over an internal missing observation
 filled=dict(d);detail=[]
 eligible=[m for m in sorted(d) if m<=latest and str(int(m[:4])-1)+m[4:] in d]
 if len(eligible)<3:return None
 g=mean(d[m]/d[str(int(m[:4])-1)+m[4:]]-1 for m in eligible[-3:])
 recent=[previous_month(latest,n) for n in [2,1,0]]
 if method=='Recent trend' and not all(m in d for m in recent):return None
 delta=(d[latest]-d[recent[0]])/2 if all(m in d for m in recent) else 0
 cursor=previous_month(latest,-1);step=1
 while cursor<=target[-1]:
  if method=='YoY carry':
   py=str(int(cursor[:4])-1)+cursor[4:]
   if py not in d:return None
   value=d[py]*(1+g)
  elif method=='Flat level':value=d[latest]
  elif method=='Recent trend':value=d[latest]+step*delta
  else:
   ratios=[]
   for y in range(1,4):
    pm=str(int(cursor[:4])-y)+cursor[4:];prev=previous_month(pm)
    if pm in d and prev in d:ratios.append(d[pm]/d[prev])
   if len(ratios)<3:return None
   value=filled[previous_month(cursor)]*statistics.median(ratios)
  if value<=0:return None
  filled[cursor]=value;cursor=previous_month(cursor,-1);step+=1
 for m in target:detail.append(dict(month=m,observed=m in d,value=filled[m]))
 return filled,detail

def checkpoints(code,q,pub):
 start=months(q)[0];end=(date.fromisoformat(pub)-timedelta(days=1)).isoformat();out=[('Origin',start),('Pre-earnings',end)]
 for k,label in [(1,'One month'),(2,'Two months')]:
  vs=sorted([v for (c,dt),v in E.items() if c==code and start<=dt<=end and sum(m in v['data'] for m in months(q))==k],key=lambda v:v['vintage'])
  if vs:out.append((label,vs[0]['vintage']))
 return sorted(out,key=lambda z:(z[1],z[0]))
def truth(code,m,cut):
 vs=sorted([v for (c,dt),v in E.items() if c==code and dt>cut and m in v['data']],key=lambda v:v['vintage'])
 return (vs[0]['data'][m],vs[0]['vintage']) if vs else (None,None)

def run(selected):
 market=[];company=[];fits=[];excluded=[];versions=[]
 codes=sorted({r['series'] for r in selected});targets=sorted({f['period_end'] for f in FACTS if f['period_end']>='2023-06-30'})
 pub={f['period_end']:f['publication_date'] for f in FACTS}
 for code in codes:
  for q in targets:
   for stage,cut in checkpoints(code,q,pub[q]):
    v=version(code,cut);d=v['data'];observed=sum(m in d for m in months(q));available=['YoY carry','Flat level','Recent trend']+(['Seasonal step'] if code.startswith('CUUR') else [])
    versions.append(dict(series=code,quarter=q,stage=stage,cutoff=cut,vintage=v['vintage'],file=v['path'],latest_month=max(d),observed_months=observed))
    methods={m:estimate(d,q,m) for m in available}
    # Compare all eligible methods on the same forecasts. Missing seasonal history
    # or an internal data gap excludes the event for every method.
    if any(z is None for z in methods.values()):
     excluded.append(dict(series=code,quarter=q,stage=stage,cutoff=cut,reason='Internal missing observation or insufficient common history'));continue
    for method,(filled,details) in methods.items():
     x=quarterly(filled,q,agg(code))
     if x is None:continue
     perfect=dict(filled);perfect_available=True
     for t in details:
      if not t['observed']:
       av,tv=truth(code,t['month'],cut)
       if av is None:perfect_available=False
       else:perfect[t['month']]=av
     perfect_x=quarterly(perfect,q,agg(code)) if perfect_available else None
     for t in details:
      if t['observed']:continue
      actual,td=truth(code,t['month'],cut)
      market.append(dict(id=len(market)+1,series=code,quarter=q,stage=stage,cutoff=cut,observed_months=observed,month=t['month'],method=method,predicted_level=t['value'],actual_level=actual,truth_vintage=td,percentage_error=100*(t['value']/actual-1) if actual is not None else None,evaluation=cut>=SELECTION and q>='2024-09-30'))
     if cut<SELECTION or q<'2024-09-30':continue
     for sel in [s for s in selected if s['series']==code]:
      seg,metric=sel['segment'],sel['metric'];known=sorted([f for f in FACTS if f['segment']==seg and f['period_end']<q and f['publication_date']<=cut],key=lambda f:f['period_end']);tr=[(f,quarterly(d,f['period_end'],agg(code))) for f in known];tr=[(f,z) for f,z in tr if z is not None]
      if sel['window']=='Last eight':tr=tr[-8:]
      c=fit([z for f,z in tr],[f[metric] for f,z in tr])
      if not c:continue
      prediction=c['intercept']+c['beta']*x;outcome=next(f[metric] for f in FACTS if f['segment']==seg and f['period_end']==q)
      company.append(dict(id=len(company)+1,pair=sel['pair'],segment=seg,metric=metric,series=code,window=sel['window'],quarter=q,stage=stage,cutoff=cut,market_vintage=v['vintage'],observed_months=observed,method=method,n=c['n'],intercept=c['intercept'],beta=c['beta'],market_growth=x,prediction=prediction,actual=outcome,last_actual=known[-1][metric],four_mean=mean(f[metric] for f in known[-4:]),error=prediction-outcome,last_error=known[-1][metric]-outcome,mean_error=mean(f[metric] for f in known[-4:])-outcome,actual_publication=pub[q]))
      company[-1].update(perfect_missing_month_growth=perfect_x,perfect_input_prediction=c['intercept']+c['beta']*perfect_x if perfect_x is not None else None,relationship_error=c['intercept']+c['beta']*perfect_x-outcome if perfect_x is not None else None,missing_input_error=c['beta']*(x-perfect_x) if perfect_x is not None else None)
      if method=='YoY carry':
       fits.extend(dict(pair=sel['pair'],quarter=q,stage=stage,cutoff=cut,company_quarter=f['period_end'],published=f['publication_date'],market_growth=z,company_growth=f[metric]) for f,z in tr)
 # Select a monthly method using only earlier target-quarter forecasts whose
 # verification vintage is already public. Require four common earlier quarters.
 choices=[]
 for r in [r for r in company if r['method']=='YoY carry']:
  peers=[z for z in company if (z['pair'],z['quarter'],z['stage'],z['cutoff'])==(r['pair'],r['quarter'],r['stage'],r['cutoff'])]
  methods=[z['method'] for z in peers]
  past=[z for z in market if z['series']==r['series'] and z['quarter']<r['quarter'] and z['stage']==r['stage'] and z['truth_vintage'] and z['truth_vintage']<=r['cutoff'] and z['observed_months']==r['observed_months']]
  keys={m:{(z['quarter'],z['cutoff'],z['month']) for z in past if z['method']==m} for m in methods};common=set.intersection(*keys.values()) if keys else set();qs=sorted({k[0] for k in common})[-8:];common={k for k in common if k[0] in qs}
  errors={m:mean([mean([abs(z['percentage_error']) for z in past if z['method']==m and z['quarter']==q and (z['quarter'],z['cutoff'],z['month']) in common]) for q in qs]) for m in methods} if qs else {}
  method=min(methods,key=lambda m:(errors[m],METHODS.index(m))) if len(qs)>=4 else 'YoY carry'
  chosen=next(z for z in peers if z['method']==method)
  choices.append(dict(chosen,id=len(company)+len(choices)+1,method='Available-history choice',selected_method=method,calibration_quarters=len(qs),calibration_last_quarter=qs[-1] if qs else '',calibration_mape=errors.get(method),reason='Lowest earlier monthly MAPE' if len(qs)>=4 else 'Fallback: fewer than four completed quarters'))
 company+=choices
 # Only attach monthly truths for scoring; they never enter estimates or choices
 # until the corresponding preserved vintage is available.
 mscore=[]
 for code in codes:
  for stage in ['Origin','One month','Two months','Pre-earnings']:
   for method in METHODS:
    rs=[r for r in market if r['series']==code and r['stage']==stage and r['method']==method and r['evaluation'] and r['actual_level'] is not None]
    if rs:mscore.append(dict(series=code,stage=stage,method=method,quarters=len({r['quarter'] for r in rs}),missing_month_forecasts=len(rs),mape=mean(abs(r['percentage_error']) for r in rs),rmse_pct=rm([r['percentage_error'] for r in rs])))
 cscore=[]
 for pair in sorted({r['pair'] for r in company}):
  for stage in ['Origin','One month','Two months','Pre-earnings']:
   for method in METHODS+['Available-history choice']:
    rs=[r for r in company if r['pair']==pair and r['stage']==stage and r['method']==method]
    if rs:cscore.append(dict(pair=pair,stage=stage,method=method,quarters=len(rs),rmse=rm([r['error'] for r in rs]),mae=mean(abs(r['error']) for r in rs),last_rmse=rm([r['last_error'] for r in rs]),mean_rmse=rm([r['mean_error'] for r in rs])))
 save('monthly_forecasts',market);save('monthly_scores',mscore);save('company_forecasts',company);save('company_scores',cscore);save('method_choices',choices);save('training_pairs',fits);save('versions_used',versions);save('excluded_events',excluded)
 assert all(r['published']<=r['cutoff'] and r['company_quarter']<r['quarter'] for r in fits)
 assert all(r['market_vintage']<=r['cutoff']<r['actual_publication'] for r in company)
 assert all(r['calibration_last_quarter']<r['quarter'] for r in choices if r['calibration_last_quarter'])
 assert all(abs(r['error']-r['relationship_error']-r['missing_input_error'])<1e-9 for r in company if r['perfect_input_prediction'] is not None)
 # Observed month preservation: estimates must never overwrite an available value.
 for v in versions:
  d=version(v['series'],v['cutoff'])['data'];est=estimate(d,v['quarter'],'YoY carry')
  if est:assert all(t['value']==d[t['month']] for t in est[1] if t['observed'])
 validation=dict(selection_date=SELECTION,screening_quarters=4,evaluation_quarters='July 2024–March 2026 (seven targets; availability varies)',selected_relationships=len(selected),series=codes,monthly_forecasts=len(market),company_forecasts=len(company),excluded_events=len(excluded),no_future_company_training=True,no_future_market_versions=True,no_future_calibration_outcomes=True,monthly_truth='Earliest preserved later vintage, not guaranteed first official release',screen='Conditional completed-quarter check using selection-date vintages; not a real-time forecast',evaluation='Retrospective development; these periods were inspected previously',policy_accuracy_tested=False)
 (P/'validation.json').write_text(json.dumps(validation,indent=2))
 print(json.dumps(dict(selected=selected,monthly_scores=mscore,company_scores=cscore,validation=validation),indent=2))
def worked_example():
 company=json.loads((P/'company_forecasts.json').read_text())
 rows=[r for r in company if r['segment']=='Beauty' and r['metric']=='price_contribution' and r['quarter']=='2025-06-30' and r['stage']=='Two months']
 v=version('CUUR0000SEGB02','2025-07-01');d=v['data'];monthly=[]
 for m in months('2025-06-30'):
  values={method:estimate(d,'2025-06-30',method)[0][m] for method in METHODS}
  actual,td=(d[m],v['vintage']) if m in d else truth('CUUR0000SEGB02',m,'2025-07-01')
  monthly.append(dict(month=m,prior_year=d[str(int(m[:4])-1)+m[4:]],observed=m in d,actual=actual,truth_date=td,**values))
 seasonal=[dict(year=y,may=d[f'{y}-05-01'],june=d[f'{y}-06-01'],ratio=d[f'{y}-06-01']/d[f'{y}-05-01']) for y in [2022,2023,2024]]
 (P/'worked_example.json').write_text(json.dumps(dict(company=rows,monthly=monthly,seasonal=seasonal,market_file=v['path']),indent=2))

if __name__=='__main__':
 run(screen())
 worked_example()

