#!/usr/bin/env python3
"""Render laptop and phone previews of national blueprint pages and measure what each one downloads.

Run from the repository root:
  python3 tools/preview_nations.py kenya barbados afghanistan [--out /tmp/pn-nations] [--fonts DIR] [--libs DIR]
  python3 tools/preview_nations.py --all --no-shots          every open blueprint, measurements only

- Requests for this repository's raw.githubusercontent.com and jsDelivr files are answered from the local
  checkout, so the page reads the local data/*.json, archive/ and pages/manifest.json.
- --libs: a folder with node_modules/globe.gl (npm install globe.gl@2.31.0), so a page that still loads
  globe.gl can be measured as it is today; node_modules/three-globe/example/img/earth-day.jpg stands in for
  the Media Library Earth texture. Without it, those requests fail and the page shows its fallback.
- Other perfectnations.com images (which the build machine cannot reach) are answered with stand-in pictures
  of the same kind, so the layout is exact while the photographs are not.
- --fonts: a folder holding the @fontsource packages barlow-condensed and barlow-semi-condensed.
Writes <slug>-laptop.png (1440 x 900, full page), <slug>-laptop-first.png (the first screen),
<slug>-phone.png (390 x 844, full page) and <slug>-phone-first.png, and prints, for each page: its height, how
far down the ReDesign Studio starts, whether the globe drew, sideways scroll, script errors, and the
requests and bytes downloaded (compressed size estimated with gzip, as the server sends it).
"""
import argparse
import gzip
import io
import json
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
    im.save(buf, 'JPEG', quality=72)
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
    return ''.join(css)


