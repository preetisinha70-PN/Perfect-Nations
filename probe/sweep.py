"""Temporary (10 Nov 2026): open every live page in the manifest once (laptop, real Chrome) and record script errors,
whether any inline script was rewritten by WordPress (&#038; inside a script), and how each globe ended."""
import asyncio, json, time
from playwright.async_api import async_playwright
m = json.load(open('pages/manifest.json'))['pages']
SLUGS = ['colombia','ecuador','egypt','ethiopia','fiji','ghana','indonesia','jamaica','jordan','mexico','morocco','pakistan',
         'philippines','senegal','sri-lanka','ukraine','vietnam','kenya','barbados']
URLS = ['https://perfectnations.org/blueprints/%s/' % s for s in SLUGS]
READ = """() => {
  const g = document.querySelector('.bpx-globe');
  const amp = [...document.scripts].filter(s => !s.src && s.textContent.indexOf('&#038;') >= 0).length;
  return {dataGlobe: g ? g.getAttribute('data-globe') : null, amp, live: (document.documentElement.outerHTML.match(/pn-live: pn-[a-z0-9-]+(?!hd|ft)[^>]*?-->/g) || []).filter(x => x.indexOf('pn-hd') < 0 && x.indexOf('pn-ft') < 0)};
}"""
async def main():
    out = []
    async with async_playwright() as p:
        b = await p.chromium.launch(channel='chrome', headless=False, args=['--no-sandbox', '--disable-blink-features=AutomationControlled', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'], ignore_default_args=['--enable-automation'])
        ctx = await b.new_context(viewport={'width': 1440, 'height': 900})
        await ctx.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined});")
        page = await ctx.new_page()
        errs = []
        page.on('pageerror', lambda e: errs.append(str(e)[:160]))
        for u in URLS:
            errs.clear(); r = {'url': u}
            for attempt in range(3):
                try:
                    resp = await page.goto(u, wait_until='load', timeout=60000)
                    r['status'] = resp.status if resp else None
                    if r['status'] == 200: break
                    await page.wait_for_timeout(4500)
                except Exception as e:
                    r['err'] = str(e)[:120]
            await page.wait_for_timeout(2500)
            try:
                r.update(await page.evaluate(READ))
            except Exception as e:
                r['err'] = str(e)[:120]
            r['pageerrors'] = list(errs)
            out.append(r)
            print('%-60s %s errors=%d amp=%s globe=%s' % (u, r.get('status'), len(errs), r.get('amp'), r.get('dataGlobe')), flush=True)
        await b.close()
    json.dump(out, open('probe-out/sweep.json', 'w'), indent=1)
asyncio.run(main())
