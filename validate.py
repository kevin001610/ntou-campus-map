import json,re
from pathlib import Path
from html.parser import HTMLParser
root=Path(__file__).parent/'dist'
places=json.loads((root/'data/places.json').read_text()); codes=json.loads((root/'data/codes.json').read_text())
assert len(places)==70 and {p['id'] for p in places}==set(range(1,71))
assert len(codes)==40 and len({c['code'] for c in codes})==40
for p in places:
 assert 0<=p['x']<=1806 and 0<=p['y']<=785
 assert len(p['polygon'].split())>=3
 for xy in p['polygon'].split():
  x,y=map(float,xy.split(',')); assert 0<=x<=1806 and 0<=y<=785
 for code in p['codes']: assert p['id'] in next(c for c in codes if c['code']==code)['locationIds']
for c in codes:
 for i in c['locationIds']: assert c['code'] in places[i-1]['codes']
code={c['code']:c for c in codes}
assert code['EE1']['locationIds']==[62] and code['EE2']['locationIds']==[63]
assert code['CC3']['locationIds']==code['MEB']['locationIds']==[8]
assert code['MAF']['locationIds']==[38,39,41]
assert code['HRE']['locationIds']==code['MZ-']['locationIds']==[]
assert code['CE-']['locationIds']==[61]
data=json.loads((root/'data/courses.json').read_text());courses=data['courses']
assert len(courses)==data['recordCount']
assert len({c['recordId'] for c in courses})==len(courses)
for c in courses:
 assert c['name'] and c['teacher'] and c['buildingCode']
 if c['buildingCode'] not in code:
  assert c['locationStatus']=='unmapped' and c['locationId'] is None and c['rawRoom']==c['buildingCode']
 assert c['rawRoom']==c['buildingCode']+c['room']
 assert len(c['timeCode'])%3==0 and c['day'] in range(1,8)
 if c['locationId'] is not None:assert c['locationId'] in code[c['buildingCode']]['locationIds']
 elif len(code.get(c['buildingCode'],{'locationIds':[]})['locationIds'])==1:raise AssertionError('Missed precise mapping')
class CheckHTML(HTMLParser):
 def __init__(self):super().__init__();self.ids=set()
 def handle_starttag(self,tag,attrs):
  d=dict(attrs)
  if 'id' in d:
   assert d['id'] not in self.ids;self.ids.add(d['id'])
  for key in ('src','href'):
   v=d.get(key,'')
   if v and not v.startswith(('data:','#','http','./')):assert (root/v).is_file(),v
p=CheckHTML();p.feed((root/'index.html').read_text())
js=(root/'app.js').read_text()
for i in re.findall(r"\$\('#([A-Za-z0-9]+)'\)",js):
 assert i in p.ids or f'id="{i}"' in js,i
print('PASS: all 70 locations, 40 codes, reciprocal mappings, ambiguous codes, course records, HTML IDs and local assets.')
