#!/usr/bin/env python3
"""Build every national blueprint page (pages/blueprint-<slug>.html) from one template.

Blueprint v12.0 (10 November 2026). One design for every nation, so a change is made once and reaches all.
v12.0: light reading sections, Earthrise accents (the Steward-General, 10 Nov 2026: "the site is a little dark and
heavy to read; make as many sections as possible the lighter colour, with the Earthrise for the accents"). Colour
only, in the LIGHT block at the end of tools/nation/style.css: the hero (the globe and the nation at a glance) stays
Earthrise; What we do, 01 Assets, 02 Capital, Already working in <Nation>, 03 Solutions, the Letter, Work with us and
the close read on ivory and paper, alternating. Earthrise stays for the accents: the What we do tiles and the seal,
the lead Assets card, the laurels of Capital on an Earthrise disc, the seven stars on an Earthrise panel, the price
of Perfect <Nation>, the Sovereign Mandate, the co-design cards and the playbook Solution. Gold only for button
fills, the logo (always on Earthrise) and money (a deep gold, #8C6A12, on light).
v11.5: three changes for clarity (the Steward-General, 9 Nov 2026). 1. "The register" is "Capital already committed"
wherever a visitor reads it (the label, the hero tile link, the empty state and the Sources); the anchor bp-register
and the data key capital.register are unchanged. 2. "Already working in <Nation>" is its own band directly after
02 Capital (the record, Capital already committed and the Newswire) and before 03 Solutions, no longer inside Work
with us, with one line under its heading: "Independent firms and social enterprises already at work in <Nation>,
highlighted by Perfect Nations. None is a partner of Perfect Nations." Its cards, sources and links are kept.
3. Perfect Nations is "a new-age sovereign advisory firm, and its clients are nations", never a bank; the names of
real banks and their instruments are kept as they are.
v11.4: the Solution Perfect Nations designs for the nation leads its Solutions (the Steward-General, 9 Nov 2026:
"compose solutions that Perfect Nations designs"): its idea, The challenge and What Perfect Nations advises, linked to
State of Nations (#solution-NN). The market deals about the nation follow as Deal Notes (#deal-NN, or their own page),
from "deals" in data/state-of-nations.json and the nation's own file. The playbook brief shows only for a nation
without a designed Solution.
v11.3: the logo in one gold, #E3C258, with nothing dimmed: each What we do tile draws its own part alone, and
the faint cup under the seven stars of Solutions is gone (the Steward-General, 9 Nov 2026).
Also v11.3: fewer words (the Steward-General, 9 Nov 2026: "Fewer words everywhere: one headline and one line per
section across the site, with the detail one click away"). Each section shows an eyebrow, one headline, one line
and then its tiles, cards, figures or stars; further paragraphs and method notes sit behind a native
<details class="bpx-more"><summary>Read more</summary> in the section. The hero and What we do keep one line each;
the register shows four lines (its dates and terms open with the line); the Newswire shows three headlines, then
All news; a Solution shows The challenge and What Perfect Nations advises, and The deal opens on a click (its
label and text unchanged); the terms of the mandates sit behind Read more. Figures and sources are all kept.
v11.2 (the Steward-General, 9 Nov 2026): in What we do, the cup is the symbol for Assets; under the three tiles the
whole logo is a seal as large as the tile symbols, with "The whole logo: a Perfect Nation, where every citizen has
all seven basic standards of living, led by good governance."; in Work with us, Co-design it with us sits on an
ivory panel so the section does not look all alike.
v11.1: What Perfect Nations advises, in place of how FfD and SI solve it (the Steward-General, 9 Nov 2026). Each
Solution card reads 01 The challenge, 02 What Perfect Nations advises (the field "advises" of the Solution in
data/state-of-nations.json); the Solution for <Nation> reads 01 The challenge, 02 The deal (the instrument at work
in the nation, or the deal that proved it, with its source), 03 What Perfect Nations advises (the "advises" of the
standard in data/solutions-by-nation.json). The Solutions lead and the empty card say the same.
v11.0: the blueprint follows the new homepage (the Steward-General, 7-8 Nov 2026): Perfect Nations as a
new-age sovereign advisory firm, whose clients are nations, doing three things in the
order of the logo: 01 Assets (the gold), 02 Capital (the laurels), 03 Solutions (the seven stars, Perfect
Capita, last); the cup (good governance) is referenced in one line, and the whole logo, lit, is a Perfect
Nation. The page reads like the country page of a new-age sovereign advisory firm, in one scroll (as of v11.5):
  the hero (the globe, the nation, what Perfect Nations does for it, and the nation at a glance in sourced
  figures) -> What we do for <Nation> (three tiles drawn from the logo kit, and the seal) -> 01 Assets (five
  typographic cards, no photographs) -> 02 Capital (the record, Capital already committed and the Newswire)
  -> Already working in <Nation> (independent firms and social enterprises, none a partner) -> 03 Solutions
  (the seven stars of the logo in place of the wheel, each with the nation's own figure and source; the
  price of Perfect <Nation> where the data has it; the Solutions) -> the Letter -> Work with us (the
  ReDesign Studio and its three mandates, with Writings, Voices and the Co-designers) ->
  the close (the flag edition) and the Sources. Gold hairlines in place of the painted seams. No composite
  coverage score is shown: each standard keeps its own sourced figure.
v10.2: the second Nation Portrait, the flag edition, closes the page beside "Design Perfect <Nation> with us"
(40 nations; see FLAG_EDITION). It shows once pn-portrait-flag-<slug>.png is in the Media Library.
v10.1: FfD before SI (the Steward-General, 8 Nov 2026): innovative financing for development (FfD) is named
first and super intelligence (SI) second, and the abbreviation is written FfD.

Each page is built from:
  tools/nation/style.css    the design (scoped to the page root #pn-bp-<slug>; written with #R)
  tools/nation/script.js    the live page: reads data/<slug>.json, and near the Solutions
                            data/solutions-by-nation.json and data/state-of-nations.json
  tools/nation/globe.js     the nation globe: a small WebGL Earth with the nation in gold (no globe.gl)
  tools/nation/<slug>.json  the words that belong to the page and not to the data: the Letter, the portrait,
                            the people of the nation, the mandate moves, how Perfect Capita is measured,
                            the sources, the Nation Steward photo and the nation's outline
  data/<slug>.json          the Nation Steward's file: the page is built with today's figures, so the page
                            code (the fallback) matches what the live file shows
  data/solutions-by-nation.json, data/state-of-nations.json  (when present) the Solutions
  pages/home-logo-kit.html  the logo in its parts (pnk-*), drawn once in the page
  pages/header.html         the cup of the logo, beside the eyebrow of the hero

Run from the repository root:
  python3 tools/build_nations.py                 build every open blueprint
  python3 tools/build_nations.py kenya ghana     build these only
  python3 tools/build_nations.py --solutions PATH --son PATH   read the Solutions files from elsewhere
Then: python3 tools/check_page.py pages/blueprint-*.html, previews with tools/preview_nations.py, raise each
pn-bp-<slug> version in pages/manifest.json (this script does it with --manifest) and open a pull request
"For approval: 44 blueprints vX.Y, ...". Never edit a built page by hand.
Never put the word "laurel" in a class name or an id: the site header replaces any svg[class*="laurel"] with
the cup mark. The drawing of the laurels is "wreath".

A new nation: write tools/nation/<slug>.json (copy one and change every line), make sure data/<slug>.json exists,
run the build, add pn-bp-<slug> to the manifest.
"""
import argparse
import html
import json
import math
import re
import sys
import urllib.parse
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PAGES, DATA, HERE = ROOT / 'pages', ROOT / 'data', ROOT / 'tools' / 'nation'
VERSION = '12.8'  # every email from a blueprint goes to contact@perfectnations.com, in place of the .org address (the Steward-General, 12 Nov 2026)
# v12.7: a nation may name its own statistics office as the population source (pop_source in its page words); first, Cuba, re-measured on the delivery test (the Steward-General, 12 Nov 2026)
# v12.6: portraits for the 151 Nation Stewards who showed initials, generated in the Media Library in the house style (the Steward-General, 12 Nov 2026)
# v12.5: the globe turns like the real Earth, west to east (continents drift left to right), one turn every 90 seconds, as on the homepage (the Steward-General, 12 Nov 2026)
# v12.4: Voices of Perfect Nations: great local leaders, honest, dedicated and committed to basic standards of living for every citizen (the Steward-General, 11 Nov 2026)
# v12.3: the first edition of a new blueprint: the Letter stands alone until its portrait is painted, the Steward's initials until the photo; new nations join the manifest (10 Nov 2026)
# v12.2: the page scripts are written so the WordPress formatter leaves them alone: the moving globe starts on every blueprint, Mexico included (10 Nov 2026)
# v12.1: the Earth picture of the globe comes from the repository (jsDelivr, then GitHub), then the Media Library (10 Nov 2026)
# v12.0: light reading sections, Earthrise accents (the Steward-General, 10 Nov 2026)
# v11.9: Discuss this Solution on every designed Solution; Plan a Blueprint Lab opens The Blueprint Lab, ?about=lab (the Steward-General, 10 Nov 2026)
# v11.8: the globe with the nation in gold is drawn into the page, so the map shows on every phone even when the Earth picture or WebGL cannot (10 Nov 2026)
# v11.7: the letterhead carries the registered mark, Perfect Nations&#174; (10 Nov 2026)
# v11.6: the close button of every pop-up is one design: a gold X drawn as two strokes, centred in a circle (the Steward-General, 9 Nov 2026)
# The Earth picture of the globe (NASA Blue Marble), in this order: jsDelivr and GitHub, which both answer with
# Access-Control-Allow-Origin *, so a browser may paint the picture on the moving globe; then the Media Library copy.
# Checked live on 10 Nov 2026 in a real Chrome window: all three answer with Access-Control-Allow-Origin * and can be
# painted on the globe. (The v12.1 belief that the Media Library copy could not was wrong: the gold map alone came
# from the WordPress formatter breaking the page scripts, fixed in v12.2 by wp_script().)
# The files are assets/globe/earth-1536.jpg and earth-1024.jpg in this repository.
_GH = 'preetisinha70-PN/perfect-nations'
EARTH = {'lg': ['https://cdn.jsdelivr.net/gh/%s@main/assets/globe/earth-1536.jpg' % _GH,
                'https://raw.githubusercontent.com/%s/main/assets/globe/earth-1536.jpg' % _GH,
                'https://perfectnations.com/wp-content/uploads/2026/10/pn-globe-earth-day-1536x768.jpg'],
         'sm': ['https://cdn.jsdelivr.net/gh/%s@main/assets/globe/earth-1024.jpg' % _GH,
                'https://raw.githubusercontent.com/%s/main/assets/globe/earth-1024.jpg' % _GH,
                'https://perfectnations.com/wp-content/uploads/2026/10/pn-globe-earth-day-1024x512.jpg']}
