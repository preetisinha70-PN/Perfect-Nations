#!/usr/bin/env python3
"""Build every national blueprint page (pages/blueprint-<slug>.html) from one template.

Blueprint v10.2 (8 November 2026). One design for every nation, so a change is made once and reaches all.
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
  pages/home-seams.html, pages/header.html                   the painted seams and the cup of the logo

Run from the repository root:
  python3 tools/build_nations.py                 build every open blueprint
  python3 tools/build_nations.py kenya ghana     build these only
  python3 tools/build_nations.py --solutions PATH --son PATH   read the Solutions files from elsewhere
Then: python3 tools/check_page.py pages/blueprint-*.html, previews with tools/preview_nations.py, raise each
pn-bp-<slug> version in pages/manifest.json (this script does it with --manifest) and open a pull request
"For approval: 44 blueprints vX.Y, ...". Never edit a built page by hand.

A new nation: write tools/nation/<slug>.json (copy one and change every line), make sure data/<slug>.json exists,
run the build, add pn-bp-<slug> to the manifest.
"""
import argparse
import html
import json
import math
import random
import re
import sys
import urllib.parse
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PAGES, DATA, HERE = ROOT / 'pages', ROOT / 'data', ROOT / 'tools' / 'nation'
VERSION = '10.2'
EARTH = {'lg': 'https://perfectnations.org/wp-content/uploads/2026/10/pn-globe-earth-day-1536x768.jpg',
         'sm': 'https://perfectnations.org/wp-content/uploads/2026/10/pn-globe-earth-day-1024x512.jpg'}
ORDER = ['Food', 'Water', 'Shelter', 'Energy', 'Education', 'Health', 'Livelihoods']
COLOURS = ['#8A5A12', '#0E5A80', '#9A3E22', '#C08A12', '#1F4C96', '#167A5F', '#2F5A2A']
ICONS = [
    '<path d="M3 11h18a9 9 0 0 1-18 0z"/><path d="M8 3c-1 1.5 1 2.5 0 4M12 3c-1 1.5 1 2.5 0 4M16 3c-1 1.5 1 2.5 0 4"/>',
    '<path d="M12 3s-6 7-6 11a6 6 0 0 0 12 0c0-4-6-11-6-11z"/><path d="M9.5 15a2.5 2.5 0 0 0 2.5 2.5"/>',
    '<path d="M3 11l9-7 9 7"/><path d="M5 9.5V20h14V9.5"/><path d="M10 20v-6h4v6"/>',
    '<path d="M13 2L4 14h7l-1 8 9-12h-7z"/>',
    '<path d="M2 5c3-1 7-1 10 1 3-2 7-2 10-1v14c-3-1-7-1-10 1-3-2-7-2-10-1z"/><path d="M12 6v14"/>',
    '<path d="M12 21s-8-5-8-11a4.5 4.5 0 0 1 8-3 4.5 4.5 0 0 1 8 3c0 6-8 11-8 11z"/><path d="M7 12h3l1-2 2 4 1-2h3"/>',
    '<path d="M12 21v-9"/><path d="M12 12C12 8 9 6 5 6c0 4 3 6 7 6z"/><path d="M12 10c0-3 2-5 6-5 0 3-2 5-6 5z"/><path d="M7 21h10"/>',
]
CAT = {'govt': 'Government', 'humanitarian': 'Humanitarian', 'multi': 'Multilateral', 'regional': 'Regional',
       'bilat': 'Bilateral', 'private': 'Private', 'impact': 'Impact'}
MONEY = re.compile(r'^(?:[A-Z]{0,3}\$|\u20ac|\u00a3|\u20b9|\u20a6|~?\$|(?:USD|EUR|KSh|Sh|GHS|ZAR|FCFA|CFA|MAD|EGP|ETB|NGN|PKR|BDT|INR|IDR|PHP|VND|LKR|MXN|COP|JOD|FJD|UAH|BBD|BWP|AOA|MZN|TZS|UGX|RWF|ZMW|MWK|NAD|SZL|LSL|SOS|SSP|CDF|BIF|MGA|XAF|XOF|JMD|BRL|R)\s?\d)')
ASSET_SIZES = '(min-width:1100px) 236px, (min-width:700px) 31vw, 72vw'
MOVES = ['Identify the assets', 'Estimate Perfect Capita', 'Co-design the capital architecture', 'Launch the instruments']
TIERS = [
    ('Mandate 01', '3 hours', 'The Nation Briefing', 'A private session for the people who decide.', 'The gap, named and sized', 'Request a Nation Briefing'),
    ('Mandate 02', '3 days', 'The Blueprint Lab', 'Your team and ours, working the blueprint together.', 'The structure, drawn', 'Plan a Blueprint Lab'),
    ('Mandate 03', 'End to end', 'The Sovereign Mandate', 'Led personally by the President and CEO.', 'A structure ready for market', 'Discuss a Sovereign Mandate'),
]


def plain(s):
    return '' if s is None else str(s)


def ent(s):
    """Plain text to HTML: escaped, every non-ASCII character as an entity, so the page stays ASCII."""
    return html.escape(plain(s), quote=True).encode('ascii', 'xmlcharrefreplace').decode('ascii')


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


def money(v, m):
    return '<span class="bpx-money">%s</span>' % ent(v) if m else ent(v)


def js_str(o):
    """JSON for a script block, ASCII only and safe inside <script>."""
    s = json.dumps(o, ensure_ascii=True, separators=(',', ':'))
    return s.replace('</', '<\\/')


def mailto(subject, body=None):
    q = 'subject=' + urllib.parse.quote(subject, safe='')
    if body:
        q += '&body=' + urllib.parse.quote(body, safe='')
    return 'mailto:contact@perfectnations.org?' + q


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


# ---------------------------------------------------------------- the seven standards

def num(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool) and 0 <= v <= 100


def fmt(v):
    r = round(v * 10) / 10
    return str(int(r)) if r == int(r) else str(r)


def lab(n):
    return 'Livelihood' if n == 'Livelihoods' else n


