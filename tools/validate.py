"""데이터 검사: python3 tools/validate.py"""
import json,sys,os
d=json.load(open(os.path.join(os.path.dirname(__file__),'..','data.json'),encoding='utf-8'))
S,T,N=d['scenarios'],d['terms'],d['news'];err=[];warn=[]
LV={'입문','이론','기본','계통','사례','심화'};TG={'nuc','thermal','grid','etc','gen'}
ids=[s['id'] for s in S]
if len(ids)!=len(set(ids)):err.append('중복 시나리오 id')
for s in S:
  for k in('id','lv','title','intro','steps'):
    if not s.get(k):err.append(f"{s.get('id')}: {k} 없음")
  if s.get('lv') not in LV:err.append(f"{s['id']}: lv {s.get('lv')}")
  if s.get('tg') and s['tg'] not in TG:err.append(f"{s['id']}: tg {s['tg']}")
  for i,q in enumerate(s['steps']):
    w=f"{s['id']}#{i+1}";t=q.get('type','mc');o=q.get('o',[])
    if len(o)<2 or len(set(o))!=len(o):err.append(w+': 보기 개수/중복')
    if t=='multi':
      if not q.get('ans') or any(not 0<=a<len(o) for a in q['ans']):err.append(w+': ans')
    elif t!='order' and not 0<=q.get('a',-1)<len(o):err.append(w+': a 범위')
    for x in q.get('l',[]):
      if x not in T:err.append(w+f': 없는 용어 {x}')
    if 'w' in q and len(q['w'])!=len(o):err.append(w+': w 길이≠보기 수')
    if len(q.get('e',''))<60:warn.append(w)
    if t=='mc':
      L=[len(x) for x in o]
      if L[q['a']]>max(L[:q['a']]+L[q['a']+1:])*1.5:warn.append(w+' (정답만 김)')
for n in N:
  if not n.get('src',{}).get('url'):err.append(n['id']+': 출처 없음')
print(f"시나리오 {len(S)} · 문항 {sum(len(s['steps']) for s in S)} · 용어 {len(T)} · 뉴스 {len(N)}")
print(f"경고 {len(warn)}개(짧은 해설/정답 길이 티)")
if err:print('오류:',*err[:30],sep='\n  ');sys.exit(1)
print('오류 없음')
