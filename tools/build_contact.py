#!/usr/bin/env python3
"""Refresh the generated blocks of the Contact page, pages/contact.html.

The page is edited by hand, except two blocks that this script writes in place:
  GENERATED:RULE   the style of the gold line, copied from pages/home-rule.html (the line itself,
                   <div class="pn-rule">, sits under the letterhead; since v6.1, 9 Nov 2026, it
                   replaces the painted botanical seam, the Steward-General's decision)
  GENERATED:DATA   a JSON block the page reads: the open blueprints (from pages/manifest.json),
                   so that "Write to us" from a published nation opens "Share a vision or story"
                   and "Ask for this blueprint" from any other nation opens "Ask for a blueprint";
                   and the paintings and books a visitor can enquire about (from art/catalogue.json)

Run from the repository root:  python3 tools/build_contact.py
Run it whenever a blueprint is published or a painting or book is added. Then run
tools/check_page.py on the page, raise "pn-contact" in pages/manifest.json and open a pull
request "For approval: Contact vX.Y, [what changed]". The Contact Steward (skill
steward-contact) runs this.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PAGES = ROOT / 'pages'
PAGE = PAGES / 'contact.html'


def open_blueprints():
    data = json.loads((PAGES / 'manifest.json').read_text(encoding='utf-8'))
    out = []
    for key, entry in data.get('pages', {}).items():
        if not isinstance(entry, dict) or '@' in key:
            continue
        if not entry.get('file', '').startswith('pages/blueprint-'):
            continue
        m = re.search(r'/blueprints/([a-z0-9-]+)/?$', entry.get('url', ''))
        if m and m.group(1) not in out:
            out.append(m.group(1))
    return sorted(out)


def works():
    cat = json.loads((ROOT / 'art' / 'catalogue.json').read_text(encoding='utf-8'))
    paintings, books = [], []
    for p in cat.get('paintings', []):
        if p.get('enquire') and p.get('title'):
            paintings.append({'id': p['enquire'], 'title': p['title'], 'nation': p.get('nation', '')})
    for b in cat.get('books', []):
        if b.get('enquire') and b.get('title'):
            nation = re.sub(r'^Perfect\s+', '', b['title']).strip()
            books.append({'id': b['enquire'], 'title': b['title'], 'nation': nation, 'status': b.get('status', '')})
    return paintings, books


def data_block():
    paintings, books = works()
    opened = open_blueprints()
    payload = {'open': opened, 'paintings': paintings, 'books': books}
    text = json.dumps(payload, ensure_ascii=True, separators=(',', ':')).replace('</', '<\\/')
    return '<script type="application/json" id="ct-data">%s</script>' % text, len(opened), len(paintings), len(books)


def rule_block():
    code = (PAGES / 'home-rule.html').read_text(encoding='utf-8').strip()
    return re.sub(r'^\s*<!--.*?-->\s*', '', code, count=1, flags=re.S)  # drop the part banner


def put(page, name, body):
    pat = re.compile(r'(<!-- GENERATED:%s\b[^>]*-->)(.*?)(<!-- /GENERATED:%s -->)' % (name, name), re.S)
    if not pat.search(page):
        sys.exit('marker GENERATED:%s not found in %s' % (name, PAGE.name))
    return pat.sub(lambda m: m.group(1) + '\n' + body + '\n' + m.group(3), page, count=1)


def main():
    page = PAGE.read_text(encoding='utf-8')
    block, n_open, n_paint, n_book = data_block()
    page = put(page, 'DATA', block)
    page = put(page, 'RULE', rule_block())
    first = re.search(r'\bid\s*=\s*["\'](pn-[a-z0-9-]+)["\']', page, re.I)
    if not first or first.group(1) != 'pn-contact':
        sys.exit('the first pn- id must be pn-contact, found %s' % (first.group(1) if first else None))
    bad = [(i, c) for i, c in enumerate(page) if ord(c) > 126]
    if bad:
        sys.exit('non-ASCII characters in the page: %r' % bad[:5])
    PAGE.write_text(page, encoding='utf-8')
    print('pages/contact.html %d characters: %d open blueprints, %d paintings, %d books'
          % (len(page), n_open, n_paint, n_book))


if __name__ == '__main__':
    main()
