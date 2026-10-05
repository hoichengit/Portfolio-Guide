import fs from 'node:fs/promises';
import {Workbook,SpreadsheetFile} from '@oai/artifact-tool';
const root=decodeURIComponent(new URL('../',import.meta.url).pathname);
const dir=root+'outputs/april_guidance_sample';
const w=Workbook.create(),s=w.worksheets.add('Quarter sales target');
s.showGridLines=false;
s.getRange('A1:F36').format.font={name:'Arial',size:12,color:'#16324F'};
s.getRange('A1:F36').format.rowHeight=25;
s.getRange('A1:A36').format.columnWidth=3;
s.getRange('B1:B36').format.columnWidth=40;
s.getRange('C1:E36').format.columnWidth=20;
s.getRange('F1:F36').format.columnWidth=3;
s.getRange('B2').values=[['P&G | Sales needed in April–June']];
s.getRange('B2').format.font={size:18,bold:true};
s.getRange('B3').values=[['Information available: 24 Apr 2026 | Amounts in USD millions']];
s.getRange('B5:E5').values=[['Company guidance reference','Low','Midpoint','High']];
s.getRange('B5:E5').format={fill:'#16324F',font:{color:'#FFFFFF',bold:true},rowHeight:30};
s.getRange('B6:E6').values=[['FY2026 sales growth',.01,null,.05]];
s.getRange('D6').formulas=[['=(C6+E6)/2']];
s.getRange('C6:E6').setNumberFormat('0.0%;(0.0%);0.0%');
s.getRange('B8:B11').values=[['Implied FY2026 sales'],['Less: nine-month actual sales'],['Sales needed: Apr–Jun 2026'],['Growth vs Apr–Jun 2025']];
for(const col of ['C','D','E']){
 s.getRange(col+'8').formulas=[['=$C$17*(1+'+col+'6)']];
 s.getRange(col+'9').formulas=[['=$C$23']];
 s.getRange(col+'10').formulas=[['='+col+'8-'+col+'9']];
 s.getRange(col+'11').formulas=[['='+col+'10/$C$18-1']];
}
s.getRange('C8:E10').setNumberFormat('"$"#,##0.00;("$"#,##0.00);"$"0.00');
s.getRange('C11:E11').setNumberFormat('0.00%;(0.00%);0.00%');
s.getRange('B10:E11').format.fill='#EDF3FA';s.getRange('B10:E11').format.font.bold=true;
s.getRange('C11:E11').conditionalFormats.add('cellIs',{operator:'lessThan',formula:0,format:{font:{color:'#BA2525'}}});
s.getRange('C11:E11').conditionalFormats.add('cellIs',{operator:'greaterThan',formula:0,format:{font:{color:'#21734B'}}});
s.getRange('B13').values=[['These are implied company targets, not independent scenarios.']];
s.getRange('B14').values=[['The midpoint is arithmetic; it is not a company-endorsed base case.']];
s.getRange('B16:D16').values=[['Reported sales inputs','USD millions','Source']];
s.getRange('B16:D16').format={fill:'#DFE7EF',font:{bold:true}};
s.getRange('B17:D18').values=[['FY2025 sales',84284,'S1'],['Apr–Jun 2025 sales',20889,'S1']];
s.getRange('B20:D22').values=[['Jul–Sep 2025 sales',22386,'S2'],['Oct–Dec 2025 sales',22208,'S3'],['Jan–Mar 2026 sales',21235,'S4']];
s.getRange('B23').values=[['Nine-month sales subtotal']];s.getRange('C23').formulas=[['=SUM(C20:C22)']];
s.getRange('C17:C23').setNumberFormat('"$"#,##0;("$"#,##0);"$"0');
s.getRange('C17:C22').format.font.color='#0000FF';s.getRange('C23').format.font.color='#000000';
s.getRange('B23:D23').format.fill='#EDF3FA';
s.getRange('B25').values=[['Check: full-year reconciliation']];
for(const col of ['C','D','E'])s.getRange(col+'25').formulas=[['='+col+'9+'+col+'10-'+col+'8']];
s.getRange('C25:E25').setNumberFormat('0.00;(0.00);0.00');
s.getRange('B27').values=[['Sources: net sales rows; S4 also supplies the annual growth limits.']];
const sources=[
 ['S1 | 29 Jul 2025','https://www.pginvestor.com/news/news-details/2025/PG-Announces-Fourth-Quarter-and-Fiscal-Year-2025-Results/default.aspx'],
 ['S2 | 24 Oct 2025','https://www.pginvestor.com/news/news-details/2025/PG-Announces-Fiscal-Year-2026-First-Quarter-Results/default.aspx'],
 ['S3 | 22 Jan 2026','https://www.pginvestor.com/news/news-details/2026/PG-Announces-Fiscal-Year-2026-Second-Quarter-Results/default.aspx'],
 ['S4 | 24 Apr 2026','https://www.pginvestor.com/news/news-details/2026/PG-Announces-Fiscal-Year-2026-Third-Quarter-Results/default.aspx']
];
sources.forEach((v,i)=>{s.getRange('B'+(28+i*2)).values=[[v[0]]];s.getRange('B'+(29+i*2)).values=[[v[1]]];s.getRange('B'+(29+i*2)).format.font.size=10;});
// Confirm a change to the annual growth input flows through the same calculation.
s.getRange('C6').values=[[0.02]];w.recalculate();
if(Math.abs(s.getRange('C10').values[0][0]-20140.68)>1e-7)throw new Error('Input-change check failed');
s.getRange('C6').values=[[0.01]];w.recalculate();
console.log((await w.inspect({kind:'table',range:"'Quarter sales target'!B5:E11",include:'values,formulas',tableMaxRows:7,tableMaxCols:4})).ndjson);
console.log((await w.inspect({kind:'match',searchTerm:'#REF!|#DIV/0!|#VALUE!|#NAME\\?|#NUM!',options:{useRegex:true,maxResults:10}})).ndjson);
for(const [name,range] of [['quarter_target','B2:E14'],['quarter_inputs','B16:E25']]){
 const img=await w.render({sheetName:s.name,range,scale:2});await fs.writeFile(dir+'/'+name+'_preview.png',new Uint8Array(await img.arrayBuffer()));
}
await (await SpreadsheetFile.exportXlsx(w)).save(dir+'/PG_2_Quarter_Sales_Target.xlsx');
await fs.writeFile(dir+'/quarter_target_checks.json',JSON.stringify({as_of:'2026-04-24',nine_month_sales:65829,prior_year_quarter_sales:20889,implied_quarter_sales:s.getRange('C10:E10').values[0],implied_growth:s.getRange('C11:E11').values[0],reconciliation:s.getRange('C25:E25').values[0],input_change_check:'passed'},null,2));
