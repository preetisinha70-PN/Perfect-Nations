#!/usr/bin/env python3
"""Build the State of Nations page (perfectnations.org/state-of-nations/) and its nation data.

The page is about Solutions: one Solution that Perfect Nations designs for every open blueprint nation,
to end extreme poverty and secure the seven basic standards of living, with innovative finance first and
super intelligence second.
v8.0: Perfect Nations Solutions, designed by Perfect Nations (the Steward-General, 9 Nov 2026).
  "dispatches" in data/state-of-nations.json now holds the designed Solutions (kind "design"): no, slug,
  nation, blueprint, title, standfirst (the idea), challenge (sourced), advises (finance first, then a
  sentence that begins "With super intelligence,"), how (Assets, Capital, Solutions), proof (the deal that
  proves it, from data/capital-architecture.json or a nation's record), first (the first move), standards,
  figure, caption, gap_seen and sources. The market deals that were Solutions move to "deals" and show as
  Deal Notes above the wire. The nation finder band is retired: the page links each Solution to the
  nation's seven standards in data/solutions-by-nation.json, which now names the nation's design.
v7.3: fewer words, and richer advice that weaves in super intelligence (the Steward-General, 9 Nov 2026).
  One headline and one line per band, the detail one click away in a Read more disclosure or the
  dispatch; the ticker carries three Solutions and five deals; the count above each standard's nations
  is shorter. The PLAYBOOK advice is unchanged here.
v7.2: What Perfect Nations advises, in place of how FfD and SI solve it (the Steward-General, 9 Nov 2026).
  Each Solution reads as an advisory firm's advice to a client: the challenge, then what Perfect Nations advises
  (the field "advises" in data/state-of-nations.json and in each standard of the playbook below). The
  steps of a Solution are 01 The challenge, 02 The deal, 03 What Perfect Nations advises.

    python3 tools/build_state_of_nations.py           build pages/state-of-nations.html and the data
    python3 tools/build_state_of_nations.py --data    rebuild data/solutions-by-nation.json only

Sources (never edited here):
  src/state-of-nations.html        the page itself (style, markup, script), root id pn-son
  data/state-of-nations.json       the Solutions ("dispatches") and the wire; kept by the Correspondent
  data/<nation>.json               each open blueprint: coverage, guarantees, capital.register;
                                   kept by the Nation Stewards
  data/blueprints.json             the index of open blueprints (names, urls)
  data/capital-architecture.json   the instrument library whose deals prove the playbook
  pages/home-rule.html             the gold line between sections, shared with the homepage (in place
                                   of the painted botanical seams since v7.2, 9 Nov 2026)

Writes:
  data/solutions-by-nation.json    the page reads it on every visit; it mirrors the nation files and
                                   adds no fact (data: commit straight to main)
  pages/state-of-nations.html      the one-file page, served by the Perfect Nations Live Pages plugin
                                   (manifest key pn-son); goes through a pull request

The State of Nations Steward (skill steward-state-of-nations) runs the page build; the Correspondent
runs --data after every watch. Plain ASCII out: every other character becomes an HTML entity.
"""
import html
import json
import re
import sys
import unicodedata
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / 'data'
PAGES = ROOT / 'pages'
SRC = ROOT / 'src' / 'state-of-nations.html'
OUT = PAGES / 'state-of-nations.html'
NATION_DATA = DATA / 'solutions-by-nation.json'
sys.path.insert(0, str(ROOT / 'tools'))

VERSION = '8.5'  # Solutions No. 45 to 50: Cameroon, Chad, Cuba, Iraq, Palestine and Nigeria, after Energy and Health were re-measured (the Steward-General, 12 Nov 2026)
# v8.4: light reading sections, Earthrise accents (the Steward-General, 10 Nov 2026)
# v8.3: Discuss this Solution in the reader of every Solution (the Steward-General, 10 Nov 2026)
# v8.2: the close button of every pop-up is one design: a gold X drawn as two strokes, centred in a circle (the Steward-General, 9 Nov 2026)
ORDER = ['Food', 'Water', 'Shelter', 'Energy', 'Education', 'Health', 'Livelihood']
MONTHS = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September',
          'October', 'November', 'December']
WIRE_STATIC = 12     # wire items written into the page (the live file replaces them)
SOL_SHOWN = 7        # Solutions shown on a laptop before Show all (the lead and six)
TICK_WIRE = 5        # deals in the moving list, after the three newest Solutions
SITE = 'https://perfectnations.org'

