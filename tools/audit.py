"""전체 화면 점검: 모든 탭·계통도(버튼·빠른 설정)·용어·복습 모드를 돌며 JS 오류와 390px 가로 넘침을 찾는다.
python3 tools/audit.py  (test.py와 같이 playwright 필요, 실DB는 건드리지 않음)"""
import asyncio,sys,os,threading,http.server,functools
from playwright.async_api import async_playwright
try:sys.stdout.reconfigure(encoding='utf-8')
except Exception:pass
ROOT=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..')
class H(http.server.SimpleHTTPRequestHandler):
  def log_message(self,*a):pass
srv=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(H,directory=ROOT))
threading.Thread(target=srv.serve_forever,daemon=True).start();URL=f'http://127.0.0.1:{srv.server_port}/index.html'
async def main():
  async with async_playwright() as p:
    b=await p.chromium.launch();pg=await b.new_page(viewport={'width':390,'height':844})
    errs=[];pg.on('pageerror',lambda e:errs.append(str(e)));pg.on('console',lambda m:m.type=='error' and errs.append('console:'+m.text))
    await pg.route('**/config.js',lambda r:r.fulfill(body='',content_type='text/javascript'))
    await pg.goto(URL);await pg.wait_for_timeout(1200);await pg.evaluate('D.pref={co:["all"],at:1};close()')
    wide=[]
    async def chk(tag):
      w=await pg.evaluate('document.documentElement.scrollWidth')
      if w>390:
        el=await pg.evaluate('''[...document.querySelectorAll("*")].filter(e=>e.getBoundingClientRect().right>392).slice(0,3).map(e=>e.tagName+"."+e.className+":"+(e.textContent||"").slice(0,30))''')
        wide.append((tag,w,el))
    for t in ['home','scn','review','map','terms','news','wrong','rank']:
      await pg.evaluate(f'go("{t}")');await chk(t)
    dgs=await pg.evaluate('DGORDER')
    for dg in dgs:
      await pg.evaluate(f'DG="{dg}";go("map")');await chk('map:'+dg)
      if dg!='nuc':
        presets=await pg.evaluate(f'Object.keys(DGS["{dg}"].P)')
        for pr in presets:
          await pg.evaluate(f'dgPreset("{dg}","{pr}");mapTab()');await chk(f'map:{dg}:{pr}')
        ids=await pg.evaluate(f'DGS["{dg}"].N.filter(n=>n.k==="src"||n.k==="cb").map(n=>n.id)')
        for i in ids:
          await pg.evaluate(f'{{const s=dgState("{dg}");s["{i}"]=s["{i}"]?0:1;mapTab()}}')
        await chk(f'map:{dg}:toggled')
      boxes=await pg.query_selector_all('.map .box')
      if boxes:
        await boxes[0].click();opened=await pg.evaluate('!!document.querySelector(".sheet")')
        if not opened:errs.append(f'map {dg}: box click opened no sheet')
        await pg.evaluate('close()')
    # nuc map buttons
    await pg.evaluate('DG="nuc";go("map")')
    n=len(await pg.query_selector_all('[data-m],[data-preset]'))
    for j in range(n):
      await (await pg.query_selector_all('[data-m],[data-preset]'))[j].click()
    await chk('map:nuc:clicked')
    keys=await pg.evaluate('Object.keys(T)')
    for k in keys:
      await pg.evaluate(f'sheet({repr(k)})');await chk('term:'+k)
    await pg.evaluate('close()')
    for tm in ['dict','cards']:
      await pg.evaluate(f'termMode="{tm}";card=null;go("terms")');await chk('terms:'+tm)
    cats=await pg.evaluate('CATS')
    for c in cats:
      await pg.evaluate(f'termMode="dict";termCat={repr(c)};termsTab()');await chk('cat:'+c)
    # review modes
    for kind,expr in [('pair','run({kind:"pair",title:"x",items:pairItems(10),end:()=>endBasic("x","review")})'),('quick','run({kind:"quick",title:"x",items:quickItems(),end:()=>endBasic("x","review")})')]:
      for rep in range(3):
        await pg.evaluate(expr)
        while await pg.evaluate('!!R'):
          o=await pg.query_selector('.opt:not([disabled])')
          if not o:break
          t=await pg.evaluate('(R.items[R.i].type||"mc")')
          if t=='order':
            for x in await pg.query_selector_all('[data-ord]'):await x.click()
          elif t=='multi':
            await o.click();await pg.click('#multiOk')
          else:await o.click()
          await chk(kind);await pg.click('#next')
    # news answer
    await pg.evaluate('go("news")')
    nq=await pg.query_selector('[data-nq]')
    if nq:await nq.click()
    await chk('news-answered')
    # wrong answers path + wrong tab
    await pg.evaluate('startScn(SCN[5].id)')
    while await pg.evaluate('!!R'):
      t=await pg.evaluate('(R.items[R.i].type||"mc")')
      if t=='order':
        for x in reversed(await pg.query_selector_all('[data-ord]')):await x.click()
      elif t=='multi':
        await (await pg.query_selector('[data-mk]')).click();await pg.click('#multiOk')
      else:
        await pg.evaluate('(()=>{const k=R.order.findIndex(o=>!o.ok);document.querySelector(`[data-k="${k}"]`).click()})()')
      await pg.click('#next')
    await chk('scn-end');await pg.evaluate('go("wrong")');await chk('wrong-filled');await pg.evaluate('go("review")');await chk('review-filled')
    await pg.evaluate('startReview()');await chk('review-run')
    print('JS 오류:',errs or '없음');print('가로 넘침:',wide or '없음')
    await b.close()
    if errs or wide:raise SystemExit(1)
asyncio.run(main())