def pt(r, a):
    a = (a - 90) * math.pi / 180
    return '%.1f %.1f' % (300 + r * math.cos(a), 300 + r * math.sin(a))


def arc(ra, rb, a0, a1):
    return 'M%sA%s %s 0 0 1 %sL%sA%s %s 0 0 0 %sZ' % (pt(rb, a0), rb, rb, pt(rb, a1), pt(ra, a1), ra, ra, pt(ra, a0))


def standards(d):
    g = {x['name']: x for x in d.get('guarantees') or [] if x.get('name') in ORDER}
    if len(g) != 7:
        sys.exit('%s: the file does not hold the seven standards' % d.get('nation'))
    scored = [n for n in ORDER if num(g[n].get('value'))]
    cov = d.get('coverage') or {}
    score = cov.get('score') if num(cov.get('score')) else None
    set_by = cov.get('set_by')
    set_by = 'Livelihoods' if set_by == 'Livelihood' else set_by
    low = min(scored, key=lambda n: g[n]['value']) if scored else None
    if score is not None:
        bind = set_by if (set_by in g and num(g[set_by].get('value')) and g[set_by]['value'] == score) else low
    else:
        bind = set_by if set_by in g else low
    return g, scored, score, bind


def wheel(name, g, score, bind, unscored):
    parts = ['<svg class="bw-wheel" viewBox="0 0 600 600" aria-labelledby="bw-w-t" role="group" focusable="false">',
             '<title id="bw-w-t">%s: coverage of the seven basic living standards</title>' % ent(name),
             '<circle cx="300" cy="300" r="290" class="bw-ring"/><g class="bw-ticks">']
    for k in range(7):
        parts.append('<line x1="%s" y1="%s" x2="%s" y2="%s"/>' % tuple(pt(284, k * 360 / 7).split() + pt(296, k * 360 / 7).split()))
    parts.append('</g>')
    for k, n in enumerate(ORDER):
        v = g[n].get('value')
        a0, a1 = k * 360 / 7 + 0.8, (k + 1) * 360 / 7 - 0.8
        mid = (k + 0.5) * 360 / 7
        cx, cy = (float(x) for x in pt(212, mid).split())
        fill = arc(148, 148 + 124 * v / 100, a0, a1) if num(v) else ''
        label = '%s, coverage %s of 100' % (lab(n), fmt(v)) if num(v) else '%s, not scored' % lab(n)
        parts.append(
            '<g class="bw-seg%s" data-i="%d" aria-label="%s">'
            '<path d="%s" fill="%s" opacity=".22"/><path class="bw-fill" d="%s" fill="%s"/>'
            '<path class="bw-bind" d="%s" fill="none" stroke="#7E5A0C" stroke-width="2.5" stroke-dasharray="6 4"%s/>'
            '<g transform="translate(%.1f %.1f) scale(1.6) translate(-12 -12)" class="bw-ic">%s</g>'
            '<text x="%.1f" y="%.1f" text-anchor="middle" class="bw-lab">%s</text>'
            '<text x="%.1f" y="%.1f" text-anchor="middle" class="bw-val">%s</text></g>'
            % (' is-bind' if n == bind else '', k, ent(label), arc(148, 272, a0, a1), COLOURS[k], fill, COLOURS[k],
               arc(148, 272, a0, a1), '' if n == bind else ' style="display:none"', cx, cy - 20, ICONS[k],
               cx, cy + 18, lab(n).upper(), cx, cy + 38, fmt(v) if num(v) else '&#8211;'))
    c2 = fmt(score) if score is not None else ''
    c3 = ('OF 100 &#183; SET BY %s' % lab(bind).upper()) if score is not None else ent((unscored or {}).get('center', 'NOT SCORED'))
    parts.append('<circle cx="300" cy="300" r="136" class="bw-core"/><circle cx="300" cy="300" r="122" class="bw-core-line"/>'
                 '<text x="300" y="262" text-anchor="middle" class="bw-c1">COVERAGE</text>'
                 '<text x="300" y="338" text-anchor="middle" class="bw-c2">%s</text>'
                 '<text x="300" y="368" text-anchor="middle" class="bw-c3">%s</text></svg>' % (c2, c3))
    return ''.join(parts)


# ---------------------------------------------------------------- the sections

def hero(d, p):
    h = d.get('hero') or {}
    name = d['nation']
    stats = ''.join('<li><b>%s</b><span>%s</span></li>' % (money(s['value'], bool(MONEY.match(s['value']))), ent(s['label']))
                    for s in h.get('stats') or [] if s.get('value') and s.get('label'))
    long_name = ' is-long' if len(name) > 11 else ''
    return (
        '<section class="bpx-band bpx-er bpx-hero" aria-labelledby="bp-h1"><div class="bpx-in bpx-hero__grid">'
        '<div class="bpx-hero__head"><div class="bpx-kick"><span class="bpx-cup">%s</span><p class="bpx-eb">%s</p></div>'
        '<h1 class="bpx-h1%s" id="bp-h1">%s</h1><p class="bpx-lead">%s</p></div>'
        '<div class="bpx-globe-cell"><div class="bpx-globe" id="%s-globe" role="img" aria-label="%s, in gold on the globe">'
        '<span class="bpx-globe__sky"></span><canvas class="bpx-globe__still"></canvas><canvas class="bpx-globe__gl"></canvas></div></div>'
        '<ul class="bpx-stats bpx-hero__stats">%s</ul>'
        '<div class="bpx-btns bpx-hero__ctas"><a class="bpx-btn" href="#bp-studio">Enter the ReDesign Studio</a>'
        '<a class="bpx-btn bpx-btn--line" href="#bp-solutions">Solutions</a>'
        '<a class="bpx-btn bpx-btn--line" href="#bp-letter">Read the Letter</a></div>'
        '</div></section>'
        % (cup(), ent(p['eyebrow']), long_name, ent(name), ent(h.get('lead', '')), p['slug'], ent(name), stats))


