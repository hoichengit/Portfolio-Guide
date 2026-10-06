"""Retrospective, release-aligned rolling forecasts. June actual is scoring-only.

Rules are specified before this run, but after the analyst saw prior results.
This is development evidence, never an untouched prospective test.
"""
from pathlib import Path
import json,csv,hashlib,statistics,math,ast
from datetime import date
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from replay_releases import quarterly, fit, months, previous_month

ROOT=Path(__file__).resolve().parents[1]; D=ROOT/'data/forecast_improvement'; O=ROOT/'outputs/forecast_improvement'
D.mkdir(exist_ok=True);O.mkdir(exist_ok=True)
mean=statistics.mean
ns=dict(mean=mean,statistics=statistics,months=months,previous_month=previous_month)
fn=next(n for n in ast.parse((ROOT/'src/test_two_stage.py').read_text()).body if isinstance(n,ast.FunctionDef) and n.name=='estimate')
exec(compile(ast.Module(body=[fn],type_ignores=[]),'existing_month_estimator','exec'),ns)
estimate=ns['estimate'];agg=lambda code:'sum' if code=='RSHPCS' else 'mean'
E={};manifest=[]
for folder,file in [('release_backtest','vintage_manifest'),('driver_tests','market_manifest')]:
 for r in json.loads((ROOT/f'data/{folder}/{file}.json').read_text()):
  if r['status']=='downloaded':manifest.append(dict(r,path=f'data/{folder}/'+r['file']))
def version(code,cut):
 candidates=[r for r in manifest if r['series']==code and r['vintage']<=cut]+[r for (c,d),r in E.items() if c==code and d<=cut]
 if not candidates:return None
 r=max(candidates,key=lambda r:r['vintage']);key=code,r['vintage']
 if key not in E:
  d={m:float(v) for m,v in list(csv.reader((ROOT/r['path']).open()))[1:] if v not in ['', '.']}
  E[key]=dict(r,data=d)
 return E[key]
FACTS=json.loads((ROOT/'data/driver_tests/pg_quarterly.json').read_text())
def read(p):return json.loads((ROOT/p).read_text())
def save(n,d):
 (D/(n+'.json')).write_text(json.dumps(d,indent=2))
 if isinstance(d,list) and d:
  with (D/(n+'.csv')).open('w') as f:
   w=csv.DictWriter(f,fieldnames=list(dict.fromkeys(k for r in d for k in r)));w.writeheader();w.writerows(d)
CONFIG=dict(start='2023-06-30',target='2026-06-30',cutoff='2026-04-24',min_selection=4,score_window=8,bias_window=4,bias_weight=.5,challenger_improvement=.10,draws=100000,seed=20260424,df=5,sd_floor=1.,correlation_shrinkage=.5)
METHODS=['Last actual','Four-quarter mean','Recent two mean','Prior-year quarter','Market level','Anchored market change','Half last + market','Market bias correction']
save('config',CONFIG)
FROZEN=read('data/april24_forecast/frozen_forecast.json')
LABELS=['Baby / Feminine / Family volume','Beauty organic sales','Beauty volume','Beauty pricing','Fabric & Home volume','Health Care pricing']
for r in read('data/april24_forecast/market_manifest.json'):
 d={m:float(v) for m,v in list(csv.reader((ROOT/'data/april24_forecast'/r['file']).open()))[1:] if v not in ['', '.']}
 E[(r['series'],r['vintage'])]=dict(r,data=d,path='data/april24_forecast/'+r['file'])
SHA=hashlib.sha256((ROOT/'data/april24_forecast/frozen_forecast.json').read_bytes()).hexdigest()

def select(past):
 if len(past)<CONFIG['min_selection']:return 'Last actual',{},'Warm-up: fewer than four completed tests'
 past=past[-CONFIG['score_window']:]
 scores={m:mean(abs(z['predictions'][m]-z['actual']) for z in past) for m in METHODS}
 base=min(METHODS[:2],key=lambda m:(scores[m],METHODS.index(m)))
 best=min(METHODS,key=lambda m:(scores[m],METHODS.index(m)))
 chosen=best if scores[best]<scores[base]*(1-CONFIG['challenger_improvement']) else base
 return chosen,scores,'Challenger beats simple benchmark by >10%' if chosen not in METHODS[:2] else 'Keep lower-error simple benchmark'

