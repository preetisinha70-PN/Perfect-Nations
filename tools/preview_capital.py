"""Headless previews of the Capital Architecture page, laptop 1440x900 and phone 390x844.

    python3 tools/preview_capital.py

Wraps pages/capital-architecture.html in the header and footer, routes GitHub and jsDelivr reads to
this repository, uses local Barlow fonts, paints stand-ins for the Media Library pictures (the shell
cannot reach perfectnations.com), and blocks every other host. Screenshots go to /tmp/pn-preview/.
Needs: pip install playwright pillow (Chromium), and the fonts once:
    cd /tmp/pn-fonts && npm init -y && npm install @fontsource/barlow-condensed @fontsource/barlow-semi-condensed
"""
import io
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter
from playwright.sync_api import sync_playwright

REPO = Path(__file__).resolve().parent.parent
OUT = Path('/tmp/pn-preview')
OUT.mkdir(exist_ok=True)
FONTS = Path('/tmp/pn-fonts/node_modules/@fontsource')

# Stand-in pictures, by a word in the file name: sky colour, ground colour, accent.
PALETTE = {
    'brazil': ((92, 168, 120), (18, 74, 40), (46, 140, 70)),
    'india': ((240, 196, 120), (150, 70, 40), (230, 120, 60)),
    'ecuador': ((120, 180, 230), (190, 110, 70), (240, 210, 160)),
    'chile': ((70, 140, 220), (215, 160, 100), (40, 60, 110)),
    'kenya': ((60, 150, 140), (20, 60, 70), (230, 200, 90)),
}


def stand_in(name):
    key = next((k for k in PALETTE if k in name), 'kenya')
    sky, ground, acc = PALETTE[key]
    w, h = 768, 480
    img = Image.new('RGB', (w, h), sky)
    d = ImageDraw.Draw(img)
    for y in range(h):
        t = y / h
        c = tuple(int(sky[i] * (1 - t) + ground[i] * t) for i in range(3))
        d.line([(0, y), (w, y)], fill=c)
    rnd = random.Random(key)
    for _ in range(26):
        x, y, r = rnd.randint(0, w), rnd.randint(int(h * .45), h), rnd.randint(18, 70)
        d.ellipse([x - r, y - r, x + r, y + r], fill=acc)
    img = img.filter(ImageFilter.GaussianBlur(3))
    buf = io.BytesIO()
    img.save(buf, 'JPEG', quality=80)
    return buf.getvalue()


FACES = ''
for fam, folder, weights in (('Barlow Condensed', 'barlow-condensed', (400, 500, 600, 700)),
                             ('Barlow Semi Condensed', 'barlow-semi-condensed', (400, 500, 600))):
    for wt in weights:
        FACES += "@font-face{font-family:'%s';font-weight:%d;font-style:normal;src:url('/fonts/%s-latin-%d-normal.woff2') format('woff2');}\n" % (fam, wt, folder, wt)

