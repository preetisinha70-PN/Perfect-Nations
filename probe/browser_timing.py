"""Real Chrome window, first-time visitor. Step 1: open the page with no cookies and time how long until the real
page arrives (the CDN may first answer 403 with a browser check). Step 2: open it again in the same window (check
passed, browser cache off) and record first paint, largest paint and load, once as the site is now and once with
the sitewide unpkg.com globe.gl head script blocked. Also saves the 403 page once so we can see what it is."""
import asyncio, json, time
from playwright.async_api import async_playwright
PAGES = ['/', '/blueprints/kenya/', '/about/', '/state-of-nations/']
PHONE_UA = 'Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Mobile Safari/537.36'
OBS = """
window.__pn = {lcp: 0, lcpEl: '', long: 0};
new PerformanceObserver(l => { for (const e of l.getEntries()) { window.__pn.lcp = e.startTime; window.__pn.lcpEl = (e.element && (e.element.tagName + (e.element.id ? '#' + e.element.id : ''))) || e.url || ''; } }).observe({type: 'largest-contentful-paint', buffered: true});
new PerformanceObserver(l => { for (const e of l.getEntries()) { window.__pn.long += Math.max(0, e.duration - 50); } }).observe({type: 'longtask', buffered: true});
"""
READ = """() => {
  const n = performance.getEntriesByType('navigation')[0];
  const fcp = (performance.getEntriesByName('first-contentful-paint')[0] || {}).startTime || 0;
  return {status: n.responseStatus || 0, ttfb: Math.round(n.responseStart), dcl: Math.round(n.domContentLoadedEventEnd), load: Math.round(n.loadEventEnd),
          fcp: Math.round(fcp), lcp: Math.round(window.__pn.lcp), lcpEl: window.__pn.lcpEl, tbt: Math.round(window.__pn.long),
          globe: typeof Globe !== 'undefined', canvas: !!document.querySelector('canvas')};
}"""
saved = {'done': False}
async def wait_real(page, docs, t0, limit=60):
    while time.time() - t0 < limit:
        ok = [d for d in docs if d[1] == 200]
        if ok:
            try:
                await page.wait_for_load_state('load', timeout=60000)
                st = await page.evaluate("() => (performance.getEntriesByType('navigation')[0] || {}).responseStatus || 0")
                if st == 200:
                    return round(time.time() - t0, 2)
            except Exception:
                pass
        await asyncio.sleep(0.25)
    return None
async def one(b, path, kind, cond, stealth):
    opts = dict(viewport={'width': 412, 'height': 915}, device_scale_factor=2.6, is_mobile=True, has_touch=True, user_agent=PHONE_UA) if kind == 'phone' else dict(viewport={'width': 1440, 'height': 900})
    ctx = await b.new_context(**opts)
    await ctx.add_init_script(OBS)
    if stealth:
        await ctx.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined});")
    await ctx.route('**/unpkg.com/**', (lambda r: r.abort()) if cond == 'no-unpkg' else (lambda r: r.continue_()))
    page = await ctx.new_page()
    docs = []; t0 = [time.time()]
    async def on_resp(r):
        if r.request.resource_type == 'document' and r.request.frame == page.main_frame:
            docs.append([round(time.time() - t0[0], 2), r.status])
            if r.status == 403 and not saved['done']:
                saved['done'] = True
                try:
                    body = await r.text()
                except Exception as e:
                    body = 'unreadable: ' + str(e)
                json.dump({'url': r.url, 'headers': await r.all_headers(), 'body': body[:20000]}, open('probe-out/cdn-403.json', 'w'), indent=1)
    page.on('response', lambda r: asyncio.ensure_future(on_resp(r)))
    cdp = await ctx.new_cdp_session(page)
    await cdp.send('Network.enable')
    await cdp.send('Network.setCacheDisabled', {'cacheDisabled': True})
    if kind == 'phone':
        await cdp.send('Network.emulateNetworkConditions', {'offline': False, 'latency': 150, 'downloadThroughput': 9e6 / 8, 'uploadThroughput': 1.5e6 / 8})
        await cdp.send('Emulation.setCPUThrottlingRate', {'rate': 4})
    t0[0] = time.time()
    first = None
    try:
        await page.goto('https://perfectnations.org' + path, wait_until='commit', timeout=60000)
        first = await wait_real(page, docs, t0[0])
    except Exception as e:
        print('first visit error', str(e)[:120])
    first_docs = list(docs)
    await page.wait_for_timeout(1500)
    docs.clear(); t0[0] = time.time()
    d = None
    try:
        await page.goto('https://perfectnations.org' + path, wait_until='load', timeout=90000)
        await page.wait_for_timeout(6000 if 'kenya' in path else 3000)
        d = await page.evaluate(READ)
    except Exception as e:
        print('second visit error', str(e)[:120])
    d = d or {}
    d.update({'path': path, 'kind': kind, 'cond': cond, 'stealth': stealth, 'first_visit_s': first, 'first_docs': first_docs, 'second_docs': list(docs)})
    await ctx.close()
    return d
async def main():
    out = []
    async with async_playwright() as p:
        b = await p.chromium.launch(channel='chrome', headless=False, args=['--no-sandbox', '--disable-blink-features=AutomationControlled'], ignore_default_args=['--enable-automation'])
        for rnd in (1, 2):
            for path in PAGES:
                for kind in ('phone', 'laptop'):
                    for cond in (('now', 'no-unpkg') if rnd == 1 else ('no-unpkg', 'now')):
                        d = await one(b, path, kind, cond, stealth=(rnd == 2)); d['round'] = rnd; out.append(d)
                        print(f"r{rnd} {kind:6} {cond:8} {path:20} first-visit={d['first_visit_s']}s docs={d['first_docs']} | again: status={d.get('status')} FCP={d.get('fcp')} LCP={d.get('lcp')} DCL={d.get('dcl')} load={d.get('load')} TBT={d.get('tbt')} globe={d.get('globe')} canvas={d.get('canvas')} docs2={d['second_docs']}", flush=True)
        await b.close()
    json.dump(out, open('probe-out/browser.json', 'w'), indent=1)
asyncio.run(main())