def replay(facts):
 records=[];provenance=[];training=[]
 for i,spec in enumerate(FROZEN):
  seg,metric,code=spec['segment'],spec['metric'],spec['series'];sf=sorted([f for f in facts if f['segment']==seg],key=lambda f:f['period_end'])
  targets=sorted({f['period_end'] for f in sf if CONFIG['start']<=f['period_end']<CONFIG['target']})+[CONFIG['target']]
  local=[]
  for q in targets:
   previous=[f for f in sf if f['period_end']<q]
   cut=CONFIG['cutoff'] if q==CONFIG['target'] else previous[-1]['publication_date']
   known=[f for f in previous if f['publication_date']<=cut]
   if len(known)<8:continue
   v=version(code,cut)
   if v is None:continue
   d=v['data'];est=estimate(d,q,'YoY carry')
   if est is None:continue
   filled,detail=est;x=quarterly(filled,q,agg(code));pairs=[(f,quarterly(d,f['period_end'],agg(code))) for f in known];pairs=[(f,z) for f,z in pairs if z is not None]
   c=fit([z for f,z in pairs],[f[metric] for f,z in pairs])
   recent=pairs[-8:];rc=fit([z for f,z in recent],[f[metric] for f,z in recent])
   if c is None or rc is None or x is None:continue
   last=known[-1][metric];four=mean(f[metric] for f in known[-4:]);yp=q[:4];prior=str(int(yp)-1)+q[4:];season=next((f[metric] for f in known if f['period_end']==prior),four)
   past=[z for z in local if z['publication']<=cut and z['quarter']<q]
   market=c['intercept']+c['beta']*x
   correction=CONFIG['bias_weight']*mean(z['actual']-z['predictions']['Market level'] for z in past[-CONFIG['bias_window']:]) if len(past)>=4 else 0
   preds=dict(zip(METHODS,[last,four,mean(f[metric] for f in known[-2:]),season,market,last+rc['beta']*(x-pairs[-1][1]),.5*last+.5*market,market+correction]))
   chosen,scores,reason=select(past)
   row=dict(index=i,metric=LABELS[i],quarter=q,cutoff=cut,predictions=preds,selected_method=chosen,prediction=preds[chosen],selection_quarters=len(past[-8:]),selection_last=max((z['quarter'] for z in past),default=''),selection_scores=scores,reason=reason,eligible=len(past)>=4)
   # Attach outcome only after forecasts and selection are complete.
   actual=next((f for f in sf if f['period_end']==q),None)
   if q!=CONFIG['target']:
    row.update(actual=actual[metric],publication=actual['publication_date'])
    assert row['publication']>cut
   records.append(row);local.append(row)
   provenance.append(dict(metric=LABELS[i],quarter=q,cutoff=cut,latest_company_quarter=known[-1]['period_end'],latest_company_publication=known[-1]['publication_date'],series=code,vintage=v['vintage'],vintage_age_days=(date.fromisoformat(cut)-date.fromisoformat(v['vintage'])).days,latest_market_month=max(d),target_months_observed=sum(t['observed'] for t in detail),file=v['path'],forecast_market_growth=x,market_intercept=c['intercept'],market_beta=c['beta'],recent_beta=rc['beta'],last_matched_market_growth=pairs[-1][1],market_bias_adjustment=correction))
   training.extend(dict(metric=LABELS[i],target=q,cutoff=cut,company_quarter=f['period_end'],publication=f['publication_date'],market_growth=z,company_growth=f[metric]) for f,z in pairs)
   assert v['vintage']<=cut and all(f['publication_date']<=cut and f['period_end']<q for f,z in pairs)
 return records,provenance,training

records,provenance,training=replay([f for f in FACTS if f['period_end']<CONFIG['target']])
# Adding/altering future company observations must not change forecasts.
poison=[f for f in FACTS if f['period_end']<CONFIG['target']]
for seg in {r['segment'] for r in FROZEN}:
 base=max((f for f in FACTS if f['segment']==seg),key=lambda f:f['period_end'])
 poison.append(dict(base,period_end=CONFIG['target'],publication_date='2026-07-29',**{k:99999 for k in ['organic_sales_growth','organic_volume_growth','price_contribution']}))