ORDER = ['Food', 'Water', 'Shelter', 'Energy', 'Education', 'Health', 'Livelihoods']
COLOURS = ['#8A5A12', '#0E5A80', '#9A3E22', '#C08A12', '#1F4C96', '#167A5F', '#2F5A2A']
CAT = {'govt': 'Government', 'humanitarian': 'Humanitarian', 'multi': 'Multilateral', 'regional': 'Regional',
       'bilat': 'Bilateral', 'private': 'Private', 'impact': 'Impact'}
MONEY = re.compile(r'^(?:[A-Z]{0,3}\$|€|£|₹|₦|~?\$|(?:USD|EUR|KSh|Sh|GHS|ZAR|FCFA|CFA|MAD|EGP|ETB|NGN|PKR|BDT|INR|IDR|PHP|VND|LKR|MXN|COP|JOD|FJD|UAH|BBD|BWP|AOA|MZN|TZS|UGX|RWF|ZMW|MWK|NAD|SZL|LSL|SOS|SSP|CDF|BIF|MGA|XAF|XOF|JMD|BRL|R)\s?\d)')
MOVES = ['Identify the assets', 'Estimate Perfect Capita', 'Co-design the capital architecture', 'Launch the instruments']
TIERS = [
    ('Mandate 01', '3 hours', 'The Nation Briefing', 'A private session for the people who decide.', 'The gap, named and sized', 'Request a Nation Briefing'),
    ('Mandate 02', '3 days', 'The Blueprint Lab', 'Your team and ours, working the blueprint together.', 'The structure, drawn', 'Plan a Blueprint Lab'),
    ('Mandate 03', 'End to end', 'The Sovereign Mandate', 'Led personally by the President and CEO.', 'A structure ready for market', 'Discuss a Sovereign Mandate'),
]
# The seven stars of the logo, left to right, as the homepage draws them (home-perfect-capita.html v6.1):
# (index in ORDER, star of the logo kit, centre x, centre y, the crown). Food is the larger centre star.
STARS = [(1, 's0', 69.5, 171.2, False), (2, 's1', 138.3, 114.2, False), (3, 's2', 219.7, 77.2, False),
         (0, 's3', 319.6, 75.9, True), (4, 's4', 420.2, 77.2, False), (5, 's5', 501.6, 114.2, False),
         (6, 's6', 570.6, 171.2, False)]
STAR_T = 'translate(43.0 30.0) scale(1.85) translate(-105.9 -19.8)'


def plain(s):
    return '' if s is None else str(s)


def ent(s):
    """Plain text to HTML: escaped, every non-ASCII character as an entity, so the page stays ASCII."""
    return html.escape(plain(s), quote=True).encode('ascii', 'xmlcharrefreplace').decode('ascii')


def curl(s):
    """A headline as its source wrote it, with curly quotation marks, as the site copy requires (v12.5)."""
    s = plain(s)
    s = re.sub(r"(?<=[\w.,!?;:)\]])'", '\u2019', s)
    s = s.replace("'", '\u2018')
    s = re.sub(r'(^|[\s(\[])"', '\\1\u201c', s)
    return s.replace('"', '\u201d')


def raw(s):
    """HTML kept from a page (already escaped): non-ASCII characters as entities."""
    return plain(s).encode('ascii', 'xmlcharrefreplace').decode('ascii')


def https(u, allow_mail=False):
    u = plain(u)
    if allow_mail and re.match(r'^mailto:[^\s"\'<>]+$', u):
        return u
    if not re.match(r'^https://[^\s"\'<>()\\]+$', u):
        raise ValueError('not an https link without quotes, brackets or spaces: %r' % u)
    return u


def ok_https(u):
    return bool(re.match(r'^https://[^\s"\'<>()\\]+$', plain(u)))


def money(v, m):
    return '<span class="bpx-money">%s</span>' % ent(v) if m else ent(v)


def js_str(o):
    """JSON for a script block, ASCII only and safe inside <script>."""
    s = json.dumps(o, ensure_ascii=True, separators=(',', ':'))
    return s.replace('</', '<\\/')


def wp_script(js):
    """v12.2: an inline script the WordPress formatter leaves alone.
    A blueprint placed in a WordPress (block editor) page goes through wptexturize, which reads anything from a
    < to the next > as a tag and rewrites each & in it as &#038;. Inside a script that turns `m.x<1.&&m.y>0.`
    into `m.x<1.&#038;&#038;m.y>0.`: a syntax error, so on Mexico (10 Nov 2026) neither script ran and the globe
    stayed on the drawn gold map. Elementor pages (Kenya) skip the formatter, which is why only some nations broke.
    wptexturize skips HTML comments, so the script is written as one: <!-- opens a one-line comment in a
    classic script, and //--> closes it. The script must not hold -->, <!-- or <script, which would end the
    comment early or change how the browser reads the closing tag."""
    low = js.lower()
    for bad in ('-->', '<!--', '<script', '</script'):
        if bad in low:
            sys.exit('a blueprint script holds %r, which the WordPress-safe wrapper cannot carry' % bad)
    return '<script>\n<!--\n%s\n//-->\n</script>' % js


def mailto(subject, body=None):
    q = 'subject=' + urllib.parse.quote(subject, safe='')
    if body:
        q += '&body=' + urllib.parse.quote(body, safe='')
    return 'mailto:contact@perfectnations.com?' + q


def short_date(iso):
    try:
        d = datetime.strptime(iso, '%Y-%m-%d')
        return '%d %s %d' % (d.day, d.strftime('%b'), d.year)
    except (TypeError, ValueError):
        return plain(iso)


def long_date(iso):
    try:
        d = datetime.strptime(iso, '%Y-%m-%d')
        return '%d %s %d' % (d.day, d.strftime('%B'), d.year)
    except (TypeError, ValueError):
        return plain(iso)


MEDIA = {}


def srcset(url, widths):
    """The srcset of smaller copies that exist in the Media Library (tools/nation/media.json) and keep the
    picture's shape (a square crop never stands in for a portrait), or '' when none is known."""
    m = re.search(r'-(\d+)x(\d+)\.\w+$', url)
    cands = MEDIA.get(url) or []
    if not cands:
        return ''
    if m:
        ratio = int(m.group(2)) / int(m.group(1))
    else:
        big = [c for c in cands if re.search(r'-(\d+)x(\d+)\.\w+$', c[1])]
        if not big:
            return ''
        bm = re.search(r'-(\d+)x(\d+)\.\w+$', big[-1][1])
        ratio = int(bm.group(2)) / int(bm.group(1))
    out = []
    for w, u in cands:
        cm = re.search(r'-(\d+)x(\d+)\.\w+$', u)
        if w in widths and cm and abs(int(cm.group(2)) / int(cm.group(1)) - ratio) < 0.02:
            out.append('%s %dw' % (u, w))
    return ', '.join(out) if len(out) > 1 else ''


def img_attrs(url, widths, sizes):
    ss = srcset(url, widths)
    return ' srcset="%s" sizes="%s"' % (ent(ss), sizes) if ss else ''


def cup():
    src = (PAGES / 'header.html').read_text(encoding='utf-8')
    m = re.search(r'<svg[^>]*data-pn-cup="1"[^>]*>.*?</svg>', src, re.S)
    if not m:
        sys.exit('the cup icon was not found in pages/header.html')
    svg = re.sub(r'\sclass="[^"]*"', '', m.group(0), count=1)
    return re.sub(r'\sid="[^"]*"', '', svg)


def kit():
    """The logo kit of the homepage (pnk-cl, pnk-cc, pnk-lc, pnk-s0..pnk-s6, pnk-gold), drawn once in the page."""
    src = (PAGES / 'home-logo-kit.html').read_text(encoding='utf-8')
    m = re.search(r'<svg class="pnk-kit".*?</svg>', src, re.S)
    if not m or 'laurel' in m.group(0).lower():
        sys.exit('the logo kit was not found in pages/home-logo-kit.html')
    return m.group(0)


# ---------------------------------------------------------------- the logo, part by part

def _stars(cls=''):
    return ''.join('<use%s href="#pnk-s%d"/>' % (cls, i) for i in range(7))


# v11.3: the logo in one gold (#E3C258, pnk-gold in the logo kit) and nothing dimmed: each tile draws its own part
# alone, framed to fit (the cup, the laurels, the seven stars), as What we do does on the homepage and About.
ART = {
    'cup': '<svg class="bpx-art bpx-art--cup" viewBox="82.5 153 346 346" aria-hidden="true" focusable="false">'
           '<g class="lit"><use href="#pnk-cl" clip-path="url(#pnk-cc)"/></g></svg>',
    'wreath': '<svg class="bpx-art bpx-art--wreath" viewBox="10 63.75 491 491" aria-hidden="true" focusable="false">'
              '<g class="lit"><use href="#pnk-cl" clip-path="url(#pnk-lc)"/></g></svg>',
    'stars': '<svg class="bpx-art bpx-art--stars" viewBox="96 -45 320 220" aria-hidden="true" focusable="false">'
             '<g class="lit">%s</g></svg>' % _stars(),
}
SEAL = ('<svg class="bpx-seal" viewBox="0 0 512 512" aria-hidden="true" focusable="false"><circle class="disc" cx="256" cy="256" r="252"/>'
        '<circle class="rim" cx="256" cy="256" r="236"/><g transform="translate(256 262) scale(.7) translate(-256 -256)">'
        '<use href="#pnk-cl"/>%s</g></svg>' % _stars())


def more(inner, about, cls=''):
    """One click away (v11.3): a native disclosure. The summary reads Read more; its accessible name says what opens."""
    return ('<details class="bpx-more%s"><summary aria-label="Read more: %s">Read more</summary><div class="bpx-more__b">%s</div></details>'
            % ((' ' + cls) if cls else '', ent(about), inner))


def first_sentence(s):
    """The first sentence of a text, and the rest (or ''), split only where a full stop is followed by a capital."""
    t = plain(s).strip()
    m = re.search('(?<=[.!?])\\s+(?=[A-Z\u201c\u2026"])', t)
    return (t[:m.start()], t[m.end():]) if m else (t, '')


def chip(n, label):
    return ('<a class="bpx-ch" href="#bp-do" aria-label="Step %s of 03, %s. Back to What we do">%s</a>' % (n, label, n))


def step_eb(n, verb, part, name):
    return '<p class="bpx-eb bpx-eb--step">%s<span><b>%s</b> &#183; %s &#183; %s</span></p>' % (chip(n, verb), verb, part, name)