# ---------------------------------------------------------------------------------------------
# THE PLAYBOOK: for each standard, the instrument that closes the gap, the deal that proved it, and
# what Perfect Nations advises ("advises", written from "ffd" and "si" and adding no fact; it opens with
# the nations it addresses, as the label above it already names Perfect Nations; the page and the
# blueprints show "advises", and keep "ffd" and "si" in the data only). "lib" names an instrument in
# data/capital-architecture.json, whose figure, place, year and source are used unchanged. Food and
# Health carry their own primary source.
# Changing a line here is a page change: raise VERSION and open a pull request.
# ---------------------------------------------------------------------------------------------
PLAYBOOK = {
    'Food': {
        'head': 'Protect the harvest before it fails.',
        'name': 'Sovereign drought insurance',
        'ffd': 'Parametric cover releases funds on measured rainfall, so food reaches families within weeks of a failed season, without waiting for an appeal.',
        'proof': {'where': 'Malawi', 'year': '2024', 'figure': '$11.2M',
                  'label': 'released after the El Niño drought, for food aid to about 235,000 households',
                  'source': 'African Development Bank, August 2024',
                  'url': 'https://www.afdb.org/en/news-and-events/press-releases/african-development-bank-group-and-african-risk-capacity-group-issue-112-million-insurance-payout-government-malawi-73593'},
        'si': 'SI reads rainfall, harvests and food prices district by district, sets the trigger and prices the cover before the season begins.',
        'advises': 'Nations where food is furthest from reach should buy drought insurance that releases funds on measured rainfall, with the trigger and the price of the cover set district by district before the season begins. With super intelligence, rainfall and harvests can be read field by field, so that funds reach families within weeks of a failed season, before hunger does.',
        'first': 'sovereign drought insurance',
    },
    'Water': {
        'head': 'Turn cheaper debt into safe water.',
        'name': 'Debt-for-climate-resilience swap',
        'ffd': 'Guarantees replace costly debt with cheaper debt, and the savings are committed to water and sewerage.',
        'lib': 'debt-for-climate',
        'si': 'SI maps every household without safe water at home, prices each connection, and follows the savings into every main and treatment plant.',
        'advises': 'Nations where water is furthest from reach should swap costly debt for cheaper, guaranteed debt and commit the savings to water and sewerage. With super intelligence, every saving can be followed into each household connection, main and treatment plant, and the next connection planned where the need is greatest.',
        'first': 'a debt-for-resilience swap bound to water',
    },
    'Shelter': {
        'head': 'Ring-fence bond money for homes and sanitation.',
        'name': 'Social bond',
        'ffd': 'The proceeds can be spent only on eligible homes, toilets and sewers, reported to investors every year.',
        'lib': 'social-bond',
        'si': 'SI finds the homes without a safe toilet, groups them into programmes investors can finance, and reports each unit delivered.',
        'advises': 'Nations where shelter is furthest from reach should issue a social bond whose proceeds can be spent only on eligible homes, toilets and sewers. With super intelligence, each unit can be planned, priced and verified, and reported to investors every year, until every family has a safe home.',
        'first': 'a social bond for homes and sanitation',
    },
    'Energy': {
        'head': 'Finance clean power and clean cooking at national scale.',
        'name': 'Sovereign green bond',
        'ffd': 'Bond money ring-fenced for clean energy under a published framework, with every allocation reported to investors.',
        'lib': 'green-bond',
        'si': 'SI counts the households still cooking with wood, charcoal or kerosene, prices the switch per home, and tracks every project the bond finances.',
        'advises': 'Nations where energy is furthest from reach should issue a sovereign green bond ring-fenced for clean power and clean cooking. With super intelligence, the switch can be priced for every household still cooking with wood, charcoal or kerosene, and every project the bond finances reported to investors.',
        'first': 'a sovereign green bond for clean power and cooking',
    },
    'Education': {
        'head': 'Finance learning, not only classrooms.',
        'name': 'Program-for-Results',
        'ffd': 'Each tranche of the loan is released only when pupils reach an agreed learning level, verified independently.',
        'lib': 'program-for-results',
        'si': 'SI tracks reading levels school by school, sets the targets that release each tranche, and flags the schools falling behind.',
        'advises': 'Nations where education is furthest from reach should borrow on a Program-for-Results basis, releasing each tranche only when pupils reach an agreed learning level, verified independently. With super intelligence, reading levels can be tracked school by school, so that every child who falls behind is reached in time.',
        'first': 'a Program-for-Results that rewards learning',
    },
    'Health': {
        'head': 'Let lower debt costs finance care.',
        'name': 'Debt-for-health guarantee',
        'ffd': 'A development bank guarantee cuts the cost of existing debt, and the savings are bound to the health system before they can be spent elsewhere.',
        'proof': {'where': 'Barbados', 'year': '2026', 'figure': '$175M',
                  'label': 'IDB guarantee, 20 years; about US$160 million of the savings for health care',
                  'source': 'Inter-American Development Bank, project BA-U0003',
                  'url': 'https://www.iadb.org/en/project/BA-U0003'},
        'si': 'SI prices the essential services each citizen lacks, finds the costly debt to refinance, and follows every saving into clinics and care.',
        'advises': 'Nations where health is furthest from reach should refinance costly debt behind a development bank guarantee and bind the savings to the health system before they can be spent elsewhere. With super intelligence, every saving can be followed into clinics and care, and services planned where citizens are furthest from them.',
        'first': 'a debt-for-health guarantee',
    },
    'Livelihood': {
        'head': 'Let local banks lend to the enterprises that hire.',
        'name': 'Small-business credit guarantee',
        'ffd': 'A facility guarantees most of each small-business loan, so local banks lend to firms they would otherwise turn away.',
        'lib': 'sme-credit-guarantee',
        'si': 'SI matches enterprises to lenders, prices the risk the guarantee must carry, and counts the jobs each loan creates.',
        'advises': 'Nations where livelihoods are furthest from reach should set up a facility that guarantees most of each small-business loan, so that local banks lend to the firms they would otherwise turn away. With super intelligence, lenders can assess firms that have no credit history, and every job each loan creates can be counted.',
        'first': 'a small-business credit guarantee',
    },
}