again,_,_=replay(poison)
assert [{k:r[k] for k in ['metric','quarter','prediction','selected_method']} for r in records]==[{k:r[k] for k in ['metric','quarter','prediction','selected_method']} for r in again]
save('release_inputs',provenance);save('training_pairs',training)
flat=[dict(metric=r['metric'],quarter=r['quarter'],cutoff=r['cutoff'],actual=r.get('actual'),publication=r.get('publication'),selected_method=r['selected_method'],prediction=r['prediction'],selection_quarters=r['selection_quarters'],selection_last=r['selection_last'],eligible=r['eligible'],**r['predictions']) for r in records]
save('rolling_forecasts',flat);save('selection_log',records)
hist=[r for r in records if r['quarter']<CONFIG['target'] and r['eligible']]
scores=[]
for label in LABELS+['All six measures']:
 rr=[r for r in hist if label=='All six measures' or r['metric']==label]
 for method in METHODS+['Rolling selection']:
  es=[(r['prediction'] if method=='Rolling selection' else r['predictions'][method])-r['actual'] for r in rr]
  scores.append(dict(metric=label,method=method,n=len(es),mae=mean(abs(e) for e in es),rmse=math.sqrt(mean(e*e for e in es))))
save('historical_scores',scores)
target=[r for r in records if r['quarter']==CONFIG['target']]
assert len(target)==6
# Save unscored new forecasts and their selection audit before loading June actuals.
save('revised_forecast',target)
pre_actual_sha=hashlib.sha256((D/'revised_forecast.json').read_bytes()).hexdigest()
actuals=read('data/april24_forecast/variance.json')
comparison=[]
for i,r in enumerate(target):
 a=actuals[i]['actual'];old=FROZEN[i]['forecast'];p=r['prediction']
 comparison.append(dict(metric=r['metric'],method=r['selected_method'],old_forecast=old,new_forecast=p,actual=a,old_error=abs(old-a),new_error=abs(p-a),last=r['predictions']['Last actual'],four=r['predictions']['Four-quarter mean']))
save('target_comparison',comparison)

# Error calibration uses completed rolling-selection forecasts, never June actuals.
common=sorted(set.intersection(*[{r['quarter'] for r in hist if r['metric']==label} for label in LABELS]))
errs=np.array([[next(r['actual']-r['prediction'] for r in hist if r['quarter']==q and r['metric']==label) for label in LABELS] for q in common])
assert len(common)>=4
N=CONFIG['draws'];df=CONFIG['df'];rng=np.random.default_rng(CONFIG['seed']);R=np.corrcoef(errs,rowvar=False);R=np.nan_to_num(R);np.fill_diagonal(R,1);R=.5*R+.5*np.eye(6)
rawscale=np.sqrt((errs**2).mean(axis=0));scale=np.maximum(rawscale,CONFIG['sd_floor'])
z=rng.multivariate_normal(np.zeros(6),R,N)*np.sqrt((df-2)/rng.chisquare(df,N))[:,None]
points=np.array([r['prediction'] for r in target]);draw=points+z*scale
probs=[]
for i,r in enumerate(target):
 v=draw[:,i];lo,med,hi=np.quantile(v,[.1,.5,.9]);a=actuals[i]['actual']
 probs.append(dict(metric=r['metric'],forecast=points[i],n=len(common),rms_error=rawscale[i],used_scale=scale[i],p10=lo,median=med,p90=hi,below_count=int((v<points[i]-1).sum()),near_count=int(((v>=points[i]-1)&(v<=points[i]+1)).sum()),above_count=int((v>points[i]+1).sum()),draws=N,actual=a,actual_percentile=float((v<=a).mean()),covered=bool(lo<=a<=hi)))
 assert sum(probs[-1][k] for k in ['below_count','near_count','above_count'])==N