# ---------------------------------------------------------------- the seven standards

def num(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool) and 0 <= v <= 100


def fmt(v):
    r = round(v * 10) / 10
    return str(int(r)) if r == int(r) else str(r)


def lab(n):
    return 'Livelihood' if n == 'Livelihoods' else n


def pop_fmt(n):
    if not isinstance(n, (int, float)) or isinstance(n, bool) or n <= 0:
        return ''
    if n < 1e6:
        return '{:,}'.format(int(round(n)))
    if n < 1e9:
        return '%.1fm' % (n / 1e6)
    return '%.2fbn' % (n / 1e9)


def standards(d):
    """The seven standards and the one furthest from reach: the Nation Steward's set_by when it names one
    of the seven, otherwise the lowest figure. No composite score is computed or shown."""
    g = {x['name']: x for x in d.get('guarantees') or [] if x.get('name') in ORDER}
    if len(g) != 7:
        sys.exit('%s: the file does not hold the seven standards' % d.get('nation'))
    scored = [n for n in ORDER if num(g[n].get('value'))]
    cov = d.get('coverage') or {}
    set_by = cov.get('set_by')
    set_by = 'Livelihoods' if set_by == 'Livelihood' else set_by
    if set_by in g:
        bind = set_by
    else:
        bind = min(scored, key=lambda n: g[n]['value']) if scored else None
    return g, bind


def shown(x):
    """The figure of one standard as HTML: the Nation Steward's display, else the value, else a dash."""
    if plain(x.get('display')):
        return ent(x['display'])
    return fmt(x['value']) if num(x.get('value')) else '&#8211;'


def star_value(x):
    """The figure on a star: a word longer than seven letters (for example 'Not measured') becomes a dash on
    the star, and stays in full in the card beneath and in the list of the seven figures."""
    t = shown_text(x)
    return shown(x) if len(t) <= 7 else '&#8211;'


def shown_text(x):
    return plain(x.get('display')) or (fmt(x['value']) if num(x.get('value')) else '\u2013')


def gap_label(text, gap):
    t = plain(text).strip()
    t = t.split(':')[0] if ':' in t else re.split(r'(?<=\.)\s', t)[0]
    t = t.rstrip('.').strip()
    if t.startswith('Of ') and re.search(r'(%|in \d+)$', plain(gap)):
        t = 'of ' + t[3:]
    return t


def pop_source(p):
    # a nation whose own statistics office is the population of record names it in its page words (Cuba, 12 Nov 2026)
    if plain(p.get('pop_source')):
        return plain(p['pop_source'])
    m = re.search(r'population,? (\d{4})', plain((p.get('sources') or [''])[0]))
    return 'World Bank, %s' % m.group(1) if m else 'World Bank'


def price_ok(cov):
    return bool(re.match(r'^\$[0-9][0-9.,]*(bn|m|B|M)?$', plain(cov.get('price')))) and bool(re.match(r'^\$[0-9][0-9,]*$', plain(cov.get('perfect_capita'))))


# ---------------------------------------------------------------- the sections


# ---------------------------------------------------------------- the globe drawn into the page (v11.8)
GLOBE_DIST, GLOBE_RAD = 2.25, 0.47   # the camera of tools/nation/globe.js: 2.25 radii out, the sphere 0.47 of the box


def globe_svg(slug, gl):
    """The nation in gold on the globe, drawn at build time as SVG with the camera of globe.js at its first frame
    (centred on the nation, tilted to 0.82 of its latitude). It is in the page before any script or picture, so
    the map is always there: on a slow phone, when the Earth picture cannot load, or without WebGL. The moving
    Earth fades in over it when it is ready. A small nation (or one with no outline) also gets the gold marker."""
    D2R = math.pi / 180
    lat0, lng0 = float(gl['lat']), float(gl['lng'])
    lon, lat = lng0 * D2R, lat0 * D2R * 0.82
    cp, sp, cl, sl = math.cos(lon), math.sin(lon), math.cos(lat), math.sin(lat)
    m = [cp, -sp * sl, sp * cl, 0, cl, sl, -sp, -cp * sl, cp * cl]
    R = 1000 * GLOBE_RAD
    F = R * math.sqrt(GLOBE_DIST * GLOBE_DIST - 1)

    def proj(lo, la):
        a, b = la * D2R, lo * D2R
        w = (math.cos(a) * math.sin(b), math.sin(a), math.cos(a) * math.cos(b))
        nx = m[0] * w[0] + m[3] * w[1] + m[6] * w[2]
        ny = m[1] * w[0] + m[4] * w[1] + m[7] * w[2]
        nz = m[2] * w[0] + m[5] * w[1] + m[8] * w[2]
        if nz > 1 / GLOBE_DIST:
            x, y = F * nx / (GLOBE_DIST - nz), F * ny / (GLOBE_DIST - nz)
            return 500 + x, 500 - y, True
        h = math.hypot(nx, ny) or 1.0
        return 500 + R * nx / h, 500 - R * ny / h, False

    def fmt(v):
        return ('%.1f' % v).rstrip('0').rstrip('.')

    # the nation, and the box the WebGL mask uses (the same test decides the marker)
    land, n, x0, x1, y0, y1 = [], 0, 1e9, -1e9, 1e9, -1e9
    for g in gl.get('outline') or []:
        polys = g['coordinates'] if g.get('type') == 'MultiPolygon' else [g['coordinates']]
        for rings in polys:
            for ring in rings:
                pts = [proj(pt[0], pt[1]) for pt in ring]
                for pt in ring:
                    x = (pt[0] - lng0 + 540) % 360 - 180
                    n += 1
                    x0, x1, y0, y1 = min(x0, x), max(x1, x), min(y0, pt[1]), max(y1, pt[1])
                if len(pts) < 3 or not any(v for _, _, v in pts):
                    continue
                land.append('M' + 'L'.join('%s %s' % (fmt(a), fmt(b)) for a, b, _ in pts) + 'Z')
    small = True
    if n:
        mx, my = max(0.8, (x1 - x0) * 0.08), max(0.8, (y1 - y0) * 0.08)
        small = (x1 - x0 + 2 * mx) * (y1 - y0 + 2 * my) < 40

    # a faint graticule, every 30 degrees, drawn only on the near side
    grat = []
    lines = [[(lo, la) for la in range(-80, 81, 4)] for lo in range(-180, 180, 30)]
    lines += [[(lo, la) for lo in range(-180, 181, 4)] for la in (-60, -30, 0, 30, 60)]
    for line in lines:
        seg = []
        for lo, la in line:
            x, y, vis = proj(lo, la)
            if vis:
                seg.append('%s %s' % (fmt(x), fmt(y)))
            elif seg:
                if len(seg) > 1:
                    grat.append('M' + 'L'.join(seg))
                seg = []
        if len(seg) > 1:
            grat.append('M' + 'L'.join(seg))

    mark = ''
    if small:
        x, y, _ = proj(lng0, lat0)
        mark = ('<circle cx="%s" cy="%s" r="30" fill="#E3C258" fill-opacity=".25"/>'
                '<circle cx="%s" cy="%s" r="15" fill="#E3C258" stroke="#FFF2B2" stroke-width="3"/>') % (fmt(x), fmt(y), fmt(x), fmt(y))
    k = 'bpg-' + slug
    return (
        '<svg class="bpx-globe__sky" viewBox="0 0 1000 1000" aria-hidden="true" focusable="false">'
        '<defs><radialGradient id="%(k)s-sea" cx="36%%" cy="30%%" r="70%%"><stop offset="0" stop-color="#3E8FB0"/>'
        '<stop offset=".42" stop-color="#145E7A"/><stop offset=".78" stop-color="#0B3D45"/><stop offset="1" stop-color="#072A30"/></radialGradient>'
        '<radialGradient id="%(k)s-halo"><stop offset=".86" stop-color="#5DB5E8" stop-opacity=".24"/><stop offset="1" stop-color="#5DB5E8" stop-opacity="0"/></radialGradient></defs>'
        '<circle cx="500" cy="500" r="545" fill="url(#%(k)s-halo)"/>'
        '<circle cx="500" cy="500" r="%(r)s" fill="url(#%(k)s-sea)" stroke="#BFE3FF" stroke-opacity=".22" stroke-width="2"/>'
        '<path d="%(grat)s" fill="none" stroke="#E3C258" stroke-opacity=".16" stroke-width="1.5"/>'
        '%(land)s%(mark)s</svg>'
    ) % {'k': k, 'r': fmt(R), 'grat': ''.join(grat),
         'land': ('<path d="%s" fill="#EBBE4E" fill-rule="evenodd" stroke="#FFF2B2" stroke-width="2.5" stroke-linejoin="round"/>' % ''.join(land)) if land else '',
         'mark': mark}

def hero(d, p):
    h = d.get('hero') or {}
    name = d['nation']
    cov = d.get('coverage') or {}
    g, bind = standards(d)
    cells = []
    pop = pop_fmt(d.get('population'))
    if pop:
        cells.append('<li data-k="pop"><b>%s</b><span>People</span><small>%s</small></li>' % (pop, ent(pop_source(p))))
    if bind and cov.get('gap'):
        x = g[bind]
        src = ('<a href="%s" target="_blank" rel="noopener noreferrer">%s</a>' % (ent(https(x['url'])), ent(x.get('source') or 'Source'))
               if ok_https(x.get('url')) else '<small>%s</small>' % ent(x.get('source') or ''))
        cells.append('<li data-k="gap" class="is-gap"><em>Furthest from reach &#183; <i>%s</i></em><b>%s</b><span>%s</span>%s</li>'
                     % (lab(bind), ent(cov['gap']), ent(gap_label(cov.get('gap_text'), cov['gap'])), src))
    if price_ok(cov):
        cells.append('<li data-k="price"><b class="bpx-money">%s</b><span>The price of Perfect %s, a year</span>'
                     '<a href="#bp-pc">Perfect Nations estimate</a></li>' % (ent(cov['price']), ent(name)))
    nreg = len([x for x in (d.get('capital') or {}).get('register') or [] if x.get('name') and x.get('cat') and x.get('url')])
    if nreg:
        cells.append('<li data-k="reg"><b>%d</b><span>%s on record</span><a href="#bp-register">Capital already committed</a></li>'
                     % (nreg, 'Instrument or investment' if nreg == 1 else 'Instruments and investments'))
    long_name = ' is-long' if len(name) > 11 else ''
    return (
        '<section class="bpx-band bpx-er bpx-hero" aria-labelledby="bp-h1"><div class="bpx-in bpx-hero__grid">'
        '<div class="bpx-hero__head"><div class="bpx-kick"><span class="bpx-cup">%s</span><p class="bpx-eb">%s</p></div>'
        '<h1 class="bpx-h1%s" id="bp-h1">%s</h1><p class="bpx-hero__nation">%s</p>'
        '<p class="bpx-lead">Perfect Nations values what %s owns and raises capital against it, through <b>innovative financing for development (FfD)</b> '
        'and <b>super intelligence (SI)</b>.</p></div>'
        '<div class="bpx-globe-cell"><div class="bpx-globe" id="%s-globe" role="img" aria-label="%s, in gold on the globe">'
        '%s<canvas class="bpx-globe__still"></canvas><canvas class="bpx-globe__gl"></canvas></div></div>'
        '<div class="bpx-glance"><p class="bpx-k">%s at a glance</p><ul class="bpx-stats" data-n="%d">%s</ul></div>'
        '<div class="bpx-btns bpx-hero__ctas"><a class="bpx-btn" href="#bp-studio">Work with us</a>'
        '<a class="bpx-btn bpx-btn--line" href="#bp-letter">Read the Letter to %s</a></div>'
        '</div></section>'
        % (cup(), ent(p['eyebrow']), long_name, ent(name), ent(h.get('lead', '')), ent(name), p['slug'], ent(name),
           globe_svg(p['slug'], p['globe']), ent(name), len(cells), ''.join(cells), ent(name)))


