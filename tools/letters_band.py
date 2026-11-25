#!/usr/bin/env python3
"""The "More Letters to the Nations" band at the foot of every Letter (pages/letter-dear-*.html).

Letters v8.3 (25 November 2026). Preeti Sinha, President and CEO, 25 Nov 2026, on the theme's Related Posts and
Previous Post / Next Post links under the Letters: "Nice to see the other letters here, but terrible formatting at the
moment." On Letters only, this band hides the theme's blocks (Astra related posts, Astra post navigation, Jetpack
related posts) and puts the previous and next Letters, A to Z, in the Letter's own parchment design, with a link to
every Letter in the category Letters to the Nations. Blog posts and dispatches keep the theme's blocks.

The band sits between <!--pn:more-letters ...--> and <!--/pn:more-letters--> just before the closing tag of the page
root, and is rewritten in place each time, so it never needs editing by hand. The order, the names and the links come
from pages/manifest.json (every pn-letter-<code> with a url), each Letter's own "Dear <nation>," heading and its
<!-- Excerpt: --> line. tools/build_letters.py runs this after it builds a Letter.

    python3 tools/letters_band.py              write the band into every Letter
    python3 tools/letters_band.py --manifest   also raise the version in pages/manifest.json of each Letter whose page
                                               changed (to 8.3, then 8.3.1, 8.3.2 ...), so the live plugin serves it
Then: python3 tools/check_page.py pages/letter-dear-*.html
"""
import html
import json
import re
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PAGES = ROOT / 'pages'
BASE = '8.3'
ALL_URL = 'https://perfectnations.com/category/letters-to-the-nations/'
BAND = re.compile(r'<!--pn:more-letters\b.*?<!--/pn:more-letters-->\n?', re.S)


def asc(s):
    return s.encode('ascii', 'xmlcharrefreplace').decode('ascii')


def words(s):
    """Plain text to HTML copy: escaped, curly apostrophes and quotation marks, plain ASCII."""
    s = html.escape(s, quote=False).replace("'", '’')
    return asc(s)


def bump(v):
    if not v:
        return BASE
    cur = tuple(int(x) for x in v.split('.'))
    base = tuple(int(x) for x in BASE.split('.'))
    if cur < base:
        return BASE
    cur = cur + (0,) * (3 - len(cur))
    return '%d.%d.%d' % (cur[0], cur[1], cur[2] + 1)


def sort_key(name):
    n = unicodedata.normalize('NFKD', name)
    n = ''.join(c for c in n if not unicodedata.combining(c))
    n = re.sub(r'^the\s+', '', n.strip(), flags=re.I)
    return re.sub(r'[^a-z0-9 ]', '', n.lower())


def letters(man):
    out = []
    for root, v in man['pages'].items():
        if not root.startswith('pn-letter-') or '@' in root or not v.get('url'):
            continue
        f = ROOT / v['file']
        if not f.exists():
            continue
        t = f.read_text(encoding='utf-8')
        h = re.search(r'<h1 class="lt-dear"[^>]*>(.*?)</h1>', t, re.S)
        ex = re.search(r'<!-- Excerpt: (.*?) -->', t, re.S)
        if not h:
            raise SystemExit('%s: no "Dear <nation>," heading' % v['file'])
        name = html.unescape(re.sub(r'<[^>]+>', '', h.group(1))).strip()
        name = re.sub(r'^Dear\s+', '', name).rstrip(',').strip()
        out.append({'root': root, 'code': root.rsplit('-', 1)[1].upper(), 'file': f, 'url': v['url'], 'name': name,
                    'excerpt': html.unescape(ex.group(1)).strip() if ex else ''})
    out.sort(key=lambda e: sort_key(e['name']))
    return out


