#!/usr/bin/env python3
"""National Day share cards for a nation (the Blueprints Steward, from 15 November 2026).

Draws two PNG cards in the blueprint palette for the morning of a nation's National Day: a square card
(1080 x 1080, Instagram and Facebook) and a wide card (1200 x 627, LinkedIn and X). Every card carries the
greeting, the date, the nation's outline (the mainland of the blueprint's own globe outline), the line that
Perfect Nations honours the nation and the link to its blueprint. Text comes from data/nation-protocol.json.

Usage: python3 tools/national_day_card.py <slug> --fonts <folder holding node_modules/@fontsource> [--out <folder>]
"""
import argparse, json, math, sys
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'tools'))
from build_nations import the_name, MONTH  # noqa: E402
from preview_nations import font_css  # noqa: E402

CSS = '''html,body{margin:0;overflow:hidden}
.c{position:relative;box-sizing:border-box;color:#F5F1E8;font-family:"Barlow Semi Condensed",sans-serif;overflow:hidden;
  background:radial-gradient(110% 90% at 80% 42%, #155a65 0%, #0B3D45 45%, #082A30 100%)}
.c:before{content:"";position:absolute;inset:var(--in);border:1px solid rgba(227,194,88,.38);border-radius:18px;pointer-events:none}
.k{position:relative;font-family:"Barlow Condensed",sans-serif;font-weight:700;letter-spacing:.24em;text-transform:uppercase;color:#E3C258;font-size:var(--k)}
h1{position:relative;margin:var(--hm);font-family:"Barlow Condensed",sans-serif;font-weight:600;font-size:var(--h);line-height:.95;color:#F5F1E8}
h1 em{font-style:normal;color:#E3C258}
p{position:relative;margin:0;max-width:var(--pw);font-size:var(--p);line-height:1.38;color:rgba(245,241,232,.86)}
.u{position:absolute;left:var(--pad);bottom:var(--pad);font-family:"Barlow Condensed",sans-serif;font-weight:700;letter-spacing:.14em;text-transform:uppercase;font-size:var(--u)}
.u b{color:#E3C258}
.m{position:absolute;right:var(--pad);top:var(--pad);font-family:"Barlow Condensed",sans-serif;font-weight:700;letter-spacing:.26em;text-transform:uppercase;font-size:var(--u);color:#E3C258}
.cal{display:inline-flex;flex-direction:column;align-items:center;justify-content:center;width:var(--cw);height:var(--cw);border:1.5px solid rgba(227,194,88,.7);border-radius:14px;background:rgba(227,194,88,.08);margin-bottom:var(--cm)}
.cal b{font-family:"Barlow Condensed",sans-serif;font-size:var(--cb);line-height:1;color:#E3C258}
.cal i{font-style:normal;font-family:"Barlow Condensed",sans-serif;font-weight:700;letter-spacing:.2em;font-size:var(--ci);color:rgba(245,241,232,.84);text-transform:uppercase}
svg{position:absolute;right:var(--sr);top:var(--st);filter:drop-shadow(0 0 22px rgba(227,194,88,.32))}'''
SIZES = (('square', 1080, 1080, 380,
          '--pad:84px;--in:34px;--k:22px;--hm:24px 0 26px;--h:112px;--pw:500px;--p:29px;--u:20px;--cw:96px;--cm:30px;--cb:46px;--ci:15px;--sr:80px;--st:540px'),
         ('wide', 1200, 627, 380,
          '--pad:56px;--in:22px;--k:17px;--hm:14px 0 16px;--h:80px;--pw:560px;--p:21px;--u:16px;--cw:72px;--cm:18px;--cb:34px;--ci:12px;--sr:80px;--st:118px'))


def mainland(outline):
    """The rings of the nation's mainland: the largest ring and every ring within 12 degrees of it."""
    rings = []
    for f in outline:
        for poly in (f['coordinates'] if f['type'] == 'MultiPolygon' else [f['coordinates']]):
            rings.append(poly[0])
    def area(r):
        return abs(sum(x0 * y1 - x1 * y0 for (x0, y0), (x1, y1) in zip(r, r[1:] + r[:1]))) / 2
    def centre(r):
        return sum(x for x, _ in r) / len(r), sum(y for _, y in r) / len(r)
    big = max(rings, key=area)
    cx, cy = centre(big)
    return [r for r in rings if abs(centre(r)[0] - cx) < 12 and abs(centre(r)[1] - cy) < 12]