page = (REPO / 'pages/capital-architecture.html').read_text()
header = (REPO / 'pages/header.html').read_text()
footer = (REPO / 'pages/footer.html').read_text()
HTML = """<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Capital Architecture - Perfect Nations</title>
<style>%s
html,body{margin:0;padding:0;background:#0B3D45;}
body{font-family:'Barlow Semi Condensed',Arial,sans-serif;}
/* Astra-like defaults the page must survive */
h1,h2,h3{text-shadow:0 0 6px rgba(0,0,0,.3);color:#222;text-transform:uppercase;}
ul{margin:0 0 1.5em 3em;}
p{margin:0 0 1.6em;}
button{background:#0170B9;color:#fff;padding:10px 20px;border:0;}
a{color:#0170B9;text-decoration:underline;}
</style></head><body>
%s
<main id="content" class="site-content"><div class="ast-container"><div class="elementor e-con" style="padding-top:30px"><div class="elementor-widget elementor-widget-html">
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
            f = REPO / url[len(pre):].split('?')[0]
            if f.exists():
                return r.fulfill(path=str(f), content_type='application/json')
            return r.fulfill(status=404, body='')
    if url.startswith('https://perfectnations.com/wp-content/') and url.split('?')[0].endswith(('.png', '.jpg', '.jpeg', '.webp')):
        return r.fulfill(body=stand_in(url.rsplit('/', 1)[-1]), content_type='image/jpeg')
    return r.abort()


def run():
    errors = []
    with sync_playwright() as p:
        b = p.chromium.launch()
        for name, vp, dpr in (('laptop', {'width': 1440, 'height': 900}, 1), ('phone', {'width': 390, 'height': 844}, 2)):
            ctx = b.new_context(viewport=vp, device_scale_factor=dpr, is_mobile=(name == 'phone'), has_touch=(name == 'phone'))
            pg = ctx.new_page()
            pg.on('pageerror', lambda e, n=name: errors.append('%s pageerror: %s' % (n, e)))
            pg.on('console', lambda m, n=name: errors.append('%s console %s: %s' % (n, m.type, m.text)) if m.type in ('error', 'warning') else None)
            pg.route('**/*', route)
            pg.goto('http://pn.local/index.html', wait_until='load')
            pg.wait_for_timeout(1500)
            pg.evaluate("document.fonts.ready")
            pg.screenshot(path=str(OUT / ('ca-%s-first-screen.png' % name)))
            pg.evaluate("""async () => { for (let y = 0; y < document.body.scrollHeight; y += 300) { window.scrollTo(0, y); await new Promise(r => setTimeout(r, 50)); } window.scrollTo(0, 0); }""")
            pg.wait_for_timeout(1200)
            info = pg.evaluate("""() => {
              const r = document.getElementById('pn-arch');
              const h = s => Math.round(r.querySelector(s).getBoundingClientRect().height);
              return {page: Math.round(r.getBoundingClientRect().height), hero: h('.pca-hero'), index: h('.pca-idx'),
                      record: h('.pca-rec'), close: h('.pca-close'), rows: r.querySelectorAll('.pca-row').length,
                      nations: r.querySelectorAll('.pca-nat').length, count: r.querySelector('[data-pca-n=count]').textContent,
                      scrollW: document.documentElement.scrollWidth, innerW: window.innerWidth};
            }""")
            print(name, info)
            if name == 'phone':
                assert info['scrollW'] <= info['innerW'] + 1, 'the phone page scrolls sideways'
            pg.screenshot(path=str(OUT / ('ca-%s-full.png' % name)), full_page=True)
            for sel, tag in (('.pca-hero', 'hero'), ('.pca-idx', 'toolkit'), ('.pca-rec', 'record'), ('.pca-close', 'close')):
                pg.query_selector('#pn-arch ' + sel).screenshot(path=str(OUT / ('ca-%s-%s.png' % (name, tag))))
            # open one line of the toolkit (on phones, choose its family from the chips first)
            pg.click('#pn-arch .pca-jump a[data-f="pca-f-disaster"]')
            pg.wait_for_timeout(300)
            pg.evaluate("document.getElementById('pca-i-catastrophe-bond').open = true")
            pg.wait_for_timeout(300)
            pg.query_selector('#pca-f-disaster').screenshot(path=str(OUT / ('ca-%s-open-line.png' % name)))
            # the search: every line that mentions a word, across the families
            pg.fill('#pn-arch .pca-find input', 'guarantee')
            pg.wait_for_timeout(400)
            pg.query_selector('#pn-arch .pca-idx').screenshot(path=str(OUT / ('ca-%s-search.png' % name)))
            print(name, 'search:', pg.inner_text('#pn-arch .pca-found'))
            pg.fill('#pn-arch .pca-find input', '')
            pg.wait_for_timeout(300)
            # All
            pg.click('#pn-arch .pca-jump a[data-f="all"]')
            pg.wait_for_timeout(300)
            print(name, 'all:', pg.evaluate("Math.round(document.querySelector('#pn-arch .pca-idx').getBoundingClientRect().height)"))
            pg.click('#pn-arch .pca-jump a[data-f="pca-f-sovereign"]')
            pg.wait_for_timeout(300)
            # all nations
            pg.click('#pn-arch .pca-more-n')
            pg.wait_for_timeout(300)
            pg.query_selector('#pn-arch .pca-rec').screenshot(path=str(OUT / ('ca-%s-record-all.png' % name)))
            ctx.close()
        b.close()
    print('\n'.join(errors) or 'no script errors')


if __name__ == '__main__':
    run()
