#!/usr/bin/env python3
"""Build the one-file Perfect Nations Capital Architecture page and refresh its live record.

Writes two files:
  pages/capital-architecture.html  the whole /capital-architecture/ page (root pn-arch, page 8549).
                                   The page holds ONE Elementor Custom HTML widget whose root is
                                   pn-arch; the Perfect Nations Live Pages plugin serves this file in
                                   its place. Never edit this file by hand.
  data/capital-architecture.json   the page's content (hero, the five, the toolkit, the close) and its
                                   live record. The build recounts the record from every open
                                   blueprint; the page reads the record on every visit, so the counts
                                   follow the Nation Stewards without a new page version.

The design lives in tools/capital/style.css and tools/capital/script.js; the words and figures live
in data/capital-architecture.json.

Fewer words (the Steward-General, 9 Nov 2026): each section shows one headline and one line, then its
cards. The build shows the first sentence of a section's lead; the rest of the toolkit lead, and the
method note under the record, sit one click away in a Read more disclosure (class pca-rm). The hero
shows the first sentence of hero.lead only. The gold line between the record and the close comes from the
homepage (pages/home-rule.html), so every page shares one section break.

What counts as on record: every line of capital.register in data/<slug>.json, for every open
blueprint (a pn-bp-<slug> key in pages/manifest.json). Counts, never sums: the amounts are in many
currencies.

Run from the repository root:
  python3 tools/build_capital.py            refresh the record and build the page
  python3 tools/build_capital.py --record   refresh the record in data/capital-architecture.json only
Then, for a page change: raise "pn-arch" in pages/manifest.json and open a pull request
"For approval: Capital Architecture vX.Y, ...". A record refresh alone may go straight to main (it is
data), after the checks.
"""
import html
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PAGES = ROOT / 'pages'
DATA = ROOT / 'data'
HERE = Path(__file__).resolve().parent / 'capital'
VERSION = '5.4'
NOT_NATIONS = {'state-of-nations', 'ticker', 'blueprints', 'capital-architecture'}

# Who carries each line on record (the register's cat field), in the words a visitor reads.
CATS = {
    'multi': ('Multilateral', 'World Bank, IMF and peers'),
    'govt': ('Issued by the nation', 'Its own bonds and programmes'),
    'regional': ('Regional', 'Regional banks and funds'),
    'private': ('Private', 'Investors, banks and funds'),
    'bilat': ('Bilateral', 'Partner governments'),
    'impact': ('Impact', 'Impact investors, green banks'),
    'humanitarian': ('Humanitarian', 'Appeals and relief funds'),
}


def plain(s):
    return '' if s is None else str(s)


def ent(s):
    """Escape for HTML and write every non-ASCII character as an entity (the page stays ASCII)."""
    return html.escape(plain(s), quote=True).encode('ascii', 'xmlcharrefreplace').decode('ascii')


def https(u):
    u = plain(u)
    if not re.match(r'^https://[^\s"\'<>()]+$', u):
        sys.exit('not an https link without quotes, brackets or spaces: %r' % u)
    return u


def open_blueprints():
    """slug -> blueprint URL, for every pn-bp-<slug> key in the manifest."""
    man = json.loads((PAGES / 'manifest.json').read_text(encoding='utf-8'))
    out = {}
    for key, v in man['pages'].items():
        m = re.match(r'^pn-bp-([a-z-]+)$', key)
        f = re.match(r'^pages/blueprint-([a-z-]+)\.html$', v.get('file', ''))
        if m and f and v.get('url', '').startswith('https://perfectnations.com/blueprints/'):
            out[f.group(1)] = v['url']
    return out


def count_record(doc):
    bps = open_blueprints()
    cats, rows = {}, []
    for p in sorted(DATA.glob('*.json')):
        slug = p.stem
        if slug in NOT_NATIONS or slug not in bps:
            continue
        d = json.loads(p.read_text(encoding='utf-8'))
        reg = (d.get('capital') or {}).get('register') or []
        if not reg:
            continue
        for r in reg:
            c = r.get('cat') if r.get('cat') in CATS else 'multi'
            cats[c] = cats.get(c, 0) + 1
        top = reg[0]
        rows.append({
            'slug': slug, 'name': plain(d.get('nation') or slug.replace('-', ' ').title()),
            'n': len(reg), 'url': bps[slug],
            'top': plain(top.get('name')), 'amount': plain(top.get('amount')), 'money': bool(top.get('money')),
        })
    rows.sort(key=lambda r: (-r['n'], r['name']))
    by = [{'cat': c, 'label': CATS[c][0], 'sub': CATS[c][1], 'n': n}
          for c, n in sorted(cats.items(), key=lambda kv: -kv[1])]
    rec = doc['record']
    rec.update({
        'as_of': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%MZ'),
        'count': sum(r['n'] for r in rows), 'nations': len(rows), 'by': by, 'list': rows,
    })
    return doc


