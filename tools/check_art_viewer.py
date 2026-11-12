"""Open the Art of Nations viewer on every work and every book page at seven screen sizes (phones, a phone on its
side, a tablet, laptops) and report any overlap between the picture, the top bar, the arrows and the caption.

    python3 tools/check_art_viewer.py [--shots]

Stand-in pictures keep each Media Library copy's real proportions (read from the file name). Exit 1 on any overlap.
"""
import io, re, sys, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import preview_art as pa
from PIL import Image, ImageDraw
from playwright.sync_api import sync_playwright

def sized(url):
    m = re.search(r'-(\d+)x(\d+)\.(?:png|jpe?g)$', url)
    w, h = (int(m.group(1)), int(m.group(2))) if m else (1024, 1024)
    im = Image.new('RGB', (w, h), (200, 120, 60))
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, w - 1, h - 1], outline=(255, 255, 255), width=max(4, w // 100))
    d.line([(0, 0), (w, h)], fill=(20, 60, 70), width=6); d.line([(w, 0), (0, h)], fill=(20, 60, 70), width=6)
    b = io.BytesIO(); im.save(b, 'JPEG', quality=60); return b.getvalue()

CACHE = {}
orig_route = pa.route
def route(r):
    url = r.request.url
    if url.startswith('https://perfectnations.com/wp-content/uploads/'):
        if url not in CACHE: CACHE[url] = sized(url)
        return r.fulfill(body=CACHE[url], content_type='image/jpeg')
    return orig_route(r)

MEASURE = """() => {
  const v = document.querySelector('.aon-view');
  const R = s => { const e = v.querySelector(s); if (!e || e.hidden || !e.offsetParent && getComputedStyle(e).position!=='fixed') return null; const r = e.getBoundingClientRect(); return (r.width && r.height) ? {t:r.top,b:r.bottom,l:r.left,r:r.right} : null; };
  return { n: v.querySelector('.aon-view__n').textContent, h: v.querySelector('.aon-view__h').textContent,
    top: R('.aon-view__top'), img: R('.aon-view__img'), cap: R('.aon-view__cap'), hh: R('.aon-view__h'), s: R('.aon-view__s'), k: R('.aon-view__k'), acts: R('.aon-view__acts'),
    prev: R('.aon-prev'), next: R('.aon-next'), x: R('.aon-x'), vh: v.clientHeight, sh: v.scrollHeight, vw: v.clientWidth,
    nat: [v.querySelector('.aon-view__img').naturalWidth, v.querySelector('.aon-view__img').naturalHeight] };
}"""

def hit(a, b):
    return a and b and a['l'] < b['r'] - 1 and b['l'] < a['r'] - 1 and a['t'] < b['b'] - 1 and b['t'] < a['b'] - 1

def problems(m):
    out = []
    img = m['img']
    if not img: return ['no picture']
    if img['t'] < m['top']['b'] - 1: out.append('picture under the top bar')
    for k in ('hh', 's', 'k', 'acts'):
        if hit(img, m[k]): out.append('picture over the caption (%s)' % k)
    for a in ('prev', 'next'):
        if hit(m[a], img): out.append('%s arrow over the picture' % a)
        for k in ('hh', 's', 'k', 'acts'):
            if hit(m[a], m[k]): out.append('%s arrow over the caption (%s)' % (a, k))
    if img['l'] < -1 or img['r'] > m['vw'] + 1: out.append('picture wider than the screen')
    return out

SIZES = [('phone 360x640', 360, 640, True), ('phone 390x844', 390, 844, True), ('phone 412x915', 412, 915, True),
         ('phone landscape 844x390', 844, 390, True), ('tablet 820x1180', 820, 1180, True),
         ('laptop 1280x720', 1280, 720, False), ('laptop 1440x900', 1440, 900, False)]

def run(shots=False):
    bad, sizes = [], {}
    with sync_playwright() as pw:
        b = pw.chromium.launch(args=['--use-gl=swiftshader', '--enable-unsafe-swiftshader'])
        for name, w, h, mobile in SIZES:
            ctx = b.new_context(viewport={'width': w, 'height': h}, device_scale_factor=2 if mobile else 1, is_mobile=mobile, has_touch=mobile)
            pg = ctx.new_page(); pg.route('**/*', route)
            pg.goto('http://pn.local/', wait_until='load'); pg.wait_for_timeout(600)
            # every work: open the first, then step through all of them
            pg.evaluate("document.querySelector('[data-open]').scrollIntoView()")
            first = pg.locator('.aon-origin [data-open], .aon-origin .aon-frame').first
            first.click(); pg.wait_for_timeout(500)
            total = int((pg.inner_text('.aon-view__n') or '1 / 1').split('/')[-1])
            seen = []
            for i in range(total):
                pg.wait_for_function("() => { const i=document.querySelector('.aon-view__img'); return i.complete && i.naturalWidth > 0; }", timeout=5000)
                pg.wait_for_timeout(60)
                m = pg.evaluate(MEASURE)
                p = problems(m)
                seen.append((m['h'], round(m['img']['r'] - m['img']['l']) if m['img'] else 0, round(m['img']['b'] - m['img']['t']) if m['img'] else 0, m['sh'] > m['vh'] + 1))
                if p: bad.append((name, m['n'], m['h'], p))
                if shots and i in (0, 1, 5):
                    pg.screenshot(path='/tmp/pn-preview/viewer-%s-%02d.png' % (name.replace(' ', '_'), i))
                pg.keyboard.press('ArrowRight')
            pg.keyboard.press('Escape'); pg.wait_for_timeout(200)
            # every book page
            for bk in pg.locator('.aon-bk').all():
                bk.locator('.aon-acts [data-look]').first.scroll_into_view_if_needed()
                bk.locator('.aon-acts [data-look]').first.click(); pg.wait_for_timeout(400)
                n = pg.inner_text('.aon-view__n') or '1 / 1'
                for i in range(int(n.split('/')[-1])):
                    pg.wait_for_function("() => { const i=document.querySelector('.aon-view__img'); return i.complete && i.naturalWidth > 0; }", timeout=5000)
                    pg.wait_for_timeout(60)
                    m = pg.evaluate(MEASURE); p = problems(m)
                    if p: bad.append((name, 'book ' + m['n'], m['h'], p))
                    pg.keyboard.press('ArrowRight')
                pg.keyboard.press('Escape'); pg.wait_for_timeout(200)
            sizes[name] = {'works': total, 'smallest picture': min(s[1] * s[2] for s in seen) ** .5 // 1, 'scrolls': sum(1 for s in seen if s[3])}
            ctx.close()
        b.close()
    for k, v in sizes.items(): print(k, v)
    print('problems:', len(bad))
    seen_kind = {}
    for name, n, h, p in bad:
        key = (name, tuple(p))
        seen_kind.setdefault(key, []).append(h)
    for (name, p), hs in seen_kind.items():
        print(' ', name, '|', '; '.join(p), '|', len(hs), 'works, e.g.', hs[:3])
    return len(bad)

if __name__ == '__main__':
    sys.exit(1 if run('--shots' in sys.argv) else 0)
