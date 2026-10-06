"""Reconstruct the 24-Apr-2026 forecast, then score a separately supplied outcome.

Reads the preceding two-stage test outputs. No June-2026 outcome is an input to
freeze(). The original method implementation is reused without loading its archive.
"""
from pathlib import Path
import ast, csv, json, math, statistics, hashlib, sys
from datetime import datetime, timezone
from replay_releases import fit, quarterly, months, previous_month

ROOT=Path(__file__).resolve().parents[1]
P=ROOT/'data/april24_forecast'; P.mkdir(parents=True,exist_ok=True)
CUT='2026-04-24'; TARGET='2026-06-30'; mean=statistics.mean
METHODS=['YoY carry','Flat level','Recent trend','Seasonal step']
def read(path): return json.loads((ROOT/path).read_text())
def save(name,rows):
 (P/(name+'.json')).write_text(json.dumps(rows,indent=2))
 if isinstance(rows,list) and rows:
  with (P/(name+'.csv')).open('w') as f:
   w=csv.DictWriter(f,fieldnames=list(dict.fromkeys(k for r in rows for k in r)));w.writeheader();w.writerows(rows)

# Reuse the exact existing estimator, rather than silently changing its rules.
tree=ast.parse((ROOT/'src/test_two_stage.py').read_text())
fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='estimate')
namespace=dict(mean=mean,statistics=statistics,months=months,previous_month=previous_month)
exec(compile(ast.Module(body=[fn],type_ignores=[]),'existing_two_stage_estimator','exec'),namespace)
estimate=namespace['estimate']

