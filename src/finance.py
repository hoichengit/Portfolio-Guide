"""Cutoff-gated SEC facts; transparent five-year unlevered cash-flow model."""
from pathlib import Path
import json,datetime,csv,sys
R=Path(__file__).resolve().parents[1];CUTOFF='2026-08-31';PROV=[]
TAGS={
'revenue':['RevenueFromContractWithCustomerExcludingAssessedTax','Revenues','SalesRevenueNet'],
'cogs':['CostOfRevenue','CostOfGoodsAndServicesSold'], 'sga':['SellingGeneralAndAdministrativeExpense'],
'ebit':['OperatingIncomeLoss'],'pretax':['IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest','IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments'],
'net_income':['NetIncomeLoss'],'tax':['IncomeTaxExpenseBenefit'],'cfo':['NetCashProvidedByUsedInOperatingActivities'],
'capex':['PaymentsToAcquirePropertyPlantAndEquipment'],'da':['DepreciationDepletionAndAmortization','DepreciationDepletionAndAmortizationPropertyPlantAndEquipment','DepreciationAmortizationAndAccretionNet','Depreciation'],
'sbc':['ShareBasedCompensation'],'dividends':['PaymentsOfDividends','PaymentsOfDividendsCommonStock'],
'cash':['CashAndCashEquivalentsAtCarryingValue','CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents'],
'ar':['AccountsReceivableNetCurrent'],'inventory':['InventoryNet','InventoryFinishedGoodsNetOfReserves'],
'ap':['AccountsPayableCurrent'],'assets':['Assets'],'equity':['StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest','StockholdersEquity'],
'debt_current':['LongTermDebtCurrent','LongTermDebtAndCapitalLeaseObligationsCurrent'],'debt_long':['LongTermDebtNoncurrent','LongTermDebt'],
'ppe':['PropertyPlantAndEquipmentNet'],'shares':['WeightedAverageNumberOfDilutedSharesOutstanding'],
'eps':['EarningsPerShareDiluted'],'interest':['InterestExpenseNonOperating','InterestExpenseNonoperating','InterestAndDebtExpense']}
INSTANT={'cash','ar','inventory','ap','assets','equity','debt_current','debt_long','ppe'}
def facts(co):return json.loads((R/f'raw_data/{co}_companyfacts.json').read_text())['facts']
def pick(co,key,end,start=None,required=True):
 f=facts(co);tags=TAGS.get(key,[key]);unit='shares' if key=='shares' else 'USD/shares' if key=='eps' else 'USD'
 for tag in tags:
  vals=[x for x in f['us-gaap'].get(tag,{}).get('units',{}).get(unit,[]) if x.get('end')==end and x.get('filed','9999')<=CUTOFF and x.get('form') in ['10-K','10-Q'] and (start is None and 'start' not in x or x.get('start')==start)]
  if vals:
   x=sorted(vals,key=lambda x:(x['filed'],x.get('accn','')))[-1];PROV.append(dict(company=co,metric=key,tag=tag,unit=unit,**x));return x['val']/(1 if unit=='USD/shares' else 1e6)
 if required:raise ValueError((co,key,end,start))
 return None

def history(co):
 out=[];month=6 if co=='PG' else 5
 for y in range(2022,2027):
  end=f'{y}-{month:02}-'+('30' if co=='PG' else '31');start=f'{y-1}-{month+1:02}-01';d={'year':y,'end':end}
  for k in TAGS:
   d[k]=pick(co,k,end,None if k in INSTANT else start,required=k not in ['ebit','interest','da','debt_current'])
  if d['ebit'] is None:d['ebit']=d['revenue']-d['cogs']-d['sga']
  if co=='PG':d['debt_current']=pick(co,'DebtCurrent',end)
  if d['da'] is None:raise ValueError(('missing DA',co,y))
  d['consolidated_ni']=d['pretax']-d['tax'];d['liabilities']=d['assets']-d['equity'];d['debt']=d['debt_current']+d['debt_long'];d['gross_margin']=1-d['cogs']/d['revenue'];d['ebit_margin']=d['ebit']/d['revenue'];d['fcf']=d['cfo']-d['capex'];out.append(d)
 return out

