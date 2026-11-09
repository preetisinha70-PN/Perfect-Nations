#!/usr/bin/env python3
"""Build the one-file Perfect Nations homepage, pages/home.html.

The homepage is pasted once into ONE Elementor Custom HTML widget on page 13465 (slug home-2).
Its first root id is pn-home, so the Perfect Nations Live Pages plugin serves this file in place
of the paste. The parts below stay separate files so each can be edited and checked on its own;
this script joins them, in order, with the gold line (pages/home-rule.html) at the section break.

Before joining, it writes the static Solutions cards into pages/home-solutions.html (the blocks
GENERATED:SOLUTIONS, SOLUTIONS-COUNT and SOLUTIONS-LATEST) from data/state-of-nations.json, so the
section shows the latest Solutions even when the live file cannot be read.

Run from the repository root:  python3 tools/build_home.py
Then bump "pn-home" in pages/manifest.json and open a pull request "For approval: Homepage vX.Y ...".
"""
import html
import json
import re
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PAGES = ROOT / 'pages'
DATA = ROOT / 'data'
SITE = 'https://perfectnations.org'
VERSION = '10.1'
SOLUTIONS_SHOWN = 6
MONTHS = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September',
          'October', 'November', 'December']

# The page, top to bottom. 'rule' places the gold line (pages/home-rule.html) between two sections.
# 9 Nov 2026, the Steward-General: the gold line replaces the painted botanical seams everywhere, so
# the seams (pages/home-seams.html and the seam drawing that was here) are retired from the site.
# v10.0 (8 Nov 2026), the Steward-General's decision, after Goldman Sachs, J.P. Morgan and the World Bank:
# the homepage leads with outcomes, research and original work, and says only a little about the
# structure of the firm. The hero, the Capital Wire, the Blueprints of Nations, then the Solutions from
# State of Nations (new, home-solutions.html), a short What we do band whose tiles open the About page,
# and the close. The Cup (Vision and Mission), Assets, Capital, Perfect Capita and the Founder's Vision
# move to the About page (tools/build_about.py copies the parts there); their part files stay.
# v9.0.1 (8 Nov 2026): the Capital laurels show again (no class name may contain "laurel": header v19.1
# replaces any such drawing with the cup mark).
# v9.0 (8 Nov 2026): Assets. Capital. Solutions. (the gold, the laurels, the seven stars); FfD before SI.
ORDER = [
    'nations-menu.html',          # the moving list of 195 nations (also on other pages)
    'home-hero.html',             # 01 Civilization Re-Defined / Designing the Prosperity of Nations
    'home-capital-wire.html',     # 01b the Capital Wire, the deal tape (kept by the Correspondent)
    'home-blueprints.html',       # 02 Blueprints of Nations
    'rule',
    'home-solutions.html',        # 03 Solutions for Nations: the latest Solutions from State of Nations
    'home-steps.html',            # 04 What we do: Assets. Capital. Solutions. (ivory; tiles open the About page)
    'home-pledge.html',           # 05 The close: What could your nation become? The ReDesign Studio
]

def ascii_html(text):
    """Escape for HTML, curl straight apostrophes, and turn every non-ASCII character into an entity."""
    text = re.sub(r'\s+', ' ', str(text)).strip().replace("'", '\u2019')
    return html.escape(text, quote=True).encode('ascii', 'xmlcharrefreplace').decode('ascii')


def is_money(fig):
    return bool(re.match(r'^(?:[A-Z]{1,3}\s?)?[$\u00a3\u20ac\u20a6]|^[A-Z]{2,3}\s?[0-9]', fig))


def day(iso, long=False):
    y, m, d = iso.split('-')
    return '%d %s %s' % (int(d), MONTHS[int(m) - 1] if long else MONTHS[int(m) - 1][:3], y)


def source_name(label):
    return re.split(r',|:| \(| \u201c', str(label or ''))[0].strip()


def solutions():
    """The published Solutions, newest first (as the live script in home-solutions.html sorts them)."""
    son = json.loads((DATA / 'state-of-nations.json').read_text(encoding='utf-8'))
    ds = [s for s in son.get('dispatches', [])
          if isinstance(s.get('no'), int) and s.get('title') and re.match(r'^\d{4}-\d{2}-\d{2}$', str(s.get('date', '')))]
    ds.sort(key=lambda s: (s['date'], s['no']), reverse=True)
    return ds


