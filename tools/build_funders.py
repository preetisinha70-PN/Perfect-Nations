#!/usr/bin/env python3
"""Build the one-file Perfect Nations For Funders page.

Writes pages/for-funders.html, the whole /for-funders/ page (root pn-fund). The page holds ONE Custom HTML
block or Elementor widget whose root is pn-fund; the Perfect Nations Live Pages plugin serves this file in
its place. Never edit the page file by hand: the words live in data/for-funders.json, the design in
tools/funders/style.css and the behaviour in tools/funders/script.js.

Every figure is counted or copied, never typed:
  - the open blueprints (pn-bp-<slug> keys in pages/manifest.json);
  - the deals on record and the instruments in the toolkit (data/capital-architecture.json);
  - the Solutions in the pipeline (data/deal-pipeline.json, built by tools/build_pipeline.py);
  - the fifteen sources of capital (the `funders` key of data/capital-architecture.json, shared with the
    Capital Architecture page);
  - the deals on the Capital Wire tape (data/ticker.json, read again live on every visit);
  - the Matches of the week (data/for-funders.json `match.items`), each built on a Solution of State of Nations.

Run from the repository root:
  python3 tools/build_pipeline.py      (when the Solutions change)
  python3 tools/build_funders.py
Then raise "pn-fund" in pages/manifest.json and open a pull request "For approval: For Funders vX.Y, ...".
"""
import html
import json
import re
import sys
from datetime import date, datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PAGES = ROOT / 'pages'
DATA = ROOT / 'data'
HERE = Path(__file__).resolve().parent / 'funders'
VERSION = '2.0'
REPO = 'preetisinha70-PN/perfect-nations'
RAW = 'https://raw.githubusercontent.com/%s/main/data/' % REPO
CDN = 'https://cdn.jsdelivr.net/gh/%s@main/data/' % REPO
ORDER = ['Food', 'Water', 'Shelter', 'Energy', 'Education', 'Health', 'Livelihood']
FINANCE = ['Development banks', 'Private investors', 'Corporate partners']
MONTHS = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October',
          'November', 'December']


def ent(s):
    return html.escape('' if s is None else str(s), quote=True).encode('ascii', 'xmlcharrefreplace').decode('ascii')


def link(u):
    if not re.match(r'^(https://|mailto:|#pf-)[^\s"\'<>()]+$', u or ''):
        sys.exit('not an https, mailto or #pf- link without quotes, brackets or spaces: %r' % u)
    return u


def load(name):
    return json.loads((DATA / name).read_text(encoding='utf-8'))


def js_json(obj):
    """JSON for a <script type="application/json"> block: ASCII only, and no "</" that could close the block."""
    return json.dumps(obj, ensure_ascii=True, separators=(',', ':')).replace('</', '<\\/')


def long_date(iso):
    d = date.fromisoformat(iso)
    return '%d %s %d' % (d.day, MONTHS[d.month - 1], d.year)


def ext(url, text, cls=''):
    return '<a%s href="%s" target="_blank" rel="noopener noreferrer">%s</a>' % (
        ' class="%s"' % cls if cls else '', ent(link(url)), ent(text))


# ---------------------------------------------------------------------------------------------------- figures
def figures(pipe):
    man = json.loads((PAGES / 'manifest.json').read_text(encoding='utf-8'))
    bps = sum(1 for k in man['pages'] if k.startswith('pn-bp-'))
    cap = load('capital-architecture.json')
    inst = sum(len(f['items']) for f in cap['index']['families'])
    rec = cap['record']
    return [
        (bps, 'nation blueprints', 'https://perfectnations.com/blueprints/'),
        (pipe['count']['lines'], 'Solutions in the pipeline', '#pf-pipe'),
        (rec['count'], 'deals on record across %d nations' % rec['nations'], 'https://perfectnations.com/capital-architecture/#pca-record'),
        (inst, 'instruments in the toolkit, each proved by a real deal', 'https://perfectnations.com/capital-architecture/#pca-index'),
    ]


