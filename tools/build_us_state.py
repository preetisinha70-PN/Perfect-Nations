#!/usr/bin/env python3
"""Build a Perfect Nations STATE blueprint: perfectnations.com/50-states/<slug>/ (first: New York, 10 Nov 2026).

  python3 tools/build_us_state.py new-york      writes pages/us-<slug>.html (root pn-us-<slug>)

Reads:
  data/us/states/<slug>.json   the words, the figures found on official pages (each with a source id) and the sources
  data/us-states.json          population, GDP and the share below the poverty line (the 50 States file)
  data/us/raw/<slug>/          official downloads: ACS 2025 B27001 (health insurance), ACS 2020-2024 B17001 by county
                               (with the county names), NAEP 2024 reading (NAEP Data Service), USDA ERR-358 table 4
  tools/us/counties-albers-10m.json   us-atlas 3 (ISC): Census Bureau county outlines, Albers USA; the state is drawn
                                      at build time, so the page loads no map file and no library
  tools/us/state/style.css, script.js the design (scoped to #ROOT, replaced by the page root)
A figure written "computed:<name>" in the blueprint file is filled here from those files; nothing is estimated.

The page goes live when pages/manifest.json carries the key pn-us-<slug> with its url; the 50 States page and the
header search then turn the state bright gold by themselves. The WordPress page /50-states/<slug>/ holds ONE Custom HTML
block with <div id="pn-us-<slug>"> and a fallback line. Never edit the built page by hand.
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
sys.path.insert(0, str(ROOT / 'tools'))
from build_us_states import dp, num, money, people_fmt, logo_parts  # noqa: E402

PAGES, DATA, US = ROOT / 'pages', ROOT / 'data', ROOT / 'tools' / 'us'
STAR = 'M12 2.2l2.9 6.3 6.9.7-5.2 4.6 1.5 6.8L12 17.1l-6.1 3.5 1.5-6.8L2.2 9.2l6.9-.7z'
BINS = [10.0, 12.5, 15.0, 20.0]
BIN_LABELS = ['Under 10%', '10 to 12.5%', '12.5 to 15%', '15 to 20%', '20% and over']
BIN_COLOURS = ['#F1E2C9', '#E3BE93', '#CF9064', '#B0623C', '#7E3420']


def ent(s):
    return html.escape('' if s is None else str(s), quote=True).encode('ascii', 'xmlcharrefreplace').decode('ascii')


def pct(v, d=1):
    return ('%.' + str(d) + 'f%%') % v


# ------------------------------------------------------------------------------------------- figures
def computed(st, slug):
    us50 = json.loads((DATA / 'us-states.json').read_text(encoding='utf-8'))
    s = next(x for x in us50['states'] if x['slug'] == slug)
    us = us50['us']
    raw = DATA / 'us' / 'raw' / slug
    c = {
        'gdp': money(s['gdp_musd']),
        'gdp_words': money(s['gdp_musd']).replace('tn', ' trillion').replace('bn', ' billion'),
        'people': people_fmt(s['population']),
        'poverty': pct(s['poverty']['share']),
        'poverty_us': pct(us['poverty']['share']),
        'poverty_below': '{:,}'.format(s['poverty']['below']),
    }
    # health insurance: ACS 2025 1-year B27001, the 18 "No health insurance coverage" cells over the universe
    rows = [l.rstrip('\n').split('|') for l in (raw / 'acsdt1y2025-b27001-ny-us.dat').read_text().splitlines()]
    idx = {h: i for i, h in enumerate(rows[0])}
    shells = (raw / 'shells-2025-B27001.txt').read_text()
    no = [int(m) for m in re.findall(r'\|B27001_(\d{3})\|No health insurance coverage\|', shells)]
    if len(no) != 18:
        sys.exit('B27001: expected 18 uninsured cells, found %d' % len(no))
    share = {}
    for r in rows[1:]:
        tot = int(r[idx['B27001_E001']])
        share[r[0]] = 100.0 * sum(int(r[idx['B27001_E%03d' % n]]) for n in no) / tot
    c['uninsured'] = pct(share['0400000US' + st['fips']])
    c['uninsured_us'] = pct(share['0100000US'])
    # NAEP 2024 reading, grade 4, at or above Proficient (public schools)
    ny = json.loads((raw / 'naep-reading-g4-2024-ny.json').read_text())['result'][0]
    nt = json.loads((raw / 'naep-reading-g4-2024-nt.json').read_text())['result'][0]
    if ny['jurisdiction'] != st['abbr'] or ny['stattype'] != 'ALC:AP' or ny['year'] != 2024:
        sys.exit('NAEP file is not %s 2024 at or above Proficient' % st['abbr'])
    c['reading'] = '%d%%' % round(ny['value'])
    c['reading_us'] = '%d%%' % round(nt['value'])
    # USDA ERR-358 table 4: food insecurity, average 2022-2024
    t4 = (raw / 'usda-err358-table4-states.txt').read_text()
    def row(code):
        m = re.search(r'^%s\s+[\d,]+\s+[\d,]+\s+([\d.]+)\s' % re.escape(code), t4, re.M)
        if not m:
            sys.exit('USDA table 4: no row for %s' % code)
        return float(m.group(1))
    c['food'] = pct(row(st['abbr']))
    c['food_us'] = pct(row('U.S.'))
    return c


def fill(text, c):
    def sub(m):
        k = m.group(1)
        if k not in c:
            sys.exit('no computed value for %s' % k)
        return c[k]
    return re.sub(r'computed:([a-z_]+)', sub, text)


def counties(st, slug):
    raw = DATA / 'us' / 'raw' / slug
    names = {}
    for l in (raw / 'geos-2024-5y-ny-counties.txt').read_text(encoding='latin-1').splitlines()[1:]:
        g, n = l.split('|', 1)
        names[g[-5:]] = n.split(',')[0].replace(' County', '')
    out = {}
    lines = (raw / 'acsdt5y2024-b17001-ny-counties.dat').read_text().splitlines()
    if lines[0].split('|')[:4] != ['GEO_ID', 'B17001_E001', 'B17001_M001', 'B17001_E002']:
        sys.exit('unexpected B17001 county columns')
    for l in lines[1:]:
        r = l.split('|')
        if r[0].startswith('0500000US' + st['fips']):
            f = r[0][-5:]
            out[f] = (names[f], int(r[1]), int(r[3]))
    return out


# ------------------------------------------------------------------------------------------- the map
def state_paths(fips, width=1000.0, tol=0.55):
    topo = json.loads((US / 'counties-albers-10m.json').read_text(encoding='utf-8'))
    sx, sy = topo['transform']['scale']
    tx, ty = topo['transform']['translate']
    geoms = [g for g in topo['objects']['counties']['geometries'] if g['id'].startswith(fips)]
    used = set()
    for g in geoms:
        polys = g['arcs'] if g['type'] == 'MultiPolygon' else [g['arcs']]
        for poly in polys:
            for ring in poly:
                for i in ring:
                    used.add(i if i >= 0 else ~i)
    absarcs = {}
    for i in used:
        x = y = 0
        pts = []
        for qx, qy in topo['arcs'][i]:
            x += qx
            y += qy
            pts.append((x * sx + tx, y * sy + ty))
        absarcs[i] = pts
    xs = [p[0] for a in absarcs.values() for p in a]
    ys = [p[1] for a in absarcs.values() for p in a]
    minx, miny, maxx, maxy = min(xs), min(ys), max(xs), max(ys)
    k = width / (maxx - minx)
    pad = 6.0
    arcs = {i: dp([((x - minx) * k + pad, (y - miny) * k + pad) for x, y in a], tol) for i, a in absarcs.items()}
    w, h = width + 2 * pad, (maxy - miny) * k + 2 * pad
    out = {}
    for g in geoms:
        polys = g['arcs'] if g['type'] == 'MultiPolygon' else [g['arcs']]
        d = []
        for poly in polys:
            for ring in poly:
                pts = []
                for i in ring:
                    a = arcs[i] if i >= 0 else arcs[~i][::-1]
                    pts.extend(a if not pts else a[1:])
                pts = [(round(x, 1), round(y, 1)) for x, y in pts]
                ded = [pts[0]]
                for p in pts[1:]:
                    if p != ded[-1]:
                        ded.append(p)
                if len(ded) < 3:
                    continue
                s = 'M%s,%s' % (num(ded[0][0]), num(ded[0][1]))
                px, py = ded[0]
                rel = []
                for x, y in ded[1:]:
                    rel.append('%s,%s' % (num(round(x - px, 1)), num(round(y - py, 1))))
                    px, py = x, y
                d.append(s + 'l' + ' '.join(rel) + 'z')
        out[g['id']] = ''.join(d)
    return out, (w, h)


def bin_of(v):
    for i, t in enumerate(BINS):
        if v < t:
            return i
    return len(BINS)


# ------------------------------------------------------------------------------------------- the page
def build(slug):
    st = json.loads((DATA / 'us' / 'states' / (slug + '.json')).read_text(encoding='utf-8'))
    c = computed(st, slug)
    S = st['sources']
    for k, v in S.items():
        for u in (v['url'], v.get('url2', 'https://x.y')):
            if not re.match(r'^https://[^\s"\'<>()]+$', u):
                sys.exit('source %s: not an https link: %r' % (k, u))
    order = []

    def src(k, cls='pnst-src'):
        if not k:
            return ''
        if k not in S:
            sys.exit('unknown source %s' % k)
        if k not in order:
            order.append(k)
        return '<a class="%s" href="%s" title="%s" rel="noopener">%s</a>' % (cls, S[k]['url'], ent(S[k]['label']), ent(S[k]['short']))

    T = lambda s: ent(fill(s, c))  # noqa: E731
    root = 'pn-us-' + slug
    cty = counties(st, slug)
    paths, (vw, vh) = state_paths(st['fips'])
    if set(paths) != set(cty):
        sys.exit('counties: outlines %d, figures %d' % (len(paths), len(cty)))

    # hero
    h = st['hero']
    figs = ''.join('<li><b class="%s">%s</b><span>%s %s</span></li>' % (
        'pnst-money' if f['money'] else '', T(f['value'].replace('computed:', 'computed:')), T(f['label']), src(f['src'])) for f in h['figures'])
    hero_svg = ('<svg viewBox="0 0 %s %s" role="img" aria-label="%s, its %d counties, in gold" focusable="false">'
                '<g class="pnst-ol">%s</g><g class="pnst-cl">%s</g></svg>') % (
        num(vw), num(vh), ent(st['name']), len(paths),
        ''.join('<path d="%s" stroke="#E3C258" stroke-width=".6"/>' % d for d in paths.values()),
        ''.join('<path d="%s"/>' % d for d in paths.values()))
    hero = '''
<section class="pnst-band pnst-hero" aria-labelledby="pnst-h1">
  <div class="pnst-in pnst-top">
    <div class="pnst-intro">
      <p class="pnst-eb"><a href="https://perfectnations.com/50-states/" data-pn-same-tab="1">%s</a></p>
      <h1 class="pnst-h1" id="pnst-h1">%s</h1>
      <p class="pnst-line">%s</p>
      <p class="pnst-sub">%s</p>
    </div>
    <div class="pnst-statemap">%s<p class="pnst-cap">%d counties</p></div>
    <div class="pnst-facts">
      <ul class="pnst-figs">%s</ul>
      <div class="pnst-ctas">
        <a class="pnst-btn" href="#pnst-solutions" data-pn-same-tab="1">The solutions</a>
        <a class="pnst-btn pnst-btn--line" href="https://perfectnations.com/50-states/">All 50 states</a>
      </div>
    </div>
  </div>
</section>''' % (T(h['eyebrow']), ent(st['name']), T(h['line']), T(h['sub']), hero_svg, len(paths), figs)

    # 01 assets
    A = st['assets']
    cup = '<span class="pnst-as__mark" aria-hidden="true"><svg viewBox="82.5 153 346 346" focusable="false"><use href="#pnus-k-cl" clip-path="url(#pnus-k-cc)"/></svg></span>'
    items = []
    for i, a in enumerate(A['items'], 1):
        items.append('<li class="pnst-as%s">%s<p class="pnst-as__n">%02d</p><p class="pnst-as__f%s">%s</p><h3>%s</h3><p class="pnst-as__l">%s</p>%s</li>' % (
            ' pnst-as--lead' if a.get('lead') else '', cup if a.get('lead') else '', i,
            ' pnst-money' if a['money'] and not a.get('lead') else '', T(a['figure']), T(a['name']), T(a['line']), src(a['src'])))
    assets = '''
<section class="pnst-band pnst-iv" id="pnst-assets" aria-labelledby="pnst-h2a">
  <div class="pnst-in">
    <div class="pnst-head"><div><p class="pnst-eb">01 &middot; Assets &middot; What %s owns</p><h2 class="pnst-h2" id="pnst-h2a">%s</h2></div><p class="pnst-lead">%s</p></div>
    <ul class="pnst-assets">%s</ul>
  </div>
</section>''' % (ent(st['name']), T(A['title']), T(A['line']), ''.join(items))

    # 02 the seven standards, and the county map
    P = st['standards']
    rows = []
    for s in P['items']:
        gap = s['status'] == 'gap'
        fig = '' if gap else '<b>%s</b>' % T(s['figure'])
        rows.append('<li class="pnst-std pnst-std--%s"><span class="pnst-std__ic" aria-hidden="true"><svg viewBox="0 0 24 24" focusable="false"><path d="%s"/></svg></span>'
                    '<p class="pnst-std__nm">%s%s</p><span class="pnst-chip pnst-chip--%s">%s</span><p class="pnst-std__l">%s %s</p></li>' % (
                        s['status'], STAR, T(s['name']), fig, s['status'], ent(P['status_names'][s['status']]), T(s['label']), src(s['src'])))
    shares = {f: 100.0 * b / u for f, (n, u, b) in cty.items()}
    ch_paths = ''.join('<path class="pnst-c%d" d="%s" data-n="%s" data-v="%.1f" data-p="%s" tabindex="0" role="button" aria-label="%s: %.1f%% below the poverty line"/>' % (
        bin_of(shares[f]), paths[f], ent(cty[f][0]), shares[f], '{:,}'.format(cty[f][2]), ent(cty[f][0]), shares[f]) for f in sorted(paths))
    ranked = sorted(cty, key=lambda f: -shares[f])
    hi, lo = ranked[0], ranked[-1]
    legend = ''.join('<li><i style="background:%s"></i>%s</li>' % (BIN_COLOURS[i], BIN_LABELS[i]) for i in range(5))
    table = ''.join('<li><span>%s</span><b>%.1f%%</b></li>' % (ent(cty[f][0]), shares[f]) for f in ranked)
    mapcard = '''<div class="pnst-mapcard">
      <h3>%s</h3><p>%s %s</p>
      <div class="pnst-ch"><svg viewBox="0 0 %s %s" role="group" aria-label="Map: share below the poverty line by county" focusable="false">%s</svg><div class="pnst-tip" role="status" hidden></div></div>
      <ul class="pnst-legend" aria-label="Share below the poverty line">%s</ul>
      <p class="pnst-mapnote">Highest: %s, %.1f%%. Lowest: %s, %.1f%%. Statewide in 2025: %s.</p>
      <details><summary>All %d counties</summary><ol class="pnst-ctab">%s</ol></details>
    </div>''' % (T(P['map_title']), T(P['map_line']), src(P['map_src']), num(vw), num(vh), ch_paths, legend,
                 ent(cty[hi][0]), shares[hi], ent(cty[lo][0]), shares[lo], c['poverty'], len(cty), table)
    pc = '''
<section class="pnst-band pnst-pp" id="pnst-standards" aria-labelledby="pnst-h2b">
  <div class="pnst-in">
    <div class="pnst-head"><div><p class="pnst-eb">02 &middot; The seven basic standards of living</p><h2 class="pnst-h2" id="pnst-h2b">%s</h2></div><p class="pnst-lead">%s</p></div>
    <div class="pnst-pc"><ol class="pnst-stds">%s</ol>%s</div>
  </div>
</section>''' % (T(P['title']), T(P['line']), ''.join(rows), mapcard)

    # 03 solutions
    Q = st['solutions']
    sols = ''.join('<li class="pnst-sol pnst-sol--%s"><p class="pnst-sol__k"><span>%s</span><span class="pnst-chip pnst-chip--%s">%s</span></p><h3>%s</h3>'
                   '<dl><dt>The challenge</dt><dd class="pnst-sol__c">%s %s</dd><dt>What Perfect Nations advises</dt><dd>%s</dd></dl></li>' % (
                       q['status'], T(q['phase']), q['status'], ent(P['status_names'][q['status']]), T(q['standard']), T(q['challenge']), src(q['src']), T(q['advises']))
                   for q in Q['items'])
    solutions = '''
<section class="pnst-band pnst-iv" id="pnst-solutions" aria-labelledby="pnst-h2c">
  <div class="pnst-in">
    <div class="pnst-head"><div><p class="pnst-eb">03 &middot; Solutions</p><h2 class="pnst-h2" id="pnst-h2c">%s</h2></div><p class="pnst-lead">%s</p></div>
    <ol class="pnst-sols">%s</ol>
    <p class="pnst-hold">%s</p>
  </div>
</section>''' % (T(Q['title']), T(Q['line']), sols, T(Q['hold']))

    # 04 capital
    K = st['capital']
    caps = ''.join('<li class="pnst-cap1"><p class="pnst-cap1__f">%s%s</p><h3>%s<span>%s</span></h3><p>%s %s</p></li>' % (
        '<small>%s</small>' % ent(k['prefix']) if k['prefix'] else '', T(k['figure']), T(k['name']), T(k['year']), T(k['line']), src(k['src'])) for k in K['items'])
    capital = '''
<section class="pnst-band pnst-pp" id="pnst-capital" aria-labelledby="pnst-h2d">
  <div class="pnst-in">
    <div class="pnst-head"><div><p class="pnst-eb">04 &middot; Capital already committed</p><h2 class="pnst-h2" id="pnst-h2d">%s</h2></div><p class="pnst-lead">%s</p></div>
    <ul class="pnst-caps">%s</ul>
  </div>
</section>''' % (T(K['title']), T(K['line']), caps)

    # close and sources (in order of first use)
    for k in S:
        if k not in order:
            order.append(k)
    srcs = ''.join('<li>%s. <a href="%s" rel="noopener">%s</a>%s</li>' % (
        ent(S[k]['label']), S[k]['url'], ent(re.sub(r'^https://(www\.)?', '', S[k]['url']).split('/')[0]),
        (' &middot; <a href="%s" rel="noopener">%s</a>' % (S[k]['url2'], ent(re.sub(r'^https://(www\.)?', '', S[k]['url2']).split('/')[0])) if S[k].get('url2') else '')) for k in order)
    name_q = st['name'].replace(' ', '%20')
    close = '''
<div class="pn-rule" aria-hidden="true"></div>
<section class="pnst-band pnst-iv pnst-close" aria-labelledby="pnst-h2e">
  <div class="pnst-in">
    <div class="pnst-close__in">
      <div><p class="pnst-eb">Work with us</p><h2 class="pnst-h2" id="pnst-h2e">%s</h2><p class="pnst-lead">%s</p></div>
      <div class="pnst-ctas">
        <a class="pnst-btn" href="https://perfectnations.com/contact/?about=briefing&amp;country=%s">Request a briefing</a>
        <a class="pnst-btn pnst-btn--line" href="https://perfectnations.com/design-studio/">The ReDesign Studio</a>
        <a class="pnst-btn pnst-btn--line" href="https://perfectnations.com/50-states/">All 50 states</a>
      </div>
    </div>
    <details class="pnst-srcs"><summary>Sources (%d)</summary><ol>%s</ol></details>
    <p class="pnst-note">Every figure carries its source and year. Where no primary figure is published, the standard is shown as not yet measured. Perfect Nations&reg; is an independent advisory firm; the institutions named are cited for reference and do not endorse this blueprint.</p>
  </div>
</section>''' % (T(st['close']['title']), T(st['close']['line']), name_q, len(order), srcs)

    rule = (PAGES / 'home-rule.html').read_text(encoding='utf-8').strip()
    rule = re.sub(r'^\s*<!--.*?-->\s*', '', rule, count=1, flags=re.S)
    css = (US / 'state' / 'style.css').read_text(encoding='utf-8').strip().replace('#ROOT', '#' + root)
    js = (US / 'state' / 'script.js').read_text(encoding='utf-8').strip().replace("'ROOT'", "'%s'" % root)
    today = datetime.now(timezone.utc).strftime('%Y-%m-%d')
    head = '''<!-- ===========================================================================
PERFECT NATIONS - THE BLUEPRINT OF %s (THE 50 STATES) - THE WHOLE PAGE IN ONE FILE - v%s - %s
perfectnations.com/50-states/%s/ holds ONE Custom HTML block whose root is %s. The Perfect Nations Live Pages
plugin serves this file from GitHub in its place. Never edit this file by hand: edit data/us/states/%s.json (words,
figures, sources) or tools/us/state/ (design), run python3 tools/build_us_state.py %s, and open a pull request.
v1.0: the first state blueprint (the Steward-General, 10 Nov 2026). Bands: the gold state (Earthrise); 01 Assets
(ivory); 02 the seven standards and the county map (paper); 03 Solutions, in order (ivory); 04 Capital already
committed (paper); the gold line; Work with us and Sources (ivory). Water and Energy are shown as not yet measured:
no primary state figure was confirmed (EDITORIAL: add when the Surveyor confirms one).
=========================================================================== -->
''' % (ent(st['name'].upper()), st['version'], today, slug, root, slug, slug)
    body = '<div id="%s" data-version="%s">\n%s\n%s%s%s%s%s%s%s\n</div>\n' % (root, st['version'], rule, logo_parts(), hero, assets, pc, solutions, capital, close)
    page = head + '<style>\n%s\n</style>\n' % css + body + '<script>\n%s\n</script>\n' % js
    ids = re.findall(r'\bid\s*=\s*["\'](pn-[a-z0-9-]+)["\']', page)
    if ids[:1] != [root] or set(ids) != {root}:
        sys.exit('only the root may carry a pn- id: %s' % sorted(set(ids)))
    bad = [ch for ch in page if ord(ch) > 126]
    if bad:
        sys.exit('non-ASCII characters: %r' % bad[:5])
    out = PAGES / ('us-%s.html' % slug)
    out.write_text(page, encoding='utf-8')
    print('%s: %d characters; %d counties; %d sources; computed %s' % (out.relative_to(ROOT), len(page), len(cty), len(order),
          ', '.join('%s=%s' % kv for kv in sorted(c.items()))))


if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    build(sys.argv[1])
