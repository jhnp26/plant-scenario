"""전체 시나리오 자동 풀이 테스트: python3 tools/test.py  (pip install playwright && playwright install chromium 필요)"""
import asyncio,os,threading,http.server,functools
from playwright.async_api import async_playwright
ROOT=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..')
class H(http.server.SimpleHTTPRequestHandler):
  def log_message(self,*a):pass
srv=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(H,directory=ROOT))
threading.Thread(target=srv.serve_forever,daemon=True).start();URL=f'http://127.0.0.1:{srv.server_port}/index.html'
async def main():
  async with async_playwright() as p:
    b=await p.chromium.launch();pg=await b.new_page(viewport={'width':390,'height':844})
    errs=[];pg.on('pageerror',lambda e:errs.append(str(e)))
    await pg.route('**/config.js',lambda r:r.fulfill(body='',content_type='text/javascript'))  # 오프라인 모드(실DB 안 건드림)
    await pg.goto(URL);await pg.wait_for_timeout(1500);await pg.evaluate('D.pref={co:["all"],at:1};close()')
    sw=await pg.evaluate('document.documentElement.scrollWidth')
    data=await pg.evaluate('SCN.map(s=>({id:s.id,items:scnItems(s).map(x=>({t:x.type||"mc",o:x.o,a:x.a,ans:x.ans}))}))')
    probs=[]
    for s in data:
      await pg.evaluate(f'startScn("{s["id"]}")')
      for k,it in enumerate(s['items']):
        opts=await pg.query_selector_all('.opt');texts=[(await o.inner_text()).strip() for o in opts]
        if it['t']=='order':
          for line in it['o']:
            i=[j for j,t in enumerate(texts) if t.endswith(line)][0];await opts[i].click()
        elif it['t']=='multi':
          for j in it['ans']:await opts[texts.index(it['o'][j])].click()
          await pg.click('#multiOk')
        else:await opts[texts.index(it['o'][it['a']])].click()
        if not await pg.query_selector('.res.r'):probs.append((s['id'],k))
        await pg.click('#next')
    print(len(data),'개 시나리오 · 문제',probs or '없음','· JS 오류',errs or '없음','· 가로폭',sw)
    await b.close()
    if probs or errs or sw>390:raise SystemExit(1)
asyncio.run(main())
