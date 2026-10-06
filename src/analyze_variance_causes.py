from pathlib import Path
import json,csv,hashlib,shutil,os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT=Path(os.environ.get('PG_PROJECT_ROOT',Path(__file__).resolve().parents[1]))
P=Path(__file__).resolve().parents[1]
D=P/'data' if P.name=='pg_causes' else P/'data/variance_causes'
O=P/'outputs' if P.name=='pg_causes' else P/'outputs/variance_causes'
D.mkdir(parents=True,exist_ok=True);O.mkdir(parents=True,exist_ok=True)
def read(p):return json.loads((ROOT/p).read_text())
def save(n,d):
 (D/(n+'.json')).write_text(json.dumps(d,indent=2))
 if isinstance(d,list) and d:
  with (D/(n+'.csv')).open('w') as f:
   w=csv.DictWriter(f,fieldnames=list(d[0]));w.writeheader();w.writerows(d)
frozen=read('data/april24_forecast/frozen_forecast.json');var=read('data/april24_forecast/variance.json');hist=read('data/two_stage/company_forecasts.json');facts=read('data/driver_tests/pg_quarterly.json');diag=read('data/april24_forecast/error_diagnosis.json')
labels=['Baby / Feminine / Family volume','Beauty organic sales','Beauty volume','Beauty pricing','Fabric & Home volume','Health Care pricing']
errors=[];raw=[]
for i,r in enumerate(frozen):
 hs=[h for h in hist if h['segment']==r['segment'] and h['metric']==r['metric'] and h['series']==r['series'] and h['stage']=='Origin' and h['method']=='Available-history choice' and h['actual_publication']<='2026-04-24']
 vals={}
 for h in hs:
  pred=h[{'Market model':'prediction','Last actual':'last_actual','Four-quarter mean':'four_mean'}[r['selected_model']]]
  e=h['actual']-pred;vals[h['quarter']]=e
  raw.append(dict(metric=labels[i],quarter=h['quarter'],published=h['actual_publication'],historical_forecast=pred,actual=h['actual'],actual_minus_forecast=e,selected_method=r['selected_model']))
 errors.append(vals)
common=sorted(set.intersection(*[set(x) for x in errors]));E=np.array([[d[q] for d in errors] for q in common]);assert len(common)>=5
config=json.loads((D/'simulation_config.json').read_text())
mu=E.mean(axis=0);raw_sd=E.std(axis=0,ddof=1);sd=np.maximum(raw_sd,config['sd_floor']);corr=np.corrcoef(E,rowvar=False);shrink=config['correlation_shrinkage'];R=(1-shrink)*corr+shrink*np.eye(6)
# A deliberately explicit distribution assumption, not a fitted causal model.
# t(5) innovations have unit marginal variance after the scaling below.
N=config['draws'];seed=config['seed'];df=config['df'];assert df>2 and 0<=shrink<=1 and config['sd_floor']>=0;rng=np.random.default_rng(seed)
Z=rng.multivariate_normal(np.zeros(6),R,size=N)*np.sqrt((df-2)/rng.chisquare(df,size=N))[:,None]
point=np.array([r['forecast'] for r in frozen]);actual=np.array([r['actual'] for r in var]);resid=mu+Z*sd;draw=point+resid
cal=[];result=[]
for i,r in enumerate(frozen):
 below=(draw[:,i]<point[i]-1).mean();near=((draw[:,i]>=point[i]-1)&(draw[:,i]<=point[i]+1)).mean();above=(draw[:,i]>point[i]+1).mean()
 vals=dict(metric=labels[i],forecast=point[i],actual=actual[i],n=len(common),historical_bias=mu[i],historical_sd=raw_sd[i],used_sd=sd[i],center=point[i]+mu[i],p10=float(np.quantile(draw[:,i],.1)),median=float(np.median(draw[:,i])),p90=float(np.quantile(draw[:,i],.9)),below=float(below),near=float(near),above=float(above),prob_positive=float((draw[:,i]>0).mean()),actual_percentile=float((draw[:,i]<=actual[i]).mean()))
 assert abs(below+near+above-1)<1e-12
 result.append(vals)
 cal.append(dict(metric=labels[i],forecast=point[i],bias=mu[i],historical_sd=raw_sd[i],sd=sd[i],sd_floor=config['sd_floor'],n=len(common),df=df,shrink=shrink,method=r['selected_model']))
