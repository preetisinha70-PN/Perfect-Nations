#!/usr/bin/env python3
"""Build the one-file Perfect Nations Blueprints page and its live index.

Writes two files:
  pages/blueprints.html   the whole /blueprints/ page (root pn-blueprints), pasted once into ONE
                          Elementor Custom HTML widget on page 14775; the Perfect Nations Live Pages
                          plugin serves this file in place of the paste.
  data/blueprints.json    the live index of open blueprints (name, region, Nation Steward, headline
                          figure). The page reads it on every visit, so the figures follow the
                          Nation Stewards without a new page version.

What counts as an open blueprint: every pn-bp-<slug> key in pages/manifest.json (the same list the
homepage planet, the Nations Menu and the homepage count read). The page also reads the manifest on
every visit, so a blueprint merged there turns gold on the map, joins the tiles, the counts and the
atlas at once, before this build runs again.

The world: the outlines and the nation table are read from pages/home-hero.html (window.PNHG_WORLD
and window.PNHG_CFG, Natural Earth 1:50m), so the homepage planet and this map share one source.
The map is drawn here, at build time, on the Equal Earth projection (every nation at its true size),
so the page paints its map with no script and no geodata request.

The page itself is pages/blueprints-atlas.html (style, markup, script; edit that file), with slots
the build fills:  <!--pn:map-->  <!--pn:tabs-->  <!--pn:tiles-->  <!--pn:regions-->  <!--pn:seam-->
<!--pn:n-live-->  <!--pn:n-regions-->  <!--pn:n-total-->  <!--pn:n-soon-->  /*pn:cfg*/null

Run from the repository root:
  python3 tools/build_blueprints.py            build both files
  python3 tools/build_blueprints.py --index    rebuild data/blueprints.json only (no page change)
Then, for a page change: raise "pn-blueprints" in pages/manifest.json and open a pull request
"For approval: Blueprints page vX.Y, ...". The index alone may go straight to main (it is data).
"""
import html
import json
import math
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PAGES = ROOT / 'pages'
DATA = ROOT / 'data'
VERSION = '6.1'

ORDER = [
    'nations-menu.html',      # the moving list of 195 nations (also on the homepage)
    'home-seams.html',        # the painted-seam drawings and strip style (shared with the homepage)
    'blueprints-atlas.html',  # 01 the golden map, 02 the open blueprints, 03 every nation
]

BASE = 'https://perfectnations.org/blueprints/'
# The frames the region tabs fly to: [west, east, south, north] in degrees. The world frame leaves
# out Antarctica; Oceania stops at Samoa and Tonga rather than running on into an empty Pacific.
VIEWS = {'world': [-180, 180, -58, 84], 'oceania': [110, 194, -48, 9]}
SHORT = {'africa': 'Africa', 'asia': 'Asia', 'middle-east': 'Middle East', 'europe': 'Europe',
         'americas': 'Americas', 'oceania': 'Oceania'}

# ---------------------------------------------------------------- the Equal Earth projection
A1, A2, A3, A4 = 1.340264, -0.081106, 0.000893, 0.003796
M = math.sqrt(3) / 2
RAD = math.pi / 180


def ee(lon, lat):
    th = math.asin(M * math.sin(lat * RAD))
    t2 = th * th
    t6 = t2 * t2 * t2
    x = 2 * math.sqrt(3) * (lon * RAD) * math.cos(th) / (3 * (9 * A4 * t6 * t2 + 7 * A3 * t6 + 3 * A2 * t2 + A1))
    y = th * (A1 + A2 * t2 + t6 * (A3 + A4 * t2))
    return x, y


MAXX = ee(180, 0)[0]
MAXY = ee(0, 90)[1]
VW = 10000
SCALE = VW / (2 * MAXX)
VH = int(round(2 * MAXY * SCALE))


def px(lon, lat):
    x, y = ee(lon, lat)
    return (x + MAXX) * SCALE, (MAXY - y) * SCALE


def ipt(lon, lat):
    x, y = px(lon, lat)
    return int(round(x)), int(round(y))


def num_join(vals):
    """SVG numbers, as short as possible: a minus sign separates numbers by itself."""
    out = ''
    for v in vals:
        s = str(v)
        out += s if (not out or s.startswith('-')) else ' ' + s
    return out


