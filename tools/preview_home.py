#!/usr/bin/env python3
"""Render laptop and phone previews of the one-file homepage (pages/home.html) with headless Chromium.

Run from the repository root:
  python3 tools/preview_home.py [pages/home.html] --out /tmp/pn-home --libs DIR [--fonts DIR]

- WebGL draws with SwiftShader, so the golden planet renders.
- --libs: a folder with node_modules/three and node_modules/globe.gl
  (npm install three@0.159.0 globe.gl@2.31.0); jsDelivr requests for them are answered from it.
- --fonts: a folder with node_modules/@fontsource/barlow-condensed and barlow-semi-condensed, so the
  previews use the site's own type. If --fonts is not given, --libs is tried.
- Requests for this repository's raw.githubusercontent.com and jsDelivr files are answered from the
  local checkout (manifest, ticker, nation files).
- perfectnations.org images (which the build machine cannot reach) are answered with stand-in
  pictures, so the layout is exact while the photographs are not.
Writes home-laptop.png, home-laptop-first.png (1440 x 900), home-phone.png and home-phone-first.png
(390 x 844), prints the section order, the height of each section, script errors and failed requests.
"""
import argparse
import io
import re
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
REPO = 'preetisinha70-PN/perfect-nations'


def stand_in(w, h, seed):
    try:
        from PIL import Image, ImageDraw
    except ImportError:
        return None
    hues = [(176, 122, 30), (14, 90, 128), (154, 62, 34), (31, 76, 150), (22, 122, 95), (47, 90, 42), (11, 61, 69)]
    c = hues[seed % len(hues)]
    im = Image.new('RGB', (w, h), c)
    d = ImageDraw.Draw(im)
    for i in range(0, h, 6):
        k = i / h
        d.line([(0, i), (w, i)], fill=tuple(int(v * (0.75 + 0.5 * k)) % 256 for v in c))
    d.ellipse([w * 0.55, h * 0.1, w * 0.95, h * 0.75], fill=tuple(min(255, v + 70) for v in c))
    buf = io.BytesIO()
    im.save(buf, 'JPEG', quality=70)
    return buf.getvalue()


def font_css(fonts):
    if not fonts:
        return ''
    base = Path(fonts) / 'node_modules' / '@fontsource'
    css = []
    for fam, folder, weights in (('Barlow Condensed', 'barlow-condensed', (400, 500, 600, 700, 800)),
                                 ('Barlow Semi Condensed', 'barlow-semi-condensed', (400, 500, 600, 700))):
        for wt in weights:
            f = base / folder / 'files' / ('%s-latin-%d-normal.woff2' % (folder, wt))
            if f.exists():
                css.append("@font-face{font-family:'%s';font-weight:%d;font-style:normal;src:url('https://fonts.local%s')}" % (fam, wt, f))
    return '<style>%s</style>' % ''.join(css)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('file', nargs='?', default='pages/home.html')
    ap.add_argument('--out', default='/tmp/pn-home')
    ap.add_argument('--libs')
    ap.add_argument('--fonts')
    ap.add_argument('--only', choices=['laptop', 'phone'])
    args = ap.parse_args()
    libs = Path(args.libs) if args.libs else None
    fonts = args.fonts or args.libs
    page_html = Path(args.file).read_text(encoding='utf-8')
    name = Path(args.file).stem
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    doc = ('<!DOCTYPE html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
           '%s<style>body{margin:0;background:#0B3D45}</style></head><body>%s</body></html>') % (font_css(fonts), page_html)
    counter = {'n': 0}

    def route(r):
        url = r.request.url
        if url.startswith('https://fonts.local/'):
            p = Path(url[len('https://fonts.local'):])
            return r.fulfill(status=200, body=p.read_bytes(), content_type='font/woff2')
        m = re.match(r'https://(?:raw\.githubusercontent\.com/%s/main|cdn\.jsdelivr\.net/gh/%s@main)/([^?#]+)' % (REPO, REPO), url, re.I)
        if m:
            p = ROOT / m.group(1)
            if p.exists():
                kind = {'.webp': 'image/webp', '.png': 'image/png', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg'}.get(p.suffix.lower(), 'application/json')
                return r.fulfill(status=200, body=p.read_bytes(), content_type=kind)
            return r.fulfill(status=404, body='')
        if libs and 'cdn.jsdelivr.net/npm/' in url:
            m = re.search(r'/npm/(three|globe\.gl)@[^/]+/(.+)$', url)
            if m:
                p = libs / 'node_modules' / m.group(1) / m.group(2)
                if p.exists():
                    return r.fulfill(status=200, body=p.read_bytes(), content_type='application/javascript')
        if 'perfectnations.org/wp-content/uploads/' in url and re.search(r'\.(jpe?g|png|webp)(\?|$)', url):
            counter['n'] += 1
            body = stand_in(768, 461, counter['n'])
            return r.fulfill(status=200, body=body, content_type='image/jpeg') if body else r.fulfill(status=404, body='')
        if url.startswith('data:') or url.startswith('about:'):
            return r.continue_()
        return r.fulfill(status=404, body='')

    views = (('laptop', {'width': 1440, 'height': 900}, False), ('phone', {'width': 390, 'height': 844}, True))
    with sync_playwright() as p:
        b = p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist', '--enable-unsafe-swiftshader'])
        for label, vp, mobile in views:
            if args.only and label != args.only:
                continue
            ctx = b.new_context(viewport=vp, device_scale_factor=2 if mobile else 1, is_mobile=mobile, has_touch=mobile)
            pg = ctx.new_page()
            errors, failed = [], []
            pg.on('pageerror', lambda e: errors.append(str(e)))
            pg.on('console', lambda m: errors.append(m.text) if m.type == 'error' else None)
            pg.on('requestfailed', lambda r: failed.append(r.url))
            pg.route('**/*', route)
            pg.set_content(doc, wait_until='load')
            pg.wait_for_timeout(2500)
            pg.screenshot(path=str(out / ('%s-%s-first.png' % (name, label))))
            h = pg.evaluate('document.documentElement.scrollHeight')
            for y in range(0, h, 400):
                pg.evaluate('window.scrollTo(0,%d)' % y)
                pg.wait_for_timeout(140)
            pg.evaluate('window.scrollTo(0,0)')
            pg.wait_for_timeout(2500)
            pg.screenshot(path=str(out / ('%s-%s-first.png' % (name, label))))
            h = pg.evaluate('document.documentElement.scrollHeight')
            wide = pg.evaluate('document.documentElement.scrollWidth > window.innerWidth + 1')
            secs = pg.evaluate('''() => Array.from(document.querySelectorAll('body > section[id], body > div[id^="pn-"], body > div.pn-seam'))
                .map(e => { const r = e.getBoundingClientRect(); const h = e.querySelector('h1,h2');
                  return [e.id || e.className, Math.round(r.height), h ? h.textContent.trim().replace(/\\s+/g, ' ').slice(0, 70) : '']; })''')
            pg.screenshot(path=str(out / ('%s-%s.png' % (name, label))), full_page=True)
            print('%s: height %d px, sideways scroll: %s' % (label, h, wide))
            for sid, sh, head in secs:
                if sh:
                    print('   %-22s %5d px  %s' % (sid[:22], sh, head))
            for e in errors:
                print('   script error:', e[:300])
            for f in failed:
                print('   failed request:', f)
            ctx.close()
        b.close()


if __name__ == '__main__':
    main()
