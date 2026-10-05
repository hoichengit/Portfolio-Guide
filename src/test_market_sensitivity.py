"""Exploratory associations, not causal elasticities or trading signals.

No April-June 2026 company actuals are loaded. Monthly levels are aggregated
before calculating quarterly year-on-year growth. Incomplete quarters are omitted.
"""
from pathlib import Path
import csv,json,statistics,math,calendar
from rebuild_history import save, SEGMENTS
P=Path(__file__).resolve().parents[1]/'data/history_rebuild'
mean=statistics.mean

def fit(x,y):
    xm,ym=mean(x),mean(y); ss=sum((a-xm)**2 for a in x)
    if ss<1e-12:raise ValueError('No predictor variation')
    b=sum((a-xm)*(c-ym) for a,c in zip(x,y))/ss;a=ym-b*xm
    errors=[c-a-b*v for v,c in zip(x,y)]
    r2=1-sum(e*e for e in errors)/sum((v-ym)**2 for v in y) if len(set(y))>1 else 0
    return a,b,r2

def rmse(x):return math.sqrt(mean([v*v for v in x]))

def main():
    financial=json.loads((P/'pg_quarterly.json').read_text())
    manifests=[x for x in json.loads((P/'market_manifest.json').read_text()) if x['status']=='downloaded']
    monthly=[]; quarterly=[]
    for m in manifests:
        data=list(csv.reader((P/m['file']).open()))[1:]; groups={}
        for date,value in data:
            if value in ['', '.']:continue
            value=float(value); y,mo=int(date[:4]),int(date[5:7]); qm=((mo-1)//3+1)*3
            end=f'{y}-{qm:02d}-{calendar.monthrange(y,qm)[1]}'
            groups.setdefault(end,[]).append(value)
            monthly.append(dict(series=m['series'],vintage=m['vintage'],month=date,value=value,unit=m['unit'],source_url=m['url']))
        levels={d:sum(v) if m['aggregation']=='sum' else mean(v) for d,v in groups.items() if len(v)==3}
        for date,level in sorted(levels.items()):
            previous=str(int(date[:4])-1)+date[4:]
            if previous not in levels:continue
            quarterly.append(dict(series=m['series'],vintage=m['vintage'],period_end=date,level=level,prior_year_level=levels[previous],growth_yoy=100*(level/levels[previous]-1),aggregation=m['aggregation'],months=3))
    save('market_monthly',monthly);save('market_quarterly',quarterly)
    matches=[]; tests=[]
    # Predefined diagnostic pairs. US channel turnover is not a worldwide product market.
    pairs=[(s,'organic_volume_growth','PCENDC96') for s in SEGMENTS[:5]]
    pairs += [(s,'price_contribution','CUUR0000SEGB') for s in ['Beauty','Grooming']]
    pairs += [(s,'organic_sales_growth','RSHPCS') for s in ['Beauty','Health Care']]
    for vintage in ['2026-04-24','2026-05-15']:
        for seg,metric,series in pairs:
            market={r['period_end']:r['growth_yoy'] for r in quarterly if r['series']==series and r['vintage']==vintage}
            rs=sorted([r for r in financial if r['segment']==seg and r['period_end'] in market],key=lambda r:r['period_end'])
            x=[market[r['period_end']] for r in rs];y=[r[metric] for r in rs]
            a,b,r2=fit(x,y); n=len(x)
            # Leave-one-quarter-out coefficient range: diagnostic, not a forecast score.
            bs=[fit(x[:i]+x[i+1:],y[:i]+y[i+1:])[1] for i in range(n)]
            # Expanding window holdout uses the selected vintage throughout. It is
            # deliberately labelled a same-vintage diagnostic, not real-time backtest.
            errors=[]; naive=[]
            for i in range(8,n):
                ai,bi,_=fit(x[:i],y[:i]);errors.append(y[i]-ai-bi*x[i]);naive.append(y[i]-mean(y[max(0,i-4):i]))
            for i,r in enumerate(rs):matches.append(dict(segment=seg,company_metric=metric,market_series=series,vintage=vintage,period_end=r['period_end'],market_growth=x[i],company_growth=y[i],fitted=a+b*x[i],residual=y[i]-a-b*x[i]))
            tests.append(dict(segment=seg,company_metric=metric,market_series=series,vintage=vintage,n=n,intercept=a,beta=b,r_squared=r2,loo_beta_min=min(bs),loo_beta_max=max(bs),holdouts=len(errors),diagnostic_rmse=rmse(errors),trailing4_rmse=rmse(naive),forecast_approved=False,reason='US-only proxy vs global segment; category/channel mismatch; same-vintage diagnostic, not a real-time forecast test'))
    save('matched_quarters',matches);save('sensitivity_tests',tests)
    # A simple transparent benchmark, not the final economically adjusted forecast.
    # Fixed trailing-four-quarter reported growth; benchmark skill tested vs zero growth.
    benchmarks=[]; backtests=[]
    for seg in SEGMENTS[:5]:
        rs=sorted([r for r in financial if r['segment']==seg],key=lambda r:r['period_end'])
        errors=[]; naive=[]
        for i in range(8,len(rs)):
            pred=mean([r['reported_sales_growth'] for r in rs[i-4:i]])
            actual=rs[i]['reported_sales_growth'];err=actual-pred;errors.append(err);naive.append(actual)
            backtests.append(dict(segment=seg,period_end=rs[i]['period_end'],predicted_growth=pred,reported_growth=actual,error_pp=err,zero_growth_error_pp=actual))
        targetbase=next(r['net_sales'] for r in rs if r['period_end']=='2025-06-30')
        growth=mean([r['reported_sales_growth'] for r in rs[-4:]])
        benchmarks.append(dict(segment=seg,prior_year_sales=targetbase,trailing4_growth=growth,benchmark_sales=targetbase*(1+growth/100),holdouts=len(errors),trailing4_rmse=rmse(errors),zero_growth_rmse=rmse(naive),status='Reference benchmark; not a validated final scenario'))
    save('segment_benchmarks',benchmarks);save('benchmark_backtests',backtests)
    events=[]
    for series in sorted(set(m['series'] for m in manifests)):
        a={r['month']:r['value'] for r in monthly if r['series']==series and r['vintage']=='2026-04-24'}
        b={r['month']:r['value'] for r in monthly if r['series']==series and r['vintage']=='2026-05-15'}
        newest=max(b);previous=f'{newest[:4]}-{int(newest[5:7])-1:02d}-01'
        events.append(dict(series=series,april_last_month=max(a),may_last_month=newest,latest_value=b[newest],monthly_change_pct=100*(b[newest]/b[previous]-1) if previous in b else None,new_observation_months=', '.join(sorted(set(b)-set(a))),revised_prior_months=sum(abs(b[d]-v)>1e-9 for d,v in a.items() if d in b),decision='Refresh evidence; do not apply an unvalidated global sales coefficient'))
    save('release_updates',events)
    summary=dict(financial_quarters=17,company_rows=len(financial),monthly_observations=len(monthly),matched_rows=len(matches),diagnostic_tests=len(tests),approved_market_coefficients=0,quantitative_peers=0,peer_reason='P&G-first model. No peer coefficient is used; single-quarter peer anecdotes are excluded from quantitative adjustment.',target_actuals_used=False,quarter_aggregation='Sum monthly flows; average SAAR levels and indices; require 3 observations before quarterly YoY.',diagnostic_limit='Two cutoff vintages are preserved. Historical expanding-window market tests do not replay each past release vintage.',benchmark_segment_sales=sum(x['benchmark_sales'] for x in benchmarks),corporate_prior_year_sales=274)
    (P/'results.json').write_text(json.dumps(summary,indent=2))
    print(json.dumps(summary,indent=2));print(json.dumps(tests[9:],indent=2))

if __name__=='__main__':main()