# Words that tie an instrument on a nation's record to a standard (name, detail and text are read).
AT_WORK = {
    'Food': r'\bfood|agri|\bfarm|nutrition|irrigat|\bcrops?\b',
    'Water': r'\bwater|sanitation|sewer',
    'Shelter': r'\bhous|sanitation|toilet|\bhomes?\b|slum|shelter',
    'Energy': r'\benergy|\bpower\b|electri|hydro|solar|geotherm|clean cooking|\bgrid\b|transmission',
    'Education': r'educat|\bschool|learning|literacy|teacher|pupil',
    'Health': r'\bhealth|hospital|clinic|vaccin|medical',
    'Livelihood': r'\bjobs?\b|employment|small business|\bm?smes?\b|enterprise|livelihood|entrepreneur',
}


def a(text):
    """Escape for HTML and turn every non-ASCII character into a numeric entity."""
    return html.escape(str(text), quote=True).encode('ascii', 'xmlcharrefreplace').decode('ascii')


def std_name(s):
    return 'Livelihood' if str(s).startswith('Livelihood') else str(s)


def load(p):
    return json.loads(Path(p).read_text(encoding='utf-8'))


def short_date(iso):
    y, m, d = iso.split('-')
    return '%d %s %s' % (int(d), MONTHS[int(m) - 1][:3], y)


def long_date(iso):
    y, m, d = iso.split('-')
    return '%d %s %s' % (int(d), MONTHS[int(m) - 1], y)


# ---------------------------------------------------------------------------------------------
# THE NATION DATA
# ---------------------------------------------------------------------------------------------
def playbook():
    lib = {}
    for fam in load(DATA / 'capital-architecture.json')['index']['families']:
        for it in fam.get('items', []):
            lib[it['id']] = it
    out = []
    for s in ORDER:
        p = dict(PLAYBOOK[s])
        if 'lib' in p:
            it = lib.get(p.pop('lib'))
            if not it:
                sys.exit('playbook: %s names an instrument missing from capital-architecture.json' % s)
            p['proof'] = {k: it.get(k, '') for k in ('where', 'year', 'figure', 'label', 'source', 'url')}
        p['standard'] = s
        out.append(p)
    return out