def ring_d(points, close=True):
    pts = []
    for lon, lat in points:
        p = ipt(lon, lat)
        if not pts or p != pts[-1]:
            pts.append(p)
    if close and len(pts) > 1 and pts[0] == pts[-1]:
        pts.pop()
    if len(pts) < (3 if close else 2):
        return '', None
    d = 'M' + num_join(pts[0])
    rel = []
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        rel += [x1 - x0, y1 - y0]
    d += 'l' + num_join(rel) + ('z' if close else '')
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    return d, (min(xs), min(ys), max(xs), max(ys))


def decode(ring):
    x = y = 0
    out = []
    for i in range(0, len(ring), 2):
        x += ring[i]
        y += ring[i + 1]
        out.append((x / 100.0, y / 100.0))
    return out


# ---------------------------------------------------------------- inputs
def read_world():
    src = (PAGES / 'home-hero.html').read_text(encoding='utf-8')
    w = re.search(r'window\.PNHG_WORLD=(\[.*?\]\]\]\]);', src, re.S)
    c = re.search(r'window\.PNHG_CFG=(\{.*?\});\s*\n', src, re.S)
    if not w or not c:
        sys.exit('pages/home-hero.html no longer declares PNHG_WORLD and PNHG_CFG; the map has no source')
    return json.loads(w.group(1)), json.loads(c.group(1))


def read_open(nations):
    man = json.loads((PAGES / 'manifest.json').read_text(encoding='utf-8'))
    out = []
    for k in man.get('pages', {}):
        m = re.match(r'^pn-bp-([a-z0-9-]+)$', k)
        if m:
            if m.group(1) in nations:
                out.append(m.group(1))
            else:
                print('warning: %s is in the manifest but not in the nation table' % k)
    return sorted(set(out))


MONEY = re.compile(r'(US\$|\$|€|£|¥|RMB|\bN\d|\bKSh|\bR\d|billion|million|trillion|\bbn\b)', re.I)


def headline(stats):
    """The tile figure: the first sourced monetary figure of the hero (the top instrument), else the first figure."""
    stats = [s for s in (stats or []) if isinstance(s, dict) and s.get('value')]
    if not stats:
        return None
    for s in stats:
        if MONEY.search(str(s.get('value', ''))):
            return {'value': s['value'], 'label': s.get('label', ''), 'money': True}
    s = stats[0]
    return {'value': s['value'], 'label': s.get('label', ''), 'money': False}


def plain(s):
    return html.unescape(s)


def ent(s):
    """Plain text to ASCII-only HTML."""
    return html.escape(plain(s), quote=True).encode('ascii', 'xmlcharrefreplace').decode('ascii')