def hero(doc, pipe):
    h = doc['hero']
    figs = ''.join('<li><a href="%s"><b data-n="%d">%s</b><span>%s</span></a></li>' % (ent(link(u)), n, '{:,}'.format(n), ent(t))
                   for n, t, u in figures(pipe))
    btns = ''.join('<a class="pf-btn%s" href="%s">%s</a>' % (' pf-btn--line' if b.get('line') else '', ent(link(b['url'])), ent(b['label']))
                   for b in h['buttons'])
    return (
        '<section class="pf-hero" aria-labelledby="pf-h1"><canvas class="pf-flow" aria-hidden="true"></canvas>'
        '<div class="pf-in pf-hero__g"><div class="pf-hero__t">'
        '<p class="pf-eb">%s</p><h1 class="pf-h1" id="pf-h1">%s<span class="pf-money">%s</span>%s</h1>'
        '<p class="pf-lead">%s</p><div class="pf-btns">%s</div>'
        '<p class="pf-src">%s %s</p></div>'
        '<ul class="pf-figs" aria-label="Perfect Nations in figures">%s</ul></div>'
        '<p class="pf-in pf-ll">%s</p></section>'
        % (ent(h['eyebrow']), ent(h['title_before']), ent(h['title_money']), ent(h['title_after']), ent(h['lead']), btns,
           ent(h['gap_note']), ext(h['gap_source']['url'], h['gap_source']['label']), figs, ent(h['living_line'])))


# ------------------------------------------------------------------------------------------------- the tape
def tape(doc):
    t = load('ticker.json')
    items = ''.join(
        '<li><a href="%s" target="_blank" rel="noopener noreferrer"><b>%s</b><em>%s</em><span>%s</span>%s</a></li>'
        % (ent(link(i['url'])), ent(i['nation']), ent(i['figure']), ent(i['line']),
           '<i>%s</i>' % ent(i['signal']) if i.get('signal') else '')
        for i in t['items'] if i.get('url') and i.get('figure'))
    w = doc['wire']
    return (
        '<section class="pf-tape" aria-label="%s" data-src="%sticker.json" data-mirror="%sticker.json">'
        '<div class="pf-tape__k"><b><span class="pf-pulse" aria-hidden="true"></span>%s</b>'
        '<small class="pf-tape__c">%s deals in %s nations</small></div>'
        '<div class="pf-tape__v"><ul class="pf-tape__l">%s</ul></div>'
        '<a class="pf-tape__a" href="%s">%s</a></section>'
        % (ent(w['label']), RAW, CDN, ent(w['label']), '{:,}'.format(t['count']['deals']), '{:,}'.format(t['count']['nations']),
           items, ent(link(w['link']['url'])), ent(w['link']['label'])))


# ------------------------------------------------------------------------------------------------ the match
def matches(doc, son, funders):
    sols = {d['no']: d for d in son['dispatches'] if d.get('kind') == 'design'}
    fid = {f['id']: f for f in funders['items']}
    out = []
    for m in doc['match']['items']:
        s = sols.get(m['solution'])
        if not s:
            sys.exit('Match No. %d: Solution No. %s is not a Solution of State of Nations' % (m['no'], m['solution']))
        for n in m['networks']:
            if n not in fid:
                sys.exit('Match No. %d: %r is not one of the sources of capital' % (m['no'], n))
        date.fromisoformat(m['week'])
        p = s.get('proof') or {}
        src = (s.get('sources') or [{}])[0]
        out.append({
            'no': m['no'], 'week': m['week'], 'weekText': 'Week of ' + long_date(m['week']),
            'nation': s['nation'], 'blueprint': s.get('blueprint', ''), 'standard': (s.get('standards') or [''])[0],
            'figure': s['figure'], 'caption': s['caption'], 'source': src.get('label', ''), 'sourceUrl': src.get('url', ''),
            'title': s['title'], 'advises': s['advises'], 'first': s.get('first', ''),
            'proof': {'name': p.get('name', ''), 'where': p.get('where', ''), 'year': p.get('year', ''), 'figure': p.get('figure', ''),
                      'label': p.get('label', ''), 'source': p.get('source', ''), 'url': p.get('url', '')},
            'solutionUrl': 'https://perfectnations.com/state-of-nations/#solution-%02d' % s['no'],
            'funder': m['funder'], 'why': m['why'],
            'networks': [{'id': n, 'name': fid[n]['name']} for n in m['networks']],
        })
        for u in (out[-1]['sourceUrl'], out[-1]['proof']['url'], out[-1]['solutionUrl']):
            if u:
                link(u)
    out.sort(key=lambda x: x['week'], reverse=True)
    return out


