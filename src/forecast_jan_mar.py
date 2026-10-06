"""Retrospective, release-aligned rolling forecasts. Jan–Mar actual is scoring-only.

Rules are specified before this run, but after the analyst saw prior results.
This is development evidence, never an untouched prospective test.
"""
from pathlib import Path
import json,csv,hashlib,statistics,math,ast
from datetime import date,timedelta
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from replay_releases import quarterly, fit, months, previous_month

ROOT=Path(__file__).resolve().parents[1]; D=ROOT/'data/jan_mar_replay'; O=ROOT/'outputs/jan_mar_replay'
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
CONFIG=dict(start='2023-06-30',target='2026-03-31',cutoff='2026-01-22',min_selection=4,score_window=8,bias_window=4,bias_weight=.5,challenger_improvement=.10,draws=100000,seed=20260424,df=5,sd_floor=1.,correlation_shrinkage=.5)
METHODS=['Last actual','Four-quarter mean','Recent two mean','Prior-year quarter','Market level','Anchored market change','Half last + market','Market bias correction']
FROZEN=[{'segment': 'Baby, Feminine & Family Care', 'metric': 'organic_volume_growth', 'series': 'PCENDC96'}, {'segment': 'Beauty', 'metric': 'organic_sales_growth', 'series': 'RSHPCS'}, {'segment': 'Beauty', 'metric': 'organic_volume_growth', 'series': 'PCENDC96'}, {'segment': 'Beauty', 'metric': 'price_contribution', 'series': 'CUUR0000SEGB02'}, {'segment': 'Fabric & Home Care', 'metric': 'organic_volume_growth', 'series': 'PCENDC96'}, {'segment': 'Health Care', 'metric': 'price_contribution', 'series': 'CUUR0000SEGB'}]
LABELS=['Baby / Feminine / Family volume','Beauty organic sales','Beauty volume','Beauty pricing','Fabric & Home volume','Health Care pricing']
# Correct one release-date error without changing archived source files.
for f in FACTS:
 if f['period_end']=='2025-12-31':f['publication_date']='2026-01-22'
CALENDAR={f['period_end']:f['publication_date'] for f in FACTS}
STAGE='Initial'

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
   cut=CONFIG['cutoff'] if q==CONFIG['target'] else (previous[-1]['publication_date'] if STAGE=='Initial' else (date.fromisoformat(CALENDAR[q])-timedelta(days=1)).isoformat())
   known=[f for f in previous if f['publication_date']<=cut]
   if len(known)<8:continue
   v=version(code,cut)
   if v is None:continue
   d={m:z for m,z in v['data'].items() if m<=cut};est=estimate(d,q,'YoY carry')
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


allrecords=[];allprov=[];alltrain=[];targets=[];checks=[];histories={}
for stage,cut in [('Initial','2026-01-22'),('Pre-release','2026-04-23')]:
 STAGE=stage;CONFIG['cutoff']=cut
 known=[f for f in FACTS if f['period_end']<CONFIG['target']]
 records,prov,train=replay(known)
 poisoned=known+[dict(f,**{k:99999 for k in ['organic_sales_growth','organic_volume_growth','price_contribution']}) for f in FACTS if f['period_end']>=CONFIG['target']]
 again,_,_=replay(poisoned)
 assert records==again
 # A deliberately extreme market vintage after every cutoff must be ignored.
 for code in {x['series'] for x in FROZEN}:
  E[(code,'2099-01-01')]=dict(series=code,vintage='2099-01-01',data={'2098-12-01':99999},path='poison-test-only')
 market_again,_,_=replay(known)
 assert records==market_again
 for code in {x['series'] for x in FROZEN}:del E[(code,'2099-01-01')]
 for r in records:r['stage']=stage
 for r in prov:r['stage']=stage
 for r in train:r['stage']=stage
 allrecords+=records;allprov+=prov;alltrain+=train
 targets += [r for r in records if r['quarter']==CONFIG['target']]
 histories[stage]=[r for r in records if r['quarter']<CONFIG['target'] and r['eligible']]
 checks.append(dict(stage=stage,future_actual_poison_test=True,future_market_poison_test=True))
