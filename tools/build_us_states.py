#!/usr/bin/env python3
"""Build the Perfect Nations 50 States page (perfectnations.com/50-states/) and its data file.

Writes two files:
  data/us-states.json     the 50 states: name, postal code, Census region, and three official figures each
                          (population, GDP, people below the poverty line), with the United States totals and
                          the three sources. Built from the raw downloads in data/us/raw/ (--data). It mirrors
                          the official files and adds no figure of its own (the poverty share is the Census
                          count divided by the Census universe, one decimal).
  pages/us-states.html    the whole page (root pn-us). The page holds ONE Elementor Custom HTML widget whose
                          root is pn-us; the Perfect Nations Live Pages plugin serves this file in its place.
                          Never edit this file by hand.

The design lives in tools/us/style.css and tools/us/script.js; the map is drawn at build time from
tools/us/states-albers-10m.json (us-atlas 3, ISC licence: the Census Bureau cartographic boundaries,
projected Albers USA with Alaska and Hawaii inset, 975 x 610), simplified here, so the page downloads no
map file and no library. The gold line between sections comes from pages/home-rule.html.

A state blueprint needs no new build of this page: on every visit the page reads pages/manifest.json, and
a key pn-us-<slug> (for example pn-us-texas) turns that state bright gold on the map and in the list, and
links it to the url given in the manifest.

Sources (the downloads and their addresses are listed in data/us/raw/README.md):
  Population  U.S. Census Bureau, Vintage 2025 population estimates, 1 July 2025 (NST-EST2025-ALLDATA.csv)
  GDP         U.S. Bureau of Economic Analysis, SAGDP1, current-dollar GDP, 2025 (last updated 30 Sep 2026)
  Poverty     U.S. Census Bureau, American Community Survey 2025 1-year, table B17001 (E001 universe,
              E002 income in the past 12 months below poverty level)

Run from the repository root:
  python3 tools/build_us_states.py --data   rebuild data/us-states.json from data/us/raw/
  python3 tools/build_us_states.py          build pages/us-states.html (and check the data file first)
Then raise "pn-us" in pages/manifest.json and open a pull request "For approval: The 50 States vX.Y, ...".
"""
import csv
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
RAW = DATA / 'us' / 'raw'
HERE = Path(__file__).resolve().parent / 'us'
VERSION = '1.1'

# Postal codes by FIPS (the Census Bureau's state codes). DC (11) is not a state and is not listed.
ABBR = {
    '01': 'AL', '02': 'AK', '04': 'AZ', '05': 'AR', '06': 'CA', '08': 'CO', '09': 'CT', '10': 'DE', '12': 'FL',
    '13': 'GA', '15': 'HI', '16': 'ID', '17': 'IL', '18': 'IN', '19': 'IA', '20': 'KS', '21': 'KY', '22': 'LA',
    '23': 'ME', '24': 'MD', '25': 'MA', '26': 'MI', '27': 'MN', '28': 'MS', '29': 'MO', '30': 'MT', '31': 'NE',
    '32': 'NV', '33': 'NH', '34': 'NJ', '35': 'NM', '36': 'NY', '37': 'NC', '38': 'ND', '39': 'OH', '40': 'OK',
    '41': 'OR', '42': 'PA', '44': 'RI', '45': 'SC', '46': 'SD', '47': 'TN', '48': 'TX', '49': 'UT', '50': 'VT',
    '51': 'VA', '53': 'WA', '54': 'WV', '55': 'WI', '56': 'WY',
}
# The four Census regions (the REGION column of the population file).
REGIONS = [('1', 'northeast', 'Northeast'), ('2', 'midwest', 'Midwest'), ('3', 'south', 'South'), ('4', 'west', 'West')]