def match_card(m, answer):
    p = m['proof']
    proof = ''
    if p.get('name'):
        proof = ('<div class="pf-m__row"><h4>The proof</h4><p><b>%s</b>, %s %s: <em class="pf-gold">%s</em> %s. %s</p></div>'
                 % (ent(p['name']), ent(p['where']), ent(p['year']), ent(p['figure']), ent(p['label']),
                    ext(p['url'], p['source']) if p.get('url') else ''))
    chips = ''.join('<a class="pf-chip" href="#pf-who-%s">%s</a>' % (ent(n['id']), ent(n['name'])) for n in m['networks'])
    return (
        '<article class="pf-m" data-no="%d"><div class="pf-m__l">'
        '<p class="pf-m__k"><b>Match No. %d</b><span>%s</span></p>'
        '<h3 class="pf-m__n">%s</h3><p class="pf-m__s">%s</p>'
        '<p class="pf-m__f">%s</p><p class="pf-m__c">%s. %s</p></div>'
        '<div class="pf-m__r">'
        '<div class="pf-m__row"><h4>The Solution</h4><p class="pf-m__t">%s</p><p>%s</p></div>%s'
        '<div class="pf-m__row pf-m__fit"><h4>The funder that fits</h4><p class="pf-m__t">%s</p><p>%s</p><p class="pf-chips">%s</p></div>'
        '<div class="pf-btns"><a class="pf-btn" href="%s">%s</a><a class="pf-btn pf-btn--line" href="%s">Read the Solution</a></div>'
        '</div></article>'
        % (m['no'], m['no'], ent(m['weekText']), ent(m['nation']), ent(m['standard']), ent(m['figure']), ent(m['caption']),
           ext(m['sourceUrl'], m['source']) if m['sourceUrl'] else '', ent(m['title']), ent(m['advises']), proof,
           ent(m['funder']), ent(m['why']), chips, ent(link(answer['url'])), ent(answer['label']), ent(link(m['solutionUrl']))))


def match(doc, son, funders, today):
    mm = doc['match']
    items = matches(doc, son, funders)
    live = [m for m in items if m['week'] <= today]
    cur = live[0] if live else items[-1]
    earlier = [m for m in items if m['week'] < cur['week']]
    rail = ''.join('<li><button type="button" data-no="%d"><b>No. %d</b><span>%s</span><em>%s</em></button></li>'
                   % (m['no'], m['no'], ent(m['nation']), ent(m['weekText'])) for m in earlier)
    return (
        '<section class="pf-band pf-match" id="pf-match" aria-labelledby="pf-mh"><div class="pf-in">'
        '<div class="pf-head"><p class="pf-eb">%s</p><h2 class="pf-h2" id="pf-mh">%s</h2><p class="pf-lead">%s</p></div>'
        '<div class="pf-m__slot">%s</div>'
        '<div class="pf-m__more"%s><p>Earlier Matches</p><ul class="pf-m__rail">%s</ul></div>'
        '<p class="pf-note">%s</p></div>'
        '<script type="application/json" class="pf-matches">%s</script>'
        '<script type="application/json" class="pf-answer">%s</script></section>'
        % (ent(mm['eyebrow']), ent(mm['title']), ent(mm['lead']), match_card(cur, mm['answer']),
           '' if rail else ' hidden', rail, ent(mm['note']), js_json(items), js_json(mm['answer'])))


