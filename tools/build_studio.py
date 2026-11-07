#!/usr/bin/env python3
"""Refresh the generated blocks of the ReDesign Studio page, pages/design-studio.html.

The page is edited by hand, except three blocks that this script writes in place:
  GENERATED:SEAMS    the painted-seam drawings and style, copied from pages/home-seams.html
  GENERATED:SEAM     one seam strip (variant c), drawn by tools/build_home.py
  GENERATED:NATIONS  the finder of open nation ReDesign Studios, one entry per published
                     blueprint in pages/manifest.json

Run from the repository root:  python3 tools/build_studio.py
Then run tools/check_page.py on the page, raise "pn-ds" in pages/manifest.json and open a pull
request "For approval: ReDesign Studio vX.Y, [what changed]". The ReDesign Studio Steward
(skill steward-redesign-studio) runs this.
"""
import html
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PAGES = ROOT / 'pages'
PAGE = PAGES / 'design-studio.html'
sys.path.insert(0, str(ROOT / 'tools'))
from build_home import seam  # noqa: E402  (the homepage build draws the seams)


def ascii_html(text):
    """Escape for HTML and turn every non-ASCII character into a numeric entity."""
    return html.escape(text, quote=True).encode('ascii', 'xmlcharrefreplace').decode('ascii')


def nations():
    data = json.loads((PAGES / 'manifest.json').read_text(encoding='utf-8'))
    seen, out = set(), []
    for key, entry in data.get('pages', {}).items():
        if not isinstance(entry, dict) or '@' in key:
            continue
        if not entry.get('file', '').startswith('pages/blueprint-'):
            continue
        url = entry.get('url', '')
        if not url or url in seen:
            continue
        seen.add(url)
        name = re.sub(r'\s*blueprint\b.*$', '', entry.get('title', ''), flags=re.I).strip()
        out.append((name, url))
    out.sort(key=lambda p: p[0].replace('ô', 'o').lower())
    return out


def nations_block():
    rows = nations()
    opts = '\n'.join('            <option value="%s">%s</option>' % (ascii_html(u), ascii_html(n)) for n, u in rows)
    return ('          <label for="ds-nation">Find your nation&#8217;s Studio &middot; <b>%d open</b></label>\n'
            '          <select id="ds-nation" name="nation" required>\n'
            '            <option value="">Choose your nation</option>\n%s\n'
            '          </select>' % (len(rows), opts)), len(rows)


def seams_block():
    code = (PAGES / 'home-seams.html').read_text(encoding='utf-8').strip()
    code = re.sub(r'^\s*<!--.*?-->\s*', '', code, count=1, flags=re.S)  # drop the part banner
    return code


def put(page, name, body):
    pat = re.compile(r'(<!-- GENERATED:%s\b[^>]*-->)(.*?)(<!-- /GENERATED:%s -->)' % (name, name), re.S)
    if not pat.search(page):
        sys.exit('marker GENERATED:%s not found in %s' % (name, PAGE.name))
    return pat.sub(lambda m: m.group(1) + '\n' + body + '\n' + m.group(3), page, count=1)


def main():
    page = PAGE.read_text(encoding='utf-8')
    block, count = nations_block()
    page = put(page, 'NATIONS', block)
    page = put(page, 'SEAMS', seams_block())
    page = put(page, 'SEAM', seam('c'))
    first = re.search(r'\bid\s*=\s*["\'](pn-[a-z0-9-]+)["\']', page, re.I)
    if not first or first.group(1) != 'pn-ds':
        sys.exit('the first pn- id must be pn-ds, found %s' % (first.group(1) if first else None))
    bad = [(i, c) for i, c in enumerate(page) if ord(c) > 126]
    if bad:
        sys.exit('non-ASCII characters in the page: %r' % bad[:5])
    PAGE.write_text(page, encoding='utf-8')
    print('pages/design-studio.html', len(page), 'characters,', count, 'nation Studios')


if __name__ == '__main__':
    main()
