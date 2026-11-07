"""Open pages in a real Chrome window as a first-time visitor (phone on 4G with a mid-range CPU, and laptop),
once as the site is now and once with the sitewide unpkg.com globe.gl head script blocked, and record
first paint, largest paint and load, plus whether the Kenya globe still draws without that script."""
import asyncio, json
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
  const u = performance.getEntriesByType('resource').filter(r => r.name.includes('unpkg') || r.name.includes('globe.gl') || r.name.includes('three'));
  const g = document.querySelector('#kenya-globe canvas, #pn-hero canvas, canvas');
  return {ttfb: Math.round(n.responseStart), dcl: Math.round(n.domContentLoadedEventEnd), load: Math.round(n.loadEventEnd),
          fcp: Math.round(fcp), lcp: Math.round(window.__pn.lcp), lcpEl: window.__pn.lcpEl, tbt: Math.round(window.__pn.long),
          globe: typeof Globe !== 'undefined', canvas: !!g, libs: u.map(r => [r.name.slice(0, 90), Math.round(r.startTime), Math.round(r.duration)])};
}"""
async def one(b, path, kind, cond):
    if kind == 'phone':
        ctx = await b.new_context(viewport={'width': 412, 'height': 915}, device_scale_factor=2.6, is_mobile=True, has_touch=True, user_agent=PHONE_UA)
    else:
        ctx = await b.new_context(viewport={'width': 1440, 'height': 900})
    await ctx.add_init_script(OBS)
    if cond == 'no-unpkg':
        await ctx.route('**/unpkg.com/**', lambda r: r.abort())
    else:
        await ctx.route('**/unpkg.com/**', lambda r: r.continue_())
    page = await ctx.new_page()
    errs = []; navs = []; docs = []
    import time; t0 = [time.time()]
    page.on('pageerror', lambda e: errs.append(str(e)[:160]))
    page.on('framenavigated', lambda f: navs.append([round(time.time() - t0[0], 2), f.url[:120]]) if f == page.main_frame else None)
    page.on('response', lambda r: docs.append([round(time.time() - t0[0], 2), r.status, r.url[:120], r.headers.get('x-litespeed-cache', ''), r.headers.get('location', ''), r.headers.get('content-type', '')[:30]]) if r.request.resource_type == 'document' else None)
    page.on('console', lambda m: errs.append('console ' + m.type + ': ' + m.text[:140]) if m.type in ('error', 'warning') else None)
    cdp = await ctx.new_cdp_session(page)
    await cdp.send('Network.enable')
    await cdp.send('Network.setCacheDisabled', {'cacheDisabled': True})
    if kind == 'phone':
        await cdp.send('Network.emulateNetworkConditions', {'offline': False, 'latency': 150, 'downloadThroughput': 9e6 / 8, 'uploadThroughput': 1.5e6 / 8})
        await cdp.send('Emulation.setCPUThrottlingRate', {'rate': 4})
    t0[0] = time.time()
    try:
        await page.goto('https://perfectnations.org' + path, wait_until='commit', timeout=60000)
        await page.wait_for_function("document.readyState === 'complete' && performance.getEntriesByType('navigation')[0].loadEventEnd > 0", timeout=90000, polling=250)
    except Exception as e:
        errs.append('wait: ' + str(e)[:120])
    await page.wait_for_timeout(8000 if 'kenya' in path else 3000)
    d = None
    for _ in range(4):
        try:
            d = await page.evaluate(READ); break
        except Exception as e:
            errs.append('evaluate: ' + str(e)[:80])
            try:
                await page.wait_for_load_state('load', timeout=60000)
            except Exception:
                pass
            await page.wait_for_timeout(3000)
    d = d or {'ttfb': 0, 'dcl': 0, 'load': 0, 'fcp': 0, 'lcp': 0, 'lcpEl': '', 'tbt': 0, 'globe': None, 'canvas': None, 'libs': []}
    d.update({'path': path, 'kind': kind, 'cond': cond, 'errors': errs[:10], 'navs': navs, 'docs': docs, 'final_url': page.url})
    await ctx.close()
    return d
async def main():
    out = []
    async with async_playwright() as p:
        b = await p.chromium.launch(channel='chrome', headless=False, args=['--no-sandbox'])
        for rnd in (1, 2):
            for path in PAGES:
                for kind in ('phone', 'laptop'):
                    for cond in (('now', 'no-unpkg') if rnd == 1 else ('no-unpkg', 'now')):
                        d = await one(b, path, kind, cond); d['round'] = rnd; out.append(d)
                        print(f"r{rnd} {kind:6} {cond:8} {path:20} FCP={d['fcp']} LCP={d['lcp']} DCL={d['dcl']} load={d['load']} TBT={d['tbt']} globe={d['globe']} canvas={d['canvas']} err={len(d['errors'])} navs={len(d['navs'])}", flush=True)
                        if len(d['navs']) > 1 or d['errors']:
                            print('   navs', d['navs']); print('   docs', d['docs']); print('   errs', d['errors'][:6], flush=True)
        await b.close()
    json.dump(out, open('probe-out/browser.json', 'w'), indent=1)
asyncio.run(main())
