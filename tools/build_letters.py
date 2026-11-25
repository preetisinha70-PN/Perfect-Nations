#!/usr/bin/env python3
"""Letters to the Nations: build pages/letter-dear-<slug>.html from tools/letters/<slug>.json.

    python3 tools/build_letters.py                  # every tools/letters/<slug>.json
    python3 tools/build_letters.py benin togo       # some
    python3 tools/build_letters.py --manifest ...   # also add or raise pn-letter-<code> in pages/manifest.json
    python3 tools/build_letters.py --wp benin       # print the WordPress post (Custom HTML block) for each

Written on 25 Nov 2026 from the 44 hand-made Letters of 30 Oct 2026 (v8.1.3), which share one stylesheet
(tools/letters/style.css, with ROOT for the root id) and one layout: the back link to the blueprint, the sheet
(letterhead, "Dear <Nation>,", the paragraphs, the quotation, the signature and seal), the Sources and the two
buttons. The 44 hand files are left as they are; this script builds the Letters of the 151 (the brief "The 151 first
editions become full blueprints", Preeti Sinha, President and CEO, 24 Nov 2026).

A Letter file (tools/letters/<slug>.json):
  {"nation": "Benin", "slug": "benin", "code": "bj", "date": "2026-11-25",
   "excerpt": "the first sentence, for the post excerpt",
   "paras": ["...", "..."],            # plain text; the quotation goes in "quote", without its marks
   "quote": "...",
   "sources": [["World Bank, 2024", "https://..."], ...]}

The page lives in WordPress as a post: category Letter To The Nations (643), slug dear-<slug>, the excerpt from the
Letter, and one Custom HTML block holding <div id="pn-letter-<code>"> with a fallback line; the Perfect Nations Live
plugin serves this file in place of that block. Publish the post only after the pull request is merged, and set
_jetpack_dont_email_post_to_subs so no email goes out. Rules: no contractions, every figure sourced, plain ASCII
in the file (the script writes entities).
"""
import argparse
import html
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HERE, PAGES = ROOT / 'tools' / 'letters', ROOT / 'pages'
VERSION = '9.0'  # the first Letters built by tools/build_letters.py (25 Nov 2026), the same design as v8.1.3
CATEGORY = 643   # Letter To The Nations
LINK = 'target="_blank" rel="noopener noreferrer"'
CONTRACTION = re.compile(r"\b\w+(n['’]t|['’](re|ve|ll|d|m))\b", re.I)


def ent(s):
    """Plain ASCII: HTML-escape, then write every other character as an entity; quotes and dashes as typed."""
    s = html.escape(s, quote=True).replace('&#x27;', '&#8217;')
    return ''.join(c if ord(c) < 128 else '&#%d;' % ord(c) for c in s)


def curly(s):
    """Straight apostrophes in the copy become curly (the site never shows a straight apostrophe)."""
    return s.replace("'", '’')


def check(spec):
    probs = []
    for k in ('nation', 'slug', 'code', 'excerpt', 'paras', 'quote', 'sources'):
        if not spec.get(k):
            probs.append('missing %s' % k)
    if not re.fullmatch(r'[a-z]{2}', spec.get('code', '')):
        probs.append('code must be two lower-case letters')
    for t in [spec.get('excerpt', ''), spec.get('quote', '')] + list(spec.get('paras') or []):
        m = CONTRACTION.search(t)
        if m:
            probs.append('contraction: %s' % m.group(0))
        if re.search(r'\bSI\b|super ?intelligence|\bSteward\b', t, re.I):
            probs.append('banned word in: %s' % t[:60])
    for label, url in spec.get('sources') or []:
        if not url.startswith('https://'):
            probs.append('source not https: %s' % url)
    return probs