save('probabilities',probs);save('calibration_errors',[dict(quarter=q,**{LABELS[i]:float(errs[j,i]) for i in range(6)}) for j,q in enumerate(common)])
# Historical interval test: each interval only uses earlier available selected errors.
coverage=[];unit=np.random.default_rng(CONFIG['seed']).standard_t(df,100000)*np.sqrt((df-2)/df);ql,qh=np.quantile(unit,[.1,.9])
for r in hist:
 prior=[z for z in hist if z['metric']==r['metric'] and z['quarter']<r['quarter'] and z['publication']<=r['cutoff']]
 if len(prior)<4:continue
 rms=math.sqrt(mean((z['actual']-z['prediction'])**2 for z in prior));s=max(rms,CONFIG['sd_floor']);lo=r['prediction']+ql*s;hi=r['prediction']+qh*s
 coverage.append(dict(metric=r['metric'],quarter=r['quarter'],cutoff=r['cutoff'],n=len(prior),lower=lo,upper=hi,actual=r['actual'],covered=bool(lo<=r['actual']<=hi),width=hi-lo))
save('interval_tests',coverage)
sens=[]
for name,ss in [('Main',scale),('No floor',rawscale),('50% wider',scale*1.5)]:
 for i,r in enumerate(target):
  v=points[i]+z[:,i]*ss[i];lo,hi=np.quantile(v,[.1,.9]);sens.append(dict(case=name,metric=r['metric'],p10=lo,p90=hi,near=float((abs(v-points[i])<=1).mean())))
save('sensitivity',sens)
summary=dict(historical_quarters=common,historical_scores=[r for r in scores if r['metric']=='All six measures'],target_old_mae=mean(r['old_error'] for r in comparison),target_new_mae=mean(r['new_error'] for r in comparison),target_last_mae=mean(abs(r['last']-r['actual']) for r in comparison),target_four_mae=mean(abs(r['four']-r['actual']) for r in comparison),interval_test_count=len(coverage),interval_coverage=mean(r['covered'] for r in coverage),interval_mean_width=mean(r['width'] for r in coverage),target_coverage=mean(r['covered'] for r in probs),stale_vintage_max_days=max(r['vintage_age_days'] for r in provenance),frozen_original_sha=SHA,new_unscored_sha=pre_actual_sha,limitations=['Retrospective redesign after all outcomes were seen; no untouched holdout.','Candidates and metric scope were chosen during prior development.','Archived vintages can predate the desired cutoff; company actuals use the preserved archive, not a full restatement-vintage database.','Six metrics overlap and are not a reconciled revenue model.','No advertising or promotion response parameters are invented.','Student t, 1pp scale floor and 50% correlation shrinkage remain analyst assumptions.','Marginal probabilities do not identify causes; historical coverage is based on few dependent observations.'])
save('summary',summary)
save('validation',dict(future_actual_poison_test=True,company_cutoffs_checked=True,market_vintages_checked=True,selection_uses_only_completed_quarters=True,probability_counts_reconcile=True,original_forecast_unchanged=SHA==hashlib.sha256((ROOT/'data/april24_forecast/frozen_forecast.json').read_bytes()).hexdigest()))
plt.rcParams.update({'font.size':11,'axes.spines.top':False,'axes.spines.right':False})
fig,ax=plt.subplots(figsize=(10,4.4));y=np.arange(6);ax.barh(y-.19,[r['old_error'] for r in comparison],.36,color='#B94142',label='Original forecast');ax.barh(y+.19,[r['new_error'] for r in comparison],.36,color='#267E70',label='Revised rule');ax.set_yticks(y,LABELS);ax.invert_yaxis();ax.set_xlabel('Absolute error (percentage points)');ax.set_title('April–June 2026: did the revised rule help?',loc='left',weight='bold');ax.legend(frameon=False);fig.tight_layout();fig.savefig(O/'target_errors.png',dpi=150);plt.close(fig)
fig,ax=plt.subplots(figsize=(10,4.5));
for i,r in enumerate(probs):
 ax.plot([r['p10'],r['p90']],[i,i],lw=9,color='#CAD8E6');ax.scatter(r['forecast'],i,color='#173B59',s=60,zorder=3,label='Revised forecast' if i==0 else None);ax.scatter(r['actual'],i,color='#B94142',marker='x',s=70,zorder=4,label='Actual' if i==0 else None)
ax.set_yticks(range(6),LABELS);ax.invert_yaxis();ax.set_xlabel('Growth rate (%) or pricing contribution (pp)');ax.set_title('Conditional 80% intervals around revised forecasts',loc='left',weight='bold');ax.legend(frameon=False);fig.tight_layout();fig.savefig(O/'revised_intervals.png',dpi=150);plt.close(fig)
print(json.dumps(dict(comparison=comparison,summary=summary),indent=2))