def card(e, kind, r):
    label = '&#8592; Previous Letter' if kind == 'prev' else 'Next Letter &#8594;'
    ex = ('<span class="lt-mex">%s</span>' % words(e['excerpt'])) if e['excerpt'] else ''
    return ('<a class="lt-mcard lt-mcard--%s" href="%s" rel="%s" aria-label="%s: Dear %s">'
            '<span class="lt-mseal" aria-hidden="true"><b>%s</b></span>'
            '<span class="lt-mct"><small>%s</small><strong>Dear %s</strong>%s</span></a>'
            % (kind, html.escape(e['url'], quote=True), r, label.replace('&#8592; ', '').replace(' &#8594;', ''),
               words(e['name']), e['code'], label, words(e['name']), ex))


def band(root, prev, nxt, count):
    R = '#' + root
    hide = ','.join('body:has(%s) %s' % (R, s) for s in (
        '.ast-single-related-posts-container', '.ast-related-posts-wrapper', '.ast-related-posts-title-section',
        '.post-navigation', '.navigation.post-navigation', '.ast-post-navigation', '#jp-relatedposts', '.jp-relatedposts'))
    css = (
        hide + '{ display:none !important; }\n'
        + '%s .lt-more{ max-width:860px; margin:clamp(40px,6vh,64px) auto 0; }\n'
        '%s .lt-more-hd{ display:flex; align-items:center; gap:16px; margin:0; font-family:var(--hd); font-size:.78rem; font-weight:700; letter-spacing:.22em; text-transform:uppercase; color:var(--idm); }\n'
        '%s .lt-more-hd::before,%s .lt-more-hd::after{ content:""; flex:1; height:1px; background:var(--ihair); }\n'
        '%s .lt-more-grid{ display:grid; grid-template-columns:1fr 1fr; gap:16px; margin-top:18px; }\n'
        '%s a.lt-mcard{ position:relative; display:flex; align-items:center; gap:18px; min-width:0; padding:20px 22px; border-radius:6px; border:1px solid rgba(26,20,12,.1); text-decoration:none; color:var(--ink); '
        'background:radial-gradient(120% 90% at 0% 0%, rgba(160,110,40,.1) 0%, transparent 45%), linear-gradient(180deg,#F7EFDE 0%,#EFE3C8 100%); '
        'box-shadow:0 1px 0 rgba(255,255,255,.6) inset, 0 10px 24px -14px rgba(60,40,10,.45); transition:transform .35s cubic-bezier(.2,.7,.2,1), box-shadow .35s ease; }\n'
        '%s a.lt-mcard:hover{ transform:translateY(-4px); box-shadow:0 1px 0 rgba(255,255,255,.6) inset, 0 22px 34px -16px rgba(60,40,10,.55); }\n'
        '%s a.lt-mcard--next{ flex-direction:row-reverse; text-align:right; }\n'
        '%s .lt-mseal{ display:flex; align-items:center; justify-content:center; flex:none; width:58px; height:58px; border-radius:50%%; '
        'background:radial-gradient(60%% 60%% at 35%% 30%%, #C2452E 0%%, #8A2418 70%%, #5E140C 100%%); '
        'box-shadow:inset 0 0 0 3px rgba(0,0,0,.18), inset 0 0 0 5px rgba(255,220,180,.18), 0 6px 14px rgba(80,20,10,.32); transition:transform .45s cubic-bezier(.2,.7,.2,1); }\n'
        '%s a.lt-mcard:hover .lt-mseal{ transform:rotate(-10deg) scale(1.06); }\n'
        '%s .lt-mseal b{ font-family:var(--hd); font-size:1.3rem; font-weight:600; line-height:1; letter-spacing:.02em; color:#F5E6C0; }\n'
        '%s .lt-mct{ display:flex; flex-direction:column; min-width:0; }\n'
        '%s .lt-mct small{ font-family:var(--hd); font-size:.72rem; font-weight:700; letter-spacing:.18em; text-transform:uppercase; color:#7E5A0C; }\n'
        '%s .lt-mct strong{ margin-top:4px; font-family:"Caveat","Segoe Script","Bradley Hand","Brush Script MT",cursive; font-weight:600; font-size:1.85rem; line-height:1.02; color:#1A140C; overflow-wrap:anywhere; }\n'
        '%s .lt-mex{ display:-webkit-box; -webkit-line-clamp:2; -webkit-box-orient:vertical; overflow:hidden; margin-top:6px; font-family:var(--sf); font-style:italic; font-size:.9rem; line-height:1.45; color:var(--idm); }\n'
        '%s .lt-more-all{ display:flex; justify-content:center; margin-top:20px; }\n'
        '@media (max-width:640px){ %s .lt-more{ margin-top:36px; } %s .lt-more-hd{ font-size:.66rem; letter-spacing:.16em; gap:10px; } %s .lt-more-grid{ gap:10px; margin-top:14px; } '
        '%s a.lt-mcard{ flex-direction:column; align-items:flex-start; gap:10px; padding:14px 12px; } %s a.lt-mcard--next{ flex-direction:column; align-items:flex-end; } '
        '%s .lt-mseal{ width:42px; height:42px; } %s .lt-mseal b{ font-size:1rem; } %s .lt-mct small{ font-size:.6rem; letter-spacing:.14em; } '
        '%s .lt-mct strong{ font-size:1.4rem; } %s .lt-mex{ display:none; } %s .lt-more-all{ margin-top:14px; } }\n'
        '@media (prefers-reduced-motion:reduce){ %s a.lt-mcard,%s .lt-mseal{ transition:none; } %s a.lt-mcard:hover,%s a.lt-mcard:hover .lt-mseal{ transform:none; } }\n'
    ).replace('%s', R).replace('%%', '%')
    return ('<!--pn:more-letters v%s (25 Nov 2026): written by tools/letters_band.py from pages/manifest.json; never edit by hand-->\n'
            '<style>\n%s</style>\n'
            '<nav class="lt-more" aria-label="More Letters to the Nations">\n'
            '  <p class="lt-more-hd">More Letters to the Nations</p>\n'
            '  <div class="lt-more-grid">\n    %s\n    %s\n  </div>\n'
            '  <div class="lt-more-all"><a class="lt-btn lt-btn--line" href="%s">All %d Letters to the Nations</a></div>\n'
            '</nav>\n'
            '<!--/pn:more-letters-->\n'
            % (BASE, css, card(prev, 'prev', 'prev'), card(nxt, 'next', 'next'), ALL_URL, count))