def at_work(d, far):
    """The instrument on the nation's record that best serves its furthest standard, or None.
    The name and note count most; the text counts only when it names the standard itself."""
    best, top = None, 0
    word = re.compile(r'\b%s' % far.lower(), re.I)
    for i, r in enumerate((d.get('capital') or {}).get('register', [])):
        if not str(r.get('url', '')).startswith('https://'):
            continue
        head = ' '.join(str(r.get(k, '')) for k in ('name', 'note', 'detail'))
        text = str(r.get('text', ''))
        score = 3 * len(re.findall(AT_WORK[far], head, re.I))
        if word.search(text):
            score += 2 + len(re.findall(AT_WORK[far], text, re.I))
        if str(r.get('status', '')).lower() in ('completed', 'closed', 'cancelled', 'withdrawn'):
            score -= 1
        if score > top:
            best, top = r, score
    if not best:
        return None
    return {'name': best.get('name', ''), 'amount': best.get('amount', ''), 'money': bool(best.get('money')),
            'status': best.get('status', ''), 'url': best.get('url', '')}


def is_design(s):
    """A Solution that Perfect Nations designed (v8.0), as opposed to a deal read as a Solution before it."""
    return s.get('kind') == 'design' or bool(s.get('advises') and s.get('how'))


def design_of(solutions, name):
    """The nation's designed Solution, in brief, for the blueprints and the page: no, title, idea, advice."""
    ds = sorted([s for s in solutions if s.get('nation') == name and is_design(s)], key=lambda s: s['no'], reverse=True)
    if not ds:
        return None
    d = ds[0]
    return {'no': d['no'], 'title': d['title'], 'idea': d.get('standfirst', ''), 'advises': d.get('advises', ''),
            'url': '%s/state-of-nations/#solution-%02d' % (SITE, d['no'])}


def nations(solutions):
    index = load(DATA / 'blueprints.json')
    rows = []
    for e in index.get('open', []):
        slug = e.get('slug')
        f = DATA / ('%s.json' % slug)
        if not slug or not f.exists():
            continue
        d = load(f)
        cv = d.get('coverage') or {}
        far = std_name(cv.get('set_by') or '')
        if far not in ORDER or not cv.get('gap'):
            continue
        seven = []
        src = {}
        for g in d.get('guarantees', []):
            name = std_name(g.get('name', ''))
            if name not in ORDER:
                continue
            v = g.get('value')
            seven.append([name, g.get('display', ''), v if isinstance(v, (int, float)) else None,
                          g.get('note', ''), g.get('source', ''), g.get('url', '')])
            if name == far:
                src = {'label': g.get('source', ''), 'url': g.get('url', '')}
        seven.sort(key=lambda x: ORDER.index(x[0]))
        work = at_work(d, far)
        name = e.get('name') or d.get('nation') or slug
        rows.append({
            'slug': slug, 'name': name, 'url': e.get('url') or '%s/blueprints/%s/' % (SITE, slug),
            'standard': far, 'gap': cv.get('gap', ''), 'gap_text': cv.get('gap_text', ''),
            'source': src, 'seven': seven, 'at_work': work,
            'solutions': sorted([s['no'] for s in solutions if s.get('nation') == name and is_design(s)], reverse=True),
            'design': design_of(solutions, name),
        })
    rows.sort(key=lambda r: r['name'].replace('ô', 'o').lower())
    return rows


def std_counts(nat):
    c = {s: 0 for s in ORDER}
    for n in nat['nations']:
        c[n['standard']] += 1
    return c


def build_data():
    son = load(DATA / 'state-of-nations.json')
    data = {
        'page': 'solutions-by-nation',
        'updated': date.today().isoformat(),
        'about': ('Built by tools/build_state_of_nations.py from data/<nation>.json (coverage, guarantees, '
                  'capital.register) and data/capital-architecture.json. Read by perfectnations.org/state-of-nations/ '
                  'on every visit. Adds no fact: change a figure in its nation file, then rebuild.'),
        'standards': playbook(),
        'nations': nations(son.get('dispatches', [])),
    }
    NATION_DATA.write_text(json.dumps(data, indent=1, ensure_ascii=False) + '\n', encoding='utf-8')
    return data, son


# ---------------------------------------------------------------------------------------------
# THE PAGE PARTS (the page script draws the same markup from the live files)
# ---------------------------------------------------------------------------------------------
MARKS = re.compile('[\u0300-\u036f]')
MONEY = re.compile(r'^(?:~|Up to |About )?(?:[A-Z]{1,3}\s?)?[$]|^(?:EUR|GHS|KSh|KES|INR|FJD|R\$|M)\s?[0-9]')


def nrm(t):
    """As the page script's nrm(): lower case, no accents, words only (for the nation search)."""
    t = MARKS.sub('', unicodedata.normalize('NFD', str(t or '').lower()))
    return re.sub(r'[^a-z0-9]+', ' ', t).strip()


def std_chips(stds):
    return '<ul class="sn-std">%s</ul>' % ''.join('<li>%s</li>' % a(s) for s in stds)