SOURCES = {
    'population': {
        'label': 'U.S. Census Bureau, Vintage 2025 population estimates, 1 July 2025',
        'short': 'Census Bureau, 2025',
        'url': 'https://www.census.gov/data/tables/time-series/demo/popest/2020s-state-total.html',
    },
    'gdp': {
        'label': 'U.S. Bureau of Economic Analysis, GDP by state, 2025, current dollars (updated 30 September 2026)',
        'short': 'BEA, 2025',
        'url': 'https://www.bea.gov/data/gdp/gdp-state',
    },
    'poverty': {
        'label': 'U.S. Census Bureau, American Community Survey 2025 1-year estimates, table B17001',
        'short': 'Census Bureau, ACS 2025',
        'url': 'https://data.census.gov/table/ACSDT1Y2025.B17001',
    },
}


def ent(s):
    """Escape for HTML and write every non-ASCII character as an entity (the page stays ASCII)."""
    return html.escape('' if s is None else str(s), quote=True).encode('ascii', 'xmlcharrefreplace').decode('ascii')


def slug_of(name):
    return re.sub(r'[^a-z0-9]+', '-', name.lower()).strip('-')


# ----------------------------------------------------------------------------------------------- data
def read_population():
    rows = list(csv.DictReader(open(RAW / 'NST-EST2025-ALLDATA.csv', encoding='latin-1')))
    out, us = {}, None
    for r in rows:
        if r['SUMLEV'] == '010':
            us = int(r['POPESTIMATE2025'])
        elif r['SUMLEV'] == '040' and r['STATE'] in ABBR:
            out[r['STATE']] = (r['NAME'], r['REGION'], int(r['POPESTIMATE2025']))
    return out, us


def read_gdp():
    out, us = {}, None
    with open(RAW / 'SAGDP1__ALL_AREAS_1997_2025.csv', encoding='latin-1') as f:
        rd = csv.reader(f)
        head = next(rd)
        col = head.index('2025')
        for r in rd:
            if len(r) <= col or r[3].strip() != 'SAGDP1' or r[4].strip() != '3':
                continue
            if not r[6].strip().startswith('Current-dollar GDP (millions of current dollars)'):
                sys.exit('unexpected line 3 in SAGDP1: %r' % r[6])
            fips = r[0].strip().strip('"')[:2]
            val = float(r[col])
            if r[0].strip().strip('"') == '00000':
                us = val
            elif r[0].strip().strip('"')[2:] == '000' and fips in ABBR:
                out[fips] = val
    return out, us


def read_poverty():
    out, us = {}, None
    lines = (RAW / 'acsdt1y2025-b17001-states.dat').read_text(encoding='ascii').splitlines()
    head = lines[0].split('|')
    if head[:5] != ['GEO_ID', 'B17001_E001', 'B17001_M001', 'B17001_E002', 'B17001_M002']:
        sys.exit('unexpected columns in the B17001 file: %r' % head)
    for ln in lines[1:]:
        g, e1, m1, e2, m2 = ln.split('|')[:5]
        rec = (int(e1), int(e2), int(m2))
        if g == '0100000US':
            us = rec
        elif g.startswith('0400000US') and g[9:] in ABBR:
            out[g[9:]] = rec
    return out, us


