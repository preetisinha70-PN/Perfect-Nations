"""Open each page in a real Chrome window (not headless) as a first-time visitor, on a phone over 4G and
on a laptop over broadband, and record where the time goes."""
import asyncio, json, sys
from playwright.async_api import async_playwright
PAGES = ['/', '/blueprints/', '/blueprints/kenya/', '/about/', '/state-of-nations/', '/art-of-nations/']
PHONE_UA = 'Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Mobile Safari/537.36'
OBS = """
window.__pn = {lcp: 0, lcpEl: '', long: 0, longN: 0, cls: 0};
new PerformanceObserver(l => { for (const e of l.getEntries()) { window.__pn.lcp = e.startTime; window.__pn.lcpEl = (e.element && (e.element.tagName + (e.element.id ? '#' + e.element.id : '') + (e.element.className && typeof e.element.className === 'string' ? '.' + e.element.className.split(' ')[0] : ''))) || e.url || ''; } }).observe({type: 'largest-contentful-paint', buffered: true});
new PerformanceObserver(l => { for (const e of l.getEntries()) { window.__pn.long += Math.max(0, e.duration - 50); window.__pn.longN++; } }).observe({type: 'longtask', buffered: true});
new PerformanceObserver(l => { for (const e of l.getEntries()) { if (!e.hadRecentInput) window.__pn.cls += e.value; } }).observe({type: 'layout-shift', buffered: true});
"""
READ = """() => {
  const n = performance.getEntriesByType('navigation')[0];
  const fcp = (performance.getEntriesByName('first-contentful-paint')[0] || {}).startTime || 0;
  const res = performance.getEntriesByType('resource').map(r => ({u: r.name.slice(0, 150), t: r.initiatorType, s: r.transferSize, d: Math.round(r.duration), st: Math.round(r.startTime), rb: r.renderBlockingStatus || ''}));
  return {ttfb: Math.round(n.responseStart), html_done: Math.round(n.responseEnd), dcl: Math.round(n.domContentLoadedEventEnd), load: Math.round(n.loadEventEnd),
          fcp: Math.round(fcp), lcp: Math.round(window.__pn.lcp), lcpEl: window.__pn.lcpEl, tbt: Math.round(window.__pn.long), longN: window.__pn.longN, cls: +window.__pn.cls.toFixed(3),
          html_bytes: n.transferSize, html_size: n.decodedBodySize, n_res: res.length, bytes: res.reduce((a, r) => a + (r.s || 0), 0) + n.transferSize, res: res};
}"""
async def one(b, path, kind):
    if kind == 'phone':
        ctx = await b.new_context(viewport={'width': 412, 'height': 915}, device_scale_factor=2.6, is_mobile=True, has_touch=True, user_agent=PHONE_UA)
    else:
        ctx = await b.new_context(viewport={'width': 1440, 'height': 900})
    await ctx.add_init_script(OBS)
    page = await ctx.new_page()
    cdp = await ctx.new_cdp_session(page)
    await cdp.send('Network.enable')
    await cdp.send('Network.setCacheDisabled', {'cacheDisabled': True})
    if kind == 'phone':  # 4G: 9 Mbps down, 1.5 up, 120 ms; CPU 4x slower, like a mid-range phone
        await cdp.send('Network.emulateNetworkConditions', {'offline': False, 'latency': 120, 'downloadThroughput': 9e6 / 8, 'uploadThroughput': 1.5e6 / 8})
        await cdp.send('Emulation.setCPUThrottlingRate', {'rate': 4})
    hdr = {}
    page.on('response', lambda r: hdr.update({'x-litespeed-cache': r.headers.get('x-litespeed-cache', ''), 'status': r.status}) if r.url.rstrip('/') == ('https://perfectnations.org' + path).rstrip('/') else None)
    try:
        await page.goto('https://perfectnations.org' + path, wait_until='load', timeout=90000)
    except Exception as e:
        print('timeout', path, kind, str(e)[:100])
    await page.wait_for_timeout(4000)
    d = await page.evaluate(READ)
    d.update(hdr); d['path'] = path; d['kind'] = kind
    await ctx.close()
    return d
async def main():
    out = []
    async with async_playwright() as p:
        b = await p.chromium.launch(channel='chrome', headless=False, args=['--no-sandbox'])
        for path in PAGES:
            for kind in ('phone', 'laptop'):
                d = await one(b, path, kind); out.append(d)
                print(f"{kind:6} {path:24} cache={d.get('x-litespeed-cache','?'):4} TTFB={d['ttfb']} FCP={d['fcp']} LCP={d['lcp']} load={d['load']} TBT={d['tbt']} bytes={d['bytes']//1024}KB req={d['n_res']}", flush=True)
        await b.close()
    json.dump(out, open('probe-out/browser.json', 'w'), indent=1)
asyncio.run(main())