def studio(d, p):
    name = d['nation']
    rooms = [('#bp-solutions', 'Solutions', True), ('#bp-mandates', 'Mandates', False), ('#bp-assets', 'Assets', False),
             ('#bp-pc', 'Perfect Capita', False), ('#bp-capital', 'Capital', False), ('#bp-enterprises', 'Enterprises', False),
             ('#bp-voices', 'Voices', False)]
    rooms_html = ''.join('<li><a%s href="%s">%s</a></li>' % (' class="is-key"' if k else '', h, t) for h, t, k in rooms)
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
            '<details><summary>The four moves at this depth</summary><ol class="bpx-mv">%s</ol></details>'
            '<a class="bpx-btn" href="%s" target="_blank" rel="noopener noreferrer">%s</a></li>'
            % (' bpx-tier--top' if t == 2 else '', k, dur, title, line, leave, mv, ent(https('https://perfectnations.org/contact/?about=%s&country=%s' % ('commission' if t == 2 else 'studio', urllib.parse.quote(name, safe='')))), cta))
    return (
        '<section class="bpx-band bpx-iv bpx-studio" id="bp-studio" aria-labelledby="bp-entry-h"><div class="bpx-in">'
        '<div class="bpx-studio__top"><div><p class="bpx-studio__k">You are entering</p>'
        '<h2 class="bpx-studio__h" id="bp-entry-h"><span>The Perfect %s</span>ReDesign Studio</h2>'
        '<p class="bpx-studio__l">%s</p></div>'
        '<div class="bpx-studio__side"><ul class="bpx-rooms" aria-label="Inside the ReDesign Studio">%s</ul>'
        '<div class="bpx-co"><p>%s</p><a class="bpx-btn" href="%s">Become a Co-designer</a></div></div></div>'
        '<div id="bp-mandates"><div class="bpx-mhead"><h3>One mission. Three depths.</h3>'
        '<p>Every mandate makes the same four moves for %s. What changes is how deep we go, and how far the work travels toward market.</p></div>'
        '<ol class="bpx-moves" aria-label="The four moves of every mandate">%s</ol>'
        '<p class="bpx-swipe" aria-hidden="true">Swipe for the three mandates</p><ol class="bpx-tiers bpx-rail">%s</ol><p class="bpx-terms">%s</p></div>'
        '</div></section>'
        % (ent(name), ent(p['people']), rooms_html, raw(p['codesigner']), ent(co), ent(name), moves, ''.join(tiers),
           ent(p['mandates']['terms'])))


def solution_card(x, sig_name, sig_role):
    no = int(x.get('no') or 0)
    href = x['url'] if re.match(r'^https://', plain(x.get('url'))) else 'https://perfectnations.org/state-of-nations/#solution-%02d' % no
    body = ''
    if x.get('challenge') and x.get('ffd') and x.get('si'):
        body = '<ul class="bpx-sol__how">%s</ul>' % ''.join(
            '<li><b>%s</b><strong>%s</strong><span>%s</span></li>' % (n, t, ent(w))
            for n, t, w in (('01', 'The challenge', x['challenge']), ('02', 'How FfD solves it', x['ffd']), ('03', 'How SI solves it', x['si'])))
    elif x.get('standfirst') or x.get('summary'):
        body = '<p>%s</p>' % ent(x.get('standfirst') or x.get('summary'))
    fig = ''
    if x.get('figure'):
        fig = '<p class="bpx-sol__fig"><b>%s</b>%s</p>' % (ent(x['figure']), '<span>%s</span>' % ent(x['caption']) if x.get('caption') else '')
    return (
        '<li class="bpx-sol"><p class="bpx-sol__k"><b>Solution No. %02d</b><time datetime="%s">%s</time></p>'
        '<h3><a href="%s" target="_blank" rel="noopener noreferrer">%s</a></h3>%s%s'
        '<div class="bpx-sol__foot"><span class="bpx-sig">From<b>%s</b><small>%s</small></span>'
        '<a class="bpx-btn" href="%s" target="_blank" rel="noopener noreferrer">Read the Solution</a></div></li>'
        % (no, ent(x.get('date', '')), ent(x.get('label') or short_date(x.get('date'))), ent(https(href)), ent(x['title']), body, fig,
           ent(sig_name), ent(sig_role), ent(https(href))))


def solution_brief(name, sbn, slug):
    me = next((n for n in sbn.get('nations', []) if n.get('slug') == slug), None)
    if not me:
        return ''
    play = next((s for s in sbn.get('standards', []) if s.get('standard') == me.get('standard')), None)
    if not play:
        return ''
    src = me.get('source') or {}
    ch = ent(((me.get('gap') + ' ') if me.get('gap') else '') + plain(me.get('gap_text')))
    if src.get('url'):
        ch += ' <a href="%s" target="_blank" rel="noopener noreferrer">%s</a>' % (ent(https(src['url'])), ent(src.get('label') or 'Source'))
    ffd = ent('%s: %s' % (play['name'], play['ffd']))
    aw = me.get('at_work')
    if aw and aw.get('name') and aw.get('url'):
        ffd += ent(' At work in %s: %s%s.' % (name, aw['name'], (', ' + aw['amount']) if aw.get('amount') else ''))
        ffd += ' <a href="%s" target="_blank" rel="noopener noreferrer">Source</a>' % ent(https(aw['url']))
    elif play.get('proof') and play['proof'].get('url'):
        pr = play['proof']
        ffd += ent(' Proved in %s, %s: %s %s.' % (pr['where'], pr['year'], pr['figure'], pr['label']))
        ffd += ' <a href="%s" target="_blank" rel="noopener noreferrer">%s</a>' % (ent(https(pr['url'])), ent(pr.get('source') or 'Source'))
    rows = ''.join('<li><b>%s</b><strong>%s</strong><span>%s</span></li>' % r for r in (
        ('01', 'The challenge', ch), ('02', 'How FfD solves it', ffd), ('03', 'How SI solves it', ent(play['si']))))
    return (
        '<li class="bpx-sol bpx-sol--brief"><p class="bpx-sol__k"><b>The Solution for %s</b><span>%s</span></p>'
        '<h3>%s</h3><ul class="bpx-sol__how">%s</ul>'
        '<div class="bpx-sol__foot"><span class="bpx-sig">Co-design it in<b>The ReDesign Studio</b></span>'
        '<a class="bpx-btn" href="#bp-mandates">The three mandates</a></div></li>'
        % (ent(name), ent(me['standard']), ent(play.get('head') or ''), rows))