save('unscored_forecasts',targets)
forecast_sha=hashlib.sha256((D/'unscored_forecasts.json').read_bytes()).hexdigest()
# Outcomes only enter scoring after both forecasts have been saved.
actual=[next(f[s['metric']] for f in FACTS if f['segment']==s['segment'] and f['period_end']==CONFIG['target']) for s in FROZEN]
comparison=[];probs=[];intervals=[];summaries=[];calibration=[]
for stage in ['Initial','Pre-release']:
 tt=[r for r in targets if r['stage']==stage];hist=histories[stage]
 common=sorted(set.intersection(*[{r['quarter'] for r in hist if r['metric']==label} for label in LABELS]))
 errors=np.array([[next(r['actual']-r['prediction'] for r in hist if r['quarter']==q and r['metric']==label) for label in LABELS] for q in common])
 R=np.nan_to_num(np.corrcoef(errors,rowvar=False));np.fill_diagonal(R,1);R=.5*R+.5*np.eye(6)
 scale=np.maximum(np.sqrt((errors**2).mean(axis=0)),1.)
 rng=np.random.default_rng(CONFIG['seed']);z=rng.multivariate_normal(np.zeros(6),R,100000)*np.sqrt(3/rng.chisquare(5,100000))[:,None]
 for i,r in enumerate(tt):
  comparison.append(dict(stage=stage,metric=r['metric'],cutoff=r['cutoff'],forecast=r['prediction'],actual=actual[i],error=r['prediction']-actual[i],absolute_error=abs(r['prediction']-actual[i]),method=r['selected_method'],last=r['predictions']['Last actual'],four=r['predictions']['Four-quarter mean']))
  v=r['prediction']+z[:,i]*scale[i];lo,hi=np.quantile(v,[.1,.9])
  probs.append(dict(stage=stage,metric=r['metric'],forecast=r['prediction'],p10=lo,p90=hi,scale=scale[i],below=float((v<r['prediction']-1).mean()),near=float((abs(v-r['prediction'])<=1).mean()),above=float((v>r['prediction']+1).mean()),actual=actual[i],covered=bool(lo<=actual[i]<=hi),calibration_quarters=len(common)))
  assert abs(sum(probs[-1][k] for k in ['below','near','above'])-1)<1e-10
 for j,q in enumerate(common):calibration.append(dict(stage=stage,quarter=q,**dict(zip(LABELS,errors[j].tolist()))))
 unit=np.random.default_rng(CONFIG['seed']).standard_t(5,100000)*np.sqrt(3/5);ql,qh=np.quantile(unit,[.1,.9])
 for r in hist:
  prior=[x for x in hist if x['metric']==r['metric'] and x['quarter']<r['quarter'] and x['publication']<=r['cutoff']]
  if len(prior)<4:continue
  sd=max(1.,math.sqrt(mean((x['actual']-x['prediction'])**2 for x in prior)))
  lo=r['prediction']+ql*sd;hi=r['prediction']+qh*sd
  intervals.append(dict(stage=stage,quarter=r['quarter'],metric=r['metric'],lower=lo,upper=hi,actual=r['actual'],covered=bool(lo<=r['actual']<=hi)))
 cc=[x for x in comparison if x['stage']==stage];ii=[x for x in intervals if x['stage']==stage]
 summaries.append(dict(stage=stage,target_mae=mean(x['absolute_error'] for x in cc),last_mae=mean(abs(x['last']-x['actual']) for x in cc),four_mae=mean(abs(x['four']-x['actual']) for x in cc),historical_mae=mean(abs(x['prediction']-x['actual']) for x in hist),historical_quarters=common,interval_tests=len(ii),interval_coverage=mean(x['covered'] for x in ii),target_covered=sum(x['covered'] for x in probs if x['stage']==stage)))
save('comparison',comparison);save('probabilities',probs);save('summary',summaries);save('release_inputs',allprov);save('training_pairs',alltrain);save('rolling_forecasts',allrecords);save('interval_tests',intervals);save('calibration_errors',calibration)
save('validation',dict(tests=checks,unscored_forecast_sha256=forecast_sha,company_dates_before_cutoffs=all(r['latest_company_publication']<=r['cutoff'] for r in allprov),market_dates_before_cutoffs=all(r['vintage']<=r['cutoff'] and r['latest_market_month']<=r['cutoff'] for r in allprov),target_excluded_from_training=all(r['company_quarter']<CONFIG['target'] for r in alltrain),target_actual=actual,retrospective_design=True))
save('config',dict(CONFIG,snapshots={'Initial':'2026-01-22','Pre-release':'2026-04-23'},date_correction={'quarter':'2025-12-31','old':'2026-01-23','correct':'2026-01-22'},rules_unchanged_from_previous_development=True))
fig,ax=plt.subplots(figsize=(10,4.5))
for i in range(6):
 rr=[r for r in comparison if r['metric']==LABELS[i]]
 ax.scatter(rr[0]['forecast'],i-.13,color='#183A55',label='22 Jan forecast' if i==0 else None)
 ax.scatter(rr[1]['forecast'],i+.13,color='#198570',label='23 Apr update' if i==0 else None)
 ax.scatter(actual[i],i,marker='x',s=65,color='#B52B2D',label='24 Apr actual' if i==0 else None)
ax.set_yticks(range(6),LABELS);ax.invert_yaxis();ax.set_xlabel('Growth (%) / pricing contribution (pp)');ax.set_title('Jan–Mar 2026: pre-release reconstruction');ax.legend();fig.tight_layout();fig.savefig(O/'comparison.png',dpi=160)
print(json.dumps(dict(summary=summaries,comparison=comparison,target_inputs=[x for x in allprov if x['quarter']==CONFIG['target']]),indent=2))
