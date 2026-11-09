#!/usr/bin/env python3
"""Refresh the generated blocks of the About page, pages/about.html.

The page is edited by hand, except the blocks that this script writes in place:
  GENERATED:NCOUNT    the number of Nation Stewards (one per open blueprint); NCOUNT2 the same,
                      on the Show all button
  GENERATED:TCOUNT    the number of SI Researchers (six research Stewards plus the Nation Stewards)
  GENERATED:NSTEWARDS the Nation Stewards: one linked card per open blueprint in
                      data/blueprints.json, with the Steward's name from data/<slug>.json and the
                      portrait the nation's own blueprint uses (pages/blueprint-<slug>.html)
v11.2 (9 Nov 2026): fewer words, one headline and one line per section, the detail behind Read more
(the Steward-General). The parts carry the cuts; this script is unchanged but for its version.
v11.1 (9 Nov 2026): the gold line (pages/home-rule.html, styled in GENERATED:LOGO-KIT) in place of
the painted botanical seams, the Steward-General's decision; the page places <div class="pn-rule">
between sections by hand, and this script no longer writes any seam.
v11.0 (8 Nov 2026): the structure of the firm moves from the homepage to this page, so the page
reuses the homepage parts rather than copies of their code. Each block below is the part file as
it stands (its banner dropped), with a one-line note naming the file and its version:
  GENERATED:LOGO-KIT  the logo in its parts (pages/home-logo-kit.html), once, for every part
                      that draws the logo; and the gold line (pages/home-rule.html)
  GENERATED:STEPS     What we do: Assets. Capital. Solutions. (pages/home-steps.html, #pn-steps)
  GENERATED:ASSETS    01 Assets, the gold: Sovereign Assets (pages/home-assets.html, #pn-assets)
  GENERATED:CAPITAL   02 Capital, the laurels: Capital Architecture (pages/home-capital.html, #pn-capital)
  GENERATED:CAPITA    03 Solutions, the seven stars: Perfect Capita (pages/home-perfect-capita.html, #pn-capita)
  GENERATED:VISION    The Founder's Vision (pages/home-vision.html, #pn-vision)
To change one of these sections, edit its part and run this script (and tools/build_home.py if the
homepage shows it too). Each part scopes its style to its own root id, so the page's own style
(scoped to #pn-about .ab-*) and the parts' styles do not meet. The script refuses a page whose ids
are not unique, or whose first pn- id is not pn-about.

Run from the repository root:  python3 tools/build_about.py
Run it whenever a blueprint is added. Then run tools/check_page.py on the page, raise "pn-about"
in pages/manifest.json and open a pull request "For approval: About vX.Y, [what changed]".
The About Steward (skill steward-about) runs this.
"""
import html
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PAGES = ROOT / 'pages'
DATA = ROOT / 'data'
PAGE = PAGES / 'about.html'
VERSION = '11.2'
RESEARCH_STEWARDS = 6
# The homepage parts this page shows, by block name (see the docstring).
PARTS = [
    ('STEPS', 'home-steps.html'),
    ('ASSETS', 'home-assets.html'),
    ('CAPITAL', 'home-capital.html'),
    ('CAPITA', 'home-perfect-capita.html'),
    ('VISION', 'home-vision.html'),
]


def ascii_html(text):
    """Escape for HTML and turn every non-ASCII character into a numeric entity."""
    return html.escape(text, quote=True).encode('ascii', 'xmlcharrefreplace').decode('ascii')


def initials(name):
    parts = [p for p in re.split(r'[\s-]+', name) if p]
    return (parts[0][0] + (parts[-1][0] if len(parts) > 1 else '')).upper()


def portrait(slug, steward):
    """The portrait the nation's blueprint shows: the img whose alt begins with the Steward's name."""
    f = PAGES / ('blueprint-%s.html' % slug)
    if not f.exists():
        return ''
    text = f.read_text(encoding='utf-8')
    for tag in re.findall(r'<img\b[^>]*>', text):
        alt = re.search(r'\balt="([^"]*)"', tag)
        src = re.search(r'\bsrc="(https://[^"]+)"', tag)
        if alt and src and html.unescape(alt.group(1)).startswith(steward + ','):
            return src.group(1)
    return ''


