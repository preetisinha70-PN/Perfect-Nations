"""Temporary (10 Nov 2026): why the Mexico blueprint globe shows only the gold map on the live site.
Opens the live page in a real Chrome window (phone and laptop), as a first-time visitor, and records:
the served globe script and its settings, data-globe, console errors, every Earth picture request with its
answer and headers, whether the browser can paint each picture on a canvas, WebGL, and a screenshot."""
import asyncio, json, re, sys, time
from playwright.async_api import async_playwright

PATHS = sys.argv[1:] or ['/blueprints/mexico/']
PHONE_UA = 'Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Mobile Safari/537.36'
STATE = """async () => {
  const g = document.querySelector('.bpx-globe');
  const out = {};
  out.found = !!g;
  if (g) {
    out.dataGlobe = g.getAttribute('data-globe'); out.dataReady = g.getAttribute('data-ready'); out.cls = g.className;
    out.children = [...g.children].map(c => ({tag: c.tagName, cls: c.getAttribute('class'), w: c.width || c.clientWidth, h: c.height || c.clientHeight, op: getComputedStyle(c).opacity}));
    out.box = [g.clientWidth, g.clientHeight];
  }
  const html = document.documentElement.outerHTML;
  out.live = (html.match(/pn-live: [^>]*?-->/g) || []).slice(0, 6);
  const scripts = [...document.scripts];
  out.scripts = scripts.length;
  const gs = scripts.filter(s => (s.textContent || '').indexOf('pnGlobe') >= 0);
  out.globeScripts = gs.map(s => ({type: s.type, len: s.textContent.length, attrs: [...s.attributes].map(a => a.name + '=' + a.value.slice(0, 80)), head: s.textContent.slice(0, 200)}));
  const tex = html.match(/"tex":\\{[^}]*\\}/);
  out.tex = tex ? tex[0] : null;
  out.metaCSP = [...document.querySelectorAll('meta[http-equiv]')].map(m => m.getAttribute('http-equiv') + ': ' + m.content);
  const t = document.createElement('canvas');
  out.webgl = !!(t.getContext('webgl') || t.getContext('experimental-webgl'));
  out.dpr = window.devicePixelRatio; out.vw = innerWidth;
  /* try each Earth address the way globe.js does, and paint it on a canvas */
  let urls = [];
  try { const j = JSON.parse(tex[0].slice(6)); urls = [...j.lg, ...j.sm]; } catch (e) { out.texErr = String(e); }
  out.imgTests = [];
  for (const u of urls) {
    const r = await new Promise(res => {
      const im = new Image(); im.crossOrigin = 'anonymous'; const t0 = performance.now();
      const done = (ok, why) => {
        let paint = null;
        if (ok) { try { const c = document.createElement('canvas'); c.width = 8; c.height = 8; const x = c.getContext('2d'); x.drawImage(im, 0, 0, 8, 8); x.getImageData(0, 0, 1, 1); paint = 'ok'; } catch (e) { paint = String(e).slice(0, 120); } }
        res({u, ok, why, ms: Math.round(performance.now() - t0), w: im.naturalWidth, paint});
      };
      im.onload = () => done(true, 'load'); im.onerror = () => done(false, 'error');
      setTimeout(() => done(false, 'timeout 15s'), 15000);
      im.src = u;
    });
    out.imgTests.push(r);
  }
  return out;
}"""


async def wait_real(page, docs, t0, limit=60):
    while time.time() - t0 < limit:
        if any(d[1] == 200 for d in docs):
            try:
                await page.wait_for_load_state('load', timeout=60000)
                st = await page.evaluate("() => (performance.getEntriesByType('navigation')[0] || {}).responseStatus || 0")
                if st == 200:
                    return round(time.time() - t0, 2)
            except Exception:
                pass
        await asyncio.sleep(0.25)
    return None