def what_we_do(d):
    name = d['nation']
    g, bind = standards(d)
    items = [x for x in (d.get('assets') or {}).get('items') or [] if x.get('name')]
    names = [x['name'] for x in items]
    if len(names) > 1:
        # v11.3: the names are on the cards below, so the tile names the first and the last
        q1 = '%s sovereign assets, valued, from %s to %s.' % ((['No', 'One', 'Two', 'Three', 'Four', 'Five', 'Six', 'Seven'][len(names)] if len(names) < 8 else str(len(names))), names[0], names[-1])
    else:
        q1 = 'We value what %s owns: its sovereign assets, from its people to its land.' % name
    lines = [x for x in (d.get('capital') or {}).get('register') or [] if x.get('name') and x.get('cat') and x.get('url')]
    # v11.3: one short line a tile; the kinds of source are the filters of the register, so they are not repeated here
    q2 = (('One instrument on record, sourced.' if len(lines) == 1 else '%d instruments and investments on record, every one sourced.' % len(lines)) if lines
          else 'The instruments that raise capital against those assets, from every source.')
    q3 = 'Seven basic standards of living, star by star.%s' % ((' %s is furthest from reach today.' % lab(bind)) if bind else '')
    tiles = [('01', 'Assets', 'The cup', '#bp-assets', ART['cup'], q1),
             ('02', 'Capital', 'The laurels', '#bp-capital', ART['wreath'], q2),
             ('03', 'Solutions', 'The seven stars', '#bp-pc', ART['stars'], q3)]
    lis = ''.join(
        '<li style="--i:%d"><a class="bpx-t" href="%s" aria-label="Step %s, %s: %s. %s">%s<span class="bpx-t__top"><span class="bpx-n">%s</span>'
        '<span class="bpx-t__v">%s</span></span><span class="bpx-t__p">%s</span><span class="bpx-t__q">%s</span></a></li>'
        % (i, href, n, v, part, ent(q), art, n, v, part, ent(q)) for i, (n, v, part, href, art, q) in enumerate(tiles))
    return (
        '<section class="bpx-band bpx-iv bpx-do" id="bp-do" aria-labelledby="bp-do-h"><div class="bpx-in">'
        '<div class="bpx-do__head"><div><p class="bpx-eb">What we do for %s</p>'
        '<h2 class="bpx-h2 bpx-do__h" id="bp-do-h"><span>Assets.</span> <span>Capital.</span> <span>Solutions.</span></h2></div>'
        '<p class="bpx-lead">Perfect Nations is a new-age sovereign advisory firm, and its clients are nations.</p></div>'
        '<ol class="bpx-map" aria-label="The three steps for %s, one for each part of the logo">%s</ol>'
        '<div class="bpx-all">%s<p><b>The whole logo:</b> a Perfect Nation, where every citizen has all seven basic standards '
        'of living, led by good governance.</p></div>'
        '</div></section>' % (ent(name), ent(name), lis, SEAL))


def assets(d):
    a = d.get('assets') or {}
    name = d['nation']
    cards = []
    for i, x in enumerate(a.get('items') or []):
        if not x.get('name'):
            continue
        cards.append(
            '<li class="bpx-acard" style="--i:%d"><span class="bpx-acard__n" aria-hidden="true">%02d</span>'
            '<p class="bpx-acard__fig"><b>%s</b>%s</p><h3>%s</h3>%s</li>'
            % (i, i + 1, ent(x.get('figure') or ''), '<span>%s</span>' % ent(x['label']) if x.get('label') else '',
               ent(x['name']), '<p>%s</p>' % ent(x['text']) if x.get('text') else ''))
    if not cards:
        cards = ['<li class="bpx-acard"><span class="bpx-acard__n" aria-hidden="true">01</span><h3>The ledger of %s is in preparation.</h3>'
                 '<p>The Surveyor values what the nation owns, from its people to its land, with a source for every figure.</p></li>' % ent(name)]
    return (
        '<section class="bpx-band bpx-er bpx-assets" id="bp-assets" aria-labelledby="bp-assets-h"><div class="bpx-in">'
        '<div class="bpx-head"><div>%s<h2 class="bpx-h2" id="bp-assets-h">%s</h2></div>'
        '<p class="bpx-lead">Each is owned today, earns today, and can carry %s toward seven basic standards of living for every citizen.</p></div>'
        '<ul class="bpx-acards" data-n="%d">%s</ul>'
        '<div class="bpx-foot"><a class="bpx-link" href="#bp-sources">Every figure, with its source</a>'
        '<a class="bpx-link" href="https://perfectnations.com/sovereign-assets/" target="_blank" rel="noopener noreferrer">The Sovereign Assets ledger</a></div>'
        '</div></section>' % (step_eb('01', 'Assets', 'The cup', 'Sovereign Assets'),
                              ent(a.get('heading') or 'Five assets no balance sheet counts.'), ent(name), len(cards), ''.join(cards)))


def stew_face(photo, steward):
    """The Nation Steward's photo; v12.3: a new blueprint without one shows the Steward's initials in a gold ring."""
    if ok_https(photo):
        return ('<img src="%s"%s alt="%s, %s" width="44" height="44" loading="lazy" decoding="async" onerror="this.style.display=\'none\'">'
                % (ent(https(photo)), img_attrs(photo, (100, 150), '44px'), ent(steward.get('name', '')), ent(steward.get('role', ''))))
    ini = ''.join(w[0] for w in plain(steward.get('name')).split()[:2] if w)
    return '<i class="bpx-stew__ini" aria-hidden="true">%s</i>' % ent(ini or 'PN')


def capital(d, p):
    name = d['nation']
    c = d.get('capital') or {}
    recs = ''.join('<li><b>%s</b><span>%s</span><a href="%s" target="_blank" rel="noopener noreferrer">%s</a></li>'
                   % (money(x['value'], x.get('money')), ent(x['text']), ent(https(x['url'])), ent(x.get('source') or 'Source'))
                   for x in c.get('record') or [] if x.get('value') and x.get('text') and x.get('url'))
    lines = [x for x in c.get('register') or [] if x.get('name') and x.get('cat') and x.get('url')]
    count = {}
    irs = []
    for i, x in enumerate(lines):
        cat = re.sub(r'[^a-z]', '', x['cat'])
        tone = re.sub(r'[^a-z]', '', plain(x.get('tone'))) or 'active'
        count[cat] = count.get(cat, 0) + 1
        by = ''.join('<span>%s</span>' % ent(s) for s in x.get('by') or [] if s)
        # v11.3: a line shows its kind, its status, its name and its amount; the dates and terms open with it
        irs.append(
            '<li class="bpx-ir%s" data-cat="%s"><details><summary><span class="bpx-tags"><span class="bpx-cat">%s</span><span class="bpx-stat bpx-stat--%s">%s</span></span>'
            '<span class="bpx-ir__n">%s</span><span class="bpx-ir__a">%s</span></summary><div class="bpx-ir__b">%s%s%s%s'
            '<a class="bpx-ir__src" href="%s" target="_blank" rel="noopener noreferrer">Source</a></div></details></li>'
            % (' bpx-ir--more' if i >= 4 else '', cat, CAT.get(cat, cat), tone, ent(x.get('status') or 'Active'), ent(x['name']),
               money(x['amount'], x.get('money')) if x.get('amount') else '',
               '<p class="bpx-ir__d">%s</p>' % ent(x['detail']) if x.get('detail') else '',
               '<p class="bpx-ir__note">%s</p>' % ent(x['note']) if x.get('note') else '', '<p>%s</p>' % ent(x['text']) if x.get('text') else '',
               '<p class="bpx-ir__by">%s</p>' % by if by else '', ent(https(x['url']))))
    if not irs:
        irs = ['<li class="bpx-ir bpx-ir--none"><p>The capital already committed to %s is being gathered: every instrument and investment on record, with its source.</p></li>' % ent(name)]
    keys = ['all'] + [k for k in CAT if count.get(k)]
    filters = ''.join('<button type="button" class="bpx-fb%s" data-filter="%s" aria-pressed="%s">%s <span>%d</span></button>'
                      % (' is-on' if k == 'all' else '', k, 'true' if k == 'all' else 'false', 'All' if k == 'all' else CAT[k],
                         len(lines) if k == 'all' else count[k]) for k in keys) if lines else ''
    steward = d.get('steward') or {}
    wire = []
    for w in (d.get('newswire') or [])[:5]:
        if not (w.get('title') and plain(w.get('url')).startswith('https://')):
            continue
        t, hl = curl(w['title']), curl(w.get('highlight')) if w.get('highlight') else None
        b = ent(t)
        if hl and hl in t:
            i = t.index(hl)
            b = ent(t[:i]) + '<span class="bpx-money">%s</span>' % ent(hl) + ent(t[i + len(hl):])
        wire.append('<li><time datetime="%s">%s</time><a href="%s" target="_blank" rel="noopener noreferrer"><b>%s</b></a><span class="bpx-src">%s</span></li>'
                    % (ent(w.get('date', '')), ent(w.get('label') or short_date(w.get('date'))), ent(https(w['url'])), b, ent(w.get('source', ''))))
    if not wire:
        wire = ['<li class="bpx-wire__none"><b>The first sourced news for %s is in review.</b></li>' % ent(name)]
    return (
        '<section class="bpx-band bpx-lg bpx-cap" id="bp-capital" aria-labelledby="bp-cap-h"><div class="bpx-in">'
        '<div class="bpx-head bpx-cap__head">%s<div>%s<h2 class="bpx-h2" id="bp-cap-h">%s</h2></div>'
        '<div><p class="bpx-lead">Bonds, guarantees, swaps and loans that raise capital against what %s owns, every line sourced.</p>'
        '<a class="bpx-link" href="https://perfectnations.com/capital-architecture/" target="_blank" rel="noopener noreferrer">Capital Architecture</a></div></div>'
        '%s'
        '<div class="bpx-cap__grid"><div id="bp-register"><p class="bpx-k">Capital already committed</p>'
        '<div class="bpx-filters" role="group" aria-label="Show lines by who provides them">%s</div>'
        '<ul class="bpx-irs" id="bp-irs">%s</ul><button type="button" class="bpx-showall" id="bp-showall"%s>Show all %d lines</button></div>'
        '<div class="bpx-nw" id="bp-newswire"><div class="bpx-nw__h"><h3>The %s Newswire</h3>'
        '<a class="bpx-link" href="https://perfectnations.com/state-of-nations/#sn-wire" target="_blank" rel="noopener noreferrer">The Solutions Wire</a></div>'
        '<div class="bpx-stew">%s'
        '<p><b>%s</b><span>%s &#183; SI Researcher</span><time datetime="%s">Last updated %s</time></p></div>'
        '<ul class="bpx-wire">%s</ul><button type="button" class="bpx-showall bpx-allnews" hidden>All news</button></div></div>'
        '</div></section>'
        % (ART['wreath'].replace('bpx-art bpx-art--wreath', 'bpx-art bpx-art--wreath bpx-mark'),
           step_eb('02', 'Capital', 'The laurels', 'Capital Architecture'), ent(c.get('heading') or 'Capital tied to human outcomes.'), ent(name),
           ('<p class="bpx-k">The record in figures</p><ul class="bpx-recs bpx-rail">%s</ul>' % recs) if recs else '',
           filters, ''.join(irs), '' if len(lines) > 4 else ' hidden', len(lines),
           ent(name), stew_face(p.get('steward_photo'), steward),
           ent(steward.get('name', '')), ent(steward.get('role', '')), ent(d.get('updated', '')), ent(long_date(d.get('updated'))),
           ''.join(wire)))