def build_data():
    pop, pop_us = read_population()
    gdp, gdp_us = read_gdp()
    pov, pov_us = read_poverty()
    for name, d in (('population', pop), ('GDP', gdp), ('poverty', pov)):
        if set(d) != set(ABBR):
            sys.exit('%s: %d states, missing %s' % (name, len(d), sorted(set(ABBR) - set(d))))
    region = {code: (slug, label) for code, slug, label in REGIONS}
    states = []
    for fips in sorted(ABBR, key=lambda k: pop[k][0]):
        name, reg, people = pop[fips]
        uni, below, moe = pov[fips]
        states.append({
            'slug': slug_of(name), 'name': name, 'abbr': ABBR[fips], 'fips': fips,
            'region': region[reg][0],
            'population': people,
            'gdp_musd': round(gdp[fips], 1),
            'poverty': {'below': below, 'moe': moe, 'universe': uni, 'share': round(100.0 * below / uni, 1)},
        })
    doc = {
        'page': 'us-states',
        'updated': datetime.now(timezone.utc).strftime('%Y-%m-%d'),
        'about': 'The 50 States page (perfectnations.com/50-states/). Built by python3 tools/build_us_states.py --data '
                 'from the official files in data/us/raw/; adds no figure of its own. poverty.share = below / universe, '
                 'one decimal. gdp_musd: millions of current US dollars.',
        'sources': SOURCES,
        'regions': [{'slug': s, 'name': n} for _, s, n in REGIONS],
        'us': {
            'population': pop_us,
            'gdp_musd': round(gdp_us, 1),
            'poverty': {'below': pov_us[1], 'moe': pov_us[2], 'universe': pov_us[0],
                        'share': round(100.0 * pov_us[1] / pov_us[0], 1)},
        },
        'states': states,
    }
    (DATA / 'us-states.json').write_text(json.dumps(doc, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print('data/us-states.json: %d states; United States %s people, GDP %s, %s below the poverty line (%s%%)' % (
        len(states), f"{pop_us:,}", money(gdp_us), people_fmt(pov_us[1]), doc['us']['poverty']['share']))
    return doc


# ----------------------------------------------------------------------------------------------- formats
def money(musd):
    """Millions of dollars to the site's short form: $4.10tn, $812bn, $52.3bn."""
    if musd >= 1e6:
        return '$%.2ftn' % (musd / 1e6)
    b = musd / 1e3
    return '$%dbn' % round(b) if b >= 100 else '$%.1fbn' % b


def people_fmt(n):
    """39.4m, 589k."""
    return '%.1fm' % (n / 1e6) if n >= 1e6 else '%dk' % round(n / 1e3)


# ----------------------------------------------------------------------------------------------- the map
def dp(points, tol):
    """Douglas-Peucker on one arc; the ends stay fixed, so shared borders stay shared."""
    if len(points) < 3:
        return points
    keep = [False] * len(points)
    keep[0] = keep[-1] = True
    stack = [(0, len(points) - 1)]
    while stack:
        a, b = stack.pop()
        ax, ay = points[a]
        bx, by = points[b]
        dx, dy = bx - ax, by - ay
        ln = math.hypot(dx, dy)
        best, idx = -1.0, -1
        for i in range(a + 1, b):
            px, py = points[i]
            # a closed arc (an island drawn as one loop) has equal ends: measure from that point instead
            d = abs(dy * px - dx * py + bx * ay - by * ax) / ln if ln > 1e-9 else math.hypot(px - ax, py - ay)
            if d > best:
                best, idx = d, i
        if best > tol and idx > 0:
            keep[idx] = True
            stack.append((a, idx))
            stack.append((idx, b))
    return [p for p, k in zip(points, keep) if k]


def load_map(tol=0.45):
    topo = json.loads((HERE / 'states-albers-10m.json').read_text(encoding='utf-8'))
    sx, sy = topo['transform']['scale']
    tx, ty = topo['transform']['translate']
    arcs = []
    for arc in topo['arcs']:
        x = y = 0
        pts = []
        for qx, qy in arc:
            x += qx
            y += qy
            pts.append((x * sx + tx, y * sy + ty))
        arcs.append(dp(pts, tol))

    def ring(idx):
        pts = []
        for i in idx:
            a = arcs[i] if i >= 0 else arcs[~i][::-1]
            pts.extend(a if not pts else a[1:])
        return pts

    shapes = {}
    for g in topo['objects']['states']['geometries']:
        polys = g['arcs'] if g['type'] == 'MultiPolygon' else [g['arcs']]
        shapes[g['id']] = [[ring(r) for r in poly] for poly in polys]
    return shapes


def path_d(polys):
    out = []
    for poly in polys:
        for r in poly:
            pts = [(round(x, 1), round(y, 1)) for x, y in r]
            dedup = [pts[0]]
            for p in pts[1:]:
                if p != dedup[-1]:
                    dedup.append(p)
            if len(dedup) < 3:
                continue
            seg = ['M%s,%s' % (num(dedup[0][0]), num(dedup[0][1]))]
            px, py = dedup[0]
            rel = []
            for x, y in dedup[1:]:
                rel.append('%s,%s' % (num(round(x - px, 1)), num(round(y - py, 1))))
                px, py = x, y
            seg.append('l' + ' '.join(rel) + 'z')
            out.append(''.join(seg))
    return ''.join(out)


def num(v):
    s = ('%.1f' % v).rstrip('0').rstrip('.')
    s = s.replace('-0.', '-.') if s.startswith('-0.') else (s[1:] if s.startswith('0.') else s)
    return '0' if s in ('', '-0', '-') else s


def centroid(polys):
    """Area-weighted centroid of the largest polygon's outer ring, and the polygon's bounding box."""
    best = None
    for poly in polys:
        r = poly[0]
        a = cx = cy = 0.0
        for (x0, y0), (x1, y1) in zip(r, r[1:] + r[:1]):
            c = x0 * y1 - x1 * y0
            a += c
            cx += (x0 + x1) * c
            cy += (y0 + y1) * c
        if abs(a) < 1e-9:
            continue
        cand = (abs(a) / 2, cx / (3 * a), cy / (3 * a), r)
        if best is None or cand[0] > best[0]:
            best = cand
    xs = [p[0] for p in best[3]]
    ys = [p[1] for p in best[3]]
    return best[1], best[2], best[0], (min(xs), min(ys), max(xs), max(ys))


# Where a label sits better than at the centroid (map units), and the small eastern states labelled
# beside the map with a leader line.
NUDGE = {'FL': (14, 4), 'MI': (10, 22), 'LA': (-10, -2), 'KY': (6, 3), 'ID': (0, 22), 'CA': (-8, 0),
         'MN': (-6, 10), 'WV': (-3, 5), 'VA': (8, 2), 'NY': (8, 2), 'TN': (0, 1), 'AK': (0, 0), 'HI': (14, 10),
         'NC': (8, 0), 'SC': (2, 2), 'OK': (14, 0), 'TX': (6, 6), 'ME': (0, 2), 'ND': (0, 0)}
CALLOUT = ['VT', 'NH', 'MA', 'RI', 'CT', 'NJ', 'DE', 'MD']


def map_svg(doc, shapes):
    by_fips = {s['fips']: s for s in doc['states']}
    paths, labels, leaders = [], [], []
    ys = {}
    for fips, polys in sorted(shapes.items()):
        d = path_d(polys)
        if fips not in by_fips:     # the District of Columbia: drawn, not a state
            paths.append('<path class="pnus-dc" d="%s"/>' % d)
            continue
        s = by_fips[fips]
        paths.append('<path class="pnus-st" data-s="%s" data-r="%s" tabindex="0" role="button" aria-label="%s" d="%s"/>' % (
            s['slug'], s['region'], ent(s['name']), d))
        cx, cy, area, box = centroid(polys)
        dx, dy = NUDGE.get(s['abbr'], (0, 0))
        if s['abbr'] in CALLOUT:
            ys[s['abbr']] = (cx, cy, s)
        else:
            labels.append('<text class="pnus-lb%s" data-s="%s" x="%s" y="%s">%s</text>' % (
                ' pnus-lb--s' if area < 900 else '', s['slug'], num(cx + dx), num(cy + dy + 3.5), s['abbr']))
    # callouts: stacked down the right edge, east of New England and the Mid-Atlantic
    y0, step, lx = 152, 21.5, 918
    for i, ab in enumerate(CALLOUT):
        cx, cy, s = ys[ab]
        ty = y0 + i * step
        leaders.append('<path class="pnus-ld" data-s="%s" d="M%s,%sL%s,%sH%s"/>' % (
            s['slug'], num(cx), num(cy), num(lx - 22), num(ty), num(lx - 6)))
        labels.append('<text class="pnus-lb pnus-lb--c" data-s="%s" x="%s" y="%s">%s</text>' % (s['slug'], num(lx), num(ty + 3.5), ab))
    return ('<svg class="pnus-svg" viewBox="0 0 975 610" role="group" aria-label="Map of the 50 states" focusable="false">'
            '<g class="pnus-states">%s</g><g class="pnus-leaders" aria-hidden="true">%s</g>'
            '<g class="pnus-labels" aria-hidden="true">%s</g></svg>') % (''.join(paths), ''.join(leaders), ''.join(labels))


# ----------------------------------------------------------------------------------------------- the page
def check_data(doc):
    if doc.get('page') != 'us-states' or len(doc.get('states', [])) != 50:
        sys.exit('data/us-states.json is not the 50 States file')
    for k, v in doc['sources'].items():
        if not re.match(r'^https://[^\s"\'<>()]+$', v['url']):
            sys.exit('source %s: not an https link: %r' % (k, v['url']))


def state_rows(doc):
    rows = []
    for s in doc['states']:
        p = s['poverty']
        rows.append(
            '<li class="pnus-row" id="pnus-%s" data-s="%s" data-r="%s" data-n="%s" data-p="%d" data-g="%s" data-v="%s">'
            '<button type="button" class="pnus-row__b" aria-label="%s on the map">'
            '<span class="pnus-row__ab" aria-hidden="true">%s</span>'
            '<span class="pnus-row__nm">%s</span></button>'
            '<span class="pnus-row__f pnus-row__f--g"><b>%s</b><small>GDP</small></span>'
            '<span class="pnus-row__f"><b>%s</b><small>People</small></span>'
            '<span class="pnus-row__f"><b>%s%%</b><small>Below the poverty line</small></span>'
            '<a class="pnus-row__go" href="https://perfectnations.com/contact/?country=%s" data-ask="1">'
            '<span class="pnus-row__st">In preparation</span><span class="pnus-row__ac">Ask for it</span></a>'
            '</li>' % (
                s['slug'], s['slug'], s['region'], ent(s['name']), s['population'], s['gdp_musd'], p['share'],
                ent(s['name']), s['abbr'], ent(s['name']), money(s['gdp_musd']), people_fmt(s['population']),
                ('%.1f' % p['share']), s['name'].replace(' ', '%20')))
    return ''.join(rows)


def state_json(doc):
    out = {}
    for s in doc['states']:
        p = s['poverty']
        out[s['slug']] = [s['name'], s['abbr'], s['region'], money(s['gdp_musd']), people_fmt(s['population']),
                          people_fmt(p['below']), '%.1f' % p['share']]
    return json.dumps(out, separators=(',', ':'), ensure_ascii=True)


def logo_parts():
    """The parts of the logo, from the logo kit (pages/home-logo-kit.html), renamed so they never meet the kit's
    own ids: the cup and laurels (one shape) with the clips for the cup alone and the laurels alone, and the seven
    stars. The steps band draws the cup (01 Assets), the laurels (02 Capital) and the stars (03 Solutions), each
    alone, in its one gold, on an Earthrise disc (the logo is never drawn straight onto ivory)."""
    src = (PAGES / 'home-logo-kit.html').read_text(encoding='utf-8')
    parts = []
    for pat in (r'<path id="pnk-cl"[^>]*/>', r'<clipPath id="pnk-cc".*?</clipPath>', r'<clipPath id="pnk-lc".*?</clipPath>') + tuple(
            r'<path id="pnk-s%d"[^>]*/>' % i for i in range(7)):
        m = re.search(pat, src, re.S)
        if not m:
            sys.exit('not found in pages/home-logo-kit.html: %s' % pat)
        parts.append(re.sub(r'id="pnk-', 'id="pnus-k-', m.group(0), count=1))
    return '<svg class="pnus-defs" width="0" height="0" aria-hidden="true" focusable="false"><defs>%s</defs></svg>' % ''.join(parts)


def build_page(doc):
    check_data(doc)
    shapes = load_map()
    us = doc['us']
    src = doc['sources']
    css = (HERE / 'style.css').read_text(encoding='utf-8').strip()
    js = (HERE / 'script.js').read_text(encoding='utf-8').strip()
    tpl = (HERE / 'template.html').read_text(encoding='utf-8').strip()
    rule = (PAGES / 'home-rule.html').read_text(encoding='utf-8').strip()
    rule = re.sub(r'^\s*<!--.*?-->\s*', '', rule, count=1, flags=re.S)
    counts = {r['slug']: sum(1 for s in doc['states'] if s['region'] == r['slug']) for r in doc['regions']}
    fill = {
        'rule': rule,
        'map': map_svg(doc, shapes),
        'logo': logo_parts(),
        'us_people': people_fmt(us['population']),
        'us_gdp': money(us['gdp_musd']),
        'us_poor': people_fmt(us['poverty']['below']),
        'us_share': '%.1f' % us['poverty']['share'],
        'src_pop': ent(src['population']['label']), 'url_pop': src['population']['url'], 'short_pop': ent(src['population']['short']),
        'src_gdp': ent(src['gdp']['label']), 'url_gdp': src['gdp']['url'], 'short_gdp': ent(src['gdp']['short']),
        'src_pov': ent(src['poverty']['label']), 'url_pov': src['poverty']['url'], 'short_pov': ent(src['poverty']['short']),
        'rows': state_rows(doc),
        'states_json': state_json(doc),
        'n_northeast': counts['northeast'], 'n_midwest': counts['midwest'], 'n_south': counts['south'], 'n_west': counts['west'],
        'version': VERSION,
    }

    def sub(m):
        k = m.group(1)
        if k not in fill:
            sys.exit('template slot without a value: %s' % k)
        return str(fill[k])
    body = re.sub(r'<!--pn:([a-z_]+)-->', sub, tpl)
    today = datetime.now(timezone.utc).strftime('%Y-%m-%d')
    head = '''<!-- ===========================================================================
PERFECT NATIONS - THE 50 STATES - THE WHOLE PAGE IN ONE FILE - v%s - %s
perfectnations.com/50-states/ holds ONE Elementor Custom HTML widget (or Custom HTML block) whose root is
pn-us. The Perfect Nations Live Pages plugin serves this file from GitHub in its place. Never edit this file
by hand: edit tools/us/ (design and words) or rebuild data/us-states.json, run
python3 tools/build_us_states.py, and open a pull request.
v1.1: the page script sits inside an HTML comment marker, so the WordPress formatter cannot turn its double
ampersands into entities on the block-editor page (10 Nov 2026).
v1.0: the section for the 50 states of the United States, where state blueprints will open (the
Steward-General, 10 Nov 2026). Bands: 01 the golden map of the 50 states (Earthrise, the hero stays deep for
the map), with region tabs and a card for each state; 02 every state in one line (ivory): GDP, people and
the share below the poverty line, sortable, searchable; 03 how a state blueprint works (paper); the gold
line; 04 the close (ivory). Figures: Census Bureau (population, Vintage 2025; poverty, ACS 2025) and BEA
(GDP 2025). A state turns bright gold when a pn-us-[slug] key is merged into pages/manifest.json.
=========================================================================== -->
''' % (VERSION, today)
    # v1.1: the script sits inside an HTML comment, so the WordPress formatter cannot turn its && into &#038;&#038;
    page = head + '<style>\n%s\n</style>\n' % css + body + '\n<script><!--\n%s\n//--></script>\n' % js
    first = re.search(r'\bid\s*=\s*["\'](pn-[a-z0-9-]+)["\']', page, re.I)
    if not first or first.group(1) != 'pn-us':
        sys.exit('the first pn- id must be pn-us, found %s' % (first.group(1) if first else None))
    others = set(re.findall(r'\bid\s*=\s*["\'](pn-[a-z0-9-]+)["\']', page, re.I)) - {'pn-us'}
    if others:
        sys.exit('only the root may carry a pn- id (the plugin reads them): %s' % sorted(others))
    bad = [(i, c) for i, c in enumerate(page) if ord(c) > 126]
    if bad:
        sys.exit('non-ASCII characters in the page: %r' % bad[:5])
    (PAGES / 'us-states.html').write_text(page, encoding='utf-8')
    print('pages/us-states.html: %d characters (%d of them the map)' % (len(page), len(fill['map'])))


def main():
    if '--data' in sys.argv:
        build_data()
        return
    doc = json.loads((DATA / 'us-states.json').read_text(encoding='utf-8'))
    build_page(doc)


if __name__ == '__main__':
    main()