save('historical_errors',raw);save('common_errors',[dict(quarter=q,**{labels[i]:float(E[j,i]) for i in range(6)}) for j,q in enumerate(common)])
save('calibration',cal);save('probabilities',result)
sens=[]
for name,bias,scale in [('Main: 1pp SD floor',mu,sd),('Historical SD only',mu,raw_sd),('No bias adjustment',np.zeros(6),sd),('Wider errors (1.5x)',mu,sd*1.5)]:
 sims=point+bias+Z*scale
 for i,label in enumerate(labels):sens.append(dict(case=name,metric=label,below=float((sims[:,i]<point[i]-1).mean()),near=float((abs(sims[:,i]-point[i])<=1).mean()),above=float((sims[:,i]>point[i]+1).mean()),p10=float(np.quantile(sims[:,i],.1)),p90=float(np.quantile(sims[:,i],.9))))
save('sensitivity',sens)
joint=[]
for shrinkv in [0,.5,1]:
 rr=(1-shrinkv)*corr+shrinkv*np.eye(6);rg=np.random.default_rng(seed);zz=rg.multivariate_normal(np.zeros(6),rr,size=N)*np.sqrt((df-2)/rg.chisquare(df,size=N))[:,None];dev=mu+zz*sd
 joint.append(dict(shrinkage=shrinkv,three_or_more_below=float(((dev<-1).sum(axis=1)>=3).mean()),all_within_one=float((abs(dev)<=1).all(axis=1).mean())))
save('joint_sensitivity',joint)
# A small reproducible display sample, not a second simulation or another fitted model.
with (D/'simulation_sample.csv').open('w') as f:
 w=csv.writer(f);w.writerow(['Draw',*labels]);w.writerows([[i+1,*map(float,draw[i])] for i in range(1000)])
counts=[dict(metric=labels[i],below=int((resid[:,i]<-1).sum()),near=int((abs(resid[:,i])<=1).sum()),above=int((resid[:,i]>1).sum()),draws=N) for i in range(6)];save('counts',counts)
meta=dict(seed=seed,draws=N,distribution='Multivariate Student t',df=df,correlation_shrinkage=shrink,common_quarters=common,calibration_cutoff='2026-04-24',target='2026-06-30',historical_error_sign='actual minus forecast',formula='frozen point + historical mean error + historical SD * unit-variance correlated t innovation',scope='Six separate measures; not an additive revenue model or probabilities of causal explanations.',limitations=['Only six common historical quarters; 100000 draws do not add historical evidence.','Models were selected using this same small historical evaluation sample; optimism is possible.','Origin timing differs from the April 24 post-report timing.','Distribution and 50% correlation shrinkage are analyst assumptions, not validated parameters.','The April–June outcome is not used to calibrate the simulation; this design is retrospective.','Bias adjustment is a new sensitivity layer, not a revision to the frozen point forecasts.'],correlation=corr.tolist(),used_correlation=R.tolist(),max_monte_carlo_standard_error=float(.5/np.sqrt(N)),original_forecast_sha256=hashlib.sha256((ROOT/'data/april24_forecast/frozen_forecast.json').read_bytes()).hexdigest())
meta['minimum_sd_pp']=config['sd_floor'];meta['formula']='frozen point + historical mean error + max(historical SD, configured floor) * unit-variance correlated t innovation';meta['limitations'].append('The SD floor is an analyst risk assumption, not an estimate established by the six historical observations. The no-floor case is reported separately.')
save('simulation_method',meta)
# Quarterly financial reconciliation, all USD million; not budget differences.
fin=[dict(metric='Net sales',prior=20889,actual=21203),dict(metric='Cost of products sold',prior=10631,actual=10920),dict(metric='Gross profit',prior=10258,actual=10283),dict(metric='SG&A',prior=5903,actual=6334),dict(metric='Operating income',prior=4355,actual=3949)]
save('financials',[dict(r,change=r['actual']-r['prior'],change_pct=r['actual']/r['prior']-1) for r in fin])
assert 21203-10920-6334==3949 and 314-289-431==-406
gm=[('Productivity',160),('Net tariffs / recoveries',40),('Other / rounding',20),('Pricing',10),('Product mix',-120),('Product / pack investment',-70),('Commodities',-40)]
sg=[('Reinvestment, mainly marketing',410),('Other / rounding',20),('Productivity',-300)]
assert sum(x[1] for x in gm)==0 and sum(x[1] for x in sg)==130
save('cost_drivers',[dict(measure='Core gross margin',driver=k,basis_points=v) for k,v in gm]+[dict(measure='Core SG&A ratio',driver=k,basis_points=v) for k,v in sg])
market=[]
for code in ['PCENDC96','RSHPCS','CUUR0000SEGB02','CUUR0000SEGB']:
 r=next(x for x in frozen if x['series']==code);d=next(x for x in diag if x['series']==code)
 market.append(dict(series=code,forecast_growth=r['market_growth'],later_growth=d['later_market_growth'],difference=d['later_market_growth']-r['market_growth'],vintage='2026-08-01'))