# --------------------------------------------------------------------------------------------- the pipeline
def pipeline(doc, pipe):
    p = doc['pipeline']
    c = pipe['count']
    cols = FINANCE + ['']
    names = FINANCE + [p['lead_column']]
    short = ['Dev. banks', 'Private', 'Corporate', 'Lead']
    top = max(c['matrix'][s][f] for s in ORDER for f in cols) or 1
    head = ''.join('<th scope="col"><span class="pf-l">%s</span><span class="pf-s">%s</span></th>' % (ent(n), ent(sh)) for n, sh in zip(names, short))
    rows = ''
    for s in ORDER:
        cells = ''.join(
            '<td><button type="button" class="pf-cell%s" data-std="%s" data-fin="%s" style="--a:%.2f" aria-label="%d %s Solutions, %s">%d</button></td>'
            % (' is-lo' if 0.08 + 0.82 * c['matrix'][s][f] / top < 0.55 else '', ent(s), ent(f or 'lead'), 0.08 + 0.82 * c['matrix'][s][f] / top,
               c['matrix'][s][f], ent(s), ent(n), c['matrix'][s][f])
            for f, n in zip(cols, names))
        rows += '<tr><th scope="row">%s<small>%d</small></th>%s</tr>' % (ent(s), c['by_standard'][s], cells)
    totals = ''.join('<td><b>%d</b></td>' % (c['by_finance'][f] if f else c['by_finance']['Lead and State of Nations Solutions']) for f in cols)
    matrix = ('<table class="pf-mx"><caption>%s</caption><thead><tr><td></td>%s</tr></thead><tbody>%s</tbody>'
              '<tfoot><tr><th scope="row">All<small>%d</small></th>%s</tr></tfoot></table>'
              % (ent(p['matrix_title']), head, rows, c['lines'], totals))

    def chips(name, values, label):
        return ('<div class="pf-f" role="group" aria-label="%s"><span>%s</span>%s</div>'
                % (ent(label), ent(label), ''.join('<button type="button" class="pf-fc%s" data-k="%s" data-v="%s">%s</button>'
                                                    % (' is-on' if v == '' else '', name, ent(v), ent(t)) for v, t in values)))
    filters = (chips('std', [('', 'All')] + [(s, s) for s in ORDER], 'Standard')
               + chips('fin', [('', 'All')] + [(f, f) for f in FINANCE] + [('lead', p['lead_column'])], 'Funder')
               + chips('reg', [('', 'All')] + [(r, '%s %d' % (r, n)) for r, n in c['by_region'].items()], 'Region'))
    feat = [x for x in pipe['lines'] if x['kind'] == 'solution'][:6]
    cards = ''.join(line_card(x) for x in feat)
    return (
        '<section class="pf-band pf-pipe" id="pf-pipe" aria-labelledby="pf-ph" data-src="%sdeal-pipeline.json" data-mirror="%sdeal-pipeline.json">'
        '<div class="pf-in"><div class="pf-head"><p class="pf-eb">%s</p>'
        '<h2 class="pf-h2" id="pf-ph"><span class="pf-big">%s</span> Solutions across %d nations</h2><p class="pf-lead">%s</p>'
        '<p class="pf-stage">%s</p></div>'
        '<div class="pf-pipe__g"><div class="pf-pipe__mx">%s</div>'
        '<div class="pf-pipe__ls"><div class="pf-fs">%s<label class="pf-q"><span>Nation</span><input type="search" placeholder="Search a nation" autocomplete="off"></label></div>'
        '<p class="pf-count" aria-live="polite">The newest Solutions of State of Nations. Choose a filter to open all %s.</p>'
        '<ul class="pf-lines">%s</ul>'
        '<div class="pf-btns"><button type="button" class="pf-btn pf-btn--line pf-moreb" hidden>Show more</button>'
        '<a class="pf-btn" href="%s">%s</a></div></div></div></div></section>'
        % (RAW, CDN, ent(p['eyebrow']), '{:,}'.format(c['lines']), c['nations'], ent(p['lead']), ent(p['stage']), matrix, filters,
           '{:,}'.format(c['lines']), cards, ent(link(p['request']['url'])), ent(p['request']['label'])))


