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
VERSION = '2.0'
KINDS = {
    'briefing': ('The Nation Briefing', 'nation-briefing', 'Mandate I: three hours, the Gap named and sized'),
    'lab': ('The Blueprint Lab', 'blueprint-lab', 'Mandate II: three days, the structure drawn'),
    'sovereign': ('The Sovereign Mandate', 'sovereign-mandate', 'Mandate III: end to end, a structure ready for market'),
}
NAMES = {'barbados': 'Barbados'}
FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
         '<link href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@500;600;700&amp;'
         'family=Barlow+Semi+Condensed:wght@400;500;600&amp;display=swap" rel="stylesheet">')


# The seven stars of the logo, left to right, as the blueprints draw them (tools/build_nations.py STARS):
# (standard, star of the logo kit, centre x, centre y, the crown). Food is the larger centre star.
STARS = [('Water', 0, 69.5, 171.2, False), ('Shelter', 1, 138.3, 114.2, False), ('Energy', 2, 219.7, 77.2, False),
         ('Food', 3, 319.6, 75.9, True), ('Education', 4, 420.2, 77.2, False), ('Health', 5, 501.6, 114.2, False),
         ('Livelihood', 6, 570.6, 171.2, False)]
STAR_T = 'translate(43.0 30.0) scale(1.85) translate(-105.9 -19.8)'


def stars(slug):
    """The seven stars of the logo, each filled with gold to the nation's coverage on that standard, as published on
    its blueprint (data/<slug>.json, guarantees). The standard furthest from reach carries the pulsing ring."""
    kit = (PAGES / 'home-logo-kit.html').read_text(encoding='utf-8')
    g = {('Livelihood' if x['name'].startswith('Livelihood') else x['name']): x
         for x in json.loads((ROOT / 'data' / ('%s.json' % slug)).read_text(encoding='utf-8'))['guarantees']}
    far = min(g, key=lambda n: g[n]['value'])
    defs, use, text = [], [], []
    for name, k, cx, cy, crown in STARS:
        d = re.search(r'id="pnk-s%d" d="([^"]+)"' % k, kit).group(1)
        nums = [float(v) for v in re.findall(r'-?\d+\.?\d*', d)]
        x0, x1, y0, y1 = min(nums[0::2]), max(nums[0::2]), min(nums[1::2]), max(nums[1::2])
        v = max(0.0, min(1.0, float(g[name]['value']) / 100))
        defs.append('<path id="__ROOT__-s%d" d="%s"/><clipPath id="__ROOT__-c%d" clipPathUnits="userSpaceOnUse">'
                    '<rect class="md-fill" x="%.1f" y="%.2f" width="%.1f" height="%.2f" style="animation-delay:%.2fs"/></clipPath>'
                    % (k, d, k, x0 - 1, y1 - v * (y1 - y0), x1 - x0 + 2, v * (y1 - y0) + .5, abs(k - 3) * .14))
        use.append('<use class="md-star0" href="#__ROOT__-s%d"/><use class="md-star1" href="#__ROOT__-s%d" clip-path="url(#__ROOT__-c%d)"/>' % (k, k, k))
        cls = ' '.join(c for c in ('is-crown' if crown else '', 'is-far' if name == far else '') if c)
        ly, vy = (144.2, 178.2) if crown else (cy + 43.3, cy + 70.3)
        text.append('<g%s><text class="md-l" x="%s" y="%.1f" text-anchor="middle">%s</text><text class="md-v" x="%s" y="%.1f" text-anchor="middle">%s</text></g>'
                    % (' class="%s"' % cls if cls else '', cx, ly, name.upper(), cx, vy, g[name]['display']))
    k = [s for s in STARS if s[0] == far][0]
    ring = '<circle class="md-far" cx="%s" cy="%s" r="%d"/>' % (k[2], k[3], 44 if k[4] else 27)
    label = ('%s: the seven stars of the logo, one for each basic standard of living, each filled with gold to its '
             'coverage: %s. %s is furthest from reach.' % (NAMES[slug], ', '.join('%s %s' % (s[0], g[s[0]]['display']) for s in STARS), far))
    return ('<svg class="md-stars" viewBox="0 8 640 250" role="img" aria-label="%s" focusable="false"><defs>%s</defs>%s<g transform="%s">%s</g>%s</svg>'
            % (label, ''.join(defs), ring, STAR_T, ''.join(use), ''.join(text)))


def tape(slug):
    """The live tape: the nation's own deals, written once in tools/mandates/<slug>-tape.html and run twice so the
    loop is seamless (the second copy is hidden from screen readers and from the keyboard)."""
    items = (HERE / ('%s-tape.html' % slug)).read_text(encoding='utf-8').strip()
    again = items.replace('<a ', '<a tabindex="-1" ')
    return ('<div class="md-tape" role="region" aria-label="%s on record"><div class="md-tape__t"><ul>%s</ul>'
            '<ul aria-hidden="true">%s</ul></div></div>' % (NAMES[slug], items, again))


def build(slug, standalone=None, links=None):
    name = NAMES[slug]
    css = (HERE / 'style.css').read_text(encoding='utf-8')
    out = []
    for kind, (title, path, line) in KINDS.items():
        rid = 'pn-md-%s-%s' % (kind, slug)
        body = (HERE / ('%s-%s.html' % (slug, kind))).read_text(encoding='utf-8')
        body = body.replace('<!--md:tape-->', tape(slug)).replace('<!--md:stars-->', stars(slug))
        body = body.replace('__ROOT__', rid)
        body += '\n<script>\n%s</script>\n' % (HERE / 'script.js').read_text(encoding='utf-8').replace("'ROOT'", "'%s'" % rid)
        banner = ('<!-- ===========================================================================\n'
                  'PERFECT NATIONS - %s - %s - v%s - %s\n'
                  'perfectnations.com/blueprints/%s/%s/ . Root id %s. %s.\n'
                  'An illustration of what a nation receives from the ReDesign Studio: not commissioned by the Government of\n'
                  '%s; no terms agreed. Built by tools/build_mandates.py from tools/mandates/ (never edit this file by hand).\n'
                  'v2.0 (24 Nov 2026): lighter and livelier in the same look: the answer in one gold figure that counts up, the\n'
                  'live tape of the nation\'s deals, the seven stars of the logo filling to each standard, deal tombstones that turn\n'
                  'over, steps on a drawn gold line, tap to open, a light that follows the cursor, rows that swipe on phones (Preeti\n'
                  'Sinha, President and CEO: "I find the whole site a bit word heavy ... Less wordy"; "Okay, let\'s go live").\n'
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
