#!/usr/bin/env python3
"""The Perfect Nations validation suite for a page file.

    python3 tools/check_page.py pages/blueprints.html [more files]

Checks, for each file: plain ASCII; every <style> parses (tinycss2) and holds nothing that looks like a
tag (WordPress rejects </?word in CSS); every <script> passes `node --check`; tags balance; ids are
unique; no backdrop-filter; no static <script src>; every script survives the WordPress formatter
(wptexturize, which rewrites & as &#038; inside anything it takes for a tag; added 10 Nov 2026 after it broke the
Mexico blueprint scripts); and, in the copy a visitor reads (text, title, alt, placeholder, aria-label), no
straight apostrophes and no contractions.
Exit status 1 if anything fails. Needs: pip install tinycss2, and node.
"""
import re
import subprocess
import sys
import tempfile
from html.parser import HTMLParser

import tinycss2

VOID = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'source', 'track', 'wbr'}
COPY_ATTRS = ('title', 'alt', 'placeholder', 'aria-label')
CONTRACTION = re.compile(r"\b\w+(n['’]t|['’](re|ve|ll|d|m))\b|\b(it|that|there|here|what|who|let)['’]s\b", re.I)


# WordPress's wptexturize (wp-includes/formatting.php), the part that breaks scripts: the content is split at
# anything from < to the next > (get_html_split_regex), and in every piece that is not an HTML comment each & that
# does not start an entity becomes &#038;. Pages placed in the WordPress editor go through it; Elementor pages do not.
_WP_COMMENT = r'!(?:-(?!->)[^\-]*+)*+(?:-->)?'
_WP_CDATA = r'!\[CDATA\[[^\]]*+(?:](?!]>)[^\]]*+)*+(?:]]>)?'
_WP_SPLIT = re.compile(r'(<(?:(?=!--)' + _WP_COMMENT + r'|(?=!\[CDATA\[)' + _WP_CDATA + r'|[^>]*>?))')
_WP_AMP = re.compile(r'&(?!#(?:\d+|x[a-f0-9]+);|[a-z1-4]{1,8};)', re.I)
_SCRIPT = re.compile(r'<script(?![^>]*type="application/(?:ld\+)?json")[^>]*>(.*?)</script>', re.S | re.I)


def wp_texturize_amps(html):
    return ''.join(_WP_AMP.sub('&#038;', p) if p.startswith('<') and not p.startswith('<!--') else p
                   for p in _WP_SPLIT.split(html))


class Walk(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack, self.ids, self.problems, self.copy = [], {}, [], []
        self.raw = None

    def handle_starttag(self, tag, attrs):
        self._attrs(tag, attrs)
        if tag in ('script', 'style'):
            self.raw = tag
        if tag not in VOID:
            self.stack.append((tag, self.getpos()))

    def handle_startendtag(self, tag, attrs):
        self._attrs(tag, attrs)

    def _attrs(self, tag, attrs):
        for k, v in attrs:
            if k == 'id' and v:
                self.ids.setdefault(v, []).append(self.getpos()[0])
            if k in COPY_ATTRS and v:
                self.copy.append((self.getpos()[0], v))

    def handle_endtag(self, tag):
        if tag in ('script', 'style'):
            self.raw = None
        if tag in VOID:
            return
        if not self.stack:
            self.problems.append('line %d: </%s> closes nothing' % (self.getpos()[0], tag))
            return
        if self.stack[-1][0] == tag:
            self.stack.pop()
            return
        names = [t for t, _ in self.stack]
        if tag in names:
            while self.stack and self.stack[-1][0] != tag:
                t, pos = self.stack.pop()
                self.problems.append('line %d: <%s> is never closed' % (pos[0], t))
            self.stack.pop()
        else:
            self.problems.append('line %d: </%s> closes nothing' % (self.getpos()[0], tag))

    def handle_data(self, data):
        if not self.raw and data.strip():
            self.copy.append((self.getpos()[0], data))


def check(path):
    src = open(path, encoding='utf-8').read()
    bad = []
    non = [(i, c) for i, c in enumerate(src) if ord(c) > 126]
    if non:
        bad.append('non-ASCII characters, first at offset %d: %r' % (non[0][0], non[0][1]))
    for m in re.finditer(r'<style[^>]*>(.*?)</style>', src, re.S | re.I):
        css = m.group(1)
        line = src.count('\n', 0, m.start()) + 1
        if re.search(r'</?\w', css):
            bad.append('line %d: a tag-like sequence inside CSS' % line)
        bare = re.sub(r'/\*.*?\*/|"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'', '', css, flags=re.S)
        if bare.count('{') != bare.count('}'):
            bad.append('line %d: CSS braces do not balance (%d open, %d close)' % (line, bare.count('{'), bare.count('}')))
        rules = tinycss2.parse_stylesheet(css, skip_comments=True, skip_whitespace=True)
        def walk(nodes):
            for n in nodes:
                if n.type == 'error':
                    bad.append('line %d: CSS error: %s' % (line, n.message))
                if getattr(n, 'content', None) and n.type in ('at-rule', 'qualified-rule'):
                    walk(tinycss2.parse_blocks_contents(n.content) if n.type == 'at-rule' else
                         tinycss2.parse_declaration_list(n.content))
        walk(rules)
    if re.search(r'backdrop-filter', src, re.I):
        bad.append('backdrop-filter is used')
    if re.search(r'<script[^>]*\ssrc\s*=', src, re.I):
        bad.append('a static <script src>')
    for n, m in enumerate(re.finditer(r'<script(?![^>]*type="application/(?:ld\+)?json")[^>]*>(.*?)</script>', src, re.S | re.I)):
        with tempfile.NamedTemporaryFile('w', suffix='.js', delete=False) as f:
            f.write(m.group(1))
        r = subprocess.run(['node', '--check', f.name], capture_output=True, text=True)
        if r.returncode:
            bad.append('script %d (line %d) fails node --check: %s' % (n + 1, src.count('\n', 0, m.start()) + 1, r.stderr.strip()[:300]))
    before = [m.group(1) for m in _SCRIPT.finditer(src)]
    after = [m.group(1) for m in _SCRIPT.finditer(wp_texturize_amps(src))]
    for n, (a, b) in enumerate(zip(before, after)):
        if a != b:
            bad.append('script %d would be broken by the WordPress formatter (& becomes &#038; between a < and a >); '
                       'wrap it as <script><!-- ... //--></script>' % (n + 1))
    if len(before) != len(after):
        bad.append('the WordPress formatter would change the number of scripts')
    w = Walk()
    w.feed(src)
    w.close()
    bad += w.problems
    for t, pos in w.stack:
        bad.append('line %d: <%s> is never closed' % (pos[0], t))
    for k, lines in w.ids.items():
        if len(lines) > 1:
            bad.append('id "%s" is used %d times (lines %s)' % (k, len(lines), lines[:4]))
    for line, text in w.copy:
        if "'" in text:
            bad.append('line %d: a straight apostrophe in the copy: %r' % (line, text.strip()[:80]))
        c = CONTRACTION.search(text)
        if c:
            bad.append('line %d: a contraction in the copy: %r' % (line, c.group(0)))
    return bad


def main():
    fail = False
    for p in sys.argv[1:]:
        bad = check(p)
        print('%s: %s' % (p, 'all checks passed' if not bad else '%d problem(s)' % len(bad)))
        for b in bad:
            print('  - ' + b)
        fail = fail or bool(bad)
    sys.exit(1 if fail else 0)


if __name__ == '__main__':
    main()
