#!/usr/bin/env python3
"""The Perfect Nations validation suite for one page file.

Run from the repository root:  python3 tools/check_page.py pages/perfect-capita.html [--root pn-pcap]

Checks, in order: plain ASCII; every style block parses (tinycss2) and holds nothing that looks like
an HTML tag (the WordPress validator rejects `</?word` inside CSS); every inline script passes
`node --check`; no static <script src>; no backdrop-filter; tags balance; ids are unique; the root id
is present; images come only from perfectnations.org; the visible copy has no straight apostrophes and
no contractions. Exits 1 and lists every failure, or prints one line when the page passes.
"""
import argparse
import re
import subprocess
import sys
import tempfile
from html.parser import HTMLParser
from pathlib import Path

VOID = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'source', 'track', 'wbr'}
CONTRACTIONS = re.compile(r"\b(?:[A-Za-z]+n[’']t|it[’']s|that[’']s|there[’']s|what[’']s|who[’']s|"
                          r"let[’']s|[A-Za-z]+[’'](?:re|ll|ve|d|m))\b", re.I)


class Walker(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack, self.errors, self.ids, self.copy, self.scripts, self.styles = [], [], {}, [], [], []
        self.imgs, self._in = [], None

    def handle_starttag(self, tag, attrs):
        self._tag(tag, attrs)
        if tag not in VOID:
            self.stack.append((tag, self.getpos()[0]))
        if tag in ('script', 'style'):
            self._in = tag

    def handle_startendtag(self, tag, attrs):
        self._tag(tag, attrs)

    def _tag(self, tag, attrs):
        a = dict(attrs)
        if 'id' in a:
            self.ids.setdefault(a['id'], []).append(self.getpos()[0])
        if tag == 'script' and a.get('src'):
            self.errors.append('static <script src> on line %d' % self.getpos()[0])
        if tag == 'img' and a.get('src') and not a['src'].startswith('https://perfectnations.org/'):
            self.imgs.append((self.getpos()[0], a['src']))

    def handle_endtag(self, tag):
        if tag in VOID:
            return
        if tag in ('script', 'style'):
            self._in = None
        if not self.stack:
            self.errors.append('closing </%s> with nothing open, line %d' % (tag, self.getpos()[0]))
            return
        if self.stack[-1][0] == tag:
            self.stack.pop()
            return
        names = [t for t, _ in self.stack]
        if tag in names:
            while self.stack and self.stack[-1][0] != tag:
                t, line = self.stack.pop()
                self.errors.append('<%s> opened on line %d is not closed' % (t, line))
            self.stack.pop()
        else:
            self.errors.append('stray </%s> on line %d' % (tag, self.getpos()[0]))

    def handle_data(self, data):
        if self._in == 'script':
            self.scripts.append((self.getpos()[0], data))
        elif self._in == 'style':
            self.styles.append((self.getpos()[0], data))
        else:
            self.copy.append((self.getpos()[0], data))


def css_errors(css):
    import tinycss2
    out = []

    def walk(nodes, depth=0):
        for n in nodes:
            if n.type == 'error':
                out.append(n.message)
            elif n.type in ('qualified-rule', 'at-rule') and n.content is not None:
                inner = tinycss2.parse_blocks_contents(n.content) if hasattr(tinycss2, 'parse_blocks_contents') else tinycss2.parse_declaration_list(n.content)
                walk(inner, depth + 1)
                if n.type == 'at-rule' and n.lower_at_keyword in ('media', 'supports', 'keyframes'):
                    walk(tinycss2.parse_rule_list(n.content), depth + 1)
    walk(tinycss2.parse_stylesheet(css, skip_comments=True, skip_whitespace=True))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('file')
    ap.add_argument('--root', help='root id that must be present, for example pn-pcap')
    args = ap.parse_args()
    text = Path(args.file).read_text(encoding='utf-8')
    fails = []

    bad = [(text.count('\n', 0, i) + 1, c) for i, c in enumerate(text) if ord(c) > 126]
    if bad:
        fails.append('non-ASCII characters: %r' % bad[:5])
    if re.search(r'backdrop-filter', text):
        fails.append('backdrop-filter is used')

    w = Walker()
    w.feed(text)
    w.close()
    fails += w.errors
    for t, line in w.stack:
        fails.append('<%s> opened on line %d is not closed' % (t, line))
    for k, lines in w.ids.items():
        if len(lines) > 1:
            fails.append('duplicate id "%s" on lines %s' % (k, lines))
    if args.root and args.root not in w.ids:
        fails.append('root id %s is missing' % args.root)
    for line, src in w.imgs:
        fails.append('image from another host on line %d: %s' % (line, src))

    for line, css in w.styles:
        m = re.search(r'</?\w+', css)
        if m:
            fails.append('HTML-like sequence "%s" inside CSS (style block from line %d)' % (m.group(0), line))
        for e in css_errors(css):
            fails.append('CSS parse error in style block from line %d: %s' % (line, e))

    for line, js in w.scripts:
        if not js.strip():
            continue
        with tempfile.NamedTemporaryFile('w', suffix='.js', delete=False) as f:
            f.write(js)
        r = subprocess.run(['node', '--check', f.name], capture_output=True, text=True)
        if r.returncode:
            fails.append('script from line %d fails node --check: %s' % (line, r.stderr.strip().splitlines()[-1] if r.stderr.strip() else ''))

    for line, data in w.copy:
        if "'" in data:
            fails.append('straight apostrophe in copy on line %d: %r' % (line, data.strip()[:80]))
        for m in CONTRACTIONS.finditer(data):
            fails.append('contraction "%s" in copy on line %d' % (m.group(0), line))

    if fails:
        print('%s: %d problem(s)' % (args.file, len(fails)))
        for f in fails:
            print('  -', f)
        sys.exit(1)
    print('%s: passes (%d characters, %d style blocks, %d scripts, %d ids)' % (
        args.file, len(text), len(w.styles), len([s for s in w.scripts if s[1].strip()]), len(w.ids)))


if __name__ == '__main__':
    main()