def stars_svg(name, g, bind):
    parts = ['<svg class="bpx-stars has-on" viewBox="0 0 640 452" role="group" aria-labelledby="bp-stars-t" focusable="false">'
             '<title id="bp-stars-t">%s: the seven stars of the logo, one for each basic standard of living, rising from the cup; '
             'Food is the larger centre star. Each star carries the figure for %s.</title>'
             '<g class="bpx-stars__cup" transform="translate(161.3 128.2) scale(0.62)"><use href="#pnk-cl"/></g><g class="bpx-stars__rays">' % (ent(name), ent(name))]
    for k, s, cx, cy, crown in STARS:
        parts.append('<line x1="320.0" y1="232.4" x2="%.1f" y2="%.1f"/>' % (cx, cy + (43.4 if crown else 23.7)))
    parts.append('</g>')
    for pos, (k, s, cx, cy, crown) in enumerate(STARS):
        n = ORDER[k]
        x = g[n]
        r = 63.7 if crown else 34.8
        ly, vy = (cy + 68.3, cy + 102.3) if crown else (cy + 43.3, cy + 70.3)
        label = '%s: %s%s' % (lab(n), shown_text(x), ', the standard furthest from reach' if n == bind else '')
        parts.append(
            '<g class="bpx-star%s%s%s" data-i="%d" data-pos="%d" role="button" tabindex="0" aria-pressed="%s" aria-label="%s" style="--c:%s;--d:%.2fs">'
            '<circle class="bpx-star__halo" cx="%.1f" cy="%.1f" r="%.1f"/><circle class="bpx-star__ring" cx="%.1f" cy="%.1f" r="%.1f"/>'
            '<use class="bpx-star__s" href="#pnk-%s" transform="%s"/>'
            '<text x="%.1f" y="%.1f" text-anchor="middle" class="bpx-star__l">%s</text>'
            '<text x="%.1f" y="%.1f" text-anchor="middle" class="bpx-star__v">%s</text></g>'
            % (' bpx-star--crown' if crown else '', ' is-bind' if n == bind else '', ' is-on' if n == bind else '', k, pos,
               'true' if n == bind else 'false', ent(label), COLOURS[k], abs(pos - 3) * 0.12,
               cx, cy, r, cx, cy, 44 if crown else 27, s, STAR_T, cx, ly, lab(n).upper(), cx, vy, star_value(x)))
    parts.append('</svg>')
    return ''.join(parts)


def how(rows):
    """The rows of a Solution (v11.3): The challenge and What Perfect Nations advises show (the Steward-General's two
    lines); The deal opens on a click, with its label as the summary. The texts stay as the data has them. Each text
    is HTML already."""
    out = []
    for i, (n, t, w) in enumerate(rows):
        if t != 'The deal':
            out.append('<li><b>%s</b><strong>%s</strong><span>%s</span></li>' % (n, t, w))
        else:
            out.append('<li class="bpx-sol__x"><details><summary><b>%s</b><strong>%s</strong></summary><span>%s</span></details></li>' % (n, t, w))
    return '<ul class="bpx-sol__how">%s</ul>' % ''.join(out)


def solution_card(x, sig_name, sig_role):
    """v11.4: a Solution Perfect Nations designs (kind "design"), or a Deal Note (kind "deal": a market deal read by
    Perfect Nations, from State of Nations or the nation's own file)."""
    no = int(x.get('no') or 0)
    deal = x.get('kind') == 'deal'
    href = x['url'] if re.match(r'^https://', plain(x.get('url'))) else 'https://perfectnations.com/state-of-nations/#%s-%02d' % ('deal' if deal else 'solution', no)
    body = ''
    if x.get('kind') == 'design' and x.get('standfirst'):
        body = '<p>%s</p>' % ent(x['standfirst'])
    if x.get('challenge') and x.get('advises'):
        body += how([('01', 'The challenge', ent(x['challenge'])), ('02', 'What Perfect Nations advises', ent(x['advises']))])
    elif x.get('standfirst') or x.get('summary'):
        one, rest = first_sentence(x.get('standfirst') or x.get('summary'))
        body = '<p>%s</p>%s' % (ent(one), more('<p>%s</p>' % ent(rest), x['title']) if rest else '')
    fig = ''
    if x.get('figure'):
        fig = '<p class="bpx-sol__fig"><b>%s</b>%s</p>' % (ent(x['figure']), '<span>%s</span>' % ent(x['caption']) if x.get('caption') else '')
    # v11.9: a Solution Perfect Nations designs also offers "Discuss this Solution", which opens the Contact page
    # on Discuss a Solution with this Solution and its nation chosen (?about=solution-NN&country=Nation)
    talk = ''
    if x.get('kind') == 'design' and no:
        talk = ('<a class="bpx-btn bpx-btn--line" href="%s" target="_blank" rel="noopener noreferrer">Discuss this Solution</a>'
                % ent(https('https://perfectnations.com/contact/?about=solution-%d&country=%s' % (no, urllib.parse.quote(plain(x.get('nation')), safe='')))))
    return (
        '<li class="bpx-sol"><p class="bpx-sol__k"><b>%s No. %02d</b><time datetime="%s">%s</time></p>'
        '<h3><a href="%s" target="_blank" rel="noopener noreferrer">%s</a></h3>%s%s'
        '<div class="bpx-sol__foot"><span class="bpx-sig">From<b>%s</b><small>%s</small></span>'
        '<span class="bpx-sol__acts"><a class="bpx-btn" href="%s" target="_blank" rel="noopener noreferrer">Read the %s</a>%s</span></div></li>'
        % ('Deal Note' if deal else 'Solution', no, ent(x.get('date', '')), ent(x.get('label') or short_date(x.get('date'))), ent(https(href)), ent(x['title']), body, fig,
           ent(sig_name), ent(sig_role), ent(https(href)), 'Deal Note' if deal else 'Solution', talk))


def solution_brief(name, sbn, slug):
    me = next((n for n in sbn.get('nations', []) if n.get('slug') == slug), None)
    if not me:
        return ''
    play = next((s for s in sbn.get('standards', []) if s.get('standard') == me.get('standard')), None)
    if not play or not play.get('advises'):
        return ''
    src = me.get('source') or {}
    ch = ent(((me.get('gap') + ' ') if me.get('gap') else '') + plain(me.get('gap_text')))
    if src.get('url'):
        ch += ' <a href="%s" target="_blank" rel="noopener noreferrer">%s</a>' % (ent(https(src['url'])), ent(src.get('label') or 'Source'))
    # 02 The deal: the instrument already at work in the nation, or else the deal that proved the playbook
    deal = ''
    aw = me.get('at_work')
    if aw and aw.get('name') and aw.get('url'):
        deal = ent('At work in %s: %s%s.' % (name, aw['name'], (', ' + aw['amount']) if aw.get('amount') else ''))
        deal += ' <a href="%s" target="_blank" rel="noopener noreferrer">Source</a>' % ent(https(aw['url']))
    elif play.get('proof') and play['proof'].get('url'):
        pr = play['proof']
        deal = ent('%s, proved in %s, %s: %s %s.' % (play['name'], pr['where'], pr['year'], pr['figure'], pr['label']))
        deal += ' <a href="%s" target="_blank" rel="noopener noreferrer">%s</a>' % (ent(https(pr['url'])), ent(pr.get('source') or 'Source'))
    steps = [('01', 'The challenge', ch)] + ([('02', 'The deal', deal)] if deal else [])
    steps.append(('%02d' % (len(steps) + 1), 'What Perfect Nations advises', ent(play['advises'])))
    return (
        '<li class="bpx-sol bpx-sol--brief"><p class="bpx-sol__k"><b>The Solution for %s</b><span>%s</span></p>'
        '<h3>%s</h3>%s'
        '<div class="bpx-sol__foot"><span class="bpx-sig">Co-design it in<b>The ReDesign Studio</b></span>'
        '<a class="bpx-btn" href="#bp-mandates">The three mandates</a></div></li>'
        % (ent(name), ent(me['standard']), ent(play.get('head') or ''), how(steps)))