# ---------------------------------------------------------------- the map
def build_map(world, cfg, open_set):
    nat = cfg['nations']
    region_of = {s: v[4] for s, v in nat.items()}
    lands, soon, live, dots = [], [], [], []
    boxes = {}
    drawn = set()
    for slug, rings in world:
        parts, best, best_area = [], None, -1
        for r in rings:
            pts = decode(r)
            d, bb = ring_d(pts)
            if d:
                parts.append(d)
                area = (bb[2] - bb[0]) * (bb[3] - bb[1])
                if area > best_area:
                    best, best_area = bb, area
            # the Pacific beyond the date line is drawn a second time, a full turn east, so the
            # Oceania view shows Samoa, Tonga and eastern Fiji beside the rest of the Pacific
            if pts and max(p[0] for p in pts) < -150 and min(p[1] for p in pts) < 25:
                d2, _ = ring_d([(lon + 360, lat) for lon, lat in pts])
                if d2:
                    parts.append(d2)
        if not parts:
            continue
        d = ''.join(parts)
        if not slug or slug not in nat:
            lands.append('<path d="%s"/>' % d)
            continue
        drawn.add(slug)
        boxes[slug] = best
        name = ent(nat[slug][0])
        st = 'live' if slug in open_set else 'soon'
        path = '<path id="pnbpa-c-%s" class="pnbpa-c pnbpa-c--%s" data-s="%s" d="%s"><title>%s</title></path>' % (slug, st, slug, d, name)
        if st == 'live':
            live.append('<a href="%s" target="_blank" rel="noopener noreferrer" aria-label="%s, open the blueprint in a new tab">%s</a>'
                        % (BASE + cfg.get('paths', {}).get(slug, slug) + '/', name, path))
        else:
            soon.append(path)
    # a marker for every nation too small to find at world scale, and for any nation with no outline
    for slug, rec in nat.items():
        bb = boxes.get(slug)
        if bb and max(bb[2] - bb[0], bb[3] - bb[1]) > 70:
            continue
        lon, lat = rec[3], rec[2]
        x, y = ipt(lon, lat)
        st = 'live' if slug in open_set else 'soon'
        name = ent(rec[0])
        dot = '<circle class="pnbpa-dot pnbpa-dot--%s" data-s="%s" cx="%d" cy="%d" r="40"><title>%s</title></circle>' % (st, slug, x, y, name)
        if lon < -150 and lat < 25:
            x2, y2 = ipt(lon + 360, lat)
            dot += '<circle class="pnbpa-dot pnbpa-dot--%s" data-s="%s" cx="%d" cy="%d" r="40"><title>%s</title></circle>' % (st, slug, x2, y2, name)
        if st == 'live':
            dot = '<a href="%s" target="_blank" rel="noopener noreferrer" aria-label="%s, open the blueprint in a new tab">%s</a>' % (
                BASE + cfg.get('paths', {}).get(slug, slug) + '/', name, dot)
        dots.append(dot)
        if slug not in boxes:
            boxes[slug] = (x - 60, y - 60, x + 60, y + 60)
    # the graticule and the rim of the world
    grat = []
    for lon in range(-150, 151, 30):
        d, _ = ring_d([(lon, lat) for lat in range(-90, 91, 2)], close=False)
        grat.append(d)
    for lat in (-60, -30, 0, 30, 60):
        d, _ = ring_d([(lon, lat) for lon in range(-180, 181, 2)], close=False)
        grat.append(d)
    rim_pts = [(-180, lat) for lat in range(-90, 91, 1)] + [(180, lat) for lat in range(90, -91, -1)]
    rim, _ = ring_d(rim_pts)
    svg = (
        '<svg class="pnbpa-svg" id="pnbpaSvg" viewBox="0 0 %d %d" preserveAspectRatio="xMidYMid meet" role="img" '
        'aria-labelledby="pnbpaMapT" xmlns="http://www.w3.org/2000/svg">'
        '<title id="pnbpaMapT">Every nation on Earth at its true size. Nations with an open blueprint are bright gold; '
        'the others are in preparation.</title>'
        '<path class="pnbpa-rimfill" d="%s"/>'
        '<path class="pnbpa-grat" d="%s"/>'
        '<g class="pnbpa-lands">%s</g>'
        '<g class="pnbpa-soon">%s</g>'
        '<g class="pnbpa-live">%s</g>'
        '<g class="pnbpa-dots">%s</g>'
        '<path class="pnbpa-rim" d="%s"/>'
        '</svg>'
    ) % (VW, VH, rim, ''.join(grat), ''.join(lands), ''.join(soon), ''.join(live), ''.join(dots), rim)
    return svg, boxes, drawn


def region_box(win, pad_share=0.03):
    west, east, south, north = win
    xs, ys = [], []
    for i in range(61):
        t = i / 60.0
        for lon, lat in ((west + (east - west) * t, south), (west + (east - west) * t, north),
                         (west, south + (north - south) * t), (east, south + (north - south) * t)):
            x, y = px(lon, lat)
            xs.append(x)
            ys.append(y)
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    pad = pad_share * max(x1 - x0, y1 - y0)
    return [int(x0 - pad), int(y0 - pad), int(x1 - x0 + 2 * pad), int(y1 - y0 + 2 * pad)]


def tile_box(bb):
    x0, y0, x1, y1 = bb
    w, h = max(x1 - x0, 1), max(y1 - y0, 1)
    side = max(w, h) * 1.12
    cx, cy = (x0 + x1) / 2.0, (y0 + y1) / 2.0
    return '%d %d %d %d' % (cx - side / 2, cy - side / 2, side, side)


# ---------------------------------------------------------------- the open blueprints
def read_cards(open_slugs, nat, paths):
    cards = []
    for slug in open_slugs:
        f = DATA / (slug + '.json')
        steward, fig = '', None
        if f.exists():
            try:
                d = json.loads(f.read_text(encoding='utf-8'))
                steward = (d.get('steward') or {}).get('name', '')
                fig = headline((d.get('hero') or {}).get('stats'))
            except ValueError:
                print('warning: %s is not valid JSON; its tile shows the name only' % f.name)
        cards.append({
            'slug': slug,
            'name': plain(nat[slug][0]),
            'region': nat[slug][4],
            'url': BASE + paths.get(slug, slug) + '/',
            'steward': steward,
            'figure': fig,
        })
    cards.sort(key=lambda c: c['name'].lower())
    return cards