def path(rings, size):
    lat0 = sum(y for r in rings for _, y in r) / sum(len(r) for r in rings)
    k = math.cos(math.radians(lat0))
    xs = [x * k for r in rings for x, _ in r]
    ys = [y for r in rings for _, y in r]
    minx, maxy = min(xs), max(ys)
    w, h = max(xs) - minx, maxy - min(ys)
    s = size / max(w, h)
    d = ' '.join('M' + ' L'.join('%.1f %.1f' % ((x * k - minx) * s, (maxy - y) * s) for x, y in r) + ' Z' for r in rings)
    return d, w * s, h * s


def card(slug, fonts):
    pro = json.loads((ROOT / 'data' / 'nation-protocol.json').read_text(encoding='utf-8'))['nations'][slug]
    nd = pro['national_day']
    name = pro['nation']
    idx = json.loads((ROOT / 'data' / 'blueprints.json').read_text(encoding='utf-8'))
    url = next((n['url'] for n in idx['open'] if n['slug'] == slug), 'https://perfectnations.com/blueprints/%s/' % slug)
    short = url.replace('https://', '').rstrip('/')
    rings = mainland(json.loads((ROOT / 'tools' / 'nation' / ('%s.json' % slug)).read_text(encoding='utf-8'))['globe']['outline'])
    local = nd.get('name') if nd.get('name') and nd.get('name') != nd.get('name_en') else ''
    kicker = ('%s &#183; ' % escape(local) if local else '') + 'National Day of %s' % escape(the_name(name))
    greet = escape(nd.get('greeting') or 'Happy National Day')
    honour = escape(nd.get('honour') or the_name(name))
    out = {}
    for label, w, h, size, v in SIZES:
        d, ow, oh = path(rings, size)
        out[label] = (w, h, '<!DOCTYPE html><html><head><meta charset="utf-8"><style>%s %s</style></head><body>'
            '<div class="c" style="width:%dpx;height:%dpx;padding:var(--pad);%s">'
            '<svg width="%.0f" height="%.0f" viewBox="0 0 %.1f %.1f"><path d="%s" fill="rgba(227,194,88,.09)" stroke="#E3C258" stroke-width="2.4" stroke-linejoin="round"/></svg>'
            '<div class="m">Perfect Nations&#174;</div><div class="cal"><b>%d</b><i>%s</i></div>'
            '<div class="k">%s</div><h1>%s,<br><em>%s.</em></h1>'
            '<p>Perfect Nations honours %s and its people. Our blueprint shows what %s owns, and how it can secure seven basic standards of living for all.</p>'
            '<div class="u">Read <b>Perfect %s</b> &#183; %s</div></div></body></html>'
            % (font_css(fonts), CSS, w, h, v, ow, oh, ow, oh, d, nd['day'], MONTH[nd['month'] - 1], kicker, greet,
               escape(name), honour, escape(the_name(name)), escape(name), escape(short)))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('slug')
    ap.add_argument('--fonts', required=True)
    ap.add_argument('--out', default='/tmp/pn-national-day')
    a = ap.parse_args()
    from playwright.sync_api import sync_playwright
    Path(a.out).mkdir(parents=True, exist_ok=True)
    cards = card(a.slug, a.fonts)
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        for label, (w, h, html) in cards.items():
            pg = b.new_page(viewport={'width': w, 'height': h})
            pg.route('**/*', lambda r: r.fulfill(status=200, body=Path(r.request.url[len('https://fonts.local'):]).read_bytes(), content_type='font/woff2')
                     if r.request.url.startswith('https://fonts.local/') else r.continue_())
            pg.set_content(html, wait_until='load')
            pg.wait_for_timeout(500)
            f = Path(a.out) / ('%s-national-day-%s.png' % (a.slug, label))
            pg.screenshot(path=str(f))
            pg.close()
            print(f)
        b.close()


if __name__ == '__main__':
    main()