def letter(d, p, sbn, son):
    name, slug = d['nation'], p['slug']
    pt_ = p['portrait']
    img = pt_['image']
    m = re.search(r'-(\d+)x(\d+)\.(?:png|jpe?g|webp)$', img)
    w, h = (int(m.group(1)), int(m.group(2))) if m else (768, 768)
    note = ('%s &#183; ' % ent(pt_['note'])) if pt_.get('note') else ''
    paras = ''.join('<p class="bpx-sheet__p">%s</p>' % raw(x) for x in p['letter']['paras'])
    # Solutions: the Solution for this nation (State of Nations), then every Solution about it, newest first
    steward = d.get('steward') or {}
    cards, seen = [], set()
    nos = []
    if sbn:
        me = next((n for n in sbn.get('nations', []) if n.get('slug') == slug), None)
        nos = (me or {}).get('solutions') or []
    pool = []
    for x in (son or {}).get('dispatches', []):
        if x.get('no') and x.get('title') and (x['no'] in nos or x.get('nation') == name):
            pool.append((x, 'preeti'))
    for x in d.get('dispatches') or []:
        if x.get('no') and x.get('title'):
            pool.append((x, 'steward' if x.get('author') in ('steward', 'nia') else 'preeti'))
    pool.sort(key=lambda t: (plain(t[0].get('date')), t[0]['no']), reverse=True)
    for x, who in pool:
        if x['no'] in seen:
            continue
        seen.add(x['no'])
        if who == 'steward':
            cards.append(solution_card(x, steward.get('name', ''), '%s &#183; SI Researcher' % steward.get('role', '')))
        else:
            cards.append(solution_card(x, 'Preeti Sinha', 'President and CEO, Perfect Nations'))
    lead = solution_brief(name, sbn, slug) if sbn else ''
    cards = ([lead] if lead else []) + cards[:5 if lead else 6]
    cards = [c if i < 3 else c.replace('<li class="bpx-sol"', '<li class="bpx-sol bpx-sol--more"', 1) for i, c in enumerate(cards)]
    more = ('<button type="button" class="bpx-showall bpx-solmore" aria-expanded="false">Show all %d Solutions</button>' % len(cards)) if len(cards) > 3 else ''
    if not cards:
        cards = ['<li class="bpx-sol"><p class="bpx-sol__k"><b>Solutions</b></p><h3>The first Solution for %s is in preparation.</h3>'
                 '<p>Every Solution answers three things: the challenge to the seven standards, how innovative financing solves it, and how super intelligence (SI) solves it.</p></li>' % ent(name)]
    wx_mail = mailto('Writing for Perfect %s' % name,
                     'Your name, or a pen name:\r\nWhere you live:\r\nTitle:\r\n\r\nYour vision of Perfect %s, and the economic solutions to achieve it (up to 1,500 words):\r\n\r\n\r\n'
                     'I confirm that this is my own original writing, and I give Perfect Nations permission to publish it with credit to me.\r\n' % name)
    return (
        '<section class="bpx-band bpx-lg bpx-letter" id="bp-letter" aria-labelledby="bp-letter-h"><div class="bpx-in">'
        '<div class="bpx-letter__grid"><figure class="bpx-port"><span class="bpx-frame">'
        '<img src="%s"%s alt="%s" width="%d" height="%d" loading="lazy" decoding="async"></span>'
        '<figcaption class="bpx-frame__cap">%s<small>Nation Portrait &#183; %s<a href="https://perfectnations.org/perfect-nations-gallery/" target="_blank" rel="noopener noreferrer">The Gallery</a></small></figcaption></figure>'
        '<article class="bpx-sheet"><div class="bpx-sheet__lh"><span>Perfect Nations&#8482; &#183; Letters to the Nations</span><span>%s</span></div>'
        '<h2 class="bpx-sheet__dear" id="bp-letter-h">Dear %s,</h2>%s<p class="bpx-sheet__q">%s</p>'
        '<div class="bpx-sheet__foot"><span class="bpx-sig">Yours in design,<b>Preeti Sinha</b><small>President and CEO, Perfect Nations</small></span>'
        '<a class="bpx-btn" href="%s" target="_blank" rel="noopener noreferrer">Read the full letter</a></div></article></div>'
        '<div class="bpx-solx" id="bp-solutions"><span id="bp-dispatches"></span>'
        '<div class="bpx-sols-top"><div><p class="bpx-eb">Solutions</p><h2 class="bpx-h2" id="bp-sol-h">Solutions for Perfect %s</h2>'
        '<p class="bpx-lead">How innovative financing for development (FfD) and super intelligence (SI) close the gap to the seven basic standards of living, for every citizen of %s.</p></div>'
        '<a class="bpx-link" href="https://perfectnations.org/state-of-nations/#sn-solutions" target="_blank" rel="noopener noreferrer">All Solutions</a></div>'
        '<p class="bpx-swipe" aria-hidden="true">Swipe for every Solution</p><ul class="bpx-sols bpx-rail" id="bp-sols">%s</ul>%s</div>'
        '<div class="bpx-wx" id="bp-writings"><div><p class="bpx-eb">ReDesign Studio &#183; Writings</p><h3>Write Perfect %s <em>into being.</em></h3></div>'
        '<p>An essay, an article or a true story of up to 1,500 words: your vision of Perfect %s and the economic solutions to achieve it. Original and unpublished, published with your name and your permission.'
        '<small>or email <a href="mailto:contact@perfectnations.org">contact@perfectnations.org</a></small></p>'
        '<a class="bpx-btn bpx-btn--line" href="%s">Submit your writing</a></div>'
        '</div></section>'
        % (ent(https(img)), img_attrs(img, (300, 600, 768), '(min-width:960px) 250px, 170px'), ent(pt_['alt']), w, h, ent(pt_['title']), note, ent(name), ent(name), paras, raw(p['letter']['quote']),
           ent(https(p['letter']['url'])), ent(name), ent(name), ''.join(cards), more, ent(name), ent(name), ent(wx_mail)))