async def one(b, path, kind):
    opts = dict(viewport={'width': 412, 'height': 915}, device_scale_factor=2.6, is_mobile=True, has_touch=True, user_agent=PHONE_UA) if kind == 'phone' else dict(viewport={'width': 1440, 'height': 900})
    ctx = await b.new_context(**opts)
    await ctx.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined});")
    page = await ctx.new_page()
    rec = {'path': path, 'kind': kind, 'console': [], 'errors': [], 'failed': [], 'earth': [], 'doc': None}
    docs = []
    t0 = [time.time()]

    async def on_resp(r):
        try:
            if r.request.resource_type == 'document' and r.request.frame == page.main_frame:
                docs.append([round(time.time() - t0[0], 2), r.status])
                if r.status == 200:
                    h = await r.all_headers()
                    body = ''
                    try:
                        body = await r.text()
                    except Exception as e:
                        body = 'unreadable ' + str(e)
                    i = body.find('pnGlobe')
                    rec['doc'] = {'url': r.url, 'headers': h, 'len': len(body), 'globe_src': body[max(0, i - 300): i + 2600] if i >= 0 else None,
                                  'globe_tail': body[i + 2600: i + 21500] if i >= 0 else None}
            if 'earth' in r.url or 'globe' in r.url:
                rec['earth'].append({'url': r.url, 'status': r.status, 'type': r.request.resource_type, 'headers': {k: v for k, v in (await r.all_headers()).items() if k.lower() in ('access-control-allow-origin', 'content-type', 'content-length', 'cache-control', 'server', 'x-cache', 'cf-cache-status', 'age', 'timing-allow-origin', 'cross-origin-resource-policy', 'vary')}})
        except Exception as e:
            rec['errors'].append('probe: ' + str(e)[:200])
    page.on('response', lambda r: asyncio.ensure_future(on_resp(r)))
    page.on('console', lambda m: rec['console'].append(m.type + ': ' + m.text[:300]))
    page.on('pageerror', lambda e: rec['errors'].append(str(e)[:400]))
    page.on('requestfailed', lambda r: rec['failed'].append(r.url[:200] + ' :: ' + str(r.failure)))
    cdp = await ctx.new_cdp_session(page)
    await cdp.send('Network.enable')
    await cdp.send('Network.setCacheDisabled', {'cacheDisabled': True})
    t0[0] = time.time()
    try:
        await page.goto('https://perfectnations.org' + path, wait_until='commit', timeout=60000)
        rec['first_visit_s'] = await wait_real(page, docs, t0[0])
    except Exception as e:
        rec['errors'].append('goto: ' + str(e)[:200])
    rec['docs'] = list(docs)
    await page.wait_for_timeout(12000)
    try:
        rec['state'] = await page.evaluate(STATE)
    except Exception as e:
        rec['errors'].append('state: ' + str(e)[:300])
    slug = path.strip('/').replace('/', '-') or 'home'
    try:
        g = await page.query_selector('.bpx-globe')
        if g:
            await g.scroll_into_view_if_needed()
            await page.wait_for_timeout(1500)
            await g.screenshot(path='probe-out/%s-%s-globe.png' % (slug, kind))
        await page.evaluate('window.scrollTo(0,0)')
        await page.wait_for_timeout(800)
        await page.screenshot(path='probe-out/%s-%s-hero.png' % (slug, kind))
    except Exception as e:
        rec['errors'].append('shot: ' + str(e)[:200])
    await ctx.close()
    return rec


async def main():
    out = []
    async with async_playwright() as p:
        b = await p.chromium.launch(channel='chrome', headless=False,
                                    args=['--no-sandbox', '--disable-blink-features=AutomationControlled', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'],
                                    ignore_default_args=['--enable-automation'])
        for path in PATHS:
            for kind in ('phone', 'laptop'):
                r = await one(b, path, kind)
                out.append(r)
                st = r.get('state') or {}
                print(kind, path, 'docs', r.get('docs'), 'data-globe', st.get('dataGlobe'), 'webgl', st.get('webgl'), 'errors', r['errors'][:3], flush=True)
                for t in st.get('imgTests') or []:
                    print('   ', t, flush=True)
        await b.close()
    json.dump(out, open('probe-out/globe.json', 'w'), indent=1)

asyncio.run(main())