def solution_cards(d, p, sbn, son):
    """The Solution for this nation (State of Nations), then every Solution about it, newest first."""
    name, slug = d['nation'], p['slug']
    steward = d.get('steward') or {}
    cards, seen, nos = [], set(), []
    if sbn:
        me = next((n for n in sbn.get('nations', []) if n.get('slug') == slug), None)
        nos = (me or {}).get('solutions') or []
    pool = []
    as_deal = lambda x: x if x.get('kind') else dict(x, kind='deal')
    for x in (son or {}).get('dispatches', []):
        if x.get('no') and x.get('title') and ((x['no'] in nos and x.get('kind') != 'design') or x.get('nation') == name):
            pool.append((x, 'preeti'))
    for x in (son or {}).get('deals', []):
        if x.get('no') and x.get('title') and x.get('nation') == name:
            pool.append((as_deal(x), 'preeti'))
    for x in d.get('dispatches') or []:
        if x.get('no') and x.get('title'):
            pool.append((as_deal(x), 'steward' if x.get('author') in ('steward', 'nia') else 'preeti'))
    designed = any(x.get('kind') == 'design' for x, _ in pool)
    pool.sort(key=lambda t: (t[0].get('kind') == 'design', plain(t[0].get('date')), t[0]['no']), reverse=True)
    for x, who in pool:
        key = ('s' if x.get('kind') == 'design' else 'd', x['no'])
        if key in seen:
            continue
        seen.add(key)
        if who == 'steward':
            cards.append(solution_card(x, steward.get('name', ''), '%s &#183; SI Researcher' % steward.get('role', '')))
        else:
            cards.append(solution_card(x, 'Preeti Sinha', 'President and CEO, Perfect Nations'))
    lead = solution_brief(name, sbn, slug) if sbn and not designed else ''
    cards = ([lead] if lead else []) + cards[:5 if lead else 6]
    cards = [c if i < 3 else c.replace('<li class="bpx-sol"', '<li class="bpx-sol bpx-sol--more"', 1) for i, c in enumerate(cards)]
    more = ('<button type="button" class="bpx-showall bpx-solmore" aria-expanded="false">Show all %d Solutions</button>' % len(cards)) if len(cards) > 3 else ''
    if not cards:
        cards = ['<li class="bpx-sol"><p class="bpx-sol__k"><b>Solutions</b></p><h3>The first Solution for %s is in preparation.</h3>'
                 '<p>Every Solution names the challenge to the seven standards, the deal that meets it and what Perfect Nations advises.</p></li>' % ent(name)]
    return ''.join(cards), more


def solutions(d, p, sbn, son):
    name = d['nation']
    g, bind = standards(d)
    cov = d.get('coverage') or {}
    x = g[bind] if bind else None
    # the card under the stars: the standard furthest from reach, until a star is chosen
    if x:
        call_src = ('<a id="bp-call-s" href="%s" target="_blank" rel="noopener noreferrer">%s</a>' % (ent(https(x['url'])), ent(x.get('source') or 'Source'))
                    if ok_https(x.get('url')) else '<a id="bp-call-s" hidden></a>')
        call = ('<div class="bpx-call" id="bp-call" style="--c:%s" aria-live="polite"><b id="bp-call-v">%s</b><div class="bpx-call__t">'
                '<small><span id="bp-call-n">%s</span><span id="bp-call-f"> &#183; furthest from reach</span></small><span id="bp-call-l">%s</span>%s</div></div>'
                % (COLOURS[ORDER.index(bind)], shown(x), lab(bind), ent(x.get('note') or ''), call_src))
    else:
        call = ''
    tiles = []
    for k, n in enumerate(ORDER):
        y = g[n]
        src = '<a href="%s" target="_blank" rel="noopener noreferrer">%s</a>' % (ent(https(y['url'])), ent(y.get('source') or 'Source')) if ok_https(y.get('url')) else ''
        tiles.append('<li data-i="%d" data-c="%s"%s><span>%s</span><b>%s</b>%s%s</li>' % (
            k, COLOURS[k], ' class="is-bind"' if n == bind else '', lab(n), shown(y),
            '<small>%s</small>' % ent(y['note']) if y.get('note') else '', src))
    if price_ok(cov):
        pnote = plain(cov.get('price_note')).split(':')[0].rstrip('.') or 'A Perfect Nations estimate, to be confirmed with %s' % name
        price = (
            '<div class="bpx-sum"><p class="bpx-sum__k">The price of Perfect %s</p>'
            '<div class="bpx-sum__row" role="group" aria-label="%s a person, times %s people, is %s a year: the price of Perfect %s">'
            '<div class="bpx-sum__t" data-k="pc"><b class="bpx-money">%s</b><span>Perfect Capita, per person</span></div><i aria-hidden="true">&#215;</i>'
            '<div class="bpx-sum__t" data-k="pop"><b>%s</b><span>people</span></div><i aria-hidden="true">=</i>'
            '<div class="bpx-sum__t bpx-sum__t--total" data-k="price"><b class="bpx-money">%s</b><span>The price of Perfect %s, a year</span></div></div>'
            '<p class="bpx-sum__note">%s.</p></div>'
            % (ent(name), ent(cov['perfect_capita']), '{:,}'.format(int(d.get('population') or 0)), ent(cov['price']), ent(name),
               ent(cov['perfect_capita']), '{:,}'.format(int(d.get('population') or 0)), ent(cov['price']), ent(name), ent(pnote)))
    else:
        price = ('<div class="bpx-sum bpx-sum--open"><p class="bpx-sum__k">The price of Perfect %s</p>'
                 '<p class="bpx-sum__open">To be set with %s, from its own figures and in its own prices: Perfect Capita times the people of %s, each year.</p></div>'
                 % (ent(name), ent(name), ent(name)))
    cards, more = solution_cards(d, p, sbn, son)
    return (
        '<section class="bpx-band bpx-dp bpx-pc" id="bp-pc" aria-labelledby="bp-pcx-h"><div class="bpx-in">'
        '<div class="bpx-pc__grid"><div class="bpx-pc__head">%s<h2 class="bpx-h2" id="bp-pcx-h">Perfect %s, <em>star by star.</em></h2>'
        '<p class="bpx-pc__def"><b>Perfect Capita</b> %s</p>'
        '<a class="bpx-link" href="https://perfectnations.com/perfect-capita/" target="_blank" rel="noopener noreferrer">How Perfect Capita works</a></div>'
        '<div class="bpx-pc__sky">%s%s<p class="bpx-pc__cap">Tap a star for its figure and source.</p></div>'
        '<div class="bpx-pc__rest">%s'
        '<details class="bpx-more bpx-how"><summary aria-label="Read more: the seven figures, their sources and how they are measured">Read more</summary>'
        '<div class="bpx-more__b"><ul class="bpx-std" aria-label="%s: each standard, with its source">%s</ul><p>%s <a href="https://perfectnations.com/perfect-capita/#pq-measures" target="_blank" rel="noopener noreferrer">The strict measures</a></p><p>%s</p></div></details>'
        '</div></div>'
        '<div class="bpx-solx" id="bp-solutions"><span id="bp-dispatches"></span>'
        '<div class="bpx-sols-top"><div><h3 class="bpx-h3" id="bp-sol-h">Solutions for Perfect %s</h3></div>'
        '<div class="bpx-sols-go">%s<a class="bpx-link" href="https://perfectnations.com/state-of-nations/#sn-solutions" target="_blank" rel="noopener noreferrer">All Solutions</a></div></div>'
        '<p class="bpx-swipe" aria-hidden="true">Swipe for every Solution</p><ul class="bpx-sols bpx-rail" id="bp-sols">%s</ul></div>'
        '</div></section>'
        % (step_eb('03', 'Solutions', 'The seven stars', 'Perfect Capita'), ent(name), ent(plain(p['capita'].get('pc_text')).replace('The yearly', 'is the yearly', 1)),
           stars_svg(name, g, bind), call, price, ent(name), ''.join(tiles), ent(p['capita']['est']), ent(p['capita']['measures']),
           ent(name), more, cards))


def letter(d, p):
    name = d['nation']
    pt_ = p.get('portrait') or {}
    img = pt_.get('image') or ''
    m = re.search(r'-(\d+)x(\d+)\.(?:png|jpe?g|webp)$', img)
    w, h = (int(m.group(1)), int(m.group(2))) if m else (768, 768)
    note = ('%s &#183; ' % ent(pt_['note'])) if pt_.get('note') else ''
    # v12.3 (10 Nov 2026), the first edition of a new blueprint: until its Nation Portrait is painted, the Letter
    # stands alone (no empty frame), and without a Letter page of its own the button is left out
    fig = ('<figure class="bpx-port"><span class="bpx-frame">'
           '<img src="%s"%s alt="%s" width="%d" height="%d" loading="lazy" decoding="async"></span>'
           '<figcaption class="bpx-frame__cap">%s<small>Nation Portrait &#183; %s<a href="https://perfectnations.com/art-of-nations/" target="_blank" rel="noopener noreferrer">Art of Nations</a></small></figcaption></figure>'
           % (ent(https(img)), img_attrs(img, (300, 600, 768), '(min-width:960px) 240px, 150px'), ent(pt_.get('alt') or ''), w, h, ent(pt_.get('title') or ''), note)
           if ok_https(img) else '')
    full = ('<a class="bpx-btn" href="%s" target="_blank" rel="noopener noreferrer">Read the full letter</a>' % ent(https(p['letter']['url']))
            if ok_https(p['letter'].get('url')) else '')
    paras = ''.join('<p class="bpx-sheet__p">%s</p>' % raw(x) for x in p['letter']['paras'])
    # v11.3: a longer Letter shows its opening line; the rest, word for word, is one click away (the quotation stays)
    words = sum(len(plain(x).split()) for x in p['letter']['paras'])
    one, rest = first_sentence(p['letter']['paras'][0])
    if words > 40 and rest and '<' not in ''.join(p['letter']['paras']):
        tail = ''.join('<p class="bpx-sheet__p">%s</p>' % raw(x) for x in [rest] + p['letter']['paras'][1:])
        paras = '<p class="bpx-sheet__p">%s</p>%s' % (raw(one), more(tail, 'the Letter to %s' % name))
    return (
        '<section class="bpx-band bpx-iv bpx-letter" id="bp-letter" aria-labelledby="bp-letter-h"><div class="bpx-in">'
        '<div class="bpx-letter__grid%s">%s'
        '<article class="bpx-sheet"><div class="bpx-sheet__lh"><span>Perfect Nations&#174; &#183; Letters to the Nations</span><span>%s</span></div>'
        '<h2 class="bpx-sheet__dear" id="bp-letter-h">Dear %s,</h2>%s<p class="bpx-sheet__q">%s</p>'
        '<div class="bpx-sheet__foot"><span class="bpx-sig">Yours in design,<b>Preeti Sinha</b><small>President and CEO, Perfect Nations</small></span>'
        '%s</div></article></div>'
        '</div></section>'
        % ('' if fig else ' bpx-letter__grid--solo', fig,
           ent(name), ent(name), paras, raw(p['letter']['quote']), full))