def wreath():
    """The laurels of the logo, drawn alone in one gold: the mark of Capital Architecture (the Steward-General,
    8 Nov 2026: the laurels stand for capital from every source, lifting the cup). The shape and its clip come
    from the logo kit (pages/home-logo-kit.html), renamed so they never meet the kit's own ids. Never put the
    word "laurel" in a class name on this site: the header replaces any drawing so named with the cup."""
    src = (PAGES / 'home-logo-kit.html').read_text(encoding='utf-8')
    shape = re.search(r'<path id="pnk-cl"[^>]*/>', src, re.S)
    clip = re.search(r'<clipPath id="pnk-lc".*?</clipPath>', src, re.S)
    if not shape or not clip:
        sys.exit('the laurels (pnk-cl, pnk-lc) were not found in pages/home-logo-kit.html')
    defs = ('<svg class="pca-defs" width="0" height="0" aria-hidden="true" focusable="false"><defs>%s%s</defs></svg>'
            % (shape.group(0).replace('id="pnk-cl"', 'id="pca-k-cl"'), clip.group(0).replace('id="pnk-lc"', 'id="pca-k-lc"')))
    art = ('<svg class="pca-wreath" viewBox="10 63.75 491 491" aria-hidden="true" focusable="false">'
           '<use href="#pca-k-cl" clip-path="url(#pca-k-lc)"/></svg>')
    return defs, art


def one_line(text):
    """A section's one line: its first sentence, and the rest (if any) for the Read more beneath it."""
    t = plain(text).strip()
    m = re.match(r'^(.+?[.!?])\s+(?=[A-Z\u2018\u201c])(.+)$', t, re.S)
    return (m.group(1), m.group(2)) if m else (t, '')


def read_more(paras):
    """The detail one click away: a native disclosure under a section's one line (paragraphs already escaped)."""
    paras = [p for p in paras if p]
    if not paras:
        return ''
    return ('<details class="pca-rm"><summary>Read more</summary><div class="pca-rm__b">%s</div></details>'
            % ''.join('<p>%s</p>' % p for p in paras))


def fig_html(item, cls):
    return '<span class="%s">%s</span>' % (cls, ent(item['figure'])) if item.get('figure') else ''


def hero(doc, n_inst, n_fam):
    h = doc['hero']
    five = doc['five']
    tiles = []
    for i, t in enumerate(five['items']):
        src = '<a href="%s" target="_blank" rel="noopener">%s</a>' % (ent(https(t['url'])), ent(t['source']))
        more = ''
        if t.get('more'):
            more = ' &#183; <a href="%s">How they work</a>' % ent(https(t['more']))
        where = ent(t['where']) + (' &#183; ' + ent(t['year']) if t.get('year') else '')
        src = '<span>%s</span><span>%s%s</span>' % (where, src, more)
        tiles.append(
            '<li style="--i:%d"><article class="pca-t%s">'
            '<span class="pca-t__ph"><img src="%s" alt="%s" width="768" height="480" loading="%s" decoding="async">'
            '<span class="pca-t__n">%02d</span></span>'
            '<span class="pca-t__b"><span class="pca-t__k">%s</span><h3>%s</h3><p class="pca-t__hl">%s</p>'
            '<span class="pca-t__fig"><b>%s</b><span>%s</span></span>'
            '<span class="pca-t__src">%s</span></span></article></li>'
            % (i, ' pca-t--own' if t.get('own') else '', ent(https(t['image'])), ent(t['alt']),
               'eager' if i < 2 else 'lazy', i + 1, ent(t['tag']), ent(t['name']), ent(t['headline']),
               ent(t['figure']), ent(t['label']), src))
    defs, art = wreath()
    return (
        '<section class="pca-band pca-hero" aria-labelledby="pca-h1">%s<div class="pca-in">'
        '<div class="pca-top"><div class="pca-top__t"><p class="pca-eb">%s</p>'
        '<h1 class="pca-h1" id="pca-h1">%s</h1><p class="pca-lead">%s</p></div>'
        '<figure class="pca-mark">%s<figcaption>%s</figcaption></figure></div>'
        '<div class="pca-five-h"><h2>%s</h2><a href="#pca-index">All %d instruments</a></div>'
        '<ul class="pca-five">%s</ul><p class="pca-note">%s</p>'
        '</div></section>'
        % (defs, ent(h['eyebrow']), ent(h['title']), ent(one_line(fill(h['lead'], doc))[0]), art, ent(h.get('mark', '')),
           ent(five['label']), n_inst, ''.join(tiles), ent(five['note'])))