def assets(d):
    a = d.get('assets') or {}
    name = d['nation']
    cards = []
    for i, x in enumerate(a.get('items') or []):
        tint = x.get('tint') if isinstance(x.get('tint'), list) and len(x.get('tint')) == 2 else ['#3A5A40', '#1E2E22']
        imgs = [u for u in x.get('images') or [] if re.match(r'^https://[^\s"\'<>()\\]+$', plain(u))]
        im = ('<img src="%s"%s alt="%s" width="768" height="560" loading="lazy" decoding="async" onerror="this.remove()">'
              % (ent(imgs[0]), img_attrs(imgs[0], (300, 600, 768), ASSET_SIZES), ent(x.get('alt') or x['name']))) if imgs else ''
        cards.append(
            '<li class="bpx-acard"><span class="bpx-plate" style="background-image:linear-gradient(160deg,%s 0%%,%s 100%%);">%s<span class="bpx-plate__n">%02d</span></span>'
            '<div class="bpx-acard__b"><h3>%s</h3><span class="bpx-acard__fig">%s%s</span>%s</div></li>'
            % (ent(tint[0]), ent(tint[1]), im, i + 1, ent(x['name']), money(x['figure'], x.get('money')),
               '<small>%s</small>' % ent(x['label']) if x.get('label') else '', '<p>%s</p>' % ent(x['text']) if x.get('text') else ''))
    return (
        '<section class="bpx-band bpx-er bpx-assets" id="bp-assets" aria-labelledby="bp-assets-h"><div class="bpx-in">'
        '<div class="bpx-head"><div><p class="bpx-eb">Sovereign Assets</p><h2 class="bpx-h2" id="bp-assets-h">%s</h2></div>'
        '<p class="bpx-lead" style="max-width:40ch;">Each is owned today, earns today, and can lift %s closer to Perfect Capita.</p></div>'
        '<p class="bpx-swipe" aria-hidden="true">Swipe for the five assets</p><ul class="bpx-acards bpx-rail">%s</ul>'
        '<div class="bpx-foot"><p>What each asset is worth, and how far it can carry %s toward Perfect Capita, is the question our research and our guests take up below.</p>'
        '<a class="bpx-link" href="https://perfectnations.org/sovereign-assets/" target="_blank" rel="noopener noreferrer">Sovereign Assets</a></div>'
        '</div></section>' % (ent(a.get('heading') or 'Five assets no balance sheet counts.'), ent(name), ''.join(cards), ent(name)))


