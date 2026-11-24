#!/usr/bin/env python3
"""Build the three mandates of the ReDesign Studio for a nation, as the nation receives them (v1.0, 24 Nov 2026).

Preeti Sinha, President and CEO, 24 Nov 2026: "What is the specific product a Nation Briefing, A Blueprint Lab and
A Sovereign Mandate would look like. Do all three for Barbados and publish them."

Each mandate is one page, built from one design (tools/mandates/style.css) and the nation's words
(tools/mandates/<slug>-briefing.html, -lab.html, -sovereign.html). The pages are illustrations of what a nation
receives: each says that it was not commissioned by the nation's government and that no terms have been agreed.
No prices are shown ("Scope and fees are agreed in writing before any work begins", as on the ReDesign Studio page).

    python3 tools/build_mandates.py barbados              write pages/mandate-<kind>-<slug>.html (root pn-md-<kind>-<slug>)
    python3 tools/build_mandates.py barbados --standalone DIR [--links FILE]
                                                         also write whole HTML documents to DIR, for sharing as
                                                         pages of their own; FILE (JSON) maps briefing, lab and
                                                         sovereign to the addresses the cross-links should use

Site addresses: https://perfectnations.com/blueprints/<slug>/nation-briefing/, /blueprint-lab/, /sovereign-mandate/.
Every change goes through a pull request "For approval: The three mandates for <Nation> vX.Y, ...".
"""
import json
import re
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HERE = ROOT / 'tools' / 'mandates'
PAGES = ROOT / 'pages'
VERSION = '1.1'
KINDS = {
    'briefing': ('The Nation Briefing', 'nation-briefing', 'Mandate I: three hours, the Gap named and sized'),
    'lab': ('The Blueprint Lab', 'blueprint-lab', 'Mandate II: three days, the structure drawn'),
    'sovereign': ('The Sovereign Mandate', 'sovereign-mandate', 'Mandate III: end to end, a structure ready for market'),
}
NAMES = {'barbados': 'Barbados'}
FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
         '<link href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@500;600;700&amp;'
         'family=Barlow+Semi+Condensed:wght@400;500;600&amp;display=swap" rel="stylesheet">')


def build(slug, standalone=None, links=None):
    name = NAMES[slug]
    css = (HERE / 'style.css').read_text(encoding='utf-8')
    out = []
    for kind, (title, path, line) in KINDS.items():
        rid = 'pn-md-%s-%s' % (kind, slug)
        body = (HERE / ('%s-%s.html' % (slug, kind))).read_text(encoding='utf-8').replace('__ROOT__', rid)
        banner = ('<!-- ===========================================================================\n'
                  'PERFECT NATIONS - %s - %s - v%s - %s\n'
                  'perfectnations.com/blueprints/%s/%s/ . Root id %s. %s.\n'
                  'An illustration of what a nation receives from the ReDesign Studio: not commissioned by the Government of\n'
                  '%s; no terms agreed. Built by tools/build_mandates.py from tools/mandates/ (never edit this file by hand).\n'
                  'v1.1 (24 Nov 2026): the section links keep their width on phones (they overlapped), and the theme no longer\n'
                  'sets the headings in capitals (Preeti Sinha, President and CEO: "There is a problem with the text").\n'
                  'v1.0 (24 Nov 2026, Preeti Sinha, President and CEO): the three mandates for %s, with AI after the finance.\n'
                  '=========================================================================== -->\n'
                  % (title.upper(), name.upper(), VERSION, date.today().isoformat(), slug, path, rid, line, name, name))
        page = '%s<style>\n%s</style>\n%s' % (banner, css.replace('#R', '#' + rid), body)
        bad = [(i, c) for i, c in enumerate(page) if ord(c) > 126]
        if bad:
            sys.exit('%s: non-ASCII character %r at %d' % (kind, bad[0][1], bad[0][0]))
        if re.search(r"\b(pay|pays|paid)\b", re.sub(r'<[^>]+>', ' ', body), re.I):
            sys.exit('%s: write "finance", not "pay"' % kind)
        f = PAGES / ('mandate-%s-%s.html' % (kind, slug))
        f.write_text(page, encoding='utf-8')
        out.append(f)
        print('%s: %d characters' % (f.relative_to(ROOT), len(page)))
        if standalone:
            doc = page
            for k, url in (links or {}).items():
                site = 'https://perfectnations.com/blueprints/%s/%s/' % (slug, KINDS[k][1])
                doc = doc.replace('href="%s" data-md="%s"' % (site, k), 'href="%s" data-md="%s"' % (url, k))
            doc = ('<!DOCTYPE html>\n<html lang="en"><head><meta charset="utf-8">'
                   '<meta name="viewport" content="width=device-width,initial-scale=1">'
                   '<title>%s: %s</title>%s<style>html,body{margin:0;background:#FBF8F1}</style></head>\n<body>\n%s\n</body></html>\n'
                   % (title, name, FONTS, doc))
            Path(standalone).mkdir(parents=True, exist_ok=True)
            sf = Path(standalone) / ('%s-%s.html' % (kind, slug))
            sf.write_text(doc, encoding='utf-8')
            print('  standalone: %s' % sf)
    return out


if __name__ == '__main__':
    args = sys.argv[1:]
    if not args or args[0] not in NAMES:
        sys.exit(__doc__)
    sa = args[args.index('--standalone') + 1] if '--standalone' in args else None
    ln = json.loads(Path(args[args.index('--links') + 1]).read_text()) if '--links' in args else None
    build(args[0], sa, ln)
