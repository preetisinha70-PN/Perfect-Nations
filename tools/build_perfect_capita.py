#!/usr/bin/env python3
"""Build the one-file Perfect Capita page, pages/perfect-capita.html, from src/perfect-capita.html.

The page is pasted once into ONE Elementor Custom HTML widget on /perfect-capita/ (page 9937). Its
root id is pn-pcap, so the Perfect Nations Live Pages plugin serves pages/perfect-capita.html in place
of the paste. Edit src/perfect-capita.html, never the built file. This script:
  - puts the painted seams library (pages/home-seams.html, shared with the homepage) where the source
    says <!--@SEAMS-LIBRARY-->, and a painted seam where it says <!--@SEAM:x--> (x is a to e);
  - refuses non-ASCII characters and a missing root id;
  - runs the validation suite (tools/check_page.py) on the result.

Run from the repository root:  python3 tools/build_perfect_capita.py
Then raise "pn-pcap" in pages/manifest.json and open a pull request "For approval: Perfect Capita vX.Y".
The figures on the page live in figures/perfect-capita.json and change without a build.
"""
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.dont_write_bytecode = True
sys.path.insert(0, str(ROOT / 'tools'))
from build_home import seam  # noqa: E402  (the same painted seams as the homepage)

SRC = ROOT / 'src' / 'perfect-capita.html'
OUT = ROOT / 'pages' / 'perfect-capita.html'
ROOT_ID = 'pn-pcap'


def main():
    html = SRC.read_text(encoding='utf-8')
    library = (ROOT / 'pages' / 'home-seams.html').read_text(encoding='utf-8').strip()
    if '<!--@SEAMS-LIBRARY-->' not in html:
        sys.exit('the source has no <!--@SEAMS-LIBRARY--> marker')
    html = html.replace('<!--@SEAMS-LIBRARY-->', library, 1)
    html, n = re.subn(r'<!--@SEAM:([a-e])-->', lambda m: seam(m.group(1)), html)
    if 'id="%s"' % ROOT_ID not in html:
        sys.exit('the root id %s is missing' % ROOT_ID)
    bad = [(i, c) for i, c in enumerate(html) if ord(c) > 126]
    if bad:
        sys.exit('non-ASCII characters in the source: %r' % bad[:5])
    if '<!--@' in html:
        sys.exit('an unknown <!--@ marker is left in the page')
    OUT.write_text(html, encoding='utf-8')
    print('pages/perfect-capita.html', len(html), 'characters,', n, 'seams')
    r = subprocess.run([sys.executable, str(ROOT / 'tools' / 'check_page.py'), str(OUT), '--root', ROOT_ID])
    sys.exit(r.returncode)


if __name__ == '__main__':
    main()
