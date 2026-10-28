"""데이터 검사: python3 tools/validate.py"""
import json,sys,os,re
try:sys.stdout.reconfigure(encoding='utf-8')
except Exception:pass
HERE=os.path.dirname(os.path.abspath(__file__))
d=json.load(open(os.path.join(HERE,'..','data.json'),encoding='utf-8'))
html=open(os.path.join(HERE,'..','index.html'),encoding='utf-8').read()
S,T,N=d['scenarios'],d['terms'],d['news'];err=[];warn=[]
LV={'입문','이론','기본','계통','사례','심화'};TG={'nuc','thermal','grid','etc','gen'}
CATS=set(re.findall(r'"([^"]+)"',re.search(r'const CATS=\[(.*?)\]',html).group(1)))-{'전체'}
ids=[s['id'] for s in S]
if len(ids)!=len(set(ids)):err.append('중복 시나리오 id')
for s in S:
  for k in('id','lv','tg','title','sub','intro','chain','steps'):
    if not s.get(k):err.append(f"{s.get('id')}: {k} 없음")
  if s.get('lv') not in LV:err.append(f"{s['id']}: lv {s.get('lv')}")
  if s.get('tg') and s['tg'] not in TG:err.append(f"{s['id']}: tg {s['tg']}")
  if not re.fullmatch(r'\d{4}-\d{2}-\d{2}',s.get('date','')):err.append(f"{s['id']}: date 형식")
  for i,q in enumerate(s['steps']):
    w=f"{s['id']}#{i+1}";t=q.get('type','mc');o=q.get('o',[])
    if t not in('mc','ox','multi','order'):err.append(w+f': type {t}')
    if len(o)<2 or len(set(o))!=len(o):err.append(w+': 보기 개수/중복')
    if t=='multi':
      if not q.get('ans') or any(not 0<=a<len(o) for a in q['ans']):err.append(w+': ans')
    elif t!='order' and not 0<=q.get('a',-1)<len(o):err.append(w+': a 범위')
    if t=='ox':
      if o!=["O 맞다","X 틀리다"]:err.append(w+': ox 보기는 ["O 맞다","X 틀리다"]')
      elif not q.get('e','').startswith('맞다' if q['a']==0 else '틀리다'):err.append(w+': ox 해설이 정답과 반대(맞다/틀리다로 시작)')
    if t=='order' and len(o)<3:err.append(w+': 순서 문항은 보기 3개 이상')
    for x in q.get('l',[]):
      if x not in T:err.append(w+f': 없는 용어 {x}')
    if t=='mc':
      W=q.get('w')
      if not W:err.append(w+': mc에 w(오답 해설) 없음')
      elif len(W)!=len(o):err.append(w+': w 길이≠보기 수')
      elif W[q['a']]!='' or any(not W[j] for j in range(len(o)) if j!=q['a']):err.append(w+': w는 정답 칸 "", 오답 칸은 설명')
      L=[len(x) for x in o]
      if L[q['a']]>max(L[:q['a']]+L[q['a']+1:])*1.5:warn.append(w+' (정답만 김)')
    if len(q.get('e',''))<60:warn.append(w+' (짧은 해설)')
for k,t in T.items():
  for f in('c','k','t','s','d'):
    if not t.get(f):err.append(f'용어 {k}: {f} 없음')
  if t.get('c') and t['c'] not in CATS:warn.append(f'용어 {k}: 분류 {t["c"]}는 용어 탭 분류에 없음')
  for x in t.get('l',[]):
    if x not in T:err.append(f'용어 {k}: 없는 관련 용어 {x}')
# index.html 안 계통도·짝 구별이 쓰는 용어
dg=html[html.find('const DGS'):html.find('const DGORDER')]+html[html.find('function nucMap'):html.find('const DGS')]
for x in set(re.findall(r'\bt:"([^"$]+)"',dg))|set(re.findall(r'data-t="([^"$]+)"',dg)):
  if x not in T:err.append(f'계통도: 없는 용어 {x}')
pm=re.search(r'const PAIRS=\[(.*?)\];',html,re.S)
for x in re.findall(r'"([^"]+)"',pm.group(1) if pm else ''):
  if x not in T:err.append(f'짝 구별: 없는 용어 {x}')
for n in N:
  if not re.match(r'https?://',n.get('src',{}).get('url','')):err.append(n.get('id','?')+': 출처 URL 없음/형식')
  if n.get('case') and n['case'] not in ids:err.append(n['id']+f': 없는 case {n["case"]}')
import collections
print(f"시나리오 {len(S)} · 문항 {sum(len(s['steps']) for s in S)} · 용어 {len(T)} · 뉴스 {len(N)}")
print('분야', dict(collections.Counter(s.get('tg') for s in S)))
print(f"경고 {len(warn)}개",*warn[:30],sep='\n  ')
if err:print('오류:',*err[:40],sep='\n  ');sys.exit(1)
print('오류 없음')