def tile_html(c, box):
    fig = c.get('figure')
    fig_html = ''
    if fig:
        fig_html = '<span class="pnbpa-t__v%s">%s</span><span class="pnbpa-t__l">%s</span>' % (
            ' is-money' if fig.get('money') else '', ent(fig['value']), ent(fig.get('label', '')))
    stw = '<span class="pnbpa-t__s">%s, Nation Steward</span>' % ent(c['steward']) if c.get('steward') else ''
    return (
        '<li class="pnbpa-t" data-s="%(slug)s" data-r="%(region)s">'
        '<a href="%(url)s" target="_blank" rel="noopener noreferrer">'
        '<svg class="pnbpa-t__sil" viewBox="%(box)s" aria-hidden="true" focusable="false"><use href="#pnbpa-c-%(slug)s"/></svg>'
        '<span class="pnbpa-t__n">%(name)s</span><span class="pnbpa-t__r">%(rname)s</span>%(fig)s%(stw)s'
        '<span class="pnbpa-t__go" aria-hidden="true"></span></a></li>'
    ) % {'slug': c['slug'], 'region': c['region'], 'url': c['url'], 'box': box, 'name': ent(c['name']),
         'rname': SHORT.get(c['region'], ''), 'fig': fig_html, 'stw': stw}


