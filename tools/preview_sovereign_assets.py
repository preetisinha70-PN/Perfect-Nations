#!/usr/bin/env python3
"""Headless previews of the Sovereign Assets page, laptop 1440x900 and phone 390x844.

    python3 tools/preview_sovereign_assets.py [--all]

Wraps pages/sovereign-assets.html in the header and footer, routes GitHub and jsDelivr reads to this
repository, uses local Barlow fonts and flag-icons, paints stand-in photographs for the five assets
(the Media Library cannot be reached from here), and blocks every other host. Screenshots go to
/tmp/pn-preview/. --all adds 1280x720 and 820x1180, a live file that changes (the figures, planet and
list must follow) and a live file that fails (the built-in figures must stay). It changes no file.
The stage of five assets is checked from viewport screenshots: Chromium's full-page capture can
paint a hidden scene during a crossfade.
Needs: pip install playwright pillow (Chromium), and once:
    mkdir -p /tmp/pn-fonts && cd /tmp/pn-fonts && npm init -y && npm install @fontsource/barlow-condensed @fontsource/barlow-semi-condensed flag-icons@7.6.0
"""
import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw
from playwright.sync_api import sync_playwright

REPO = Path(__file__).resolve().parent.parent
OUT = Path('/tmp/pn-preview')
OUT.mkdir(exist_ok=True)
IMG = OUT / 'sa-stand-ins'
IMG.mkdir(exist_ok=True)
NODE = Path('/tmp/pn-fonts/node_modules')
FONTS = NODE / '@fontsource'
FLAGS = NODE / 'flag-icons' / 'flags'
PNG1 = bytes.fromhex('89504e470d0a1a0a0000000d4948445200000001000000010806000000'
                     '1f15c4890000000d49444154789c6360000000000200015e2a2d1b0000000049454e44ae426082')
PAINT = {  # stand-in colours for each Media Library photograph, top to bottom
    'inga-rapids': ['#C9D6CF', '#6E8C80', '#3C5B4E', '#1C3029'],
    'barbados-reef-1': ['#BFF3EA', '#3FC4C6', '#0F7FA6', '#0A3E6E', '#061F3D'],
    'jwaneng-mine': ['#D2B183', '#B48A5C', '#8A6E4E', '#3A2E24'],
    'lobito-corridor': ['#F2B36B', '#D9763A', '#9A3E1F', '#5A2213', '#2A120B'],
    'india-varanasi-ghats': ['#F7B34A', '#D9732B', '#8E3A1E', '#3A1A14', '#160B09'],
    'Sun-India': ['#FCE7A2', '#F0B54A', '#C9782A', '#9C4F12', '#4A260C'],
    'Corridor-Angola': ['#F6C887', '#C98A4B', '#7E5A3A', '#4A3A2A', '#22201C'],
}


def stand_in(name):
    f = IMG / name
    if f.exists():
        return f.read_bytes()
    key = next((k for k in PAINT if k in name), None)
    cols = [tuple(int(c[i:i + 2], 16) for i in (1, 3, 5)) for c in (PAINT[key] if key else ['#1F6A78', '#0A3840'])]
    w, h = (1536, 960) if '1536' in name else (1024, 747) if '1024' in name else (768, 560) if '768x560' in name else (768, 480)
    im = Image.new('RGB', (w, h))
    d = ImageDraw.Draw(im)
    for y in range(h):
        t = y / (h - 1) * (len(cols) - 1)
        k = min(int(t), len(cols) - 2)
        f2 = t - k
        d.line([(0, y), (w, y)], fill=tuple(int(cols[k][i] + (cols[k + 1][i] - cols[k][i]) * f2) for i in range(3)))
    d.text((12, h - 22), 'STAND-IN PHOTOGRAPH', fill=(255, 255, 255))
    im.convert('RGB').save(f, format='JPEG', quality=85)
    return f.read_bytes()


def font_css():
    out = []
    for fam, d in (('Barlow Condensed', 'barlow-condensed'), ('Barlow Semi Condensed', 'barlow-semi-condensed')):
        for wt in (400, 500, 600, 700):
            f = FONTS / d / 'files' / ('%s-latin-%d-normal.woff2' % (d, wt))
            if f.exists():
                out.append("@font-face{font-family:'%s';font-weight:%d;src:url('https://fonts.gstatic.com/local/%s/%s') format('woff2');}" % (fam, wt, d, f.name))
    return '\n'.join(out)


def harness():
    rd = lambda p: (REPO / 'pages' / p).read_text(encoding='utf-8')
    return ('<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
            '<style>body{margin:0;background:#0B3D45}</style></head><body>'
            '<div class="elementor-location-header">%s</div>'
            '<div id="content" class="site-content"><div class="ast-container"><div class="e-con"><div class="e-con-inner">'
            '<div class="elementor-widget elementor-widget-html">%s</div></div></div></div></div>'
            '<footer class="elementor-location-footer">%s</footer></body></html>') % (rd('header.html'), rd('sovereign-assets.html'), rd('footer.html'))


