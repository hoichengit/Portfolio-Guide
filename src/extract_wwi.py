"""Read the official BACPAC native BCP records; preserve values and validate boundaries.
Analysis runs in SQLite for portability; the original SQL Server archive is retained.
"""
from pathlib import Path
import zipfile,xml.etree.ElementTree as E,struct,json,datetime,csv,sqlite3
from decimal import Decimal
R=Path(__file__).resolve().parents[1];OUT=R/'raw_data/wwi';OUT.mkdir(exist_ok=True)
z=zipfile.ZipFile(R/'raw_data/WideWorldImporters-Standard.bacpac');root=E.fromstring(z.read('model.xml'));ns={'m':root.tag.split('}')[0][1:]}
tables=['Sales.InvoiceLines','Sales.Invoices','Sales.CustomerTransactions','Sales.Customers','Sales.Orders','Sales.OrderLines','Purchasing.SupplierTransactions','Purchasing.Suppliers','Purchasing.PurchaseOrders','Purchasing.PurchaseOrderLines','Warehouse.StockItems','Warehouse.StockItemHoldings','Warehouse.StockItemTransactions','Application.TransactionTypes']
db=sqlite3.connect(R/'processed_data/wwi.sqlite');schema={};qa=[]
def prop(e,n,default=None):
 a=e.find('./m:Property[@Name="'+n+'"]',ns);return a.get('Value',default) if a is not None else default
class Reader:
 def __init__(self,b):self.b=b;self.p=0
 def take(self,n):
  assert 0<=n<=len(self.b)-self.p,(self.p,n,len(self.b));v=self.b[self.p:self.p+n];self.p+=n;return v
 def integer(self,n,signed=False):return int.from_bytes(self.take(n),'little',signed=signed)
 def val(self,c):
  typ=c['type'];nullable=c['nullable'];size={'int':4,'bigint':8,'smallint':2,'tinyint':1,'bit':1,'float':8,'date':3,'datetime2':8,'datetime':8}.get(typ)
  if typ in ['decimal','numeric']:
   n=self.integer(1)
   if n in (0,255):return None
   b=self.take(n);assert n==19,(typ,n);precision,scale,sign=b[:3];assert scale==c['scale']
   return str(Decimal(int.from_bytes(b[3:],'little'))*(1 if sign else -1)/(10**scale))
  if typ in ['nvarchar','varchar','varbinary','geography']:
   prefix=8 if c['max'] or typ=='geography' else 2
   n=self.integer(prefix,True)
   if n==-1:return None
   b=self.take(n)
   return b.decode('utf-16le' if typ=='nvarchar' else 'cp1252') if typ in ['nvarchar','varchar'] else b.hex()
  if size:
   if nullable or typ=='bit':
    n=self.integer(1)
    if n in (0,255):return None
    assert n==size,(typ,n,size,self.p)
   b=self.take(size)
   if typ in ['int','bigint','smallint','tinyint','bit']:return int.from_bytes(b,'little',signed=typ not in ['tinyint','bit'])
   if typ=='float':return struct.unpack('<d',b)[0]
   if typ=='date':return (datetime.date(1,1,1)+datetime.timedelta(days=int.from_bytes(b,'little'))).isoformat()
   if typ=='datetime2':
    date=datetime.date(1,1,1)+datetime.timedelta(days=int.from_bytes(b[5:],'little'));t=int.from_bytes(b[:5],'little')/10**c['scale'];return f'{date}T{int(t//3600):02}:{int(t%3600//60):02}:{t%60:010.7f}'
  raise ValueError(c)
for table in tables:
 target='['+table.replace('.','].[')+']';e=root.find('.//m:Element[@Type="SqlTable"][@Name="'+target+'"]',ns)
 cols=[]
 for c in e.findall('./m:Relationship[@Name="Columns"]/m:Entry/m:Element',ns):
  if c.get('Type')!='SqlSimpleColumn':continue
  t=c.find('./m:Relationship[@Name="TypeSpecifier"]/m:Entry/m:Element',ns)
  typ=t.find('.//m:References[@ExternalSource="BuiltIns"]',ns).get('Name').split('.')[-1].strip('[]')
  cols.append(dict(name=c.get('Name').split('.')[-1].strip('[]'),type=typ,nullable=prop(c,'IsNullable')!='False',scale=int(prop(t,'Scale','7' if typ=='datetime2' else '0')),max=prop(t,'IsMax')=='True'))
 schema[table]=cols;rows=[]
 for f in sorted(n for n in z.namelist() if n.startswith('Data/'+table+'/')):
  r=Reader(z.read(f))
  while r.p<len(r.b):
   start=r.p
   try:row=[r.val(c) for c in cols]
   except Exception as ex:raise RuntimeError((table,f,len(rows),start,cols[len(locals().get('row',[])):],ex))
   rows.append(row)
  assert r.p==len(r.b)
 name=table.replace('.','_');db.execute(f'DROP TABLE IF EXISTS "{name}"')
 types=['INTEGER' if c['type'] in ['int','bigint','smallint','tinyint','bit'] else 'NUMERIC' if c['type'] in ['decimal','numeric','float'] else 'TEXT' for c in cols]
 db.execute(f'CREATE TABLE "{name}" ('+', '.join('"'+c['name']+'" '+t for c,t in zip(cols,types))+')')
 db.executemany(f'INSERT INTO "{name}" VALUES ('+','.join('?' for c in cols)+')',rows);db.commit()
 with (OUT/(name+'.csv')).open('w') as f:
  w=csv.writer(f);w.writerow([c['name'] for c in cols]);w.writerows(rows)
 qa.append(dict(table=table,rows=len(rows),columns=len(cols),complete_stream_decode=True));print(table,len(rows),rows[0][:4],flush=True)
(OUT/'schema.json').write_text(json.dumps(schema,indent=2));(R/'qa/wwi_extraction.json').write_text(json.dumps(qa,indent=2))
