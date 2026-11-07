#!/usr/bin/env python3
"""Build the one-file Perfect Nations homepage, pages/home.html.

The homepage is pasted once into ONE Elementor Custom HTML widget on page 13465 (slug home-2).
Its first root id is pn-home, so the Perfect Nations Live Pages plugin serves this file in place
of the paste. The parts below stay separate files so each can be edited and checked on its own;
this script joins them, in order, with a painted seam between the Earthrise sections.

Run from the repository root:  python3 tools/build_home.py
Then bump "pn-home" in pages/manifest.json and open a pull request "For approval: Homepage vX.Y ...".
"""
import random
import re
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PAGES = ROOT / 'pages'
VERSION = '7.4'

# The page, top to bottom. 'seam' places a painted seam (variant a, b, c, ...).
ORDER = [
    'nations-menu.html',          # the moving list of 195 nations (also on other pages)
    'home-hero.html',             # 01 Civilization Re-Defined + 01a The Story of Perfect Nations
    'home-capital-wire.html',     # 01b the Capital Wire (kept by the Correspondent)
    'home-studio.html',           # The ReDesign Studio: the five moves
    'home-assets.html',           # move 01 Sovereign Assets
    'seam',
    'home-perfect-capita.html',   # move 02 Perfect Capita
    'seam',
    'home-blueprints.html',       # move 03 National Blueprints
    'seam',
    'home-capital.html',          # move 04 Capital Architecture
    'seam',
    'home-vision.html',           # Mission and Vision
    'seam',
    'home-pledge.html',           # The Pledge
]

# Motifs from the painting: symbol id, aspect (width / height), height in a 60-high strip.
MOTIFS = {
    'fern': (200 / 60, 50), 'flower': (1, 20), 'leaf': (70 / 56, 40), 'loops': (92 / 32, 22),
    'dashes': (40 / 32, 22), 'pods': (1, 46), 'feather': (140 / 44, 34), 'bowl': (1, 42),
    'rosette': (1, 40), 'dots': (1, 24), 'squares': (1, 28), 'sun': (1, 38),
}
SEQUENCES = {
    'a': ['fern', 'flower', 'dots', 'leaf', 'loops', 'pods', 'flower', 'feather', 'squares', 'bowl', 'rosette', 'dashes', 'sun', 'flower', 'fern~', 'leaf', 'dots'],
    'b': ['feather', 'flower', 'rosette', 'loops', 'squares', 'fern', 'flower', 'bowl', 'dots', 'leaf', 'sun', 'pods', 'dashes', 'flower', 'feather~', 'rosette'],
    'c': ['pods', 'dashes', 'leaf', 'flower', 'feather~', 'sun', 'loops', 'fern', 'flower', 'squares', 'rosette', 'bowl', 'flower', 'dots', 'leaf', 'fern~'],
    'd': ['rosette', 'loops', 'fern~', 'flower', 'bowl', 'dots', 'leaf', 'feather', 'flower', 'sun', 'squares', 'pods', 'dashes', 'flower', 'fern', 'leaf'],
    'e': ['leaf', 'flower', 'feather~', 'dots', 'pods', 'loops', 'rosette', 'flower', 'fern', 'sun', 'bowl', 'squares', 'flower', 'dashes', 'feather', 'leaf'],
}


def seam(variant):
    rnd = random.Random('pn-seam-' + variant)
    seq = SEQUENCES[variant]
    out, x, k = [], 40.0, 0
    while x < 1580:
        name = seq[k % len(seq)]
        k += 1
        flip = name.endswith('~')
        name = name.rstrip('~')
        aspect, h = MOTIFS[name]
        h *= 0.9 + rnd.random() * 0.2
        w = h * aspect
        y = 30 - h / 2 + (rnd.random() - 0.5) * 6
        if flip:
            g = '<g transform="translate(%.1f %.1f) scale(-1 1)"><use href="#pns-%s" x="%.1f" y="0" width="%.1f" height="%.1f"/></g>' % (x + w, y, name, 0, w, h)
        else:
            g = '<g transform="translate(%.1f %.1f)"><use href="#pns-%s" width="%.1f" height="%.1f"/></g>' % (x, y, name, w, h)
        out.append(g)
        if name == 'flower' and rnd.random() < 0.7:
            h2 = h * 0.7
            out.append('<g transform="translate(%.1f %.1f)"><use href="#pns-flower" width="%.1f" height="%.1f"/></g>' % (x + w * 0.9, y + (14 if y < 22 else -12), h2, h2))
        x += w + 20 + rnd.random() * 22
    return ('<div class="pn-seam pn-seam--%s" aria-hidden="true"><svg viewBox="0 0 1600 60" preserveAspectRatio="xMidYMid slice" focusable="false">%s</svg></div>'
            % (variant, ''.join(out)))


def main():
    today = date.today().isoformat()
    parts, letters = [], iter('abcdefgh')
    for item in ORDER:
        if item == 'seam':
            parts.append(seam(next(letters)))
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
Palette: Earthrise and ivory grounds, gold only for what a visitor can act on; the colour comes
from the painted seams (Preeti Sinha's garden painting) between the Earthrise sections.
=========================================================================== -->
<div id="pn-home" hidden></div>
''' % (VERSION, today)
    seams = (PAGES / 'home-seams.html').read_text(encoding='utf-8').strip()
    html = head + seams + '\n' + '\n'.join(parts) + '\n'
    first = re.search(r'\bid\s*=\s*["\'](pn-[a-z0-9-]+)["\']', html, re.I)
    if not first or first.group(1) != 'pn-home':
        sys.exit('the first pn- id must be pn-home, found %s' % (first.group(1) if first else None))
    bad = [(i, c) for i, c in enumerate(html) if ord(c) > 126]
    if bad:
        sys.exit('non-ASCII characters in a part: %r' % bad[:5])
    (PAGES / 'home.html').write_text(html, encoding='utf-8')
    print('pages/home.html', len(html), 'characters,', len(ORDER), 'items')


if __name__ == '__main__':
    main()