def place(t, root, b):
    t = BAND.sub('', t)
    i = t.rstrip().rfind('</div>')
    if i < 0 or ('<div id="%s">' % root) not in t:
        raise SystemExit('%s: the page root was not found' % root)
    return t[:i] + b + t[i:]


def run(man, before=None):
    """Write the band into every Letter. Returns the roots whose page now differs from `before` (root -> earlier
    text; a Letter missing from it is compared with its page on disk before this run)."""
    ls = letters(man)
    changed = []
    for i, e in enumerate(ls):
        old = e['file'].read_text(encoding='utf-8')
        new = asc(place(old, e['root'], band(e['root'], ls[i - 1], ls[(i + 1) % len(ls)], len(ls))))
        if new != old:
            e['file'].write_text(new, encoding='utf-8')
        ref = (before or {}).get(e['root'], old)
        if new != ref:
            changed.append(e['root'])
    return changed


def main():
    mpath = PAGES / 'manifest.json'
    mtxt = mpath.read_text(encoding='utf-8')
    man = json.loads(mtxt)
    changed = run(man)
    print('%d Letters, %d pages changed' % (len([k for k in man['pages'] if k.startswith('pn-letter-')]), len(changed)))
    if '--manifest' in sys.argv and changed:
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        from build_letters import dump_like
        for r in changed:
            man['pages'][r]['version'] = bump(man['pages'][r].get('version'))
        mpath.write_text(dump_like(man, mtxt), encoding='utf-8')
        print('pages/manifest.json: %d versions raised' % len(changed))


if __name__ == '__main__':
    main()
