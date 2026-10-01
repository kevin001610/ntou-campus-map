"""Read the user's four-column XLSX without editing it; preserve every source row."""
import argparse,zipfile,xml.etree.ElementTree as E,json,re,hashlib
from pathlib import Path
from collections import Counter
from decimal import Decimal, InvalidOperation
parser=argparse.ArgumentParser();parser.add_argument('xlsx');parser.add_argument('--date',required=True);parser.add_argument('--edition',default='更新課表');parser.add_argument('--coverage',choices=['partial','provided-complete'],default='partial');parser.add_argument('--exclude-location',action='append',default=[]);args=parser.parse_args()
root=Path(__file__).resolve().parents[1];ns={'m':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
codes=json.loads((root/'dist/data/codes.json').read_text());by_code={c['code']:c for c in codes};prefixes=sorted(by_code,key=len,reverse=True)
with zipfile.ZipFile(args.xlsx) as z:
 shared=[]
 if 'xl/sharedStrings.xml' in z.namelist():shared=[''.join(n.text or '' for n in si.findall('.//m:t',ns)) for si in E.fromstring(z.read('xl/sharedStrings.xml'))]
 sheet=E.fromstring(z.read('xl/worksheets/sheet1.xml'));records=[];seen=Counter();excluded_rows=[]
 for row in sheet.findall('.//m:sheetData/m:row',ns):
  values={}
  for c in row:
   v=c.find('m:v',ns);value=v.text if v is not None else ''
   if c.get('t')=='s':value=shared[int(value)]
   elif c.get('t')=='inlineStr':value=''.join(n.text or '' for n in c.findall('.//m:t',ns))
   values[re.sub(r'\d','',c.get('r'))]=value.strip()
  if row.get('r')=='1':
   assert [values.get(k) for k in 'ABCD']==['課程名稱','上課時間','上課地點','授課老師'];continue
  if not any(values.values()):continue
  name,time,room,teacher=[values.get(k,'') for k in 'ABCD']
  if room.upper() in {x.upper() for x in args.exclude_location}:
   excluded_rows.append(int(row.get('r')));continue
  assert all([name,time,room,teacher]),f'Incomplete source row {row.get("r")}'
  try:
   numeric_time=Decimal(time)
   assert numeric_time.is_finite() and numeric_time==numeric_time.to_integral_value(),f'Invalid time {time}'
   time=str(int(numeric_time))
  except InvalidOperation:
   raise ValueError(f'Unsupported time code {time}')
  assert time.isdigit() and len(time)%3==0,f'Unsupported time code {time}'
  chunks=[time[i:i+3] for i in range(0,len(time),3)]
  assert len({p[0] for p in chunks})==1 and all(1<=int(p[0])<=7 and 1<=int(p[1:])<=14 for p in chunks),f'Ambiguous time {time}'
  code=next((c for c in prefixes if room.upper().startswith(c)),None)
  known=code is not None
  code=code or room.upper()
  suffix=room[len(code):] if known else ''
  if known:assert suffix
  mapping=by_code.get(code,{'locationIds':[]})
  key=hashlib.sha256('\x1f'.join([name,time,room,teacher]).encode()).hexdigest()[:16];seen[key]+=1
  records.append({'recordId':f'import-{key}-{seen[key]}','courseId':None,'semester':None,'name':name,'teacher':teacher,'department':None,'buildingCode':code,'room':suffix,'rawRoom':room,'day':int(chunks[0][0]),'periods':'、'.join(str(int(p[1:])) for p in chunks),'timeCode':time,'locationId':mapping['locationIds'][0] if len(mapping['locationIds'])==1 else None,'locationStatus':'mapped' if len(mapping['locationIds'])==1 else ('group' if mapping['locationIds'] else 'unmapped'),'source':{'file':Path(args.xlsx).name,'sheet':'工作表1','row':int(row.get('r'))}})
 data={'semester':None,'semesterLabel':'本學期','updatedAt':args.date,'edition':args.edition,'coverage':args.coverage,'recordCount':len(records),'excludedSourceRows':excluded_rows,'sourceFile':Path(args.xlsx).name,'courses':records}
 (root/'dist/data/courses.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps({'records':len(records),'buildingCounts':dict(Counter(c['buildingCode'] for c in records)),'preciselyLocated':sum(c['locationId'] is not None for c in records),'unknownLocations':dict(Counter(c['rawRoom'] for c in records if c['locationStatus']=='unmapped')),'pendingWing':sum(c['buildingCode']=='MAF' and not c['locationId'] for c in records)},ensure_ascii=False))
