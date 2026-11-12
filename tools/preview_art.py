"""Headless previews of the Art of Nations page, laptop 1440x900 and phone 390x844.

    python3 tools/preview_art.py [--real-dir DIR]

Wraps pages/art-of-nations.html in the header and footer, uses local Barlow fonts and blocks every
other host. perfectnations.com cannot be reached from the build machine, so each Media Library image
is replaced by a painted stand-in in the nation's colours, marked STAND-IN (pass --real-dir with
files named as on the Media Library to use real images). Screenshots go to /tmp/pn-preview/art-*.png.
Checks: no script errors, nothing wider than the phone screen, the hero turns to the next painting,
the viewer opens a painting and a book, and every image URL the page asks for is listed.
Needs: pip install playwright pillow (Chromium), and the fonts once:
    cd /tmp/pn-fonts && npm init -y && npm install @fontsource/barlow-condensed @fontsource/barlow-semi-condensed
"""
import io
import json
import math
import random
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from playwright.sync_api import sync_playwright

REPO = Path(__file__).resolve().parent.parent
OUT = Path('/tmp/pn-preview')
OUT.mkdir(exist_ok=True)
FONTS = Path('/tmp/pn-fonts/node_modules/@fontsource')
REAL = Path(sys.argv[sys.argv.index('--real-dir') + 1]) if '--real-dir' in sys.argv else None
CAT = json.loads((REPO / 'art/catalogue.json').read_text(encoding='utf-8'))


def stand_in(seed, colours, label, size=800, book=False):
    rnd = random.Random(seed)
    cs = [tuple(int(c[i:i + 2], 16) for i in (1, 3, 5)) for c in colours] or [(200, 160, 80)]
    im = Image.new('RGB', (size, size), (246, 238, 220))
    d = ImageDraw.Draw(im)
    sky = cs[0] if sum(cs[0]) > 120 else cs[-1]
    for y in range(size):
        t = y / size
        d.line([(0, y), (size, y)], fill=tuple(int(250 * (1 - t) * .35 + sky[k] * (.25 + t * .45) + 60 * (1 - t)) for k in range(3)))
    peak = cs[1 % len(cs)]
    d.polygon([(size * .12, size * .78), (size * .5, size * .2), (size * .88, size * .78)], fill=peak)
    d.polygon([(size * .41, size * .33), (size * .5, size * .2), (size * .59, size * .33), (size * .54, size * .36), (size * .5, size * .32), (size * .46, size * .36)], fill=(250, 246, 236))
    pal = cs + [(242, 131, 107), (47, 181, 140), (242, 194, 48), (35, 80, 216)]
    for _ in range(46):
        x, y = rnd.uniform(.05, .95) * size, rnd.uniform(.5, .97) * size
        r = rnd.uniform(.025, .07) * size
        col = rnd.choice(pal)
        for k in range(7):
            a = k / 7 * math.tau
            cx, cy = x + math.cos(a) * r * .7, y + math.sin(a) * r * .7
            d.ellipse([cx - r * .45, cy - r * .45, cx + r * .45, cy + r * .45], fill=col, outline=(40, 30, 20))
        d.ellipse([x - r * .35, y - r * .35, x + r * .35, y + r * .35], fill=(242, 194, 48), outline=(40, 30, 20))
    for _ in range(26):
        x, y = rnd.uniform(0, 1) * size, rnd.uniform(.35, 1) * size
        d.ellipse([x - 14, y - 6, x + 14, y + 6], fill=(47, 140, 90))
    for k in range(0, size, 22):
        for (x, y) in ((k, 10), (k, size - 10), (10, k), (size - 10, k)):
            d.ellipse([x - 3, y - 3, x + 3, y + 3], fill=rnd.choice(pal))
    try:
        f = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', size // 26)
    except OSError:
        f = ImageFont.load_default()
    d.rectangle([size * .03, size * .03, size * .03 + len('STAND-IN') * size / 40 + 18, size * .03 + size / 22], fill=(26, 20, 12))
    d.text((size * .03 + 9, size * .035), 'STAND-IN', fill=(240, 214, 143), font=f)
    if book:
        d.rectangle([0, size * .8, size, size], fill=(11, 61, 69))
        d.text((size * .06, size * .85), label, fill=(244, 236, 216), font=f)
    buf = io.BytesIO()
    im.save(buf, 'JPEG', quality=82)
    return buf.getvalue()


