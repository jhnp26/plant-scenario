"""새 시나리오·용어 묶음을 data.json에 합친다: python3 tools/add_content.py batch.json
batch.json = {"terms":{키:{...}}, "scenarios":[{...}], "news":[{...}]}  (셋 다 선택)
- 시나리오는 같은 tg의 마지막 시나리오 뒤에 끼워 넣는다(목록에서 분야끼리 모이게).
- 이미 있는 id/키는 덮어쓰지 않고 멈춘다.
- 합친 뒤 index.html의 data.json?v= 숫자를 지금 시각으로 올린다.
- 끝나면 validate.py를 돌려 확인한다."""
import json,sys,os,re,datetime,subprocess
for _s in(sys.stdout,sys.stderr):
  try:_s.reconfigure(encoding='utf-8')
  except Exception:pass
HERE=os.path.dirname(os.path.abspath(__file__));ROOT=os.path.join(HERE,'..')
DJ=os.path.join(ROOT,'data.json');IX=os.path.join(ROOT,'index.html')
if len(sys.argv)!=2:sys.exit(__doc__)
d=json.load(open(DJ,encoding='utf-8'));n=json.load(open(sys.argv[1],encoding='utf-8'))
dup=[k for k in n.get('terms',{}) if k in d['terms']]
ids={s['id'] for s in d['scenarios']};dup+=[s['id'] for s in n.get('scenarios',[]) if s['id'] in ids]
nids={x['id'] for x in d['news']};dup+=[x['id'] for x in n.get('news',[]) if x['id'] in nids]
if dup:sys.exit('이미 있는 id/키: '+', '.join(dup))
d['terms'].update(n.get('terms',{}))
S=d['scenarios']
for s in n.get('scenarios',[]):
  same=[i for i,x in enumerate(S) if x.get('tg')==s.get('tg')]
  S.insert((same[-1]+1) if same else len(S),s)
d['news'].extend(n.get('news',[]))
open(DJ,'w',encoding='utf-8',newline='\n').write(json.dumps(d,ensure_ascii=False,separators=(',',':')))
v=(datetime.datetime.utcnow()+datetime.timedelta(hours=9)).strftime('%Y%m%d%H%M')
h=open(IX,encoding='utf-8').read();h2=re.sub(r'data\.json\?v=\d+',f'data.json?v={v}',h)
open(IX,'w',encoding='utf-8',newline='\n').write(h2)
print(f"추가: 시나리오 {len(n.get('scenarios',[]))} · 용어 {len(n.get('terms',{}))} · 뉴스 {len(n.get('news',[]))} · 캐시 버전 {v}")
sys.exit(subprocess.call([sys.executable,os.path.join(HERE,'validate.py')]))