def solution_card(s):
    """A Perfect Nations Solution: nation and number, the name, the idea, The challenge, What Perfect Nations
    advises, the standards it moves and Read the Solution (the reader opens on the page)."""
    no = int(s['no'])
    stds = s.get('standards', [])
    bp = ' data-bp="%s"' % a(s['blueprint']) if str(s.get('blueprint', '')).startswith('https://') else ''
    rows = [(t, s.get(k)) for t, k in (('The challenge', 'challenge'), ('What Perfect Nations advises', 'advises')) if s.get(k)]
    return ''.join([
        '<li class="sn-c" data-no="%d" data-std="%s"%s data-q="%s">' % (no, a(';'.join(stds)), bp, a(nrm('%s %s' % (s.get('nation', ''), s['title'])))),
        '<div class="sn-c__k"><b>%s</b><span>Solution No. %02d</span></div>' % (a(s.get('nation', '')), no),
        '<h3><a href="#solution-%02d">%s</a></h3>' % (no, a(s['title'])),
        '<p class="sn-c__i">%s</p>' % a(s['standfirst']) if s.get('standfirst') else '',
        '<dl class="sn-c__x">%s</dl>' % ''.join('<div><dt>%s</dt><dd>%s</dd></div>' % (t, a(w)) for t, w in rows) if rows else '',
        '<div class="sn-c__ft">%s<span class="sn-c__go">Read the Solution</span></div></li>' % std_chips(stds)])


def designs(son):
    return sorted([s for s in son.get('dispatches', []) if is_design(s)], key=lambda s: s['no'], reverse=True)


def solution_cards(son):
    ds = designs(son)
    out = []
    for i, s in enumerate(ds):
        c = solution_card(s)
        if i == 0:
            c = c.replace('<li class="sn-c"', '<li class="sn-c sn-c--lead"', 1)
        elif i >= SOL_SHOWN:
            c = c.replace('<li class="sn-c"', '<li class="sn-c" hidden', 1)
        out.append(c)
    return '\n'.join(out), len(ds)


def deal_card(d):
    """A Deal Note: a landmark deal read by Perfect Nations (a Solution before v8.0)."""
    no = int(d['no'])
    href = d['url'] if str(d.get('url', '')).startswith('https://') else '#deal-%02d' % no
    k = '<b>Deal Note No. %02d</b>' % no
    if d.get('nation'):
        k += '<span>%s</span>' % a(d['nation'])
    if re.match(r'^\d{4}-\d{2}-\d{2}$', str(d.get('date', ''))):
        k += '<time datetime="%s">%s</time>' % (a(d['date']), a(short_date(d['date'])))
    fig = ''
    if d.get('figure'):
        fig = '<p class="sn-d__f"><b%s>%s</b>%s</p>' % (' class="is-money"' if MONEY.match(d['figure']) else '', a(d['figure']),
                                                         '<span>%s</span>' % a(d['caption']) if d.get('caption') else '')
    return '<li class="sn-d" data-no="%d"><p class="sn-d__k">%s</p><h3><a href="%s">%s</a></h3>%s</li>' % (no, k, a(href), a(d['title']), fig)


def deals(son):
    """The Deal Notes, newest first: "deals", and any Solution in "dispatches" that is not a design."""
    seen, out = set(), []
    pool = list(son.get('deals', [])) + [s for s in son.get('dispatches', []) if not is_design(s)]
    pool.sort(key=lambda d: (str(d.get('date', '')), d.get('no', 0)), reverse=True)
    for d in pool:
        if not d.get('no') or not d.get('title') or d['no'] in seen:
            continue
        seen.add(d['no'])
        out.append(deal_card(d))
    return '\n'.join(out), len(out)


def wire_item(w):
    d = w['date'].split('-')
    by = w.get('by') or []
    names = ' and '.join('<b>%s</b>' % a(x) for x in by) if by else '<b>Press release</b>'
    if w.get('agency'):
        names += ', ' + a(w['agency'])
    meta = '<span class="sn-w__src">Via %s</span>' % a(w.get('source', ''))
    if w.get('type'):
        meta += '<span>%s</span>' % a(w['type'])
    if w.get('where'):
        meta += '<span>%s</span>' % a(w['where'])
    return ''.join([
        '<li class="sn-w" data-type="%s" data-region="%s" data-nation="%s">' % (
            a(w.get('type', '')), a(w.get('region', '')), a(';'.join(w.get('nations') or []))),
        '<time datetime="%s"><b>%d</b>%s %s</time>' % (a(w['date']), int(d[2]), MONTHS[int(d[1]) - 1][:3], d[0]),
        '<div><p class="sn-w__m">%s</p>' % meta,
        '<h3><a href="%s" target="_blank" rel="noopener noreferrer">%s</a></h3>' % (a(w['url']), a(w['title'])),
        '<p class="sn-w__by">%s</p></div></li>' % names])