def capita(d, p):
    name = d['nation']
    g, scored, score, bind = standards(d)
    un = p['capita'].get('unscored')
    cov = d.get('coverage') or {}
    if score is not None:
        heading = 'The %s wheel: held at %s by %s' % (name, fmt(score), lab(bind).lower())
        cov_v, cov_t = fmt(score), 'Out of 100, set by %s, the standard %s provides least.' % (lab(bind).lower(), name)
        nxt = sorted([n for n in scored if n != bind], key=lambda n: g[n]['value'])[:2]
        tail = (', with %s at %s and %s at %s next.' % (lab(nxt[0]).lower(), fmt(g[nxt[0]]['value']), lab(nxt[1]).lower(), fmt(g[nxt[1]]['value']))) if len(nxt) == 2 else '.'
        definition = ('The poverty line measures income. The Living Line measures a life: food, water, shelter, energy, education, health and livelihood. '
                      'Perfect Capita is the yearly cost, per person, of lifting everyone above the Living Line in all seven basic living standards. '
                      'Coverage scores each standard strictly out of 100, and a nation is held at its weakest: %s at %s, by %s%s'
                      % (name, fmt(score), lab(bind).lower(), tail))
    else:
        heading, cov_v, cov_t, definition = un['heading'], un['value'], un['text'], un['definition']
    four = [
        ('pc', cov.get('perfect_capita') or 'To set', 'Perfect Capita', p['capita']['pc_text']),
        ('price', cov.get('price') or 'To set', 'The price of Perfect %s' % name, p['capita']['price_text']),
        ('cov', cov_v, 'Coverage', cov_t),
        ('gap', cov.get('gap') or '', 'The Gap', cov.get('gap_text') or ''),
    ]
    four_html = ''.join('<li data-k="%s"><b>%s</b><small>%s</small><span>%s</span></li>' % (k, ent(v), ent(l), ent(t)) for k, v, l, t in four)
    tiles = []
    for n in ORDER:
        x = g[n]
        v = x.get('display') or (fmt(x['value']) if num(x.get('value')) else '&#8211;')
        src = '<a href="%s" target="_blank" rel="noopener noreferrer">%s</a>' % (ent(https(x['url'])), ent(x.get('source') or 'Source')) if plain(x.get('url')).startswith('https://') else ''
        tiles.append('<li%s><span>%s</span><b>%s</b>%s%s</li>' % (' class="is-bind"' if n == bind else '', lab(n), ent(v) if x.get('display') else v,
                                                                 '<small>%s</small>' % ent(x['note']) if x.get('note') else '', src))
    return (
        '<section class="bpx-band bpx-iv bpx-pc" id="bp-pc" aria-labelledby="bp-pcx-h"><div class="bpx-in">'
        '<div class="bpx-head"><div><p class="bpx-eb">ReDesign Studio &#183; Perfect Capita</p><h2 class="bpx-h2" id="bp-pcx-h">%s</h2></div>'
        '<a class="bpx-link" href="https://perfectnations.org/perfect-capita/" target="_blank" rel="noopener noreferrer">Perfect Capita</a></div>'
        '<div class="bpx-pc__grid"><div>%s</div><div><ul class="bpx-four" aria-label="%s: Perfect Capita and its companions">%s</ul>'
        '<details class="bpx-how"><summary>The Living Line, and how it is measured</summary><p class="bpx-def"><b>The Living Line</b><span id="bw-def">%s</span></p>'
        '<p>%s <a href="https://perfectnations.org/perfect-capita/#pq-measures" target="_blank" rel="noopener noreferrer">The strict measures</a></p><p>%s</p></details></div></div>'
        '<ul class="bpx-std" aria-label="%s: coverage of each standard, with sources">%s</ul>'
        '</div></section>'
        % (ent(heading), wheel(name, g, score, bind, un), ent(name), four_html, ent(definition),
           ent(p['capita']['est']), ent(p['capita']['measures']), ent(name), ''.join(tiles)))


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
        irs.append(
            '<li class="bpx-ir%s" data-cat="%s"><details><summary><span class="bpx-tags"><span class="bpx-cat">%s</span><span class="bpx-stat bpx-stat--%s">%s</span></span>'
            '<span class="bpx-ir__n">%s%s</span><span class="bpx-ir__a">%s</span></summary><div class="bpx-ir__b">%s%s%s'
            '<a class="bpx-ir__src" href="%s" target="_blank" rel="noopener noreferrer">Source</a></div></details></li>'
            % (' bpx-ir--more' if i >= 8 else '', cat, CAT.get(cat, cat), tone, ent(x.get('status') or 'Active'), ent(x['name']),
               '<small>%s</small>' % ent(x['detail']) if x.get('detail') else '', money(x['amount'], x.get('money')) if x.get('amount') else '',
               '<p class="bpx-ir__note">%s</p>' % ent(x['note']) if x.get('note') else '', '<p>%s</p>' % ent(x['text']) if x.get('text') else '',
               '<p class="bpx-ir__by">%s</p>' % by if by else '', ent(https(x['url']))))
    keys = ['all'] + [k for k in CAT if count.get(k)]
    filters = ''.join('<button type="button" class="bpx-fb%s" data-filter="%s" aria-pressed="%s">%s <span>%d</span></button>'
                      % (' is-on' if k == 'all' else '', k, 'true' if k == 'all' else 'false', 'All' if k == 'all' else CAT[k],
                         len(lines) if k == 'all' else count[k]) for k in keys)
    steward = d.get('steward') or {}
    wire = []
    for w in (d.get('newswire') or [])[:8]:
        if not (w.get('title') and plain(w.get('url')).startswith('https://')):
            continue
        t, hl = w['title'], w.get('highlight')
        b = ent(t)
        if hl and hl in t:
            i = t.index(hl)
            b = ent(t[:i]) + '<span class="bpx-money">%s</span>' % ent(hl) + ent(t[i + len(hl):])
        wire.append('<li><time datetime="%s">%s</time><a href="%s" target="_blank" rel="noopener noreferrer"><b>%s</b></a><span class="bpx-src">%s</span></li>'
                    % (ent(w.get('date', '')), ent(w.get('label') or short_date(w.get('date'))), ent(https(w['url'])), b, ent(w.get('source', ''))))
    return (
        '<section class="bpx-band bpx-lg bpx-cap" id="bp-capital" aria-labelledby="bp-cap-h"><div class="bpx-in">'
        '<div class="bpx-head"><div><p class="bpx-eb">The Research &#183; Capital Architecture</p><h2 class="bpx-h2" id="bp-cap-h">%s</h2></div>'
        '<a class="bpx-link" href="https://perfectnations.org/capital-architecture/" target="_blank" rel="noopener noreferrer">Capital Architecture</a></div>'
        '<p class="bpx-k">The record in figures</p><ul class="bpx-recs">%s</ul>'
        '<div id="bp-register"><p class="bpx-k">The register &#183; <span data-bpx="count">%d</span> instruments and investments on record</p>'
        '<div class="bpx-filters" role="group" aria-label="Show lines by who provides them">%s</div>'
        '<ul class="bpx-irs" id="bp-irs">%s</ul><button type="button" class="bpx-showall%s" id="bp-showall"%s>Show all %d lines</button></div>'
        '<div class="bpx-nw" id="bp-newswire"><div class="bpx-nw__h"><h3>The %s Newswire</h3>'
        '<a class="bpx-link" href="https://perfectnations.org/state-of-nations/#sn-wire" target="_blank" rel="noopener noreferrer">The Solutions Wire</a></div>'
        '<div class="bpx-stew"><img src="%s"%s alt="%s, %s" width="52" height="52" loading="lazy" decoding="async" onerror="this.style.display=\'none\'">'
        '<p><b>%s</b><span>%s &#183; SI Researcher</span>Every change is sourced and reviewed before it is published. <time datetime="%s">Last updated %s</time></p></div>'
        '<ul class="bpx-wire">%s</ul><button type="button" class="bpx-showall bpx-allnews" hidden>All news</button></div>'
        '</div></section>'
        % (ent(c.get('heading') or ''), recs, len(lines), filters, ''.join(irs), ' is-phone' if 5 < len(lines) <= 8 else '',
           '' if len(lines) > 5 else ' hidden', len(lines),
           ent(name), ent(https(p['steward_photo'])), img_attrs(p['steward_photo'], (100, 150), '52px'), ent(steward.get('name', '')), ent(steward.get('role', '')),
           ent(steward.get('name', '')), ent(steward.get('role', '')), ent(d.get('updated', '')), ent(long_date(d.get('updated'))),
           ''.join(wire)))