def line_card(x):
    fin = x.get('finance') or ('Solution No. %d' % x['no'] if x.get('no') else 'Lead Solution')
    return ('<li class="pf-line"><p class="pf-line__k"><b>%s</b><span>%s</span><span>%s</span></p>'
            '<h3><a href="%s">%s</a></h3><p>%s</p></li>'
            % (ent(x['nation']), ent(x['standard']), ent(fin), ent(link(x['url'])), ent(x['title']), ent(x['challenge'])))


# ------------------------------------------------------------------------------------------ how it works
def how(doc):
    h = doc['how']
    cards = ''.join('<li class="pf-card"><span class="pf-card__n">%s</span><h3>%s</h3><p>%s</p></li>'
                    % (ent(i['n']), ent(i['name']), ent(i['line'])) for i in h['offer'])
    steps = ''.join('<li class="pf-step"><span class="pf-step__n">%02d</span><h3>%s</h3><p>%s</p></li>'
                    % (i, ent(s['name']), ent(s['line'])) for i, s in enumerate(h['steps'], 1))
    return ('<section class="pf-band pf-how" aria-labelledby="pf-hh"><div class="pf-in">'
            '<div class="pf-head"><p class="pf-eb">%s</p><h2 class="pf-h2" id="pf-hh">%s</h2></div>'
            '<ul class="pf-cards">%s</ul><ol class="pf-steps">%s</ol></div></section>'
            % (ent(h['eyebrow']), ent(h['title']), cards, steps))


# ------------------------------------------------------------------------------------- who it serves
def who(doc, funders):
    w = doc['who']
    cols = ''
    for fam in funders['families']:
        items = [it for it in funders['items'] if it['family'] == fam['id']]
        rows = ''.join(
            '<li id="pf-who-%s"><div><b>%s</b><span>%s</span></div>%s<p><em class="pf-gold">%s</em><span>%s %s</span></p></li>'
            % (ent(it['id']), ent(it['name']), ent(it['kind']), '<small>%s</small>' % ent(it['names']) if it.get('names') else '',
               ent(it['figure']), ent(it['label']), ext(it['url'], it['source']))
            for it in items)
        cols += ('<div class="pf-fam"><div class="pf-fam__h"><b>%s</b><span>%s</span></div><ul>%s</ul></div>'
                 % (ent(fam['name']), ent(fam['line']), rows))
    return ('<section class="pf-band pf-who" id="pf-who" aria-labelledby="pf-wh"><div class="pf-in">'
            '<div class="pf-head"><p class="pf-eb">%s</p><h2 class="pf-h2" id="pf-wh">%s</h2><p class="pf-lead">%s</p></div>'
            '<div class="pf-fams">%s</div>'
            '<p class="pf-note">%s <a href="%s">%s</a></p></div></section>'
            % (ent(w['eyebrow']), ent(w['title']), ent(w['lead']), cols, ent(funders['note']),
               ent(link(w['link']['url'])), ent(w['link']['label'])))


def close(doc):
    c = doc['close']
    btns = ''.join('<a class="pf-btn%s" href="%s">%s</a>' % (' pf-btn--line' if b.get('line') else '', ent(link(b['url'])), ent(b['label']))
                   for b in c['buttons'])
    return ('<section class="pf-band pf-close" aria-labelledby="pf-ch"><div class="pf-in">'
            '<p class="pf-eb">%s</p><h2 class="pf-h2" id="pf-ch">%s</h2><p class="pf-lead">%s</p>'
            '<div class="pf-btns">%s</div><p class="pf-note">%s</p></div></section>'
            % (ent(c['eyebrow']), ent(c['title']), ent(c['lead']), btns, ent(c['note'])))