def wire(son):
    ws = [w for w in son.get('wire', []) if re.match(r'^\d{4}-\d{2}-\d{2}$', str(w.get('date', ''))) and str(w.get('url', '')).startswith('https://')]
    ws.sort(key=lambda w: w['date'], reverse=True)
    nats = set()
    for w in ws:
        for n in w.get('nations') or []:
            nats.add(n.strip().lower())
    return '\n'.join(wire_item(w) for w in ws[:WIRE_STATIC]), len(ws), len(nats)


def ticker(son):
    items = []
    for s in designs(son)[:3]:
        items.append('<a href="#solution-%02d">Solution No. %02d: %s<span>%s</span></a>' % (s['no'], s['no'], a(s['title']), a(s.get('nation', ''))))
    ws = sorted(son.get('wire', []), key=lambda w: w.get('date', ''), reverse=True)[:TICK_WIRE]
    for w in ws:
        items.append('<a href="%s" target="_blank" rel="noopener noreferrer">%s<span>%s</span></a>' % (a(w['url']), a(w['title']), a(w.get('source', ''))))
    dup = ''.join(re.sub(r'^<a ', '<a tabindex="-1" ', x) for x in items)
    return ''.join(items) + '<span class="sn-tick__dup" aria-hidden="true">%s</span>' % dup


def rule_block():
    code = (PAGES / 'home-rule.html').read_text(encoding='utf-8').strip()
    return re.sub(r'^\s*<!--.*?-->\s*', '', code, count=1, flags=re.S)


def put(page, slot, body):
    key = '<!--pn:%s-->' % slot
    if key not in page:
        sys.exit('slot %s not found in %s' % (key, SRC.name))
    return page.replace(key, body)


def build_page(nat, son):
    page = SRC.read_text(encoding='utf-8')
    cards, n_sol = solution_cards(son)
    dl, n_deal = deals(son)
    wl, n_wire, n_wnat = wire(son)
    today = date.today().isoformat()
    page = page.replace('/*pn:version*/', VERSION).replace('/*pn:built*/', today)
    page = put(page, 'rule', rule_block())
    page = put(page, 'solutions', cards)
    page = put(page, 'deals', dl)
    page = put(page, 'wire', wl)
    page = put(page, 'tick', ticker(son))
    page = page.replace('<!--pn:n-sol-->', str(n_sol))
    page = put(page, 'n-deal', str(n_deal))
    page = page.replace('<!--pn:n-wire-->', str(n_wire))
    page = put(page, 'n-wnat', str(n_wnat))
    page = put(page, 'edition', long_date(son.get('updated') or today))
    try:
        page.encode('ascii')
    except UnicodeEncodeError as e:
        bad = page[e.start:e.start + 40]
        sys.exit('non-ASCII character in the built page near: %r (write it as an HTML entity in the source)' % bad)
    m = re.search(r'\bid\s*=\s*["\'](pn-[a-z0-9-]+)["\']', page, re.I)
    if not m or m.group(1) != 'pn-son':
        sys.exit('the first pn- id must be pn-son (found %s)' % (m.group(1) if m else 'none'))
    left = re.findall(r'<!--pn:[a-z-]+-->', page)
    if left:
        sys.exit('unfilled slots: %s' % ', '.join(left))
    OUT.write_text(page, encoding='utf-8')
    return {'solutions': n_sol, 'deals': n_deal, 'wire': n_wire, 'bytes': len(page.encode('ascii'))}


def main():
    nat, son = build_data()
    counts = std_counts(nat)
    print('data/solutions-by-nation.json: %d nations (%s)' % (
        len(nat['nations']), ', '.join('%s %d' % (s, counts[s]) for s in ORDER)))
    if '--data' in sys.argv:
        return
    info = build_page(nat, son)
    print('pages/state-of-nations.html v%s: %d Solutions, %d Deal Notes, %d on the wire, %d bytes' % (
        VERSION, info['solutions'], info['deals'], info['wire'], info['bytes']))


if __name__ == '__main__':
    main()
