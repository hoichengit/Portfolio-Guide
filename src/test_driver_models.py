"""Fixed challenger models, chronological bias correction and common-sample scores."""
from pathlib import Path
import json,csv,math,statistics,copy
import numpy as np
from replay_releases import quarterly,estimate_market,prior_quarter
from extend_driver_inputs import save,P,ROOT
mean=statistics.mean
FINE={'Beauty':'CUUR0000SEGB02','Grooming':None,'Health Care':None,'Fabric & Home Care':None,'Baby, Feminine & Family Care':None}
PAIRS=[(s,'price_contribution','CUUR0000SEGB',f) for s,f in FINE.items()]+[(s,'organic_volume_growth','PCENDC96',None) for s in FINE]+[(s,'organic_sales_growth','RSHPCS',None) for s in ['Beauty','Health Care']]
def offset(q,n):
 for _ in range(n):q=prior_quarter(q)
 return q
def regress(x,y):
 if len(y)<(12 if x and len(x[0])==2 else 8):return None
 a=np.array([[1]+r for r in x],float);b=np.array(y,float)
 if np.linalg.matrix_rank(a)<a.shape[1]:return None
 c=np.linalg.lstsq(a,b,rcond=None)[0].tolist()
 return c
def main():
 facts=json.loads((P/'pg_quarterly.json').read_text()); cp=json.loads((P/'checkpoints.json').read_text())
 attempted=json.loads((P/'market_manifest.json').read_text());manifests=[r for r in attempted if r['status']=='downloaded']
 assert len(manifests)==4*len({c['cutoff'] for c in cp}), 'Resolve missing required vintages before modelling'
 market={(r['series'],r['vintage']):{d:float(v) for d,v in list(csv.reader((P/r['file']).open()))[1:] if v not in ['', '.']} for r in manifests}
 records=[];training=[];fits=[]
 for seg,metric,code,fine in PAIRS:
  ff=sorted([r for r in facts if r['segment']==seg],key=lambda r:r['period_end']); fm={r['period_end']:r for r in ff};pair=seg+' / '+metric
  for c in cp:
   q,cut,stage=c['target_quarter'],c['cutoff'],c['stage'];known=[r for r in ff if r['period_end']<q and r['publication_date']<=cut]
   assert len(known)>=8
   h=1
   while offset(q,h)!=known[-1]['period_end']:h+=1
   broad=market[code,cut];fine_data=market[fine,cut] if fine else None;agg='sum' if code=='RSHPCS' else 'mean'
   values={'Last actual':known[-1][metric],'Four-quarter mean':mean(r[metric] for r in known[-4:])}
   fitids={};observed=sum(m['observed'] for m in estimate_market(broad,q,agg)[1])
   for model in ['Broad market','Broad lag 1','Broad rolling 8','Own history']+(['Product price','Product lag 1','Own + product'] if fine else []):
    def features(t,target=False):
     if model=='Own history':
      k=offset(t,h);return [fm[k][metric]] if k in fm else None
     data=fine_data if model.startswith('Product') or model=='Own + product' else broad
     if 'lag 1' in model:x=quarterly(data,prior_quarter(t),'mean' if fine_data is data else agg)
     elif target:
      est=estimate_market(data,t,'mean' if fine_data is data else agg);x=est[0] if est else None
     else:x=quarterly(data,t,'mean' if fine_data is data else agg)
     if x is None:return None
     if model=='Own + product':
      k=offset(t,h);return [x,fm[k][metric]] if k in fm else None
     return [x]
    tr=[(r,features(r['period_end'])) for r in known];tr=[(r,x) for r,x in tr if x is not None]
    if model=='Broad rolling 8':tr=tr[-8:]
    tx=features(q,True);coef=regress([x for r,x in tr],[r[metric] for r,x in tr]);pred=sum(a*b for a,b in zip(coef,[1]+tx)) if coef and tx else None
    values[model]=pred
    if pred is None:continue
    fid=len(fits)+1;fitids[model]=fid
    xs=[x[0] for r,x in tr];zs=[x[1] if len(x)>1 else 0 for r,x in tr];ys=[r[metric] for r,x in tr]
    fits.append(dict(fit_id=fid,pair=pair,model=model,quarter=q,stage=stage,cutoff=cut,n=len(tr),sum_x=sum(xs),sum_z=sum(zs),sum_y=sum(ys),sum_xx=sum(v*v for v in xs),sum_zz=sum(v*v for v in zs),sum_xz=sum(a*b for a,b in zip(xs,zs)),sum_xy=sum(a*b for a,b in zip(xs,ys)),sum_zy=sum(a*b for a,b in zip(zs,ys)),intercept=coef[0],beta_x=coef[1],beta_z=coef[2] if len(coef)>2 else 0,target_x=tx[0],target_z=tx[1] if len(tx)>1 else 0,prediction=pred))
    for r,x in tr:training.append(dict(fit_id=fid,company_quarter=r['period_end'],publication_date=r['publication_date'],x=x[0],z=x[1] if len(x)>1 else 0,y=r[metric]))
   for model,v in values.items():
    if v is None:continue
    records.append(dict(id=len(records)+1,pair=pair,segment=seg,metric=metric,quarter=q,stage=stage,cutoff=cut,model=model,prediction=v,fit_id=fitids.get(model,0),calibration_ids='',calibration_bias=0,correction_weight=0,base_id=0,latest_company=known[-1]['period_end'],months_observed=observed))
 # Corrections use prior frozen forecasts, with actuals published by today's cutoff.
 original=list(records)
 for r in original:
  if r['model']!='Broad market':continue
  prior=[z for z in original if z['pair']==r['pair'] and z['model']=='Broad market' and z['stage']==r['stage'] and z['quarter']<r['quarter'] and next(f['publication_date'] for f in facts if f['segment']==r['segment'] and f['period_end']==z['quarter'])<=r['cutoff']]
  prior=sorted(prior,key=lambda z:z['quarter'])[-4:]
  if len(prior)<4:continue
  bias=mean(z['prediction']-next(f[r['metric']] for f in facts if f['segment']==r['segment'] and f['period_end']==z['quarter']) for z in prior)
  for weight,label in [(1,'Bias correction'),(.5,'Half correction')]:
   records.append(dict(r,id=len(records)+1,model=label,prediction=r['prediction']-weight*bias,fit_id=0,base_id=r['id'],calibration_ids=','.join(str(z['id']) for z in prior),calibration_bias=bias,correction_weight=weight))
 # Outcomes are attached only for scoring, never read by the forecast fit above.
 for r in records:
  f=next(f for f in facts if f['segment']==r['segment'] and f['period_end']==r['quarter']);r.update(actual=f[r['metric']],actual_publication=f['publication_date'],error=r['prediction']-f[r['metric']])
 save('forecasts',records);save('training',training);save('fits',fits)
 scores=[]
 for pair in sorted({r['pair'] for r in records}):
  for stage in ['Origin','Prior report','Pre-earnings']:
   rr=[r for r in records if r['pair']==pair and r['stage']==stage]
   for model in sorted({r['model'] for r in rr}):
    for sample,start in [('All available','2023'),('Recent eight','2024-06-30')]:
     rs=[r for r in rr if r['model']==model and r['quarter']>=start]
     if not rs:continue
     def bench(m):return [next(z['error'] for z in rr if z['quarter']==r['quarter'] and z['model']==m) for r in rs]
     es=[r['error'] for r in rs];rm=lambda x:math.sqrt(mean(e*e for e in x))
     scores.append(dict(pair=pair,stage=stage,model=model,sample=sample,quarters=len(rs),rmse=rm(es),mae=mean(abs(e) for e in es),bias=mean(es),last_rmse=rm(bench('Last actual')),broad_rmse=rm(bench('Broad market')),wins_vs_broad=sum(abs(a)<abs(b) for a,b in zip(es,bench('Broad market'))),forecast_ids=','.join(str(r['id']) for r in rs)))
 save('scores',scores)
 # Audit timing plus an outcome-isolation check on fitted forecasts.
 assert all(r['cutoff']<r['actual_publication'] for r in records)
 assert all(t['publication_date']<=fits[t['fit_id']-1]['cutoff'] and t['company_quarter']<fits[t['fit_id']-1]['quarter'] for t in training)
 for r in records:
  for k in r['calibration_ids'].split(','):
   if k:assert records[int(k)-1]['actual_publication']<=r['cutoff'] and records[int(k)-1]['quarter']<r['quarter']
 validation=dict(history_quarters=len({r['period_end'] for r in facts}),test_quarters=len({r['quarter'] for r in records}),stages=3,series=len({r['series'] for r in manifests}),frozen_downloads=len(manifests),forecasts=len(records),fits=len(fits),all_training_available=True,all_calibration_outcomes_available=True,target_actuals_not_in_fit=True,bias_rule='Last four completed same-stage Broad market forecast errors; minimum four; full and half correction fixed before run',selection='Retrospective development, not an untouched holdout; recent eight also inspected previously',target_2026_q2_actuals_used=False)
 (P/'validation.json').write_text(json.dumps(validation,indent=2));print(json.dumps(validation))
 print(json.dumps([r for r in scores if r['pair'].startswith(('Grooming / price','Beauty / price')) and r['stage']=='Pre-earnings' and r['sample']=='Recent eight'],indent=2))
if __name__=='__main__':main()