def counts(doc):
    """How many instruments, and how many are already in use (every line but Perfect Nations' own)."""
    items = [it for f in doc['index']['families'] for it in f['items']]
    return len(items), sum(1 for it in items if not it.get('own'))


def fill(text, doc):
    """Words in the data file may carry {n} (all instruments) and {n_used} (those already in use)."""
    n, used = counts(doc)
    return plain(text).replace('{n_used}', str(used)).replace('{n}', str(n))


def nation_names():
    """slug -> the nation's name as its own file writes it, for the link to its blueprint."""
    out = {}
    for p in DATA.glob('*.json'):
        try:
            d = json.loads(p.read_text(encoding='utf-8'))
        except ValueError:
            continue
        if isinstance(d, dict) and d.get('nation'):
            out[p.stem] = plain(d['nation'])
    return out


def index(doc, bps):
    """The toolkit: one family at a time, chosen from chips (with All), and a search across every line.
    Without script every family shows, so the page still reads in full."""
    ix = doc['index']
    names = nation_names()
    lead, rest = one_line(fill(ix['lead'], doc))
    n_all, n_used = counts(doc)
    jump, fams = [], []
    for n, f in enumerate(ix['families'], 1):
        fid = 'pca-f-' + f['id']
        jump.append('<li><a href="#%s" data-f="%s"><b>%02d</b>%s<i>%d</i></a></li>'
                    % (fid, fid, n, ent(f['short']), len(f['items'])))
        rows = []
        for it in f['items']:
            lm = ['<i>%s</i>' % ent(it['where'])]
            if it.get('year'):
                lm.append(ent(it['year']))
            if it.get('label'):
                lm.append(ent(it['label']))
            links = ['<a href="%s" target="_blank" rel="noopener">Source: %s</a>' % (ent(https(it['url'])), ent(it['source']))]
            if it.get('nation'):
                if it['nation'] not in bps:
                    sys.exit('%s links to the %s blueprint, which is not open' % (it['id'], it['nation']))
                links.append('<a class="pca-bp" href="%s">%s blueprint</a>'
                             % (ent(bps[it['nation']] + '#bp-register'), ent(names.get(it['nation'], it['where']))))
            rows.append(
                '<li><details class="pca-row%s" id="pca-i-%s"><summary>'
                '<span class="pca-r1"><span class="pca-nm">%s</span>%s</span>'
                '<span class="pca-hl">%s</span>'
                '<span class="pca-r3"><span class="pca-lm">%s</span><span class="pca-pm" aria-hidden="true"></span></span>'
                '</summary><div class="pca-more"><p>%s</p><p class="pca-links">%s</p></div></details></li>'
                % (' pca-row--own' if it.get('own') else '', ent(it['id']), ent(it['name']), fig_html(it, 'pca-fig'),
                   ent(it['headline']), ' &#183; '.join(lm), ent(it['how']), ''.join(links)))
        fams.append(
            '<section class="pca-fam" id="%s" aria-labelledby="%s-h"><div class="pca-fam__h"><span class="pca-fam__n">%02d</span>'
            '<div><h3 id="%s-h">%s</h3><p>%s</p></div><span class="pca-fam__c">%d</span></div><ul class="pca-rows">%s</ul></section>'
            % (fid, fid, n, fid, ent(f['name']), ent(f['line']), len(f['items']), ''.join(rows)))
    jump.append('<li class="pca-jump__all"><a href="#pca-index" data-f="all"><b>All</b>instruments<i>%d</i></a></li>' % n_all)
    return (
        '<section class="pca-band pca-idx" id="pca-index" aria-labelledby="pca-ih"><div class="pca-in">'
        '<div class="pca-idx__h"><div><p class="pca-eb">%s</p><h2 class="pca-h2" id="pca-ih">%s</h2><p class="pca-lead">%s</p>%s</div>'
        '<label class="pca-find"><span>Find an instrument</span><input type="search" placeholder="Search %d instruments" '
        'autocomplete="off" spellcheck="false" aria-controls="pca-fams"></label></div>'
        '<ul class="pca-jump" aria-label="Families of instruments">%s</ul>'
        '<p class="pca-found" aria-live="polite" hidden></p>'
        '<div class="pca-fams" id="pca-fams">%s</div></div></section>'
        % (ent(ix['eyebrow']), ent(fill(ix['title'], doc)), ent(lead), read_more([ent(rest)]), n_all,
           ''.join(jump), ''.join(fams)))