CONFIG={
'PG':{'name':'Procter & Gamble','price':145.12,'common_shares':2324.43306,'conversion_shares':68.3,'dilution_shares':20.5,'other_cash':0,'nci':230,'beta':.65,'debt_cost':.045,'growth':[[.01]*5,[.03]*5,[.05]*5],'margin':[[.215]*5,[.227,.23,.232,.234,.235],[.235,.24,.245,.25,.25]],'capex':.05,'terminal_g':.025,'tax':.21},
'NKE':{'name':'NIKE','price':39.06,'common_shares':1483.498703,'conversion_shares':0,'dilution_shares':1.2,'other_cash':1464,'nci':0,'beta':1.15,'debt_cost':.05,'growth':[[-.03,0,.01,.02,.02],[.02,.04,.05,.04,.03],[.05,.07,.07,.06,.05]],'margin':[[.075,.075,.08,.085,.09],[.085,.095,.105,.115,.12],[.095,.11,.125,.135,.14]],'capex':.02,'terminal_g':.025,'tax':.21}}
def model(h,c,case=1,wacc=None,g=None,growth_override=None):
 b=h[-1];shares=c['common_shares']+c['conversion_shares']+c['dilution_shares'];mc=c['price']*c['common_shares'];debt=b['debt'];w=wacc or ((.0475+c['beta']*.045)*mc+debt*c['debt_cost']*(1-c['tax']))/(mc+debt);tg=c['terminal_g'] if g is None else g
 prevrev=b['revenue'];prevwc=b['ar']+b['inventory']-b['ap'];cash=b['cash'];equity=b['equity'];assets_other=b['assets']-cash-b['ar']-b['inventory'];otherliab=b['liabilities']-debt-b['ap'];rows=[]
 dso=b['ar']/b['revenue']*365;dio=b['inventory']/b['cogs']*365;dpo=b['ap']/b['cogs']*365;dar=b['da']/b['revenue'];sbcr=b['sbc']/b['revenue'];payout=b['dividends']/b['consolidated_ni'];elapsed=(datetime.date.fromisoformat(CUTOFF)-datetime.date.fromisoformat(b['end'])).days/365
 for k in range(5):
  growth=c['growth'][case][k] if growth_override is None else growth_override;r=prevrev*(1+growth);gm=b['gross_margin']+(c['margin'][case][k]-b['ebit_margin']);cogs=r*(1-gm);sga=r*gm-r*c['margin'][case][k];ebit=r-cogs-sga;interest=debt*c['debt_cost'];ni=(ebit-interest)*(1-c['tax']);da=r*dar;sbc=r*sbcr;capex=r*c['capex'];ar=r*dso/365;inv=cogs*dio/365;ap=cogs*dpo/365;wc=ar+inv-ap;dwc=wc-prevwc;cfo=ni+da+sbc-dwc;div=max(0,ni*payout);cash+=cfo-capex-div;assets_other+=capex-da;equity+=ni+sbc-div;assets=cash+ar+inv+assets_other;liab=debt+ap+otherliab;fcff=ebit*(1-c['tax'])+da-capex-dwc;t=k+1-elapsed;fraction=1-elapsed if k==0 else 1;pv=fcff*fraction/(1+w)**t
  rows.append(dict(year=2027+k,revenue=r,growth=growth,cogs=cogs,sga=sga,ebit=ebit,interest=interest,net_income=ni,da=da,sbc=sbc,capex=capex,ar=ar,inventory=inv,ap=ap,nwc=wc,delta_nwc=dwc,cfo=cfo,dividends=div,cash=cash,other_assets=assets_other,assets=assets,liabilities=liab,equity=equity,balance_check=assets-liab-equity,fcff=fcff,discount_years=t,stub_fraction=fraction,pv=pv,margin=ebit/r));prevrev=r;prevwc=wc
 tv=rows[-1]['fcff']*(1+tg)/(w-tg);pvt=tv/(1+w)**rows[-1]['discount_years'];ev=sum(x['pv'] for x in rows)+pvt;eq=ev+b['cash']+c['other_cash']-debt-c['nci'];return dict(case=['Bear','Base','Bull'][case],wacc=w,terminal_g=tg,rows=rows,ev=ev,equity_value=eq,price=eq/shares,upside=eq/shares/c['price']-1,terminal_share=pvt/ev,shares=shares)
if __name__=='__main__':
 all={}
 for co,c in CONFIG.items():
  if len(sys.argv)>1 and co not in sys.argv[1:]:continue
  h=history(co);runs=[model(h,c,k) for k in range(3)];base=runs[1];sens=[{'wacc':w,'terminal_g':g,'price':model(h,c,1,w,g)['price']} for w in [base['wacc']-.01,base['wacc']-.005,base['wacc'],base['wacc']+.005,base['wacc']+.01] for g in [.015,.02,.025,.03,.035] if w>g]
  lo,hi=-.2,.3
  for _ in range(80):
   mid=(lo+hi)/2
   if model(h,c,1,growth_override=mid)['price']<c['price']:lo=mid
   else:hi=mid
  reverse=(lo+hi)/2
  for run in runs:assert max(abs(x['balance_check']) for x in run['rows'])<1e-6
  all[co]={'config':c,'history':h,'scenarios':runs,'sensitivity':sens,'reverse_growth':reverse,'reverse_price_check':model(h,c,1,growth_override=reverse)['price']}
  print(co,[(r['case'],round(r['price'],2)) for r in runs], 'reverse growth',reverse)
 (R/'processed_data/valuations.json').write_text(json.dumps(all,indent=2));(R/'processed_data/sec_provenance.json').write_text(json.dumps(PROV,indent=2))