IMAGES = {}
for p in CAT['paintings']:
    data = stand_in(p['slug'], p['colours'], p['title'])
    for url, _ in p['images']:
        IMAGES[url] = data
    IMAGES[p['zoom']] = data
for o in CAT.get('origins') or []:
    data = stand_in(o['slug'], ['#F2C230', '#2FB58C', '#F2836B'], o['title'])
    for url, _ in o['images']:
        IMAGES[url] = data
    IMAGES[o['zoom']] = data
for b in CAT['books']:
    cover = stand_in(b['slug'], ['#0B3D45', '#E3C258', '#2FB58C'], b['title'], book=True)
    for url, _ in b['cover']:
        IMAGES[url] = cover
    for n, (url, cap) in enumerate(b.get('pages') or []):
        IMAGES[url] = cover if n == 0 else stand_in(url, ['#F4ECD8', '#0F4C5C', '#E3C258'], cap, book=True)
FACES = ''
for fam, folder, weights in (('Barlow Condensed', 'barlow-condensed', (400, 500, 600, 700)),
                             ('Barlow Semi Condensed', 'barlow-semi-condensed', (400, 500, 600))):
    for w in weights:
        FACES += "@font-face{font-family:'%s';font-weight:%d;font-style:normal;src:url('/fonts/%s-latin-%d-normal.woff2') format('woff2');}\n" % (fam, w, folder, w)

page = (REPO / 'pages/art-of-nations.html').read_text()
header = (REPO / 'pages/header.html').read_text()
footer = (REPO / 'pages/footer.html').read_text()
HTML = """<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Art of Nations - Perfect Nations</title>
<style>%s
html,body{margin:0;padding:0;background:#0B3D45;}
body{font-family:'Barlow Semi Condensed',Arial,sans-serif;}
/* Astra-like defaults the page must survive */
h1,h2,h3{text-shadow:0 0 6px rgba(0,0,0,.3);color:#222;}
button{background:#0170B9;color:#fff;padding:10px 20px;border:0;border-radius:2px;}
a{color:#0170B9;text-decoration:underline;}
</style></head><body>
%s
<main id="content" class="site-content"><div class="ast-container"><div class="elementor e-con"><div class="elementor-widget elementor-widget-html">
%s
</div></div></div></main>
%s
</body></html>""" % (FACES, header, page, footer)

ASKED = set()


def route(r):
    url = r.request.url
    if url.startswith('http://pn.local/'):
        p = url[len('http://pn.local/'):]
        if p.startswith('fonts/'):
            name = p[len('fonts/'):]
            folder = 'barlow-semi-condensed' if name.startswith('barlow-semi') else 'barlow-condensed'
            return r.fulfill(path=str(FONTS / folder / 'files' / name), content_type='font/woff2')
        return r.fulfill(body=HTML, content_type='text/html')
    if url.startswith('https://perfectnations.com/wp-content/uploads/'):
        ASKED.add(url)
        if REAL and (REAL / url.rsplit('/', 1)[1]).exists():
            return r.fulfill(path=str(REAL / url.rsplit('/', 1)[1]))
        if url in IMAGES:
            return r.fulfill(body=IMAGES[url], content_type='image/jpeg')
        return r.fulfill(body=stand_in(url, ['#E3C258', '#0B3D45'], 'logo'), content_type='image/jpeg')
    return r.abort()