def open_slugs():
    man = json.loads((ROOT / 'pages' / 'manifest.json').read_text(encoding='utf-8'))
    out = []
    for key, v in man['pages'].items():
        m = re.match(r'^pages/blueprint-([a-z-]+)\.html$', v.get('file', ''))
        if key.startswith('pn-bp-') and m:
            out.append(m.group(1))
    return sorted(set(out))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('slugs', nargs='*')
    ap.add_argument('--all', action='store_true')
    ap.add_argument('--out', default='/tmp/pn-nations')
    ap.add_argument('--fonts')
    ap.add_argument('--libs')
    ap.add_argument('--file', help='render this file instead of pages/blueprint-<slug>.html (one slug)')
    ap.add_argument('--pages-dir', help='read pages/blueprint-<slug>.html from this folder instead (for a before and after)')
    ap.add_argument('--no-shots', action='store_true')
    ap.add_argument('--only', choices=['laptop', 'phone'])
    ap.add_argument('--json', help='write the measurements here')
    ap.add_argument('--overlay', help='a folder whose files stand in for the repository files of the same path (for example data/ from an open pull request)')
    args = ap.parse_args()
    slugs = open_slugs() if args.all else args.slugs
    if not slugs:
        sys.exit('name at least one nation, or --all')
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    libs = Path(args.libs) if args.libs else None
    earth = libs / 'node_modules/three-globe/example/img/earth-day.jpg' if libs else None
    globe_js = libs / 'node_modules/globe.gl/dist/globe.gl.min.js' if libs else None
    results = []

    with sync_playwright() as p:
        b = p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist', '--enable-unsafe-swiftshader'])
        for slug in slugs:
            path = Path(args.file) if args.file else (Path(args.pages_dir) if args.pages_dir else ROOT / 'pages') / ('blueprint-%s.html' % slug)
            page_html = path.read_text(encoding='utf-8')
            doc = ('<!DOCTYPE html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
                   '<style>%s body{margin:0;background:#0B3D45}</style></head><body>%s</body></html>') % (font_css(args.fonts), page_html)
            for label, vp, mobile in (('laptop', {'width': 1440, 'height': 900}, False), ('phone', {'width': 390, 'height': 844}, True)):
                if args.only and args.only != label:
                    continue
                stats = {'requests': 0, 'bytes': 0, 'js': 0, 'img': 0, 'data': 0, 'urls': []}
                counter = {'n': 0}

                def note(url, body, kind, packed=True):
                    n = len(gzip.compress(body)) if packed else len(body)
                    stats['requests'] += 1
                    stats['bytes'] += n
                    stats[kind] = stats.get(kind, 0) + n
                    stats['urls'].append((url[:110], n))

                def route(r):
                    url = r.request.url
                    if url.startswith('https://perfectnations.com/blueprints/') and r.request.resource_type == 'document':
                        return r.fulfill(status=200, body=doc, content_type='text/html; charset=utf-8')
                    if url.startswith('https://fonts.local/'):
                        fp = Path(url[len('https://fonts.local'):])
                        return r.fulfill(status=200, body=fp.read_bytes(), content_type='font/woff2')
                    m = re.match(r'https://(?:raw\.githubusercontent\.com/%s/main|cdn\.jsdelivr\.net/gh/%s@main)/([^?#]+)' % (REPO, REPO), url, re.I)
                    if m:
                        fp = ROOT / m.group(1)
                        if args.overlay and (Path(args.overlay) / m.group(1)).exists():
                            fp = Path(args.overlay) / m.group(1)
                        if fp.exists():
                            body = fp.read_bytes()
                            note(url, body, 'data')
                            return r.fulfill(status=200, body=body, content_type='application/json')
                        note(url, b'', 'data')
                        return r.fulfill(status=404, body='')
                    if 'cdn.jsdelivr.net/npm/globe.gl' in url and globe_js and globe_js.exists():
                        body = globe_js.read_bytes()
                        note(url, body, 'js')
                        return r.fulfill(status=200, body=body, content_type='application/javascript')
                    if 'perfectnations.com/wp-content/uploads/' in url and re.search(r'\.(jpe?g|png|webp)(\?|$)', url):
                        if re.search(r'pn-globe-earth|earth-night', url) and earth and earth.exists():
                            body = earth.read_bytes()
                            # the Media Library copy the page asks for is smaller than this stand-in: count by its size
                            sizes = {'1024x512': 52000, '1536x768': 89600, '768x384': 32900}
                            k = next((v for s, v in sizes.items() if s in url), 118900)
                            stats['requests'] += 1
                            stats['bytes'] += k
                            stats['img'] += k
                            stats['urls'].append((url[:110], k))
                            return r.fulfill(status=200, body=body, content_type='image/jpeg')
                        counter['n'] += 1
                        w, h = (150, 150) if '150x150' in url else (768, 560)
                        body = stand_in(w, h, counter['n'])
                        if body:
                            note(url, body, 'img', packed=False)
                            return r.fulfill(status=200, body=body, content_type='image/jpeg')
                        return r.fulfill(status=404, body='')
                    if url.startswith('data:') or url.startswith('about:') or url.startswith('blob:'):
                        return r.continue_()
                    stats['urls'].append(('BLOCKED ' + url[:100], 0))
                    return r.fulfill(status=404, body='')

                ctx = b.new_context(viewport=vp, device_scale_factor=2 if mobile else 1, is_mobile=mobile, has_touch=mobile)
                pg = ctx.new_page()
                errors = []
                pg.on('pageerror', lambda e: errors.append(str(e)[:200]))
                pg.on('console', lambda m: errors.append(m.text[:200]) if m.type == 'error' else None)
                pg.route('**/*', route)
                # The page is opened at its own address, so its images are same-origin, as on the live site.
                pg.goto('https://perfectnations.com/blueprints/%s/' % slug, wait_until='load')
                pg.wait_for_timeout(2500)
                first = None
                if not args.no_shots:
                    first = out / ('%s-%s-first.png' % (slug, label))
                    pg.screenshot(path=str(first))
                h = pg.evaluate('document.documentElement.scrollHeight')
                for y in range(0, h, 600):
                    pg.evaluate('window.scrollTo(0,%d)' % y)
                    pg.wait_for_timeout(90)
                pg.evaluate('window.scrollTo(0,0)')
                pg.wait_for_timeout(1500)
                h = pg.evaluate('document.documentElement.scrollHeight')
                info = pg.evaluate('''() => {
                    const r = document.querySelector('[id^="pn-bp-"]');
                    const st = document.getElementById('bp-studio');
                    const g = r && r.querySelector('.bp-globe-wrap, .bpx-globe');
                    const cv = g && g.querySelector('canvas');
                    return {
                      studio: st ? Math.round(st.getBoundingClientRect().top + window.scrollY) : null,
                      globe: !!(g && (g.classList.contains('is-live') || g.classList.contains('is-on'))),
                      canvas: cv ? [cv.width, cv.height] : null,
                      wide: document.documentElement.scrollWidth > window.innerWidth + 1,
                      live: r && r.getAttribute('data-live'),
                      solutions: document.querySelectorAll('.bpx-sol, .bp-sheet--d').length
                    }; }''')
                res = {'slug': slug, 'view': label, 'height': h, 'studio_y': info['studio'], 'globe': info['globe'],
                       'canvas': info['canvas'], 'sideways': info['wide'], 'solutions': info['solutions'],
                       'html_gz': len(gzip.compress(page_html.encode('utf-8'))), 'requests': stats['requests'] + 1,
                       'bytes': stats['bytes'] + len(gzip.compress(page_html.encode('utf-8'))),
                       'js': stats['js'], 'img': stats['img'], 'data': stats['data'], 'errors': errors[:5],
                       'blocked': [u for u, n in stats['urls'] if u.startswith('BLOCKED')][:5]}
                results.append(res)
                if not args.no_shots:
                    pg.screenshot(path=str(out / ('%s-%s.png' % (slug, label))), full_page=True)
                print('%-18s %-6s height %5d  studio at %5s  globe %-5s  %2d requests  %4d KB (html %3d KB, script %4d KB, images %4d KB, data %3d KB)  sideways %s%s' % (
                    slug, label, h, res['studio_y'], res['globe'], res['requests'], res['bytes'] // 1024, res['html_gz'] // 1024,
                    res['js'] // 1024, res['img'] // 1024, res['data'] // 1024, res['sideways'],
                    ('  ERRORS ' + ' | '.join(errors[:3])) if errors else ''))
                ctx.close()
        b.close()
    if args.json:
        Path(args.json).write_text(json.dumps(results, indent=1), encoding='utf-8')


if __name__ == '__main__':
    main()