def enterprises_voices(d, p):
    name, slug = d['nation'], p['slug']
    e = d.get('enterprises') or {}
    ents = ''.join('<li><span class="bpx-ent__s">%s</span><h3>%s</h3>%s<a href="%s" target="_blank" rel="noopener noreferrer">%s</a></li>'
                   % (ent(x.get('standard', '')), ent(x['name']), '<p>%s</p>' % ent(x['text']) if x.get('text') else '',
                      ent(https(x['url'], allow_mail=True)), ent(x.get('source') or 'Source'))
                   for x in e.get('items') or [] if x.get('name') and x.get('url'))
    rnd = random.Random('pn-eq-' + slug)
    bars = ''.join('<i style="--h:%.2f;--d:%.1fs"></i>' % (0.25 + 0.7 * math.sin(math.pi * k / 27) * (0.75 + 0.25 * rnd.random()), -(k % 9) * 0.23)
                   for k in range(28))
    nation_q = urllib.parse.quote(slug)
    return (
        '<section class="bpx-band bpx-er bpx-ent" id="bp-enterprises" aria-labelledby="bp-ent-h"><div class="bpx-in">'
        '<div class="bpx-head"><div><p class="bpx-eb">ReDesign Studio &#183; Enterprises</p><h2 class="bpx-h2" id="bp-ent-h">%s</h2></div>'
        '<a class="bpx-btn bpx-btn--line" href="%s">Suggest an enterprise</a></div>'
        '<ul class="bpx-ents">%s</ul>'
        '<div class="bpx-vx" id="bp-voices"><div><p class="bpx-eb">ReDesign Studio &#183; Voices of %s</p><span class="bpx-air"><i aria-hidden="true"></i>Launching soon</span>'
        '<h2 id="bp-voices-h">The people already <em>building it.</em></h2><div class="bpx-eq" aria-hidden="true">%s</div></div>'
        '<div><figure class="bpx-vq"><figcaption>The question every guest answers</figcaption>'
        '<blockquote>&#8220;What does %s already own, and how could it pay for a decent life for every citizen?&#8221;</blockquote></figure>'
        '<p class="bpx-vlocal">%s</p><div class="bpx-btns">'
        '<a class="bpx-btn" href="https://perfectnations.org/contact/?nation=%s&amp;topic=nominate-self" target="_blank" rel="noopener noreferrer">Nominate yourself</a>'
        '<a class="bpx-btn bpx-btn--line" href="https://perfectnations.org/contact/?nation=%s&amp;topic=guest" target="_blank" rel="noopener noreferrer">Suggest a guest</a>'
        '</div></div></div></div></section>'
        % (ent(e.get('heading') or ''), ent(mailto('An enterprise for Perfect %s' % name)), ents, ent(name), bars, ent(name),
           ent(p['voices']['local']), nation_q, nation_q))


# The second Nation Portrait, the flag edition (painted 31 October 2026; the Steward-General, 8 Nov 2026: "a
# second set of the 40 nations portraits with the flag imagery ... for other parts in the blueprints").
# It closes the page, beside "Design Perfect <Nation> with us". The file is uploaded to the Media Library in
# November 2026 as pn-portrait-flag-<slug>.png (1264 px square, from its Canva link in the Project doc
# claude/nation-portraits-v4-canva.md); until it is there, the figure removes itself and the close keeps
# one column. Afghanistan, Barbados, Kenya and Rwanda keep their own portraits and have no flag edition.
FLAG_EDITION = ('angola', 'bangladesh', 'botswana', 'brazil', 'burundi', 'colombia', 'cote-divoire', 'dr-congo', 'ecuador', 'egypt', 'eswatini', 'ethiopia', 'fiji', 'ghana', 'india', 'indonesia', 'jamaica', 'jordan', 'lesotho', 'madagascar', 'malawi', 'mexico', 'morocco', 'mozambique', 'namibia', 'nigeria', 'pakistan', 'philippines', 'republic-of-congo', 'senegal', 'somalia', 'south-africa', 'south-sudan', 'sri-lanka', 'tanzania', 'uganda', 'ukraine', 'vietnam', 'zambia', 'zimbabwe')
FLAG_DIR = 'https://perfectnations.org/wp-content/uploads/2026/11/'


def flag_fig(name, slug, title):
    if slug not in FLAG_EDITION:
        return ''
    u = FLAG_DIR + 'pn-portrait-flag-' + slug
    return (
        '<figure class="bpx-port bpx-port--flag"><span class="bpx-frame">'
        '<img src="%s-768x768.png" srcset="%s-300x300.png 300w, %s-768x768.png 768w" sizes="(min-width:960px) 300px, 200px" '
        'alt="%s, flag edition: the nation portrait of %s painted with its flag" width="768" height="768" loading="lazy" decoding="async" '
        'onerror="var f=this.closest(\'figure\');if(f){f.remove();}"></span>'
        '<figcaption class="bpx-frame__cap">%s<small>Nation Portrait, flag edition &#183; '
        '<a href="https://perfectnations.org/art-of-nations/" target="_blank" rel="noopener noreferrer">Art of Nations</a></small></figcaption></figure>'
        % (u, u, u, ent(title), ent(name), ent(title)))


def close(d, p):
    name, slug = d['nation'], p['slug']
    srcs = ''.join('<li>%s</li>' % raw(s) for s in p['sources'])
    return (
        '<section class="bpx-band bpx-dp bpx-close" aria-labelledby="bp-close-h"><div class="bpx-in bpx-close__grid"><div class="bpx-close__words">'
        '<p class="bpx-eb">The %s ReDesign Studio is open</p><h2 class="bpx-h2" id="bp-close-h">Design Perfect %s with us.</h2>'
        '<p class="bpx-lead">%s</p><div class="bpx-btns">'
        '<a class="bpx-btn" href="https://perfectnations.org/design-studio/" target="_blank" rel="noopener noreferrer">Enter the Perfect Nations ReDesign Studio</a>'
        '<a class="bpx-btn bpx-btn--line" href="https://perfectnations.org/contact/?nation=%s" target="_blank" rel="noopener noreferrer">Write to us</a>'
        '<a class="bpx-btn bpx-btn--line" href="https://perfectnations.org/blueprints/" target="_blank" rel="noopener noreferrer">All 195 nations</a></div>'
        '<details class="bpx-sources"><summary>Sources</summary><ol>%s</ol></details></div>%s</div></section>'
        '<div class="bpx-toast" id="bp-toast" role="status" aria-live="polite" hidden><span>Opening your email app. If nothing opens, write to <b>contact@perfectnations.org</b></span>'
        '<button type="button" id="bp-toast-copy">Copy address</button><button type="button" class="bpx-x" id="bp-toast-x" aria-label="Close">&#215;</button></div>'
        % (ent(name), ent(name), ent(p['close_lead']), urllib.parse.quote(slug), srcs,
           flag_fig(name, slug, p['portrait'].get('title') or ('%s in Bloom' % name))))