def page(spec, today):
    name, slug, code = spec['nation'], spec['slug'], spec['code']
    rid = 'pn-letter-' + code
    css = (HERE / 'style.css').read_text(encoding='utf-8').replace('ROOT', rid)
    bp = 'https://perfectnations.com/blueprints/%s/' % slug
    paras = '\n'.join('    <p class="lt-p">%s</p>' % ent(curly(p)) for p in spec['paras'])
    srcs = ' &middot; '.join('<a href="%s" %s>%s</a>' % (ent(u), LINK, ent(curly(l))) for l, u in spec['sources'])
    return (
        '<!-- PERFECT NATIONS . LETTERS TO THE NATIONS . DEAR %s . v%s LETTER . %s . Built by tools/build_letters.py from '
        'tools/letters/%s.json: never edit by hand . The same design as the 44 Letters of v8.1.3 . Strict Perfect Capita and '
        'the seven basic living standards . Signed by Preeti Sinha, President and CEO . WordPress post, slug dear-%s, category '
        'Letters to the Nations, one Custom HTML block -->\n'
        '<!-- Excerpt: %s -->\n'
        '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Caveat:wght@500;600&amp;display=swap">\n'
        '<style>\n%s</style>\n\n'
        '<div id="%s">\n'
        '  <a class="lt-back" href="%s" %s>The %s blueprint</a>\n'
        '  <article class="lt-sheet" aria-labelledby="lt-dear">\n'
        '    <div class="lt-lh"><span>Perfect Nations&#174; &middot; Letters to the Nations</span><span>%s</span></div>\n'
        '    <h1 class="lt-dear" id="lt-dear">Dear %s,</h1>\n'
        '%s\n'
        '    <blockquote class="lt-q">&#8220;%s&#8221;</blockquote>\n'
        '    <p class="lt-p">So this is an invitation. Bring your vision, your story and your solutions to the Perfect %s ReDesign '
        'Studio, and join the Co-designers who are already imagining what comes next. Perfect %s will not be designed for you. '
        'It will be designed by you.</p>\n'
        '    <div class="lt-sig">\n'
        '      <div><p>Yours in design,</p><b>Preeti Sinha</b><p style="font-size:.92rem;margin-top:4px;">President and CEO, Perfect Nations</p></div>\n'
        '      <span class="lt-seal" aria-hidden="true"><i>Letter</i><b>%s</b></span>\n'
        '    </div>\n'
        '  </article>\n'
        '  <p class="lt-src">Sources: %s</p>\n'
        '  <div class="lt-next">\n'
        '    <a class="lt-btn" href="%s#bp-studio" %s>Enter the ReDesign Studio</a>\n'
        '    <a class="lt-btn lt-btn--line" href="%s" %s>Read the %s blueprint</a>\n'
        '  </div>\n'
        '</div>\n'
        % (ent(name.upper()), VERSION, spec.get('date') or today, slug, slug, ent(curly(spec['excerpt'])).replace('--', '-'), css,
           rid, bp, LINK, ent(name), ent(name), ent(name), paras, ent(curly(spec['quote'])), ent(name), ent(name), code.upper(),
           srcs, bp, LINK, bp, LINK, ent(name)))


def wp_post(spec):
    """The WordPress post for a Letter: one Custom HTML block holding the root and a fallback line."""
    code, slug, name = spec['code'], spec['slug'], spec['nation']
    block = ('<!-- wp:html -->\n<div id="pn-letter-%s"><p>Dear %s, the Letter from Perfect Nations is loading. '
             '<a href="https://perfectnations.com/blueprints/%s/">Read the %s blueprint</a>.</p></div>\n<!-- /wp:html -->'
             % (code, ent(name), slug, ent(name)))
    return {'title': 'Dear %s' % name, 'slug': 'dear-%s' % slug, 'status': 'publish', 'categories': [CATEGORY],
            'excerpt': spec['excerpt'], 'content': block, 'meta': {'_jetpack_dont_email_post_to_subs': True}}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('slugs', nargs='*')
    ap.add_argument('--manifest', action='store_true')
    ap.add_argument('--wp', action='store_true', help='print the WordPress post for each Letter as JSON')
    a = ap.parse_args()
    slugs = a.slugs or sorted(p.stem for p in HERE.glob('*.json'))
    today = datetime.now(timezone.utc).strftime('%Y-%m-%d')
    specs, bad = [], False
    for s in slugs:
        spec = json.loads((HERE / ('%s.json' % s)).read_text(encoding='utf-8'))
        probs = check(spec)
        for p in probs:
            print('%s: %s' % (s, p), file=sys.stderr)
        bad = bad or bool(probs)
        specs.append(spec)
    if bad:
        sys.exit(1)
    if a.wp:
        print(json.dumps([wp_post(s) for s in specs], indent=2, ensure_ascii=False))
        return
    for spec in specs:
        out = PAGES / ('letter-dear-%s.html' % spec['slug'])
        out.write_text(page(spec, today), encoding='ascii')
        print('%s: %d characters' % (out.relative_to(ROOT), out.stat().st_size))
    if a.manifest:
        path = PAGES / 'manifest.json'
        man = json.loads(path.read_text(encoding='utf-8'))
        for spec in specs:
            man['pages']['pn-letter-' + spec['code']] = {
                'file': 'pages/letter-dear-%s.html' % spec['slug'], 'version': VERSION,
                'title': 'Letter: Dear %s' % spec['nation'], 'url': 'https://perfectnations.com/dear-%s/' % spec['slug']}
        man['updated'] = today
        path.write_text(json.dumps(man, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
        print('pages/manifest.json: %d Letters at v%s' % (len(specs), VERSION))


if __name__ == '__main__':
    main()