# ---------------------------------------------------------------- the build
def write_index(cards):
    index = {
        'about': 'The open blueprints on perfectnations.org/blueprints/, built by tools/build_blueprints.py from '
                 'pages/manifest.json and data/<nation>.json. Read by the Blueprints page on every visit.',
        'updated': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%MZ'),
        'count': len(cards),
        'open': cards,
    }
    old = None
    p = DATA / 'blueprints.json'
    if p.exists():
        try:
            old = json.loads(p.read_text(encoding='utf-8'))
        except ValueError:
            old = None
    if old and old.get('open') == cards:
        print('data/blueprints.json unchanged (%d open)' % len(cards))
        return False
    p.write_text(json.dumps(index, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print('data/blueprints.json', len(cards), 'open blueprints')
    return True


def main():
    index_only = '--index' in sys.argv
    world, cfg = read_world()
    nat = cfg['nations']
    paths = cfg.get('paths', {})
    open_slugs = read_open(nat)
    open_set = set(open_slugs)
    cards = read_cards(open_slugs, nat, paths)
    write_index(cards)
    if index_only:
        return

    svg, boxes, drawn = build_map(world, cfg, open_set)

    regions = cfg['regions']
    n_live = len(open_slugs)
    reg_live = {r['key']: sum(1 for s in r['slugs'] if s in open_set) for r in regions}
    n_regions = sum(1 for k in reg_live if reg_live[k])

    tabs = ['<button type="button" class="pnbpa-tab" data-r="world" aria-pressed="true">World<b>%d</b></button>' % n_live]
    for r in regions:
        tabs.append('<button type="button" class="pnbpa-tab" data-r="%s" aria-pressed="false">%s<b>%d</b></button>'
                    % (r['key'], SHORT[r['key']], reg_live[r['key']]))

    tiles = ''.join(tile_html(c, tile_box(boxes[c['slug']])) for c in cards)

    blocks = []
    for i, r in enumerate(regions):
        items = []
        names = sorted(r['slugs'], key=lambda s: plain(nat[s][0]).lower())
        for s in names:
            nm = ent(nat[s][0])
            if s in open_set:
                items.append('<li><a class="pnbpa-n is-open" data-s="%s" href="%s" target="_blank" rel="noopener noreferrer">%s</a></li>'
                             % (s, BASE + paths.get(s, s) + '/', nm))
            else:
                items.append('<li><span class="pnbpa-n" data-s="%s">%s</span></li>' % (s, nm))
        live_n = reg_live[r['key']]
        blocks.append(
            '<details class="pnbpa-reg" data-r="%(k)s"><summary><span class="pnbpa-reg__no" aria-hidden="true">%(no)02d</span>'
            '<span class="pnbpa-reg__h">%(name)s</span><span class="pnbpa-reg__m"><b>%(n)d</b> nations &middot; '
            '<b class="pnbpa-reg__open">%(live)d</b> open</span><span class="pnbpa-reg__chev" aria-hidden="true"></span></summary>'
            '<ul class="pnbpa-names">%(items)s</ul></details>'
            % {'k': r['key'], 'no': i + 1, 'name': ent(r['name']), 'n': len(r['slugs']), 'live': live_n, 'items': ''.join(items)})

    vb = {'world': region_box(VIEWS['world'], 0.012)}
    for r in regions:
        vb[r['key']] = region_box(VIEWS.get(r['key'], r['win']))
    asp = '%.3f' % (vb['world'][2] / float(vb['world'][3]))
    js_cfg = {
        'base': BASE,
        'paths': paths,
        'vw': VW,
        'views': vb,
        'regions': [[r['key'], plain(r['name']), SHORT[r['key']]] for r in regions],
        'nations': {s: [plain(v[0]), v[4]] for s, v in nat.items()},
        'boxes': {s: tile_box(b) for s, b in boxes.items()},
        'baked': open_slugs,
        'built': datetime.now(timezone.utc).strftime('%Y-%m-%d'),
    }

    sys.path.insert(0, str(ROOT / 'tools'))
    from build_home import seam  # the painted seams of the homepage, one arrangement per letter

    part = (PAGES / 'blueprints-atlas.html').read_text(encoding='utf-8')
    fills = {
        '<!--pn:seam-->': seam('a'),
        '<!--pn:map-->': svg,
        '<!--pn:tabs-->': ''.join(tabs),
        '<!--pn:tiles-->': tiles,
        '<!--pn:regions-->': ''.join(blocks),
        '<!--pn:asp-->': asp,
        '<!--pn:n-live-->': str(n_live),
        '<!--pn:n-regions-->': str(n_regions),
        '<!--pn:n-total-->': str(len(nat)),
        '<!--pn:n-soon-->': str(len(nat) - n_live),
        '/*pn:cfg*/null': json.dumps(js_cfg, ensure_ascii=True, separators=(',', ':')),
    }
    for k, v in fills.items():
        if k not in part:
            sys.exit('pages/blueprints-atlas.html has no %s slot' % k)
        part = part.replace(k, v)

    today = datetime.now(timezone.utc).strftime('%Y-%m-%d')
    head = '''<!-- ===========================================================================
PERFECT NATIONS - THE BLUEPRINTS PAGE - THE WHOLE PAGE IN ONE FILE - v%s - %s
Page 14775 (/blueprints/) holds ONE Elementor container (Full Width, padding 0) with ONE Custom HTML
widget whose root is pn-blueprints (a short fallback, or this whole file). The Perfect Nations Live
Pages plugin serves pages/blueprints.html from GitHub in its place, because pn-blueprints is the first
id on the page and is listed in pages/manifest.json. Never paste on this page again.
Built by tools/build_blueprints.py from the parts named below; edit a part, run the build and open a
pull request. Kept by the Blueprints Steward.
Open blueprints at this build: %d of %d. New blueprints need no new build: the page reads
pages/manifest.json and data/blueprints.json on every visit.
v6.1 (8 Nov 2026): FfD before SI (the Steward-General, 8 Nov 2026). The lead names innovative financing for
development (FfD) first and super intelligence (SI) second.
=========================================================================== -->
<div id="pn-blueprints" hidden></div>
''' % (VERSION, today, n_live, len(nat))
    out = [head]
    for item in ORDER:
        code = part if item == 'blueprints-atlas.html' else (PAGES / item).read_text(encoding='utf-8').strip()
        out.append('<!-- ======== part: pages/%s ======== -->\n%s\n' % (item, code.strip()))
    page = '\n'.join(out)
    first = re.search(r'\bid\s*=\s*["\'](pn-[a-z0-9-]+)["\']', page, re.I)
    if not first or first.group(1) != 'pn-blueprints':
        sys.exit('the first pn- id must be pn-blueprints, found %s' % (first.group(1) if first else None))
    bad = [(i, c) for i, c in enumerate(page) if ord(c) > 126]
    if bad:
        sys.exit('non-ASCII characters: %r' % bad[:5])
    (PAGES / 'blueprints.html').write_text(page, encoding='utf-8')
    print('pages/blueprints.html', len(page), 'characters;', n_live, 'open of', len(nat), 'in', n_regions, 'regions')


if __name__ == '__main__':
    main()