# ---------------------------------------------------------------- the page

def open_slugs():
    man = json.loads((PAGES / 'manifest.json').read_text(encoding='utf-8'))
    out = []
    for key, v in man['pages'].items():
        m = re.match(r'^pages/blueprint-([a-z-]+)\.html$', v.get('file', ''))
        if key.startswith('pn-bp-') and m:
            out.append(m.group(1))
    return sorted(set(out))


def build(slug, sbn, son, seam, today):
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
           'unscored': p['capita'].get('unscored') and {'heading': p['capita']['unscored']['heading'],
                                                       'center': p['capita']['unscored'].get('center', 'NOT SCORED')}}
    imgs = {}
    for x in (d.get('assets') or {}).get('items') or []:
        for u in x.get('images') or []:
            ss = srcset(u, (300, 600, 768))
            if ss:
                imgs[u] = ss
    cfg['img'] = imgs
    cfg['sizes'] = ASSET_SIZES
    script = (HERE / 'script.js').read_text(encoding='utf-8').replace('/*pn:cfg*/', 'var CFG = %s;' % js_str(cfg))
    head = (
        '<!-- PERFECT NATIONS . NATIONAL BLUEPRINT . %s . v%s . %s . Built by tools/build_nations.py: never edit by hand. -->\n'
        '<!-- v10.2 (8 November 2026): the second Nation Portrait, the flag edition, closes the page beside "Design\n'
        '     Perfect <Nation> with us" (40 nations). It shows once pn-portrait-flag-<slug>.png is in the Media Library. -->\n'
        '<!-- v10.1 (8 November 2026): FfD before SI (the Steward-General, 8 Nov 2026). The Solutions lead names\n'
        '     innovative financing for development (FfD) first and super intelligence (SI) second, and the\n'
        '     Solution rows read "How FfD solves it". -->\n'
        '<!-- v10.0 (7 November 2026): one design for all 44 blueprints, in the site palette. Earthrise first, then the\n'
        '     ReDesign Studio and its three mandates straight under the hero (no waiting for it to appear), the Letter and\n'
        '     Solutions (Lagoon), the Sovereign Assets (Earthrise), Perfect Capita (ivory), Capital Architecture and the\n'
        '     Newswire (Lagoon), Enterprises and Voices (Earthrise) and the close (Earthrise Depth), with painted seams.\n'
        '     Dispatches are now Solutions, read from State of Nations: the Solution for this nation and every Solution about it.\n'
        '     Faster: the globe is drawn by the page itself (no globe.gl or three.js, about 290 KB less), its Earth picture is\n'
        '     preloaded, the handwriting font loads only near the Letter, pictures load as they come into view, and every\n'
        '     data file is revalidated rather than downloaded again. Served live from GitHub by the Perfect Nations Live Pages\n'
        '     plugin (root %s); the code below is also the fallback when a data file cannot be read. -->\n'
        '<link rel="preconnect" href="https://raw.githubusercontent.com" crossorigin>\n'
        '<link rel="preload" as="image" href="%s" media="(min-width:768px)" crossorigin>\n'
        '<link rel="preload" as="image" href="%s" media="(max-width:767px)" crossorigin>\n'
        % (d['nation'].upper().encode('ascii', 'xmlcharrefreplace').decode('ascii'), VERSION, today, rid, EARTH['lg'], EARTH['sm']))
    body = '\n'.join([
        '<style>\n%s\n</style>' % css,
        '<div id="%s" class="bpx" data-version="%s">' % (rid, VERSION),
        seam['sprite'],
        hero(d, p),
        studio(d, p),
        letter(d, p, sbn, son),
        seam['a'],
        assets(d),
        capita(d, p),
        capital(d, p),
        seam['b'],
        enterprises_voices(d, p),
        close(d, p),
        '</div>',
        '<script>\n%s\n</script>' % globe,
        '<script>\n%s\n</script>' % script,
    ])
    page = head + body + '\n'
    first = re.search(r'\bid\s*=\s*["\'](pn-[a-z0-9-]+)["\']', page)
    if not first or first.group(1) != rid:
        sys.exit('%s: the first pn- id must be %s, found %s' % (slug, rid, first and first.group(1)))
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
    sys.path.insert(0, str(ROOT / 'tools'))
    from build_home import seam  # the painted seams of the homepage, one arrangement per letter
    seams = (PAGES / 'home-seams.html').read_text(encoding='utf-8').strip()
    sd = {'sprite': seams, 'a': seam('a'), 'b': seam('d')}
    today = datetime.now(timezone.utc).strftime('%Y-%m-%d')
    total = 0
    for s in slugs:
        n = build(s, sbn, son, sd, today)
        total += n
        print('pages/blueprint-%s.html: %d characters' % (s, n))
    print('%d pages, %d characters on average' % (len(slugs), total // max(1, len(slugs))))
    if args.manifest:
        path = PAGES / 'manifest.json'
        man = json.loads(path.read_text(encoding='utf-8'))
        for s in slugs:
            for key, v in man['pages'].items():
                if v.get('file') == 'pages/blueprint-%s.html' % s:
                    v['version'] = VERSION
        man['updated'] = today
        path.write_text(json.dumps(man, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
        print('pages/manifest.json: %d blueprints at v%s' % (len(slugs), VERSION))


if __name__ == '__main__':
    main()
