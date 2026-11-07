"""Headless previews of the Blueprints page, laptop 1440x900 and phone 390x844.

    python3 tools/preview_blueprints.py [--extra benin]

Wraps pages/blueprints.html in the header and footer, routes GitHub and jsDelivr reads to this
repository, uses local Barlow fonts and a stand-in logo, and blocks every other host. Screenshots go
to /tmp/pn-preview/. --extra <slug> adds a test blueprint to the manifest (and a stub data file) to
show that a newly merged blueprint appears by itself; it changes no file.
Needs: pip install playwright (Chromium), and the fonts once:
    cd /tmp/pn-fonts && npm init -y && npm install @fontsource/barlow-condensed @fontsource/barlow-semi-condensed
"""
import json
import struct
import sys
import zlib
from pathlib import Path

from playwright.sync_api import sync_playwright

REPO = Path(__file__).resolve().parent.parent
OUT = Path('/tmp/pn-preview')
OUT.mkdir(exist_ok=True)
FONTS = Path('/tmp/pn-fonts/node_modules/@fontsource')
EXTRA = sys.argv[sys.argv.index('--extra') + 1] if '--extra' in sys.argv else None
TAG = ('-extra-' + EXTRA) if EXTRA else ''


def png(w, h, rgb):
    raw = b''.join(b'\x00' + bytes(rgb) * w for _ in range(h))
    def chunk(t, d):
        return struct.pack('>I', len(d)) + t + d + struct.pack('>I', zlib.crc32(t + d) & 0xffffffff)
    return b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', w, h, 8, 2, 0, 0, 0)) + chunk(b'IDAT', zlib.compress(raw)) + chunk(b'IEND', b'')


STAND_IN = png(8, 8, (227, 194, 88))

FACES = ''
for fam, folder, weights in (('Barlow Condensed', 'barlow-condensed', (400, 500, 600, 700)),
                             ('Barlow Semi Condensed', 'barlow-semi-condensed', (400, 500, 600))):
    for w in weights:
        FACES += "@font-face{font-family:'%s';font-weight:%d;font-style:normal;src:url('/fonts/%s-latin-%d-normal.woff2') format('woff2');}\n" % (fam, w, folder, w)

page = (REPO / 'pages/blueprints.html').read_text()
header = (REPO / 'pages/header.html').read_text()
footer = (REPO / 'pages/footer.html').read_text()
HTML = """<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>National Blueprints - Perfect Nations</title>
<style>%s
html,body{margin:0;padding:0;background:#0B3D45;}
body{font-family:'Barlow Semi Condensed',Arial,sans-serif;}
/* Astra-like defaults the page must survive */
h1,h2,h3{text-shadow:0 0 6px rgba(0,0,0,.3);color:#222;}
ul{margin:0 0 1.5em 3em;}
button{background:#0170B9;color:#fff;padding:10px 20px;border:0;}
input[type=search]{border:1px solid #ddd;padding:8px;background:#fff;color:#333;}
a{color:#0170B9;text-decoration:underline;}
</style></head><body>
%s
<main id="content" class="site-content"><div class="ast-container"><div class="elementor e-con"><div class="elementor-widget elementor-widget-html">
%s
</div></div></div></main>
%s
</body></html>""" % (FACES, header, page, footer)


def route(r):
    url = r.request.url
    if url.startswith('http://pn.local/'):
        p = url[len('http://pn.local/'):]
        if p.startswith('fonts/'):
            name = p[len('fonts/'):]
            folder = 'barlow-semi-condensed' if name.startswith('barlow-semi') else 'barlow-condensed'
            return r.fulfill(path=str(FONTS / folder / 'files' / name), content_type='font/woff2')
        return r.fulfill(body=HTML, content_type='text/html')
    for pre in ('https://raw.githubusercontent.com/preetisinha70-PN/perfect-nations/main/',
                'https://cdn.jsdelivr.net/gh/preetisinha70-PN/perfect-nations@main/'):
        if url.startswith(pre):
            rel = url[len(pre):].split('?')[0]
            if EXTRA and rel == 'pages/manifest.json':
                m = json.loads((REPO / rel).read_text())
                m['pages']['pn-bp-' + EXTRA] = {'file': 'pages/blueprint-%s.html' % EXTRA, 'version': '1.0'}
                return r.fulfill(body=json.dumps(m), content_type='application/json')
            if EXTRA and rel == 'data/%s.json' % EXTRA:
                stub = {'nation': EXTRA.title(), 'steward': {'name': 'Test Steward'},
                        'hero': {'stats': [{'value': '$100M', 'label': 'Test figure for the preview only'}]}}
                return r.fulfill(body=json.dumps(stub), content_type='application/json')
            f = REPO / rel
            if f.exists():
                return r.fulfill(path=str(f), content_type='application/json' if rel.endswith('.json') else 'text/plain')
            return r.fulfill(status=404, body='')
    if url.startswith('https://perfectnations.org/wp-content/') and url.split('?')[0].endswith(('.png', '.jpg', '.webp')):
        return r.fulfill(body=STAND_IN, content_type='image/png')
    return r.abort()


