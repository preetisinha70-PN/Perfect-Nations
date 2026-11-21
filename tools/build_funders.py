#!/usr/bin/env python3
"""Build the one-file Perfect Nations For Funders page.

Writes pages/for-funders.html, the whole /for-funders/ page (root pn-fund). The page holds ONE Custom HTML
block or Elementor widget whose root is pn-fund; the Perfect Nations Live Pages plugin serves this file in
its place. Never edit the page file by hand: the words live in data/for-funders.json and the design in
tools/funders/style.css.

The three figures in the hero are counted, never typed: the open blueprints (pn-bp-<slug> keys in
pages/manifest.json), and the instruments and investments on record and the instruments in the toolkit
(data/capital-architecture.json, refreshed by tools/build_capital.py).

Run from the repository root:  python3 tools/build_funders.py
Then raise "pn-fund" in pages/manifest.json and open a pull request "For approval: For Funders vX.Y, ...".
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
HERE = Path(__file__).resolve().parent / 'funders'
VERSION = '1.0'


def ent(s):
    return html.escape('' if s is None else str(s), quote=True).encode('ascii', 'xmlcharrefreplace').decode('ascii')


def link(u):
    if not re.match(r'^(https://|mailto:)[^\s"\'<>()]+$', u or ''):
        sys.exit('not an https or mailto link without quotes, brackets or spaces: %r' % u)
    return u


def figures():
    man = json.loads((PAGES / 'manifest.json').read_text(encoding='utf-8'))
    bps = sum(1 for k in man['pages'] if k.startswith('pn-bp-'))
    cap = json.loads((DATA / 'capital-architecture.json').read_text(encoding='utf-8'))
    inst = sum(len(f['items']) for f in cap['index']['families'])
    rec = cap['record']
    return [
        ('{:,}'.format(bps), 'nation blueprints', 'https://perfectnations.com/blueprints/'),
        ('{:,}'.format(rec['count']), 'instruments and investments on record across %d nations' % rec['nations'],
         'https://perfectnations.com/capital-architecture/#pca-record'),
        ('{:,}'.format(inst), 'instruments in the toolkit, each proved by a real deal',
         'https://perfectnations.com/capital-architecture/#pca-index'),
    ]


def hero(doc):
    h = doc['hero']
    figs = ''.join('<li><a href="%s"><b>%s</b><span>%s</span></a></li>' % (ent(link(u)), ent(n), ent(t)) for n, t, u in figures())
    return (
        '<section class="pf-band pf-hero" aria-labelledby="pf-h1"><div class="pf-in pf-hero__g"><div>'
        '<p class="pf-eb">%s</p><h1 class="pf-h1" id="pf-h1">%s</h1><p class="pf-lead">%s</p>'
        '<p class="pf-ll">%s</p></div>'
        '<ul class="pf-figs" aria-label="Perfect Nations in figures">%s</ul></div></section>'
        % (ent(h['eyebrow']), ent(h['title']), ent(h['lead']), ent(h['living_line']), figs))


def offer(doc):
    o = doc['offer']
    cards = ''.join('<li class="pf-card"><span class="pf-card__n">%s</span><h3>%s</h3><p>%s</p></li>'
                    % (ent(i['n']), ent(i['name']), ent(i['line'])) for i in o['items'])
    return ('<section class="pf-band pf-offer" aria-labelledby="pf-oh"><div class="pf-in">'
            '<p class="pf-eb">%s</p><h2 class="pf-h2" id="pf-oh">%s</h2><ul class="pf-cards">%s</ul></div></section>'
            % (ent(o['eyebrow']), ent(o['title']), cards))


def method(doc):
    m = doc['method']
    steps = ''.join('<li class="pf-step"><span class="pf-step__n">%02d</span><h3>%s</h3><p>%s</p></li>'
                    % (i, ent(s['name']), ent(s['line'])) for i, s in enumerate(m['steps'], 1))
    return ('<section class="pf-band pf-method" aria-labelledby="pf-mh"><div class="pf-in">'
            '<p class="pf-eb">%s</p><h2 class="pf-h2" id="pf-mh">%s</h2><ol class="pf-steps">%s</ol></div></section>'
            % (ent(m['eyebrow']), ent(m['title']), steps))


def who(doc):
    w = doc['who']
    chips = ''.join('<li>%s</li>' % ent(x) for x in w['items'])
    return ('<section class="pf-band pf-who" aria-labelledby="pf-wh"><div class="pf-in">'
            '<p class="pf-eb">%s</p><h2 class="pf-h2" id="pf-wh">%s</h2><ul class="pf-chips">%s</ul>'
            '<p class="pf-more"><a href="%s">%s</a></p></div></section>'
            % (ent(w['eyebrow']), ent(w['title']), chips, ent(link(w['link']['url'])), ent(w['link']['label'])))


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
    css = (HERE / 'style.css').read_text(encoding='utf-8').strip()
    rule = (PAGES / 'home-rule.html').read_text(encoding='utf-8').strip()
    rule = re.sub(r'^\s*<!--.*?-->\s*', '', rule, count=1, flags=re.S)
    today = datetime.now(timezone.utc).strftime('%Y-%m-%d')
    head = '''<!-- ===========================================================================
PERFECT NATIONS - FOR FUNDERS - THE WHOLE PAGE IN ONE FILE - v%s - %s
The /for-funders/ page holds ONE Custom HTML block whose root is pn-fund. The Perfect Nations Live Pages
plugin serves this file from GitHub in its place, so the page changes only through GitHub. Never edit this
file by hand: edit data/for-funders.json (words) or tools/funders/style.css (design), run
python3 tools/build_funders.py, and open a pull request.
v1.0: the page for funders as clients (the Steward-General, 21 Nov 2026): what funders receive (the deal
pipeline, Match of the week, introductions), how a deal is checked (Ledger, Living Line, Design, Capital),
who it serves, and one action: request the deal pipeline. The hero figures are counted from the manifest
and data/capital-architecture.json. Institutions are named for reference only, never as partners.
=========================================================================== -->
''' % (VERSION, today)
    body = '\n'.join([
        '<style>\n%s\n</style>' % css,
        '<div id="pn-fund" data-version="%s">' % VERSION,
        rule,
        hero(doc), offer(doc), method(doc), who(doc),
        '<div class="pn-rule" aria-hidden="true"></div>',
        close(doc),
        '</div>',
    ])
    page = head + body + '\n'
    first = re.search(r'\bid\s*=\s*["\'](pn-[a-z0-9-]+)["\']', page, re.I)
    if not first or first.group(1) != 'pn-fund':
        sys.exit('the first pn- id must be pn-fund, found %s' % (first.group(1) if first else None))
    bad = [(i, c) for i, c in enumerate(page) if ord(c) > 126]
    if bad:
        sys.exit('non-ASCII characters in the page: %r' % bad[:5])
    (PAGES / 'for-funders.html').write_text(page, encoding='utf-8')
    print('pages/for-funders.html: %d characters' % len(page))


if __name__ == '__main__':
    main()