def run():
    errors, report = [], {}
    with sync_playwright() as pw:
        b = pw.chromium.launch(args=['--use-gl=swiftshader', '--enable-unsafe-swiftshader'])
        for name, vp, mobile in (('laptop', {'width': 1440, 'height': 900}, False), ('phone', {'width': 390, 'height': 844}, True)):
            ctx = b.new_context(viewport=vp, device_scale_factor=2 if mobile else 1, is_mobile=mobile, has_touch=mobile)
            pg = ctx.new_page()
            pg.on('pageerror', lambda e, n=name: errors.append('%s: %s' % (n, e)))
            pg.on('console', lambda m, n=name: errors.append('%s console: %s' % (n, m.text)) if m.type == 'error' else None)
            pg.route('**/*', route)
            pg.goto('http://pn.local/', wait_until='load')
            pg.wait_for_timeout(900)
            hero_top = pg.evaluate("document.querySelector('#pn-art').getBoundingClientRect().top + scrollY")
            pg.evaluate('(y)=>scrollTo(0,y)', hero_top)
            pg.wait_for_timeout(300)
            pg.screenshot(path=str(OUT / ('art-%s-1-first-screen.png' % name)))
            if not mobile:
                box = pg.locator('.aon-stage').bounding_box()
                pg.mouse.move(box['x'] + box['width'] * .85, box['y'] + box['height'] * .2, steps=6)
                pg.wait_for_timeout(800)
                pg.screenshot(path=str(OUT / 'art-laptop-2-frame-turns.png'))
                pg.mouse.move(5, 5)
            before = pg.inner_text('[data-cap-title]')
            pg.wait_for_timeout(7600)
            after = pg.inner_text('[data-cap-title]')
            pg.click('[data-hero="1"]')
            pg.wait_for_timeout(1200)
            clicked = pg.inner_text('[data-cap-title]')
            h = pg.evaluate('document.documentElement.scrollHeight')
            for y in range(0, h, 500):
                pg.evaluate('(y)=>scrollTo(0,y)', y)
                pg.wait_for_timeout(120)
            pg.wait_for_timeout(1200)
            top = pg.evaluate("document.querySelector('#pn-art').getBoundingClientRect().top + scrollY")
            ph = pg.evaluate("document.querySelector('#pn-art').offsetHeight")
            pg.evaluate('scrollTo(0,0)')
            pg.wait_for_timeout(200)
            pg.screenshot(path=str(OUT / ('art-%s-3-page.png' % name)), full_page=True, clip={'x': 0, 'y': top, 'width': vp['width'], 'height': ph})
            wide = pg.evaluate('document.documentElement.scrollWidth')
            origin = ''
            if pg.locator('.aon-origin').count():
                pg.locator('.aon-origin .aon-frame').scroll_into_view_if_needed()
                pg.wait_for_timeout(400)
                pg.screenshot(path=str(OUT / ('art-%s-6-origin.png' % name)))
                pg.click('.aon-origin .aon-frame')
                pg.wait_for_timeout(700)
                origin = pg.inner_text('.aon-view__h') + ' | ' + pg.inner_text('.aon-view__k')
                pg.keyboard.press('Escape')
                pg.wait_for_timeout(300)
            pg.locator('#aon-kenya .aon-frame').scroll_into_view_if_needed()
            pg.click('#aon-kenya .aon-frame')
            pg.wait_for_timeout(900)
            pg.screenshot(path=str(OUT / ('art-%s-4-viewer-painting.png' % name)))
            viewer_title = pg.inner_text('.aon-view__h')
            pg.keyboard.press('ArrowRight')
            pg.wait_for_timeout(500)
            next_title = pg.inner_text('.aon-view__h')
            pg.keyboard.press('Escape')
            pg.wait_for_timeout(300)
            pg.locator('#aon-perfect-barbados [data-look]').first.scroll_into_view_if_needed()
            pg.locator('#aon-perfect-barbados .aon-acts [data-look]').click()
            pg.wait_for_timeout(500)
            pg.click('.aon-next')
            pg.wait_for_timeout(900)
            pg.screenshot(path=str(OUT / ('art-%s-5-viewer-book.png' % name)))
            book_page = pg.inner_text('.aon-view__h') + ' ' + pg.inner_text('.aon-view__n')
            pg.keyboard.press('Escape')
            report[name] = {'page height': ph, 'document width': wide, 'hero': [before, after, clicked],
                            'viewer': [viewer_title, next_title], 'book': book_page, 'origin': origin}
            ctx.close()
        b.close()
    print(json.dumps(report, indent=2))
    print('images asked for:', len(ASKED))
    for u in sorted(ASKED):
        print('  ', u.split('/uploads/')[1])
    print('script errors:', errors or 'none')
    return 1 if errors else 0


if __name__ == '__main__':
    sys.exit(run())