def stewards():
    data = json.loads((DATA / 'blueprints.json').read_text(encoding='utf-8'))
    rows = []
    for n in data.get('open', []):
        slug, nation, url = n['slug'], n['name'], n['url']
        name = n.get('steward', '')
        f = DATA / ('%s.json' % slug)
        if f.exists():
            d = json.loads(f.read_text(encoding='utf-8'))
            name = (d.get('steward') or {}).get('name') or name
        if not name:
            continue
        rows.append((nation, name, url, portrait(slug, name)))
    rows.sort(key=lambda r: r[0].replace('ô', 'o').lower())
    return rows


def stewards_block(rows):
    out = []
    for nation, name, url, src in rows:
        img = ''
        if src:
            img = ('<img src="%s" alt="" width="150" height="150" loading="lazy" decoding="async">'
                   % ascii_html(src))
        out.append(
            '        <li><a class="ab-ns" href="%s" target="_blank" rel="noopener" '
            'title="%s, Nation Steward of %s"><span class="ab-ns__av" data-i="%s">%s</span>'
            '<span class="ab-ns__t"><b>%s</b><span>%s</span></span></a></li>'
            % (ascii_html(url), ascii_html(name), ascii_html(nation), initials(name), img,
               ascii_html(name), ascii_html(nation)))
    return '\n'.join(out)


def part_block(name):
    """A homepage part as this page shows it: the banner dropped, a note naming the file and version."""
    code = (PAGES / name).read_text(encoding='utf-8').strip()
    banner = re.match(r'\s*<!--(.*?)-->', code, re.S)
    ver = re.search(r'\bv(\d+(?:\.\d+)+)\b', banner.group(1)) if banner else None
    body = re.sub(r'^\s*<!--.*?-->\s*', '', code, count=1, flags=re.S)
    return '<!-- part: pages/%s%s -->\n%s' % (name, ' v' + ver.group(1) if ver else '', body)


def logo_kit_block():
    return '\n'.join([part_block('home-logo-kit.html'), part_block('home-rule.html')])


def put(page, name, body, inline=False):
    pat = re.compile(r'(<!-- GENERATED:%s(?![\w-])[^>]*-->)(.*?)(<!-- /GENERATED:%s -->)'
                     % (re.escape(name), re.escape(name)), re.S)
    if not pat.search(page):
        sys.exit('marker GENERATED:%s not found in %s' % (name, PAGE.name))
    sep = '' if inline else '\n'
    return pat.sub(lambda m: m.group(1) + sep + body + sep + m.group(3), page, count=1)


def main():
    page = PAGE.read_text(encoding='utf-8')
    rows = stewards()
    page = put(page, 'NCOUNT', str(len(rows)), inline=True)
    page = put(page, 'NCOUNT2', str(len(rows)), inline=True)
    page = put(page, 'TCOUNT', str(len(rows) + RESEARCH_STEWARDS), inline=True)
    page = put(page, 'NSTEWARDS', stewards_block(rows))
    page = put(page, 'LOGO-KIT', logo_kit_block())
    for block, name in PARTS:
        page = put(page, block, part_block(name))
    first = re.search(r'\bid\s*=\s*["\'](pn-[a-z0-9-]+)["\']', page, re.I)
    if not first or first.group(1) != 'pn-about':
        sys.exit('the first pn- id must be pn-about, found %s' % (first.group(1) if first else None))
    bad = [(i, c) for i, c in enumerate(page) if ord(c) > 126]
    if bad:
        sys.exit('non-ASCII characters in the page: %r' % bad[:5])
    live = re.sub(r'<(script|style)\b.*?</\1>', '', page, flags=re.S | re.I)   # ids in scripts and styles do not count
    ids = re.findall(r'\sid\s*=\s*["\']([^"\']+)["\']', live)
    twice = sorted({i for i in ids if ids.count(i) > 1})
    if twice:
        sys.exit('ids used more than once: %s' % ', '.join(twice))
    if re.search(r'pn-seam|#pns-', page):
        sys.exit('a painted seam is left on the page (the gold line, <div class="pn-rule">, replaced them)')
    if re.search(r'(?:class|id)="[^"]*laurel', page, re.I):
        sys.exit('a class or id contains "laurel" (the header replaces such drawings with the cup mark)')
    PAGE.write_text(page, encoding='utf-8')
    missing = [r[1] for r in rows if not r[3]]
    print('pages/about.html v%s,' % VERSION, len(page), 'characters,', len(PARTS), 'homepage parts,', len(rows), 'Nation Stewards',
          '(no portrait: %s)' % ', '.join(missing) if missing else '(all with portraits)')


if __name__ == '__main__':
    main()
