#!/usr/bin/env python3
"""Build the State of Nations page (perfectnations.org/state-of-nations/) and its nation data.

The page is about Solutions: how innovative financing for development (FfD) and super intelligence
(SI) close the gap to the seven basic standards of living, nation by nation.
v7.2: What Perfect Nations advises, in place of how FfD and SI solve it (the Steward-General, 9 Nov 2026).
  Each Solution reads as a bank's advice to a client: the challenge, then what Perfect Nations advises
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
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / 'data'
PAGES = ROOT / 'pages'
SRC = ROOT / 'src' / 'state-of-nations.html'
OUT = PAGES / 'state-of-nations.html'
NATION_DATA = DATA / 'solutions-by-nation.json'
sys.path.insert(0, str(ROOT / 'tools'))

VERSION = '7.2'
ORDER = ['Food', 'Water', 'Shelter', 'Energy', 'Education', 'Health', 'Livelihood']
MONTHS = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September',
          'October', 'November', 'December']
WIRE_STATIC = 12     # wire items written into the page (the live file replaces them)
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
        'head': 'Pay before the harvest fails.',
        'name': 'Sovereign drought insurance',
        'ffd': 'Parametric cover pays on measured rainfall, so food reaches families within weeks of a failed season, without waiting for an appeal.',
        'proof': {'where': 'Malawi', 'year': '2024', 'figure': '$11.2M',
                  'label': 'paid out after the El Niño drought, for food aid to about 235,000 households',
                  'source': 'African Development Bank, August 2024',
                  'url': 'https://www.afdb.org/en/news-and-events/press-releases/african-development-bank-group-and-african-risk-capacity-group-issue-112-million-insurance-payout-government-malawi-73593'},
        'si': 'SI reads rainfall, harvests and food prices district by district, sets the trigger and prices the cover before the season begins.',
        'advises': 'Nations where food is furthest from reach should buy drought insurance that pays on measured rainfall, so that food reaches families within weeks of a failed season, with the trigger and the price of the cover set district by district before the season begins.',
        'first': 'sovereign drought insurance',
    },
    'Water': {
        'head': 'Turn cheaper debt into safe water.',
        'name': 'Debt-for-climate-resilience swap',
        'ffd': 'Guarantees replace costly debt with cheaper debt, and the savings are committed to water and sewerage.',
        'lib': 'debt-for-climate',
        'si': 'SI maps every household without safe water at home, prices each connection, and follows the savings into every main and treatment plant.',
        'advises': 'Nations where water is furthest from reach should swap costly debt for cheaper, guaranteed debt and commit the savings to water and sewerage, then follow the savings into every household connection, main and treatment plant.',
        'first': 'a debt-for-resilience swap bound to water',
    },
    'Shelter': {
        'head': 'Ring-fence bond money for homes and sanitation.',
        'name': 'Social bond',
        'ffd': 'The proceeds can be spent only on eligible homes, toilets and sewers, reported to investors every year.',
        'lib': 'social-bond',
        'si': 'SI finds the homes without a safe toilet, groups them into programmes investors can finance, and reports each unit delivered.',
        'advises': 'Nations where shelter is furthest from reach should issue a social bond whose proceeds can be spent only on eligible homes, toilets and sewers, and report each unit delivered to investors every year.',
        'first': 'a social bond for homes and sanitation',
    },
    'Energy': {
        'head': 'Finance clean power and clean cooking at national scale.',
        'name': 'Sovereign green bond',
        'ffd': 'Bond money ring-fenced for clean energy under a published framework, with every allocation reported to investors.',
        'lib': 'green-bond',
        'si': 'SI counts the households still cooking with wood, charcoal or kerosene, prices the switch per home, and tracks every project the bond pays for.',
        'advises': 'Nations where energy is furthest from reach should issue a sovereign green bond ring-fenced for clean power and clean cooking, price the switch for every household still cooking with wood, charcoal or kerosene, and report every project the bond pays for.',
        'first': 'a sovereign green bond for clean power and cooking',
    },
    'Education': {
        'head': 'Pay for learning, not only for classrooms.',
        'name': 'Program-for-Results',
        'ffd': 'Each tranche of the loan is released only when pupils reach an agreed learning level, verified independently.',
        'lib': 'program-for-results',
        'si': 'SI tracks reading levels school by school, sets the targets that release each tranche, and flags the schools falling behind.',
        'advises': 'Nations where education is furthest from reach should borrow on a Program-for-Results basis, releasing each tranche only when pupils reach an agreed learning level, verified independently, and track reading levels school by school.',
        'first': 'a Program-for-Results paid on learning',
    },
    'Health': {
        'head': 'Let lower debt costs pay for care.',
        'name': 'Debt-for-health guarantee',
        'ffd': 'A development bank guarantee cuts the cost of existing debt, and the savings are bound to the health system before they can be spent elsewhere.',
        'proof': {'where': 'Barbados', 'year': '2026', 'figure': '$175M',
                  'label': 'IDB guarantee, 20 years; about US$160 million of the savings for health care',
                  'source': 'Inter-American Development Bank, project BA-U0003',
                  'url': 'https://www.iadb.org/en/project/BA-U0003'},
        'si': 'SI prices the essential services each citizen lacks, finds the costly debt to refinance, and follows every saving into clinics and care.',
        'advises': 'Nations where health is furthest from reach should refinance costly debt behind a development bank guarantee and bind the savings to the health system before they can be spent elsewhere, then follow every saving into clinics and care.',
        'first': 'a debt-for-health guarantee',
    },
    'Livelihood': {
        'head': 'Let local banks lend to the enterprises that hire.',
        'name': 'Small-business credit guarantee',
        'ffd': 'A facility guarantees most of each small-business loan, so local banks lend to firms they would otherwise turn away.',
        'lib': 'sme-credit-guarantee',
        'si': 'SI matches enterprises to lenders, prices the risk the guarantee must carry, and counts the jobs each loan creates.',
        'advises': 'Nations where livelihoods are furthest from reach should set up a facility that guarantees most of each small-business loan, so that local banks lend to the firms they would otherwise turn away, and count the jobs each loan creates.',
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


def slug_std(s):
    return std_name(s).lower()


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
            'solutions': sorted([s['no'] for s in solutions if s.get('nation') == name], reverse=True),
        })
    rows.sort(key=lambda r: r['name'].replace('ô', 'o').lower())
    return rows


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
def std_chips(stds):
    if not stds:
        return '<ul class="sn-std"><li class="is-all">All seven, through the budget</li></ul>'
    return '<ul class="sn-std">%s</ul>' % ''.join('<li>%s</li>' % a(s) for s in stds)


def solution_card(s):
    no = int(s['no'])
    url = s.get('url', '')
    href = url if url.startswith('https://') else '#solution-%02d' % no
    readable = url.startswith('https://') or bool(s.get('body'))
    title = '<a href="%s">%s</a>' % (a(href), a(s['title'])) if readable else a(s['title'])
    parts = [
        '<li class="sn-c" data-no="%d" data-std="%s">' % (no, a(';'.join(s.get('standards', [])))),
        '<div class="sn-c__k"><b>Solution No. %02d</b><span>%s</span><time datetime="%s">%s</time></div>' % (
            no, a(s.get('nation', '')), a(s['date']), a(short_date(s['date']))),
        '<h3>%s</h3>' % title,
        std_chips(s.get('standards', [])),
    ]
    rows = [(t, s.get(k)) for t, k in (('The challenge', 'challenge'), ('What Perfect Nations advises', 'advises')) if s.get(k)]
    if rows:
        parts.append('<dl class="sn-c__x">%s</dl>' % ''.join('<div><dt>%s</dt><dd>%s</dd></div>' % (t, a(w)) for t, w in rows))
    elif s.get('standfirst'):
        parts.append('<p class="sn-c__x">%s</p>' % a(s['standfirst']))
    if s.get('figure'):
        parts.append('<p class="sn-c__f"><b>%s</b><span>%s</span></p>' % (a(s['figure']), a(s.get('caption', ''))))
    parts.append('<span class="sn-c__go">%s</span></li>' % ('Read the solution' if readable else 'In press'))
    return ''.join(parts)


def solution_cards(son):
    ds = sorted(son.get('dispatches', []), key=lambda s: (s['date'], s['no']), reverse=True)
    return '\n'.join(solution_card(s) for s in ds), len(ds)


def std_counts(nat):
    c = {s: 0 for s in ORDER}
    for n in nat['nations']:
        c[n['standard']] += 1
    return c


def nation_row(n, pb):
    w = n.get('at_work')
    if w:
        amt = '<b class="%s">%s</b>' % ('sn-m' if w.get('money') else 'sn-q', a(w['amount'])) if w.get('amount') else ''
        work = ('<p class="sn-r__w"><span class="sn-r__l">At work</span><a href="%s" target="_blank" rel="noopener noreferrer">%s</a>%s</p>'
                % (a(w['url']), a(w['name']), amt))
    else:
        work = ('<p class="sn-r__w is-open"><span class="sn-r__l">First move</span>%s</p>'
                % a(pb[n['standard']]['first'][0].upper() + pb[n['standard']]['first'][1:]))
    src = n.get('source') or {}
    cite = ('<a class="sn-src" href="%s" target="_blank" rel="noopener noreferrer">%s</a>' % (a(src['url']), a(src['label']))
            if str(src.get('url', '')).startswith('https://') else '')
    sols = ''.join('<a class="sn-r__s" href="#solution-%02d">Solution No. %02d</a>' % (x, x) for x in n.get('solutions', []))
    return ''.join([
        '<li class="sn-r" data-slug="%s">' % a(n['slug']),
        '<div class="sn-r__h"><a class="sn-r__n" href="%s" target="_blank" rel="noopener noreferrer">%s</a><b class="sn-r__g">%s</b></div>' % (
            a(n['url']), a(n['name']), a(n['gap'])),
        '<p class="sn-r__t">%s %s</p>' % (a(n['gap_text']), cite),
        work, sols, '</li>'])


def finder(nat):
    pb = {p['standard']: p for p in nat['standards']}
    counts = std_counts(nat)
    first = max(ORDER, key=lambda s: (counts[s], -ORDER.index(s)))
    tabs, panels = [], []
    for s in ORDER:
        k = slug_std(s)
        on = s == first
        tabs.append('<button type="button" role="tab" class="sn-tab%s" id="sn-t-%s" aria-controls="sn-p-%s" aria-selected="%s" data-std="%s">%s<span>%d</span></button>'
                    % (' is-on' if on else '', k, k, 'true' if on else 'false', a(s), a(s), counts[s]))
        p = pb[s]
        pr = p['proof']
        proof = ('<p class="sn-proof"><span>Proven</span>%s, %s <b>%s</b> %s <a href="%s" target="_blank" rel="noopener noreferrer">%s</a></p>'
                 % (a(pr['where']), a(pr['year']), a(pr['figure']), a(pr['label']), a(pr['url']), a(pr['source'])))
        rows = [n for n in nat['nations'] if n['standard'] == s]
        if rows:
            lead = '<p class="sn-pcount"><b>%d</b> %s where %s is the standard furthest from reach</p>' % (
                len(rows), 'nation' if len(rows) == 1 else 'nations', a(s.lower()))
            body = '<ol class="sn-rows">%s</ol>' % ''.join(nation_row(n, pb) for n in rows)
        else:
            lead = ('<p class="sn-pcount">In no open blueprint is %s the standard furthest from reach. '
                    '<a href="#solution-10">Solution No. 10</a> shows how Barbados pays for it.</p>' % a(s.lower()))
            body = '<ol class="sn-rows"></ol>'
        panels.append(''.join([
            '<div class="sn-p" id="sn-p-%s" role="tabpanel" aria-labelledby="sn-t-%s" data-std="%s"%s>' % (k, k, a(s), '' if on else ' hidden'),
            '<div class="sn-pb">',
            '<div class="sn-pb__h"><p class="sn-k">%s</p><h3>%s</h3></div>' % (a(s), a(p['head'])),
            '<div class="sn-pb__c sn-pb__adv"><p class="sn-tag">What Perfect Nations advises</p><p>%s</p></div>' % a(p['advises']),
            '<div class="sn-pb__c sn-pb__deal"><p class="sn-tag">The deal &middot; %s</p>%s</div>' % (a(p['name']), proof),
            '</div>', lead, body,
            '<button type="button" class="sn-more" hidden>Show all</button>',
            '</div>']))
    return '\n'.join(tabs), '\n'.join(panels), first


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
    ds = sorted(son.get('dispatches', []), key=lambda s: (s['date'], s['no']), reverse=True)[:3]
    for s in ds:
        href = s['url'] if str(s.get('url', '')).startswith('https://') else '#solution-%02d' % s['no']
        items.append('<a href="%s">Solution No. %02d: %s<span>%s</span></a>' % (a(href), s['no'], a(s['title']), a(s.get('nation', ''))))
    ws = sorted(son.get('wire', []), key=lambda w: w.get('date', ''), reverse=True)[:8]
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
    wl, n_wire, n_wnat = wire(son)
    tabs, panels, first = finder(nat)
    today = date.today().isoformat()
    page = page.replace('/*pn:version*/', VERSION).replace('/*pn:built*/', today)
    page = put(page, 'rule', rule_block())
    page = put(page, 'solutions', cards)
    page = put(page, 'tabs', tabs)
    page = put(page, 'panels', panels)
    page = put(page, 'wire', wl)
    page = put(page, 'tick', ticker(son))
    page = put(page, 'n-sol', str(n_sol))
    page = put(page, 'n-nat', str(len(nat['nations'])))
    page = put(page, 'n-wire', str(n_wire))
    page = put(page, 'n-wnat', str(n_wnat))
    page = put(page, 'edition', long_date(son.get('updated') or today))
    page = put(page, 'first-std', first)
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
    return {'solutions': n_sol, 'nations': len(nat['nations']), 'wire': n_wire, 'bytes': len(page.encode('ascii'))}


def main():
    nat, son = build_data()
    counts = std_counts(nat)
    print('data/solutions-by-nation.json: %d nations (%s)' % (
        len(nat['nations']), ', '.join('%s %d' % (s, counts[s]) for s in ORDER)))
    if '--data' in sys.argv:
        return
    info = build_page(nat, son)
    print('pages/state-of-nations.html v%s: %d Solutions, %d nations, %d on the wire, %d bytes' % (
        VERSION, info['solutions'], info['nations'], info['wire'], info['bytes']))


if __name__ == '__main__':
    main()