def main():
    doc = json.loads((DATA / 'for-funders.json').read_text(encoding='utf-8'))
    pipe = load('deal-pipeline.json')
    son = load('state-of-nations.json')
    funders = load('capital-architecture.json')['funders']
    css = (HERE / 'style.css').read_text(encoding='utf-8').strip()
    js = (HERE / 'script.js').read_text(encoding='utf-8').strip()
    rule = (PAGES / 'home-rule.html').read_text(encoding='utf-8').strip()
    rule = re.sub(r'^\s*<!--.*?-->\s*', '', rule, count=1, flags=re.S)
    today = datetime.now(timezone.utc).strftime('%Y-%m-%d')
    head = '''<!-- ===========================================================================
PERFECT NATIONS - FOR FUNDERS - THE WHOLE PAGE IN ONE FILE - v%s - %s
The /for-funders/ page holds ONE Custom HTML block whose root is pn-fund. The Perfect Nations Live Pages
plugin serves this file from GitHub in its place, so the page changes only through GitHub. Never edit this
file by hand: edit data/for-funders.json (words), tools/funders/style.css (design) or tools/funders/script.js
(behaviour), run python3 tools/build_funders.py, and open a pull request.
v1.0: the page for funders as clients (the Steward-General, 21 Nov 2026): what funders receive (the deal
pipeline, Match of the week, introductions), how a deal is checked (Ledger, Living Line, Design, Capital),
who it serves, and one action: request the deal pipeline. The hero figures are counted from the manifest
and data/capital-architecture.json. Institutions are named for reference only, never as partners.
v1.1: Request the deal pipeline opens the contact form at Fund a nation (?about=funders), in place of an
email (the Steward-General, 22 Nov 2026).
v2.0: made for funders to act on (the Steward-General, 24 Nov 2026: "make it much more attractive to potential
funders"). 01 Earthrise hero over a field of moving capital: Finance the $4 trillion gap (Compromiso de Sevilla),
four counted figures. A live Capital Wire tape (data/ticker.json, read on every visit). 02 Match of the week: one
nation, its gap, the Solution, the proof and the funder that fits; the page shows the Match of the current week
from data/for-funders.json, with the earlier ones a tap away. 03 The deal pipeline: every Solution of the 195
blueprints in data/deal-pipeline.json (tools/build_pipeline.py), counted by standard and kind of funder in a
heat map; tap a cell or a filter and the whole pipeline loads, to read by standard, funder, region or nation.
04 How it works: three ways in, four checks. 05 Who it serves: the fifteen sources of capital of Capital
Architecture in three families, each with its sourced figure. 06 The close. Phones have their own layout.
=========================================================================== -->
''' % (VERSION, today)
    body = '\n'.join([
        '<style>\n%s\n</style>' % css,
        '<div id="pn-fund" data-version="%s">' % VERSION,
        rule,
        hero(doc, pipe), tape(doc), match(doc, son, funders, today), pipeline(doc, pipe), how(doc), who(doc, funders),
        '<div class="pn-rule" aria-hidden="true"></div>',
        close(doc),
        '</div>',
        '<script>\n%s\n</script>' % js,
    ])
    page = head + body + '\n'
    first = re.search(r'\bid\s*=\s*["\'](pn-[a-z0-9-]+)["\']', page, re.I)
    if not first or first.group(1) != 'pn-fund':
        sys.exit('the first pn- id must be pn-fund, found %s' % (first.group(1) if first else None))
    bad = [(i, c) for i, c in enumerate(page) if ord(c) > 126]
    if bad:
        sys.exit('non-ASCII characters in the page: %r' % [(i, page[max(0, i - 30):i + 5]) for i, _ in bad[:5]])
    (PAGES / 'for-funders.html').write_text(page, encoding='utf-8')
    print('pages/for-funders.html: %d characters, %d Solutions in the pipeline, %d Matches'
          % (len(page), pipe['count']['lines'], len(doc['match']['items'])))


if __name__ == '__main__':
    main()
