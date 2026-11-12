#!/usr/bin/env python3
"""Render laptop and phone previews of a page file with headless Chromium (Playwright).

Run from the repository root:
  python3 tools/preview_page.py pages/perfect-capita.html --out /tmp/previews [--fonts DIR]

- WebGL draws with SwiftShader, so the hero shader renders.
- Requests for this repository's raw.githubusercontent.com and jsDelivr files are answered from the
  local checkout, so the page reads the local figures/*.json and data/*.json.
- perfectnations.com images (which the build machine cannot reach) are answered with stand-in
  pictures drawn here, so the layout is exact while the photographs are not.
- --fonts: a folder holding the @fontsource packages barlow-condensed and barlow-semi-condensed
  (npm install @fontsource/barlow-condensed @fontsource/barlow-semi-condensed), so the previews use
  the site's own type. Without it the fallbacks (Arial Narrow, Arial) are used.
Writes <name>-laptop.png (1440 x 900, full page), <name>-phone.png (390 x 844, full page) and
<name>-phone-first.png (the first phone screen), and prints any script errors and failed requests.
"""
import argparse
import io
import re
import sys
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
    for fam, folder, weights in (('Barlow Condensed', 'barlow-condensed', (500, 600, 700)),
                                 ('Barlow Semi Condensed', 'barlow-semi-condensed', (400, 500, 600))):
        for wt in weights:
            f = base / folder / 'files' / ('%s-latin-%d-normal.woff2' % (folder, wt))
            if f.exists():
                css.append("@font-face{font-family:'%s';font-weight:%d;font-style:normal;src:url('https://fonts.local/%s')}" % (fam, wt, f))
    return '<style>%s body{margin:0;background:#0B3D45} </style>' % ''.join(css)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('file')
    ap.add_argument('--out', default='/tmp/previews')
    ap.add_argument('--fonts')
    args = ap.parse_args()
    page_html = Path(args.file).read_text(encoding='utf-8')
    name = Path(args.file).stem
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    doc = '<!DOCTYPE html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">%s</head><body>%s</body></html>' % (
        font_css(args.fonts) or '<style>body{margin:0}</style>', page_html)
    counter = {'n': 0}

    def route(r):
        url = r.request.url
        if url.startswith('https://fonts.local/'):
            p = Path(url[len('https://fonts.local'):])
            return r.fulfill(status=200, body=p.read_bytes(), content_type='font/woff2')
        m = re.match(r'https://(?:raw\.githubusercontent\.com/%s/main|cdn\.jsdelivr\.net/gh/%s@main)/(.+)$' % (REPO, REPO), url, re.I)
        if m:
            p = ROOT / m.group(1)
            if p.exists():
                return r.fulfill(status=200, body=p.read_bytes(), content_type='application/json')
            return r.fulfill(status=404, body='')
        if 'perfectnations.com/wp-content/uploads/' in url and re.search(r'\.(jpe?g|png|webp)$', url):
            counter['n'] += 1
            body = stand_in(768, 461, counter['n'])
            return r.fulfill(status=200, body=body, content_type='image/jpeg') if body else r.fulfill(status=404, body='')
        if url.startswith('data:') or url.startswith('about:'):
            return r.continue_()
        return r.fulfill(status=404, body='')

    with sync_playwright() as p:
        b = p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        for label, vp, mobile in (('laptop', {'width': 1440, 'height': 900}, False), ('phone', {'width': 390, 'height': 844}, True)):
            ctx = b.new_context(viewport=vp, device_scale_factor=2 if mobile else 1, is_mobile=mobile, has_touch=mobile)
            pg = ctx.new_page()
            errors, failed = [], []
            pg.on('pageerror', lambda e: errors.append(str(e)))
            pg.on('console', lambda m: errors.append(m.text) if m.type == 'error' else None)
            pg.on('requestfailed', lambda r: failed.append(r.url))
            pg.route('**/*', route)
            pg.set_content(doc, wait_until='load')
            pg.wait_for_timeout(1500)
            h = pg.evaluate('document.documentElement.scrollHeight')
            for y in range(0, h, 500):
                pg.evaluate('window.scrollTo(0,%d)' % y)
                pg.wait_for_timeout(120)
            pg.evaluate('window.scrollTo(0,0)')
            pg.wait_for_timeout(3200)
            wide = pg.evaluate('document.documentElement.scrollWidth > window.innerWidth + 1')
            info = pg.evaluate('''() => { const r = document.querySelector('[id^="pn-"]');
                return { figures: r && r.getAttribute('data-figures'),
                         heads: Array.from(document.querySelectorAll('h1,h2')).map(h => h.textContent.trim()) }; }''')
            if label == 'phone':
                pg.screenshot(path=str(out / ('%s-phone-first.png' % name)))
            pg.screenshot(path=str(out / ('%s-%s.png' % (name, label))), full_page=True)
            print('%s: height %d px, sideways scroll: %s, live figures: %s' % (label, h, wide, info['figures']))
            if label == 'laptop':
                for t in info['heads']:
                    print('   ', t)
            for e in errors:
                print('   script error:', e)
            for f in failed:
                print('   failed request:', f)
            ctx.close()
        b.close()


if __name__ == '__main__':
    main()
