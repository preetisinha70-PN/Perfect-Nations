#!/usr/bin/env python3
"""Build the one-file Perfect Capita page, pages/perfect-capita.html, from src/perfect-capita.html.

The page is pasted once into ONE Elementor Custom HTML widget on /perfect-capita/ (page 9937). Its
root id is pn-pcap, so the Perfect Nations Live Pages plugin serves pages/perfect-capita.html in place
of the paste. Edit src/perfect-capita.html, never the built file. This script:
  - puts the style of the gold line (pages/home-rule.html, shared with the homepage, its banner
    dropped) where the source says <!--@RULE-STYLE-->; the source places the line itself,
    <div class="pn-rule">, between sections (since v9.1, 9 Nov 2026, in place of the painted
    botanical seams, the Steward-General's decision);
  - refuses non-ASCII characters, a missing root id and images from any host but the Media Library;
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

SRC = ROOT / 'src' / 'perfect-capita.html'
OUT = ROOT / 'pages' / 'perfect-capita.html'
ROOT_ID = 'pn-pcap'


def main():
    html = SRC.read_text(encoding='utf-8')
    rule = (ROOT / 'pages' / 'home-rule.html').read_text(encoding='utf-8').strip()
    rule = re.sub(r'^\s*<!--.*?-->\s*', '', rule, count=1, flags=re.S)  # drop the part banner
    if '<!--@RULE-STYLE-->' not in html:
        sys.exit('the source has no <!--@RULE-STYLE--> marker')
    html = html.replace('<!--@RULE-STYLE-->', rule, 1)
    n = html.count('<div class="pn-rule"')
    if 'id="%s"' % ROOT_ID not in html:
        sys.exit('the root id %s is missing' % ROOT_ID)
    bad = [(i, c) for i, c in enumerate(html) if ord(c) > 126]
    if bad:
        sys.exit('non-ASCII characters in the source: %r' % bad[:5])
    if '<!--@' in html:
        sys.exit('an unknown <!--@ marker is left in the page')
    foreign = [u for u in re.findall(r'<img[^>]+src="([^"]+)"', html) if not u.startswith('https://perfectnations.org/')]
    if foreign:
        sys.exit('images from another host (the speed standard allows the Media Library only): %r' % foreign[:5])
    OUT.write_text(html, encoding='utf-8')
    print('pages/perfect-capita.html', len(html), 'characters,', n, 'gold lines')
    r = subprocess.run([sys.executable, str(ROOT / 'tools' / 'check_page.py'), str(OUT)])
    sys.exit(r.returncode)


if __name__ == '__main__':
    main()