save('market_comparison',market)
pricehist=[f for f in facts if f['segment']=='Beauty'];save('beauty_price_history',[dict(quarter=f['period_end'],pricing=f['price_contribution'],volume=f['organic_volume_growth'],organic_sales=f['organic_sales_growth']) for f in pricehist])
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'axes.spines.top':False,'axes.spines.right':False})
fig,ax=plt.subplots(figsize=(11,5.5));y=np.arange(6);ax.barh(y,[r['below']*100 for r in result],color='#C74743',label='More than 1pp below forecast');ax.barh(y,[r['near']*100 for r in result],left=[r['below']*100 for r in result],color='#CFD9E5',label='Within ±1pp');ax.barh(y,[r['above']*100 for r in result],left=[(r['below']+r['near'])*100 for r in result],color='#237C69',label='More than 1pp above forecast');
for i,r in enumerate(result):
 start=0
 for k in ['below','near','above']:
  width=r[k]*100
  if width>6:ax.text(start+width/2,i,f'{width:.0f}%',ha='center',va='center',color='white' if k!='near' else '#193650',fontweight='bold')
  start+=width
ax.set_yticks(y,labels);ax.invert_yaxis();ax.set_xlim(0,100);ax.set_xlabel('Conditional probability (%)');ax.set_title('P&G: possible April–June outcomes',loc='left',fontweight='bold',pad=16);ax.legend(loc='upper center',bbox_to_anchor=(.5,-.14),ncol=1,frameon=False);fig.text(.02,.01,'100,000 draws; six historical quarters. Historical-bias case. These are model assumptions, not causal probabilities.',fontsize=9);fig.tight_layout(rect=[0,.06,1,1]);fig.savefig(O/'probability_bands.png',dpi=160);plt.close(fig)
fig,axes=plt.subplots(1,2,figsize=(12,4.7));ax=axes[0];ax.bar(['Sales gain','COGS increase','SG&A increase','Operating profit'],[314,-289,-431,-406],color=['#237C69','#C74743','#C74743','#193650']);ax.axhline(0,color='#8794A2',lw=.7);ax.set_ylabel('Change versus Apr–Jun 2025 ($m)');ax.set_title('Higher sales did not mean higher profit',loc='left');ax.tick_params(axis='x',labelrotation=18);ax.set_ylim(-510,360)
for i,v in enumerate([314,-289,-431,-406]):ax.text(i,v+(10 if v>0 else -20),f'{v:+,}',ha='center',va='bottom' if v>0 else 'top')
ax=axes[1];i=3;ax.hist(draw[:,i],bins=np.linspace(-1,8,70),density=True,color='#CBD9E8',edgecolor='white');ax.axvline(point[i],color='#17324F',lw=2,label=f'Frozen forecast {point[i]:.2f}pp');ax.axvline(actual[i],color='#C74743',lw=2,label='Actual 1pp');ax.set_title('Beauty pricing: the actual was in the lower tail',loc='left');ax.set_xlabel('Contribution to sales growth (pp)');ax.legend(frameon=False);fig.tight_layout();fig.savefig(O/'profit_and_pricing.png',dpi=160);plt.close(fig)
save('validation',dict(financial_reconciliation=True,cost_driver_sums=True,probabilities_sum_to_one=True,no_target_actual_in_calibration=True,common_history_n=len(common),draws=N,seed=seed))
print(json.dumps(dict(results=result,joint=joint,quarters=common),indent=2))