def codesigner(s):
    """The Co-designers card in one line (v11.3): who becomes a Co-designer, and any note of the nation's own (a pen
    name, for example); the clause on the community is left out."""
    return re.sub(r'</b>: one of a community of selfless people, at home and abroad, building a nation where every citizen has a decent life\.',
                  '</b>.', plain(s))


def one_line(s):
    """Two short sentences of a lead joined as one: "A. Every message ..." becomes "A: every message ..."."""
    return re.sub(r'\. Every message', ': every message', plain(s), count=1)


def work(d, p):
    name, slug = d['nation'], p['slug']
    co = mailto('Becoming a Co-designer of Perfect %s' % name,
                'Your name:\r\nWhere you live:\r\nHow you would like to contribute (writing, a voice for the podcast, an enterprise, your expertise):\r\n')
    moves = ''.join('<li><b>%02d</b>%s</li>' % (i + 1, ent(m)) for i, m in enumerate(MOVES))
    tiers = []
    for t, (k, dur, title, line, leave, cta) in enumerate(TIERS):
        pips = ''.join('<span%s></span>' % (' class="on"' if j <= t else '') for j in range(3))
        mv = ''.join(
            '<li><b>%02d</b><span>%s</span><span class="bpx-pips" role="img" aria-label="Depth %d of 3">%s</span></li>'
            % (i + 1, ent(text), t + 1, pips)
            for i, text in enumerate(p['mandates']['moves'][t]))
        tiers.append(
            '<li class="bpx-tier%s"><p class="bpx-tier__k"><span>%s</span><span>%s</span></p><h3>%s</h3><p>%s</p>'
            '<p class="bpx-tier__leave"><span>You leave with</span>%s</p>'
            '<details class="bpx-more"><summary aria-label="Read more: the four moves of %s">Read more</summary><ol class="bpx-mv">%s</ol></details>'
            '<a class="bpx-btn%s" href="%s" target="_blank" rel="noopener noreferrer">%s</a></li>'
            % (' bpx-tier--top' if t == 2 else '', k, dur, title, line, leave, title, mv, '' if t == 2 else ' bpx-btn--line',
               ent(https('https://perfectnations.com/contact/?about=%s&country=%s' % (('briefing', 'lab', 'commission')[t], urllib.parse.quote(name, safe='')))), cta))
    wx_mail = mailto('Writing for Perfect %s' % name,
                     'Your name, or a pen name:\r\nWhere you live:\r\nTitle:\r\n\r\nYour vision of Perfect %s, and the economic solutions to achieve it (up to 1,500 words):\r\n\r\n\r\n'
                     'I confirm that this is my own original writing, and I give Perfect Nations permission to publish it with credit to me.\r\n' % name)
    nation_q = urllib.parse.quote(slug)
    return (
        '<section class="bpx-band bpx-er bpx-work" id="bp-studio" aria-labelledby="bp-entry-h"><div class="bpx-in">'
        '<div class="bpx-head"><div><p class="bpx-eb">Work with us &#183; The ReDesign Studio</p>'
        '<h2 class="bpx-h2" id="bp-entry-h">The Perfect %s <em>ReDesign Studio</em></h2></div>'
        '<div><p class="bpx-mhead">One mission, three depths: the same four moves for %s, taken as far toward market as you choose.</p>%s</div></div>'
        '<div id="bp-mandates">'
        '<ol class="bpx-moves" aria-label="The four moves of every mandate">%s</ol>'
        '<p class="bpx-swipe" aria-hidden="true">Swipe for the three mandates</p><ol class="bpx-tiers bpx-rail">%s</ol></div>'
        '<div class="bpx-co3"><div class="bpx-co3__top"><h3 class="bpx-co3__h">Co-design it with us</h3><p>%s</p></div><p class="bpx-swipe" aria-hidden="true">Swipe for three ways in</p><ul class="bpx-co3__l bpx-rail">'
        '<li id="bp-writings"><p class="bpx-co3__k">Writings</p><h4>Write Perfect %s into being.</h4>'
        '<p>Up to 1,500 words on your vision of Perfect %s, published with your name.</p>'
        '<a class="bpx-btn bpx-btn--line" href="%s">Submit your writing</a></li>'
        '<li id="bp-voices"><p class="bpx-co3__k">Voices of Perfect Nations <span class="bpx-air"><i aria-hidden="true"></i>Launching soon</span></p>'
        '<h4 id="bp-voices-h">The local leaders already building Perfect %s.</h4>'
        '<p>Great local leaders: honest, dedicated and committed to basic standards of living for all. Every guest answers one question: &#8220;What does %s already own, and how could it pay for a decent life for every citizen?&#8221;</p>'
        '<div class="bpx-btns"><a class="bpx-btn bpx-btn--line" href="https://perfectnations.com/contact/?nation=%s&amp;topic=nominate-self" target="_blank" rel="noopener noreferrer">Nominate yourself</a>'
        '<a class="bpx-btn bpx-btn--line" href="https://perfectnations.com/contact/?nation=%s&amp;topic=guest" target="_blank" rel="noopener noreferrer">Suggest a guest</a></div></li>'
        '<li><p class="bpx-co3__k">Co-designers</p><h4>Join the community.</h4><p>%s</p>'
        '<a class="bpx-btn bpx-btn--line" href="%s">Become a Co-designer</a></li></ul></div>'
        '</div></section>'
        % (ent(name), ent(name), more('<p class="bpx-terms">%s</p>' % ent(p['mandates']['terms']), 'who the mandates are for, and how scope and fees are agreed'),
           moves, ''.join(tiers), ent(p['people']),
           ent(name), ent(name), ent(wx_mail), ent(name), ent(name), nation_q, nation_q, raw(codesigner(p['codesigner'])), ent(co)))


def firms(d):
    """Already working in <Nation> (v11.5): independent firms and social enterprises at work in the nation, in their
    own band directly after 02 Capital and before 03 Solutions (the Steward-General, 9 Nov 2026). They have nothing
    to do with Perfect Nations beyond being identified and highlighted by it, so the one line under the heading says
    so, and nothing in the band suggests they work with, for or through Perfect Nations. The anchor bp-enterprises,
    the heading id bp-ent-h (script.js writes the live heading into it) and the data key enterprises are unchanged."""
    name = d['nation']
    e = d.get('enterprises') or {}
    ents = ''.join('<li><span class="bpx-ent__s">%s</span><h3>%s</h3>%s<a href="%s" target="_blank" rel="noopener noreferrer">%s</a></li>'
                   % (ent(x.get('standard', '')), ent(x['name']), '<p>%s</p>' % ent(x['text']) if x.get('text') else '',
                      ent(https(x['url'], allow_mail=True)), ent(x.get('source') or 'Source'))
                   for x in e.get('items') or [] if x.get('name') and x.get('url'))
    if not ents:
        ents = ('<li class="bpx-ents__none"><h3>The first firms and social enterprises at work in %s are being gathered.</h3>'
                '<p>Name one already at work there: it may be highlighted here, with its source.</p></li>' % ent(name))
    return (
        '<section class="bpx-band bpx-er bpx-firms" id="bp-enterprises" aria-labelledby="bp-ent-h"><div class="bpx-in">'
        '<div class="bpx-ent__h"><div><h2 class="bpx-ent__t" id="bp-ent-h">%s</h2>'
        '<p class="bpx-ent__l">Independent firms and social enterprises already at work in %s, highlighted by Perfect Nations. '
        'None is a partner of Perfect Nations.</p></div>'
        '<a class="bpx-link" href="%s">Suggest an enterprise</a></div>'
        '<p class="bpx-swipe" aria-hidden="true">Swipe for every enterprise</p><ul class="bpx-ents bpx-rail">%s</ul>'
        '</div></section>'
        % (ent(e.get('heading') or 'Already working in %s.' % name), ent(name),
           ent(mailto('An enterprise already at work in %s' % name)), ents))


# The second Nation Portrait, the flag edition (painted 31 October 2026; the Steward-General, 8 Nov 2026: "a
# second set of the 40 nations portraits with the flag imagery ... for other parts in the blueprints").
# It closes the page, beside "Design Perfect <Nation> with us". The file is uploaded to the Media Library in
# November 2026 as pn-portrait-flag-<slug>.png (1264 px square, from its Canva link in the Project doc
# claude/nation-portraits-v4-canva.md); until it is there, the figure removes itself and the close keeps
# one column. Afghanistan, Barbados, Kenya and Rwanda keep their own portraits and have no flag edition.
FLAG_EDITION = ('angola', 'bangladesh', 'botswana', 'brazil', 'burundi', 'colombia', 'cote-divoire', 'dr-congo', 'ecuador', 'egypt', 'eswatini', 'ethiopia', 'fiji', 'ghana', 'india', 'indonesia', 'jamaica', 'jordan', 'lesotho', 'madagascar', 'malawi', 'mexico', 'morocco', 'mozambique', 'namibia', 'nigeria', 'pakistan', 'philippines', 'republic-of-congo', 'senegal', 'somalia', 'south-africa', 'south-sudan', 'sri-lanka', 'tanzania', 'uganda', 'ukraine', 'vietnam', 'zambia', 'zimbabwe')
FLAG_DIR = 'https://perfectnations.com/wp-content/uploads/2026/11/'


def flag_fig(name, slug, title):
    if slug not in FLAG_EDITION:
        return ''
    u = FLAG_DIR + 'pn-portrait-flag-' + slug
    return (
        '<figure class="bpx-port bpx-port--flag"><span class="bpx-frame">'
        '<img src="%s-768x768.png" srcset="%s-300x300.png 300w, %s-768x768.png 768w" sizes="(min-width:960px) 260px, 180px" '
        'alt="%s, flag edition: the nation portrait of %s painted with its flag" width="768" height="768" loading="lazy" decoding="async" '
        'onerror="var f=this.closest(\'figure\');if(f){f.remove();}"></span>'
        '<figcaption class="bpx-frame__cap">%s<small>Nation Portrait, flag edition &#183; '
        '<a href="https://perfectnations.com/art-of-nations/" target="_blank" rel="noopener noreferrer">Art of Nations</a></small></figcaption></figure>'
        % (u, u, u, ent(title), ent(name), ent(title)))


def committed(s):
    """v11.5: the Sources name the list as visitors see it: "each register line" (or entry) becomes "each line of
    Capital already committed". Only the name of the list changes; every source, date and figure is kept."""
    return re.sub(r'\beach register (line|entry)\b', r'each \1 of Capital already committed', plain(s))