def solution_card(s, i):
    """One card, the same markup the live script draws (keep the two in step)."""
    lead, no = i == 0, int(s['no'])
    url = str(s.get('url') or '')
    href = url if re.match(r'^https://[^\s"<>]+$', url) else '%s/state-of-nations/#solution-%02d' % (SITE, no)
    out = ['<li class="pnso-c%s" data-no="%d" style="--i:%d">' % (' pnso-c--lead' if lead else '', no, i),
           '<span class="pnso-wm" aria-hidden="true">%02d</span>' % no, '<div class="pnso-l">',
           '<p class="pnso-k">%s<span>Solution No. %02d</span><time datetime="%s">%s</time></p>' % (
               '<b class="pnso-n">%s</b>' % ascii_html(s['nation']) if s.get('nation') else '', no, s['date'], day(s['date'])),
           '<h3 class="pnso-t"><a href="%s">%s</a></h3>' % (ascii_html(href), ascii_html(s['title']))]
    fig = str(s.get('figure') or '').strip()
    if fig and re.search(r'[0-9]', fig):
        out.append('<p class="pnso-f%s"><b>%s</b>%s</p>' % (
            ' is-money' if is_money(fig) else '', ascii_html(fig),
            '<span>%s</span>' % ascii_html(s['caption']) if s.get('caption') else ''))
    if lead:
        stds = [x for x in s.get('standards') or [] if x]
        if stds:
            out.append('<ul class="pnso-std" aria-label="The basic standards of living it serves">%s</ul>'
                       % ''.join('<li>%s</li>' % ascii_html(x) for x in stds))
        figs = [x for x in (s.get('figures') or [])[1:4] if x and re.search(r'[0-9]', str(x[0])) and x[1]]
        if len(figs) == 3:
            out.append('<ul class="pnso-figs" aria-label="The deal in figures">%s</ul>' % ''.join(
                '<li%s><b>%s</b><span>%s</span></li>' % (' class="is-money"' if is_money(str(x[0])) else '',
                                                         ascii_html(x[0]), ascii_html(x[1])) for x in figs))
    out.append('</div>')
    if s.get('challenge') and s.get('ffd') and s.get('si'):
        out.append('<dl class="pnso-x">%s</dl>' % ''.join(
            '<div><dt>%s</dt><dd>%s</dd></div>' % (t, ascii_html(s[k]))
            for t, k in (('The challenge', 'challenge'), ('How FfD solves it', 'ffd'), ('How SI solves it', 'si'))))
    elif s.get('standfirst'):
        out.append('<p class="pnso-sf">%s</p>' % ascii_html(s['standfirst']))
    src = next((x for x in s.get('sources') or [] if x and str(x.get('url', '')).startswith('https://') and source_name(x.get('label'))), None)
    foot = ''
    if src:
        foot = '<a class="pnso-src" href="%s" target="_blank" rel="noopener noreferrer">Source: %s</a>' % (
            ascii_html(src['url']), ascii_html(source_name(src['label'])))
    out.append('<p class="pnso-ft">%s<span class="pnso-go" aria-hidden="true">Read the Solution</span></p></li>' % foot)
    return ''.join(out)


def put(page, name, body, inline=False):
    pat = re.compile(r'(<!-- GENERATED:%s(?![\w-])[^>]*-->)(.*?)(<!-- /GENERATED:%s -->)' % (re.escape(name), re.escape(name)), re.S)
    if not pat.search(page):
        sys.exit('marker GENERATED:%s not found' % name)
    sep = '' if inline else '\n'
    return pat.sub(lambda m: m.group(1) + sep + body + sep + m.group(3), page, count=1)


def write_solutions():
    """The static Solutions in pages/home-solutions.html, from data/state-of-nations.json."""
    part = PAGES / 'home-solutions.html'
    ds = solutions()
    code = part.read_text(encoding='utf-8')
    code = put(code, 'SOLUTIONS', '\n'.join(solution_card(s, i) for i, s in enumerate(ds[:SOLUTIONS_SHOWN])))
    code = put(code, 'SOLUTIONS-COUNT', str(len(ds)), inline=True)
    code = put(code, 'SOLUTIONS-LATEST', '<time data-k="latest" datetime="%s">%s</time>' % (ds[0]['date'], day(ds[0]['date'], True)), inline=True)
    part.write_text(code, encoding='utf-8')
    return len(ds)


def main():
    today = date.today().isoformat()
    if 'home-solutions.html' in ORDER:
        n = write_solutions()
        print('pages/home-solutions.html: %d of %d Solutions written in' % (min(n, SOLUTIONS_SHOWN), n))
    parts = []
    for item in ORDER:
        if item == 'rule':
            parts.append('<div class="pn-rule" aria-hidden="true"></div>')
            continue
        code = (PAGES / item).read_text(encoding='utf-8').strip()
        parts.append('<!-- ======== part: pages/%s ======== -->\n%s' % (item, code))
    head = '''<!-- ===========================================================================
PERFECT NATIONS - HOMEPAGE - THE WHOLE PAGE IN ONE FILE - v%s - %s
Paste this file ONCE into ONE Elementor Custom HTML widget on the homepage (page 13465), in a Full
Width container with padding 0, and delete every other widget on the page. From then on the Perfect
Nations Live Pages plugin serves pages/home.html from GitHub in place of the paste (root id pn-home,
the first id on the page), so the homepage changes only through GitHub. Do not edit the paste.
Built by tools/build_home.py from the parts named below, in this order. Edit a part, run the build,
and open a pull request; never edit this file by hand.
Palette: Earthrise and ivory grounds, gold only for what a visitor can act on; a fine gold line
(pages/home-rule.html) marks each section break.
v10.1: Gold line in place of the painted botanical seams (the Steward-General, 9 Nov 2026), on every page.
=========================================================================== -->
<div id="pn-home" hidden></div>
''' % (VERSION, today)
    shared = []
    if any('#pnk-' in x for x in parts):   # the logo kit, only when a part draws the logo
        shared.append((PAGES / 'home-logo-kit.html').read_text(encoding='utf-8').strip())
    if 'rule' in ORDER:
        shared.append((PAGES / 'home-rule.html').read_text(encoding='utf-8').strip())
    page = head + '\n'.join(shared) + '\n' + '\n'.join(parts) + '\n'
    first = re.search(r'\bid\s*=\s*["\'](pn-[a-z0-9-]+)["\']', page, re.I)
    if not first or first.group(1) != 'pn-home':
        sys.exit('the first pn- id must be pn-home, found %s' % (first.group(1) if first else None))
    bad = [(i, c) for i, c in enumerate(page) if ord(c) > 126]
    if bad:
        sys.exit('non-ASCII characters in a part: %r' % bad[:5])
    if re.search(r'(?:class|id)="[^"]*laurel', page, re.I):
        sys.exit('a class or id contains "laurel" (the header replaces such drawings with the cup mark)')
    (PAGES / 'home.html').write_text(page, encoding='utf-8')
    print('pages/home.html', len(page), 'characters,', len(ORDER), 'items')


if __name__ == '__main__':
    main()