def run():
    errors = []
    with sync_playwright() as p:
        b = p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        for name, vp, dpr in (('laptop', {'width': 1440, 'height': 900}, 1), ('phone', {'width': 390, 'height': 844}, 2)):
            ctx = b.new_context(viewport=vp, device_scale_factor=dpr, is_mobile=(name == 'phone'), has_touch=(name == 'phone'))
            pg = ctx.new_page()
            pg.on('pageerror', lambda e, n=name: errors.append('%s pageerror: %s' % (n, e)))
            pg.on('console', lambda m, n=name: errors.append('%s console %s: %s' % (n, m.type, m.text)) if m.type in ('error', 'warning') else None)
            pg.on('requestfailed', lambda r, n=name: errors.append('%s blocked: %s' % (n, r.url[:120])))
            pg.route('**/*', route)
            pg.goto('http://pn.local/index.html', wait_until='load')
            pg.wait_for_timeout(1800)
            pg.evaluate("document.fonts.ready")
            top = pg.evaluate("document.getElementById('pn-bpa').getBoundingClientRect().top + window.scrollY")
            pg.screenshot(path=str(OUT / ('%s%s-first-screen.png' % (name, TAG))))
            pg.evaluate("""async () => { for (let y = 0; y < document.body.scrollHeight; y += 300) { window.scrollTo(0, y); await new Promise(r => setTimeout(r, 60)); } window.scrollTo(0, 0); }""")
            pg.wait_for_timeout(900)
            pg.screenshot(path=str(OUT / ('%s%s-full.png' % (name, TAG))), full_page=True)
            info = pg.evaluate("""() => {
              const r = document.getElementById('pn-bpa');
              const q = s => r.querySelectorAll(s).length;
              const vis = [...r.querySelectorAll('.pnbpa-t')].filter(t => !t.hidden).length;
              return {height: Math.round(r.getBoundingClientRect().height), tiles: q('.pnbpa-t'), visibleTiles: vis,
                      live: r.querySelector('[data-k=live]').textContent, regions: r.querySelector('[data-k=regions]').textContent,
                      liveShapes: q('.pnbpa-c--live'), scrollW: document.documentElement.scrollWidth, innerW: window.innerWidth};
            }""")
            print(name, info)
            if name == 'phone':
                assert info['scrollW'] <= info['innerW'] + 1, 'the phone page scrolls sideways'
            # a region: the map flies, the tiles follow
            pg.click('.pnbpa-tab[data-r="africa"]')
            pg.wait_for_timeout(1000)
            el = pg.query_selector('.pnbpa-hero')
            el.screenshot(path=str(OUT / ('%s%s-africa.png' % (name, TAG))))
            pg.click('.pnbpa-tab[data-r="americas"]')
            pg.wait_for_timeout(1000)
            el.screenshot(path=str(OUT / ('%s%s-americas.png' % (name, TAG))))
            pg.click('.pnbpa-tab[data-r="oceania"]')
            pg.wait_for_timeout(1000)
            el.screenshot(path=str(OUT / ('%s%s-oceania.png' % (name, TAG))))
            pg.query_selector('.pnbpa-open').screenshot(path=str(OUT / ('%s%s-open-oceania.png' % (name, TAG))))
            pg.click('.pnbpa-tab[data-r="world"]')
            pg.wait_for_timeout(900)
            # the search
            pg.fill('#pnbpaQ', 'congo')
            pg.wait_for_timeout(300)
            pg.query_selector('.pnbpa-open').screenshot(path=str(OUT / ('%s%s-search.png' % (name, TAG))))
            pg.query_selector('.pnbpa-every').screenshot(path=str(OUT / ('%s%s-search-atlas.png' % (name, TAG))))
            pg.fill('#pnbpaQ', '')
            pg.wait_for_timeout(200)
            # a region opened in the atlas
            pg.evaluate("document.querySelectorAll('#pn-bpa .pnbpa-reg').forEach((d,i)=>d.open=(i===0))")
            pg.wait_for_timeout(200)
            pg.query_selector('.pnbpa-every').screenshot(path=str(OUT / ('%s%s-atlas-africa.png' % (name, TAG))))
            if name == 'laptop':
                pg.evaluate("window.scrollTo(0,0)")
                pg.hover('#pnbpa-c-kenya')
                pg.wait_for_timeout(300)
                pg.query_selector('#pnbpaMap').screenshot(path=str(OUT / ('%s%s-hover.png' % (name, TAG))))
            ctx.close()
        b.close()
    print('\n'.join(errors) or 'no script errors')


if __name__ == '__main__':
    run()