def route(r, live):
    u = r.request.url
    if u.startswith('https://pn.local/'):
        return r.fulfill(body=harness(), content_type='text/html')
    if 'fonts.googleapis.com' in u:
        return r.fulfill(body=font_css(), content_type='text/css')
    if 'fonts.gstatic.com/local/' in u:
        d, name = u.split('/local/', 1)[1].split('/', 1)
        f = FONTS / d / 'files' / name
        return r.fulfill(body=f.read_bytes(), content_type='font/woff2') if f.exists() else r.fulfill(status=404, body='')
    if '/flag-icons@' in u:
        f = FLAGS / u.split('/flags/', 1)[1]
        return r.fulfill(body=f.read_bytes(), content_type='image/svg+xml') if f.exists() else r.fulfill(status=404, body='')
    if '/wp-content/uploads/' in u:
        name = u.rsplit('/', 1)[1]
        if name.startswith('pn-asset-') or any(k in name for k in PAINT):
            return r.fulfill(body=stand_in(name), content_type='image/jpeg')
        return r.fulfill(body=PNG1, content_type='image/png')
    if 'sovereign-assets.json' in u:
        if live == 'fail':
            return r.fulfill(status=404, body='')
        d = json.loads((REPO / 'data' / 'sovereign-assets.json').read_text(encoding='utf-8'))
        if live == 'changed':
            d['ledger']['assets'] += 5
            d['ledger']['nations'] += 1
            d['nations'].append({'file': 'test', 'name': 'Testland', 'url': 'https://perfectnations.com/blueprints/testland/',
                                 'assets': 5, 'lat': 50, 'lon': 10})
            d['featured'][2]['figure'] = 'TEST'
        return r.fulfill(body=json.dumps(d), content_type='application/json', headers={'access-control-allow-origin': '*'})
    if u.startswith('data:'):
        return r.continue_()
    return r.fulfill(status=204, body='')


def shoot(p, name, vw, vh, scale, live='same'):
    b = p.chromium.launch()
    ctx = b.new_context(viewport={'width': vw, 'height': vh}, device_scale_factor=scale, is_mobile=vw < 600, has_touch=vw < 600)
    pg = ctx.new_page()
    errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.on('console', lambda m: errs.append(m.text) if m.type == 'error' and live != 'fail' else None)
    pg.route('**/*', lambda r: route(r, live))
    pg.goto('https://pn.local/sovereign-assets/', wait_until='load')
    pg.wait_for_timeout(1800)
    pg.screenshot(path=str(OUT / ('sa-%s-first.png' % name)))
    h = pg.evaluate('document.documentElement.scrollHeight')
    for y in range(0, h, vh // 2):
        pg.evaluate('window.scrollTo(0,%d)' % y)
        pg.wait_for_timeout(120)
    pg.evaluate("document.getElementById('saStage').scrollIntoView({block:'center'})")
    pg.wait_for_timeout(1200)
    pg.screenshot(path=str(OUT / ('sa-%s-stage.png' % name)))
    info = pg.evaluate('''() => {
      const r = document.getElementById('pn-sov');
      return { sideways: document.documentElement.scrollWidth - window.innerWidth,
               sections: [...r.querySelectorAll('section')].map(s => s.className.replace('sa-band ', '') + ' ' + Math.round(s.getBoundingClientRect().height)),
               figures: [...r.querySelectorAll('.sa-figs b')].map(b => b.textContent), nations: r.querySelectorAll('.sa-nl li').length,
               tabs: r.querySelectorAll('.sa-tab').length, third: (r.querySelectorAll('.sa-sc__fig b')[2] || {}).textContent };
    }''')
    pg.evaluate('window.scrollTo(0,0)')
    pg.wait_for_timeout(300)
    pg.screenshot(path=str(OUT / ('sa-%s-full.png' % name)), full_page=True)
    b.close()
    return info, errs


def main():
    runs = [('laptop', 1440, 900, 1, 'same'), ('phone', 390, 844, 2, 'same')]
    if '--all' in sys.argv:
        runs += [('laptop-1280', 1280, 720, 1, 'same'), ('tablet', 820, 1180, 1, 'same'),
                 ('live-changed', 1440, 900, 1, 'changed'), ('live-fail', 390, 844, 2, 'fail')]
    bad = False
    with sync_playwright() as p:
        for name, vw, vh, sc, live in runs:
            info, errs = shoot(p, name, vw, vh, sc, live)
            print(name, json.dumps(info))
            if errs or info['sideways'] > 0:
                bad = True
                print('  PROBLEM:', errs or 'the page scrolls sideways')
    print('screenshots in', OUT)
    sys.exit(1 if bad else 0)


if __name__ == '__main__':
    main()
