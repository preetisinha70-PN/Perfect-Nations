#!/usr/bin/env python3
"""Refresh the generated blocks of the About page, pages/about.html.

The page is edited by hand, except the blocks that this script writes in place:
  GENERATED:SEAMS     the painted-seam drawings and style, copied from pages/home-seams.html
  GENERATED:SEAM-A    one seam strip (variant a), drawn by tools/build_home.py
  GENERATED:SEAM-C    one seam strip (variant c), drawn by tools/build_home.py
  GENERATED:NCOUNT    the number of Nation Stewards (one per open blueprint); NCOUNT2 the same,
                      on the Show all button
  GENERATED:TCOUNT    the number of SI Researchers (six research Stewards plus the Nation Stewards)
  GENERATED:NSTEWARDS the Nation Stewards: one linked card per open blueprint in
                      data/blueprints.json, with the Steward's name from data/<slug>.json and the
                      portrait the nation's own blueprint uses (pages/blueprint-<slug>.html)

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
RESEARCH_STEWARDS = 6
sys.path.insert(0, str(ROOT / 'tools'))
from build_home import seam  # noqa: E402  (the homepage build draws the seams)


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


def seams_block():
    code = (PAGES / 'home-seams.html').read_text(encoding='utf-8').strip()
    return re.sub(r'^\s*<!--.*?-->\s*', '', code, count=1, flags=re.S)  # drop the part banner


def put(page, name, body, inline=False):
    pat = re.compile(r'(<!-- GENERATED:%s\b[^>]*-->)(.*?)(<!-- /GENERATED:%s -->)'
                     % (re.escape(name), re.escape(name)), re.S)
    if not pat.search(page):
        sys.exit('marker GENERATED:%s not found in %s' % (name, PAGE.name))
    sep = '' if inline else '\n'
    return pat.sub(lambda m: m.group(1) + sep + body + sep + m.group(3), page, count=1)


def main():
    page = PAGE.read_text(encoding='utf-8')
    rows = stewards()
    page = put(page, 'SEAMS', seams_block())
    page = put(page, 'SEAM-A', seam('a'))
    page = put(page, 'SEAM-C', seam('c'))
    page = put(page, 'NCOUNT', str(len(rows)), inline=True)
    page = put(page, 'NCOUNT2', str(len(rows)), inline=True)
    page = put(page, 'TCOUNT', str(len(rows) + RESEARCH_STEWARDS), inline=True)
    page = put(page, 'NSTEWARDS', stewards_block(rows))
    first = re.search(r'\bid\s*=\s*["\'](pn-[a-z0-9-]+)["\']', page, re.I)
    if not first or first.group(1) != 'pn-about':
        sys.exit('the first pn- id must be pn-about, found %s' % (first.group(1) if first else None))
    bad = [(i, c) for i, c in enumerate(page) if ord(c) > 126]
    if bad:
        sys.exit('non-ASCII characters in the page: %r' % bad[:5])
    PAGE.write_text(page, encoding='utf-8')
    missing = [r[1] for r in rows if not r[3]]
    print('pages/about.html', len(page), 'characters,', len(rows), 'Nation Stewards',
          '(no portrait: %s)' % ', '.join(missing) if missing else '(all with portraits)')


if __name__ == '__main__':
    main()