def record(doc):
    r = doc['record']
    top = max([b['n'] for b in r['by']] or [1])
    multi = next((b['n'] for b in r['by'] if b['cat'] == 'multi'), 0)
    pi = sum(b['n'] for b in r['by'] if b['cat'] in ('private', 'impact'))
    bars = ''.join(
        '<li class="pca-bar" style="--i:%d"><span class="pca-bar__l"><b>%s</b><span>%s</span></span>'
        '<span class="pca-bar__t" aria-hidden="true"><i style="--w:%.1f%%"></i></span>'
        '<span class="pca-bar__c">%s</span></li>'
        % (i, ent(b['label']), ent(b['sub']), b['n'] / top * 100, '{:,}'.format(b['n'])) for i, b in enumerate(r['by']))
    nats = ''.join(
        '<li><a class="pca-nat" href="%s"><span class="pca-nat__h"><b>%s</b><span>%d on record</span></span>'
        '<span class="pca-nat__t"><span>%s</span>%s</span></a></li>'
        % (ent(https(x['url']) + '#bp-register'), ent(x['name']), x['n'], ent(x['top']),
           ('<em>%s</em>' if x['money'] else '<span>%s</span>') % ent(x['amount']) if x['amount'] else '')
        for x in r['list'])
    return (
        '<section class="pca-band pca-rec" id="pca-record" aria-labelledby="pca-rh"><div class="pca-in">'
        '<div class="pca-rec__top"><div><p class="pca-eb">%s</p>'
        '<h2 class="pca-h2" id="pca-rh"><span data-pca-n="count">%s</span> instruments and investments across '
        '<span data-pca-n="nations">%d</span> nations</h2>'
        '<p class="pca-rec__ins"><b data-pca-n="multi">%s</b> come from multilateral institutions, <b data-pca-n="pi">%d</b> '
        'from private and impact investors: Capital Architecture is designed to close that gap.</p>%s</div>'
        '<ul class="pca-bars" aria-label="Who finances the capital already committed">%s</ul></div>'
        '<ul class="pca-nats">%s</ul>'
        '<div class="pca-rec__foot"><button class="pca-btn pca-btn--line pca-more-n" type="button" '
        'aria-expanded="false" hidden>Show all nations</button></div></div></section>'
        % (ent(r['eyebrow']), '{:,}'.format(r['count']), r['nations'], '{:,}'.format(multi), pi,
           read_more(['Closing it brings private capital to the seven basic living standards.', ent(r['note'])]), bars, nats))


def close(doc):
    c = doc['close']
    btns = ''.join('<a class="pca-btn%s" href="%s">%s</a>' % (' pca-btn--line' if b.get('line') else '', ent(https(b['url'])), ent(b['label']))
                   for b in c['buttons'])
    return (
        '<section class="pca-band pca-close" aria-labelledby="pca-ch"><div class="pca-in">'
        '<p class="pca-eb">%s</p><h2 class="pca-h2" id="pca-ch">%s</h2><p class="pca-lead">%s</p>'
        '<div class="pca-btns">%s</div></div></section>'
        % (ent(c['eyebrow']), ent(c['title']), ent(c['lead']), btns))