def close(d, p):
    name, slug = d['nation'], p['slug']
    srcs = ''.join('<li>%s</li>' % raw(committed(s)) for s in p['sources'])
    return (
        '<section class="bpx-band bpx-dp bpx-close" aria-labelledby="bp-close-h"><div class="bpx-in bpx-close__grid"><div class="bpx-close__words">'
        '<p class="bpx-eb">The %s ReDesign Studio is open</p><h2 class="bpx-h2" id="bp-close-h">Design Perfect %s with us.</h2>'
        '<p class="bpx-lead">%s</p><div class="bpx-btns">'
        '<a class="bpx-btn" href="https://perfectnations.com/design-studio/" target="_blank" rel="noopener noreferrer">Enter the ReDesign Studio</a>'
        '<a class="bpx-btn bpx-btn--line" href="https://perfectnations.com/contact/?nation=%s" target="_blank" rel="noopener noreferrer">Write to us</a>'
        '<a class="bpx-btn bpx-btn--line" href="https://perfectnations.com/blueprints/" target="_blank" rel="noopener noreferrer">All 195 nations</a></div>'
        '<details class="bpx-sources" id="bp-sources"><summary>Sources</summary><ol>%s</ol></details></div>%s</div></section>'
        '<div class="bpx-toast" id="bp-toast" role="status" aria-live="polite" hidden><span>Opening your email app. If nothing opens, write to <b>contact@perfectnations.com</b></span>'
        '<button type="button" id="bp-toast-copy">Copy address</button><button type="button" class="bpx-x" id="bp-toast-x" aria-label="Close"><svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="M6.5 6.5l11 11M17.5 6.5l-11 11" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg></button></div>'
        % (ent(name), ent(name), ent(one_line(p['close_lead'])), urllib.parse.quote(slug), srcs,
           flag_fig(name, slug, (p.get('portrait') or {}).get('title') or ('%s in Bloom' % name))))


RULE = '<div class="bpx-rule" aria-hidden="true"></div>'


# ---------------------------------------------------------------- the page

def open_slugs():
    man = json.loads((PAGES / 'manifest.json').read_text(encoding='utf-8'))
    out = []
    for key, v in man['pages'].items():
        m = re.match(r'^pages/blueprint-([a-z-]+)\.html$', v.get('file', ''))
        if key.startswith('pn-bp-') and m:
            out.append(m.group(1))
    return sorted(set(out))


def build(slug, sbn, son, today):
    d = json.loads((DATA / ('%s.json' % slug)).read_text(encoding='utf-8'))
    p = json.loads((HERE / ('%s.json' % slug)).read_text(encoding='utf-8'))
    rid = p['root']
    if rid != 'pn-bp-' + slug:
        sys.exit('%s: the root must be pn-bp-%s' % (slug, slug))
    css = (HERE / 'style.css').read_text(encoding='utf-8').replace('#R', '#' + rid)
    gl = p['globe']
    globe_cfg = {'root': rid, 'lat': gl['lat'], 'lng': gl['lng'], 'outline': gl['outline'], 'tex': EARTH}
    globe = (HERE / 'globe.js').read_text(encoding='utf-8').replace('/*pn:globe-cfg*/', 'var CFG = %s;' % js_str(globe_cfg))
    steward = d.get('steward') or {}
    cfg = {'root': rid, 'slug': slug, 'name': d['nation'], 'steward': steward.get('name', ''), 'stewardRole': steward.get('role', ''),
           'colours': COLOURS}
    script = (HERE / 'script.js').read_text(encoding='utf-8').replace('/*pn:cfg*/', 'var CFG = %s;' % js_str(cfg))
    head = (
        '<!-- PERFECT NATIONS . NATIONAL BLUEPRINT . %s . v%s . %s . Built by tools/build_nations.py: never edit by hand. -->\n'
        '<!-- v12.0 (10 November 2026): light reading sections, Earthrise accents (the Steward-General, 10 Nov 2026). -->\n'
        '<!-- v11.7 (10 November 2026): the letterhead carries the registered mark, Perfect Nations&#174;. -->\n'
        '<!-- v11.5 (9 November 2026): three changes for clarity (the Steward-General, 9 Nov 2026). The register reads\n'
        '     Capital already committed; Already working in the nation is its own band after 02 Capital, its firms and\n'
        '     social enterprises independent and none a partner; Perfect Nations is a new-age sovereign advisory firm. -->\n'
        '<!-- v11.4 (9 November 2026): the Solution Perfect Nations designs for the nation leads its Solutions. -->\n'
        '<!-- v11.3 (9 November 2026): fewer words (the Steward-General, 9 Nov 2026). One headline and one line a section,\n'
        '     the detail one click away behind Read more; every figure and source kept. -->\n'
        '<!-- v11.2 (9 November 2026): the cup for Assets; the whole logo as a large seal, led by good governance; Co-design on ivory. -->\n'
        '<!-- v11.1 (9 November 2026): What Perfect Nations advises, in place of how FfD and SI solve it (the Steward-General, 9 Nov 2026)\n'
        '     Each Solution reads The challenge, then What Perfect Nations advises. -->\n'
        '<!-- v11.0 (8 November 2026): the blueprint follows the new homepage. Perfect Nations as a new-age sovereign\n'
        '     advisory firm, whose clients are nations: the hero says what it does for this nation\n'
        '     (FfD before SI) with the nation at a glance in sourced figures; What we do for the nation (Assets. Capital.\n'
        '     Solutions., drawn from the logo kit, with the cup of good governance in one line and the whole logo as a\n'
        '     seal); 01 Assets as typographic cards (no photographs); 02 Capital (the record, the register and the\n'
        '     Newswire side by side, the laurels as its mark); 03 Solutions last (the seven stars of the logo in place\n'
        '     of the wheel, each star the nation\'s own figure with its source, no composite score, the price of Perfect\n'
        '     <Nation> where the data has it, and the Solutions); the Letter; Work with us (the three mandates, Writings,\n'
        '     Voices, the Co-designers and the Enterprises); the close and the Sources. Gold hairlines, not painted seams. -->\n'
        '<!-- v10.2 (8 November 2026): the second Nation Portrait, the flag edition, closes the page beside "Design\n'
        '     Perfect <Nation> with us" (40 nations). It shows once pn-portrait-flag-<slug>.png is in the Media Library. -->\n'
        '<!-- v10.1 (8 November 2026): FfD before SI (the Steward-General, 8 Nov 2026). -->\n'
        '<!-- v10.0 (7 November 2026): one design for all 44 blueprints, in the site palette; the globe drawn by the page\n'
        '     itself. Served live from GitHub by the Perfect Nations Live Pages plugin (root %s); the code below\n'
        '     is also the fallback when a data file cannot be read. -->\n'
        '<link rel="preconnect" href="https://raw.githubusercontent.com" crossorigin>\n'
        '<link rel="preload" as="image" href="%s" media="(min-width:768px)" crossorigin>\n'
        '<link rel="preload" as="image" href="%s" media="(max-width:767px)" crossorigin>\n'
        % (d['nation'].upper().encode('ascii', 'xmlcharrefreplace').decode('ascii'), VERSION, today, rid, EARTH['lg'][0], EARTH['sm'][0]))
    body = '\n'.join([
        '<style>\n%s\n</style>' % css,
        '<div id="%s" class="bpx" data-version="%s">' % (rid, VERSION),
        kit(),
        hero(d, p),
        what_we_do(d),
        assets(d),
        RULE,
        capital(d, p),
        RULE,
        firms(d),
        RULE,
        solutions(d, p, sbn, son),
        letter(d, p),
        work(d, p),
        RULE,
        close(d, p),
        '</div>',
        wp_script(globe),
        wp_script(script),
    ])
    page = head + body + '\n'
    first = re.search(r'\bid\s*=\s*["\'](pn-[a-z0-9-]+)["\']', page)
    if not first or first.group(1) != rid:
        sys.exit('%s: the first pn- id must be %s, found %s' % (slug, rid, first and first.group(1)))
    others = set(re.findall(r'\bid\s*=\s*["\'](pn-[a-z0-9-]+)["\']', page)) - {rid}
    if others:
        sys.exit('%s: ids starting with pn- other than the root: %s' % (slug, sorted(others)))
    if re.search(r'(?:class|id)\s*=\s*["\'][^"\']*laurel', page, re.I):
        sys.exit('%s: a class or id holds the word laurel (the header would replace that drawing)' % slug)
    bad = [(i, c) for i, c in enumerate(page) if ord(c) > 126]
    if bad:
        sys.exit('%s: non-ASCII characters in the page: %r' % (slug, bad[:5]))
    (PAGES / ('blueprint-%s.html' % slug)).write_text(page, encoding='utf-8')
    return len(page)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('slugs', nargs='*')
    ap.add_argument('--solutions', default=str(DATA / 'solutions-by-nation.json'))
    ap.add_argument('--son', default=str(DATA / 'state-of-nations.json'))
    ap.add_argument('--manifest', action='store_true', help='raise every built pn-bp-<slug> to this version in pages/manifest.json')
    args = ap.parse_args()
    slugs = args.slugs or open_slugs()
    sbn = json.loads(Path(args.solutions).read_text(encoding='utf-8')) if Path(args.solutions).exists() else None
    son = json.loads(Path(args.son).read_text(encoding='utf-8')) if Path(args.son).exists() else None
    if not sbn:
        print('note: no solutions-by-nation file; the Solution for each nation is left to the live page')
    MEDIA.update(json.loads((HERE / 'media.json').read_text(encoding='utf-8'))['images'])
    today = datetime.now(timezone.utc).strftime('%Y-%m-%d')
    total = 0
    for s in slugs:
        n = build(s, sbn, son, today)
        total += n
        print('pages/blueprint-%s.html: %d characters' % (s, n))
    print('%d pages, %d characters on average' % (len(slugs), total // max(1, len(slugs))))
    if args.manifest:
        path = PAGES / 'manifest.json'
        man = json.loads(path.read_text(encoding='utf-8'))
        for s in slugs:
            hit = False
            for key, v in man['pages'].items():
                if v.get('file') == 'pages/blueprint-%s.html' % s:
                    v['version'] = VERSION
                    hit = True
            if not hit:
                # v12.3: a new blueprint joins the manifest (its pn-bp-<slug> key turns it gold across the site)
                nm = json.loads((DATA / ('%s.json' % s)).read_text(encoding='utf-8'))['nation']
                man['pages']['pn-bp-' + s] = {'file': 'pages/blueprint-%s.html' % s, 'version': VERSION,
                                             'title': '%s blueprint' % nm, 'url': 'https://perfectnations.com/blueprints/%s/' % s}
        man['updated'] = today
        path.write_text(json.dumps(man, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
        print('pages/manifest.json: %d blueprints at v%s' % (len(slugs), VERSION))


if __name__ == '__main__':
    main()