def freeze():
 facts=read('data/driver_tests/pg_quarterly.json')
 selected=read('data/two_stage/selected_relationships.json')
 company=read('data/two_stage/company_forecasts.json')
 monthly=read('data/two_stage/monthly_forecasts.json')
 manifest=read('data/april24_forecast/market_manifest.json')
 predictions=[]; marketrows=[]; training=[]; selections=[]; inputs=[]
 for sel in selected:
  seg,metric,code=sel['segment'],sel['metric'],sel['series']
  source=next(r for r in manifest if r['series']==code)
  d={m:float(v) for m,v in list(csv.reader((P/source['file']).open()))[1:] if v not in ['', '.']}
  assert max(d)<=CUT and source['vintage']==CUT
  for m,v in sorted(d.items()):
   if not any(r['series']==code and r['month']==m for r in inputs):inputs.append(dict(series=code,month=m,level=v))
  methods=METHODS if code.startswith('CUUR') else METHODS[:3]
  past=[r for r in monthly if r['series']==code and r['stage']=='Origin' and r['observed_months']==0 and r['quarter']<TARGET and r['truth_vintage'] and r['truth_vintage']<=CUT]
  common=set.intersection(*[{(r['quarter'],r['month']) for r in past if r['method']==m} for m in methods])
  qs=sorted({q for q,m in common})[-8:]
  scores={m:mean([mean([abs(r['percentage_error']) for r in past if r['method']==m and r['quarter']==q and (r['quarter'],r['month']) in common]) for q in qs]) for m in methods}
  method=min(methods,key=lambda m:(scores[m],METHODS.index(m))) if len(qs)>=4 else 'YoY carry'
  # Closest existing backtest has zero observed target months (Origin). It is not
  # a perfect match to an April-24 post-report cutoff; disclose that timing gap.
  hist=[r for r in company if r['pair']==sel['pair'] and r['stage']=='Origin' and r['method']=='Available-history choice' and r['actual_publication']<=CUT]
  rm=lambda k: math.sqrt(mean(r[k]**2 for r in hist))
  errors={'Market model':rm('error'),'Last actual':rm('last_error'),'Four-quarter mean':rm('mean_error')}
  chosen=min(errors,key=errors.get)
  known=sorted([f for f in facts if f['segment']==seg and f['period_end']<TARGET and f['publication_date']<=CUT],key=lambda f:f['period_end'])
  agg='sum' if code=='RSHPCS' else 'mean'
  pairs=[(f,quarterly(d,f['period_end'],agg)) for f in known];pairs=[(f,x) for f,x in pairs if x is not None]
  if sel['window']=='Last eight':pairs=pairs[-8:]
  coef=fit([x for f,x in pairs],[f[metric] for f,x in pairs]);assert coef
  filled,detail=estimate(d,TARGET,method);x=quarterly(filled,TARGET,agg)
  model=coef['intercept']+coef['beta']*x;last=known[-1][metric];four=mean(f[metric] for f in known[-4:])
  prediction={'Market model':model,'Last actual':last,'Four-quarter mean':four}[chosen]
  predictions.append(dict(segment=seg,metric=metric,series=code,window=sel['window'],cutoff=CUT,target=TARGET,latest_market_month=max(d),monthly_method=method,selected_model=chosen,training_n=coef['n'],intercept=coef['intercept'],beta=coef['beta'],market_growth=x,market_model_forecast=model,last_actual=last,four_mean=four,forecast=prediction,**{k:coef[k] for k in ['sx','sy','sxx','sxy']}))
  for f,z in pairs:training.append(dict(segment=seg,metric=metric,series=code,company_quarter=f['period_end'],published=f['publication_date'],market_growth=z,company_growth=f[metric]))
  selections.append(dict(segment=seg,metric=metric,series=code,model=chosen,monthly_method=method,calibration_quarters=len(qs),calibration_last_quarter=qs[-1],backtest_quarters=len(hist),model_rmse=errors['Market model'],last_rmse=errors['Last actual'],mean_rmse=errors['Four-quarter mean'],monthly_scores=json.dumps(scores)))
  if not any(r['series']==code for r in marketrows):
   for t in detail:marketrows.append(dict(series=code,month=t['month'],method=method,prior_year=d[str(int(t['month'][:4])-1)+t['month'][4:]],forecast=t['value'],observed=t['observed'],latest_month=max(d),latest_level=d[max(d)],source_url=source['source_url']))
 assert all(r['published']<=CUT and r['company_quarter']<TARGET for r in training)
 assert not any(r['observed'] for r in marketrows)
 for n,rows in [('frozen_forecast',predictions),('training_pairs',training),('model_selection',selections),('market_forecast',marketrows),('market_inputs',inputs)]:save(n,rows)
 save('sales_reference',dict(prior_year_sales=84284,nine_month_sales=65829,prior_year_quarter_sales=20889,annual_low=.01,annual_mid=.03,annual_high=.05,description='Guidance-implied reference, not an independent revenue model'))
 save('freeze_record',dict(cutoff=CUT,target=TARGET,reconstruction_created_utc=datetime.now(timezone.utc).isoformat(),forecast_sha256=hashlib.sha256((P/'frozen_forecast.json').read_bytes()).hexdigest(),no_target_actual_in_forecast=True,zero_observed_target_months=True,selection_checkpoint='Origin: closest existing zero-target-month test, not identical post-report timing',status='Retrospective reconstruction; headline Q4 actuals were seen in source discovery, but no target actual enters estimation or selection'))
 print(json.dumps(predictions,indent=2))

def score():
 forecasts=read('data/april24_forecast/frozen_forecast.json');actuals=read('data/april24_forecast/actuals.json');rows=[]
 for r in forecasts:
  a=next(x[r['metric']] for x in actuals['segments'] if x['segment']==r['segment'])
  rows.append(dict(r,actual=a,variance_pp=a-r['forecast'],model_variance_pp=a-r['market_model_forecast'],last_variance_pp=a-r['last_actual'],mean_variance_pp=a-r['four_mean']))
 save('variance',rows)
 print(json.dumps(rows,indent=2))

if __name__=='__main__':
 if '--score' in sys.argv:score()
 else:freeze()