def main():
    path = DATA / 'capital-architecture.json'
    doc = json.loads(path.read_text(encoding='utf-8'))
    doc = count_record(doc)
    path.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print('data/capital-architecture.json: %d on record across %d nations' % (doc['record']['count'], doc['record']['nations']))
    if '--record' in sys.argv:
        return

    fams = doc['index']['families']
    n_inst = sum(len(f['items']) for f in fams)
    css = (HERE / 'style.css').read_text(encoding='utf-8').strip()
    js = (HERE / 'script.js').read_text(encoding='utf-8').strip()
    rule = (PAGES / 'home-rule.html').read_text(encoding='utf-8').strip()
    rule = re.sub(r'^\s*<!--.*?-->\s*', '', rule, count=1, flags=re.S)  # the gold line's style, its banner dropped
    today = datetime.now(timezone.utc).strftime('%Y-%m-%d')
    head = '''<!-- ===========================================================================
PERFECT NATIONS - CAPITAL ARCHITECTURE - THE WHOLE PAGE IN ONE FILE - v%s - %s
Page 8549 (/capital-architecture/) holds ONE Elementor Custom HTML widget whose root is pn-arch. The
Perfect Nations Live Pages plugin serves this file from GitHub in its place, so the page changes only
through GitHub. Kept by the Capital Architecture Steward. Never edit this file by hand: edit
data/capital-architecture.json (words and figures) or tools/capital/ (design), run
python3 tools/build_capital.py, and open a pull request.
v5.0: the periodic table is retired. Every instrument is one line: its name, its headline, and the
deal that proved it, with the figure in gold; open a line for how it works and the source. Four
bands: 01 Earthrise (the five we lead with), 02 ivory (the toolkit, six families), 03 Lagoon (the
deals on record, recounted from every blueprint and read live), a painted seam, 04 Earthrise Depth
(the close). Phones have their own layout and never scroll sideways.
v5.1: Gold line in place of the painted botanical seams (the Steward-General, 9 Nov 2026).
v5.2: Fewer words (the Steward-General, 9 Nov 2026): one headline and one line per section. The hero
keeps one sentence; the rest of the toolkit lead and the record's method note sit under Read more.
v5.3: in step with the homepage and the blueprints (the Steward-General, 10 Nov 2026). The laurels of the
logo, in one gold, are the page's mark (02 Capital on the homepage); the cup and the figures row leave
the hero, as on the homepage. The record takes the blueprints' name, Capital already committed, and each
nation opens at that band of its blueprint. Debt-for-Nature Swap: Ecuador 2023, from its register. The
close leads on to Solutions, step 03.
v6.0: the toolkit grows from 31 to 80 instruments in 13 families, as a capital markets desk would
group them: sovereign bonds, labelled bonds, capital markets, equity and funds, project finance, impact
investment, pay for results, guarantees and insurance, development loans and the IMF, debt conversions,
disaster risk finance, trade and commodity finance, grants and climate funds (the Steward-General,
10 Nov 2026). Each deal comes from a blueprint's own record where one exists. Chips with counts choose
one family at a time on every screen, All shows every line, and a search finds any instrument.
v5.4: light reading sections, Earthrise accents (the Steward-General, 10 Nov 2026).
=========================================================================== -->
''' % (VERSION, today)
    body = '\n'.join([
        '<style>\n%s\n</style>' % css,
        '<div id="pn-arch" data-version="%s">' % VERSION,
        rule,
        hero(doc, n_inst, len(fams)),
        index(doc, open_blueprints()),
        record(doc),
        '<div class="pn-rule" aria-hidden="true"></div>',
        close(doc),
        '</div>',
        # wrapped as a comment so the WordPress formatter never turns && into &#038;&#038; (tools/check_page.py)
        '<script><!--\n%s\n//--></script>' % js,
    ])
    page = head + body + '\n'
    first = re.search(r'\bid\s*=\s*["\'](pn-[a-z0-9-]+)["\']', page, re.I)
    if not first or first.group(1) != 'pn-arch':
        sys.exit('the first pn- id must be pn-arch, found %s' % (first.group(1) if first else None))
    bad = [(i, c) for i, c in enumerate(page) if ord(c) > 126]
    if bad:
        sys.exit('non-ASCII characters in the page: %r' % bad[:5])
    (PAGES / 'capital-architecture.html').write_text(page, encoding='utf-8')
    print('pages/capital-architecture.html: %d characters, %d instruments in %d families' % (len(page), n_inst, len(fams)))


if __name__ == '__main__':
    main()
