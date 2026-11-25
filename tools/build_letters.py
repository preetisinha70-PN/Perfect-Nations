#!/usr/bin/env python3
"""Build the full Letters to the Nations (pages/letter-dear-<slug>.html) for the blueprints that become full editions.

Letters v8.2 (25 November 2026); v8.3 adds the More Letters band (tools/letters_band.py). The first 44 letters are hand files; this script writes the next ones in the same
design (the CSS, the header and the WordPress fallback of pages/letter-dear-kenya.html, v8.1.3), so a Letter reads the
same whichever nation it is written to. Brief: Project doc claude/full-blueprints-151.md (Preeti Sinha, President and
CEO, 24 Nov 2026: "We need to develop each of the 195 blueprints as a full blueprint").

Each Letter is built from:
  tools/nation/<slug>.json   the opening paragraph and the quotation (the Letter already on the blueprint)
  tools/letters/words.json   what the nation has already built (one paragraph, every figure from its blueprint) and
                             the sources of that paragraph, and its two-letter code (the seal and the page root)
  data/<slug>.json           the work ahead: the three standards furthest from reach, with their sourced figures,
                             and the five Sovereign Assets for the closing paragraph
The page root is #pn-letter-<code>; the WordPress post (slug dear-<slug>, category Letter To The Nations, one Custom
HTML block holding <div id="pn-letter-<code>"> and a fallback line) is published only after the pull request is merged.

    python3 tools/build_letters.py                 build every nation in tools/letters/words.json
    python3 tools/build_letters.py benin chad      build these only
    python3 tools/build_letters.py --posts         also write tools/letters/posts.json: for each Letter, the WordPress
                                                   post to publish after the merge (title, slug, category 643, excerpt,
                                                   one Custom HTML block with the root and a fallback line, and the meta
                                                   that keeps Jetpack from emailing subscribers)
    python3 tools/build_letters.py --manifest      also add or raise pn-letter-<code> in pages/manifest.json and set
                                                   the letter link (letter.url) in tools/nation/<slug>.json
Each run ends by writing the "More Letters to the Nations" band into every Letter (tools/letters_band.py); with
--manifest it raises the version of every Letter whose page changed.
Then: python3 tools/check_page.py pages/letter-dear-*.html, and python3 tools/build_nations.py --manifest so each
blueprint shows "Read the full letter". Never edit a built letter by hand; change the words and build again.
"""
import html
import json
import re
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PAGES, DATA, HERE = ROOT / 'pages', ROOT / 'data', ROOT / 'tools'
VERSION = '8.2'
TEMPLATE = PAGES / 'letter-dear-kenya.html'
TEMPLATE_ROOT = 'pn-letter-ke'
ORDER = ['Food', 'Water', 'Shelter', 'Energy', 'Education', 'Health', 'Livelihoods']
SHOW = {'Livelihoods': 'Livelihood'}


def ent(s):
    return html.escape(s or '', quote=True).replace('&#x27;', '&#8217;')


def text(s):
    """Plain words to HTML: escape, then curly apostrophes and quotation marks as the hand letters write them."""
    s = ent(s)
    return s.replace('&#8217;', '&#8217;').replace('’', '&#8217;').replace('“', '&#8220;').replace('”', '&#8221;').replace('—', '&#8212;')


def style(root):
    t = TEMPLATE.read_text(encoding='utf-8')
    font = re.search(r'<link rel="stylesheet" href="https://fonts\.googleapis\.com/css2\?family=Caveat[^>]*>', t).group(0)
    css = re.search(r'<style>.*?</style>', t, re.S).group(0)
    assert TEMPLATE_ROOT in css
    return font, css.replace(TEMPLATE_ROOT, root)


def lower_first(s):
    return s if re.match(r'^(\d|WHO|US\$|UN)', s) else s[:1].lower() + s[1:]


def plain_note(g):
    """One standard's figure as a clause a reader can follow, from its note in data/<slug>.json."""
    n, disp = (g.get('note') or '').strip(), (g.get('display') or '').strip()
    n = re.sub(r';\s*\d{4},\s*dated$', '', n)
    n = re.sub(r',\s*dated$', '', n)
    n = re.sub(r'\s*\(\d{4}\)', '', n)
    n = n.replace('; safely managed sanitation is not measured', '')
    n = n.replace('against the Living Line of 1,000', 'against the 1,000 a decent life needs')
    n = re.sub(r'^About ([\d,.]+) kWh of electricity a person a year', r'each of you uses about \1 kWh of electricity a year', n)
    if n.startswith('Not food insecure; '):
        n = n[len('Not food insecure; '):]
    m = re.match(r'^Above (.+?); ([\d.]+%) live below it$', n)
    if m:
        n = '%s live below %s' % (m.group(2), m.group(1))
    if n.startswith('City dwellers outside slums; '):
        n = n[len('City dwellers outside slums; '):].replace('live in slums', 'of city dwellers live in slums')
    if n == 'Safely managed drinking water':
        n = '%s have safely managed drinking water' % disp
    elif n.startswith('Safely managed sanitation'):
        n = '%s have safely managed sanitation%s' % (disp, n[len('Safely managed sanitation'):])
    elif n == 'WHO service coverage index':
        n = 'the WHO service coverage index stands at %s' % disp
    n = n.replace('; ', ', and ')
    return '%s (%s)' % (lower_first(n), g.get('source') or '')


def work_ahead(d):
    gs = [g for g in d['guarantees'] if isinstance(g.get('value'), (int, float))]
    gs.sort(key=lambda g: (g['value'], ORDER.index(g['name']) if g['name'] in ORDER else 9))
    a, b, c = gs[0], gs[1], gs[2]
    nm = lambda g: SHOW.get(g['name'], g['name'])
    s = ('The work ahead is plain, and it is worth saying plainly. %s sets your Coverage today: %s. %s and %s come next: %s; and %s. '
         'Each of them is within your reach.' % (nm(a), plain_note(a), nm(b), nm(c).lower(), plain_note(b), plain_note(c)))
    return s, [x for x in (a, b, c)]


def assets_phrase(d):
    names = [x['name'] for x in d['assets']['items'] if x.get('name')]
    parts = ['your ' + (n[4:] if n.startswith('The ') else n).lower() for n in names]
    s = ', '.join(parts[:-1]) + ' and ' + parts[-1] if len(parts) > 1 else parts[0]
    return s[:1].upper() + s[1:]


def imagine(name, d, lead):
    return ('%s: a morning when every family eats well and drinks clean water from a tap; when every home is sound and lit, '
            'and every meal is cooked on clean fuel; when every child walks to a school where a teacher is waiting, and reads with '
            'ease by the age of ten; when every mother lives a short walk from a clinic with a nurse on duty; and when every adult '
            'earns a decent living. None of this needs a miracle. %s are assets no balance sheet counts, and together they can carry '
            'every one of your citizens to food, water, shelter, energy, education, health and a livelihood.'
            % (lead % name, assets_phrase(d)))


def dump_like(obj, original):
    """JSON written in the same layout as the file it replaces: one line, or indented by the same number of spaces."""
    lines = original.rstrip('\n').split('\n')
    if len(lines) == 1:
        return json.dumps(obj, ensure_ascii=False) + '\n'
    return json.dumps(obj, ensure_ascii=False, indent=len(lines[1]) - len(lines[1].lstrip(' '))) + '\n'


def first_sentence(s):
    m = re.match(r'^(.+?[.!?])(\s|$)', s)
    return m.group(1) if m else s


def build(slug, w, man, today):
    d = json.loads((DATA / ('%s.json' % slug)).read_text(encoding='utf-8'))
    p = json.loads((HERE / 'nation' / ('%s.json' % slug)).read_text(encoding='utf-8'))
    name, code = d['nation'], w['iso2'].upper()
    root = 'pn-letter-%s' % code.lower()
    opening = p['letter']['paras'][0]
    if '…' in opening or '<' in opening:
        raise SystemExit('%s: the opening of the Letter is shortened or holds markup; write it in full first' % slug)
    ahead, used = work_ahead(d)
    paras = [opening, w['built'], ahead, imagine(name, d, w.get('imagine_lead') or 'Now imagine Perfect %s')]
    invite = ('So this is an invitation. Bring your vision, your story and your solutions to the Perfect %s ReDesign Studio, '
              'and join the Co-designers who are already imagining what comes next. Perfect %s will not be designed for you. '
              'It will be designed by you.' % (name, name))
    bp = (man['pages'].get(p['root']) or {}).get('url') or 'https://perfectnations.com/blueprints/%s/' % slug
    src, seen = [], set()
    for label, url in [tuple(x) for x in w['sources']] + [('%s: %s' % (g.get('source'), SHOW.get(g['name'], g['name']).lower()), g.get('url')) for g in used]:
        if url and url.startswith('https://') and url not in seen:
            seen.add(url)
            src.append('<a href="%s" target="_blank" rel="noopener noreferrer">%s</a>' % (ent(url), text(label)))
    src.append('<a href="%s#bp-sources" target="_blank" rel="noopener noreferrer">every other figure: the %s blueprint</a>' % (ent(bp), text(name)))
    font, css = style(root)
    head = ('<!-- PERFECT NATIONS . LETTERS TO THE NATIONS . DEAR %s . v8 LETTER . %s . v%s (%s): built by tools/build_letters.py in the design of the '
            'hand letters (v8.1.3): never edit by hand . The letterhead carries the registered mark, Perfect Nations&#174; . Signed by Preeti Sinha, '
            'President and CEO . WordPress post, slug dear-%s, category Letters to the Nations, one Custom HTML block -->\n'
            '<!-- Excerpt: %s -->\n' % (name.upper(), today, VERSION, today, slug, first_sentence(opening)))
    body = ''.join('    <p class="lt-p">%s</p>\n' % text(x) for x in paras)
    out = (head + font + '\n' + css + '\n\n'
           '<div id="%s">\n'
           '  <a class="lt-back" href="%s" target="_blank" rel="noopener noreferrer">The %s blueprint</a>\n'
           '  <article class="lt-sheet" aria-labelledby="lt-dear">\n'
           '    <div class="lt-lh"><span>Perfect Nations&#174; &middot; Letters to the Nations</span><span>%s</span></div>\n'
           '    <h1 class="lt-dear" id="lt-dear">Dear %s,</h1>\n'
           '%s'
           '    <blockquote class="lt-q">%s</blockquote>\n'
           '    <p class="lt-p">%s</p>\n'
           '    <div class="lt-sig">\n'
           '      <div><p>Yours in design,</p><b>Preeti Sinha</b><p style="font-size:.92rem;margin-top:4px;">President and CEO, Perfect Nations</p></div>\n'
           '      <span class="lt-seal" aria-hidden="true"><i>Letter</i><b>%s</b></span>\n'
           '    </div>\n'
           '  </article>\n'
           '  <p class="lt-src">Sources: %s</p>\n'
           '  <div class="lt-next">\n'
           '    <a class="lt-btn" href="%s#bp-studio" target="_blank" rel="noopener noreferrer">Enter the ReDesign Studio</a>\n'
           '    <a class="lt-btn lt-btn--line" href="%s" target="_blank" rel="noopener noreferrer">Read the %s blueprint</a>\n'
           '  </div>\n'
           '</div>\n'
           % (root, ent(bp), text(name), text(name), text(name), body, text(p['letter']['quote']), text(invite), code,
              ' &middot; '.join(src), ent(bp), ent(bp), text(name)))
    out = out.encode('ascii', 'xmlcharrefreplace').decode('ascii')  # the pages are plain ASCII, as the checks require
    f = PAGES / ('letter-dear-%s.html' % slug)
    f.write_text(out, encoding='utf-8')
    return f, root, name


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    words = json.loads((HERE / 'letters' / 'words.json').read_text(encoding='utf-8'))
    slugs = args or [k for k in words if not k.startswith('_')]
    mpath = PAGES / 'manifest.json'
    mtxt = mpath.read_text(encoding='utf-8')
    man = json.loads(mtxt)
    today = date.today().isoformat()
    posts = []
    before = {}
    for slug in slugs:
        r = 'pn-letter-%s' % words[slug]['iso2'].lower()
        f = PAGES / ('letter-dear-%s.html' % slug)
        before[r] = f.read_text(encoding='utf-8') if f.exists() else ''
    for slug in slugs:
        f, root, name = build(slug, words[slug], man, today)
        bp = 'https://perfectnations.com/blueprints/%s/' % slug
        opening = json.loads((HERE / 'nation' / ('%s.json' % slug)).read_text(encoding='utf-8'))['letter']['paras'][0]
        posts.append({'title': 'Dear %s' % name, 'slug': 'dear-%s' % slug, 'status': 'publish', 'categories': [643],
                      'excerpt': first_sentence(opening),
                      'content': '<!-- wp:html -->\n<div id="%s"><p>Dear %s, the full letter from Perfect Nations is loading. '
                                 '<a href="%s">Read the %s blueprint</a>.</p></div>\n<!-- /wp:html -->' % (root, ent(name), bp, ent(name)),
                      'meta': {'_jetpack_dont_email_post_to_subs': '1'}})
        print('%s: %d characters' % (f.relative_to(ROOT), len(f.read_text(encoding='utf-8'))))
        if '--manifest' in sys.argv:
            url = 'https://perfectnations.com/dear-%s/' % slug
            man['pages'][root] = {'file': 'pages/letter-dear-%s.html' % slug, 'version': (man['pages'].get(root) or {}).get('version') or VERSION,
                                  'title': 'Letter: Dear %s' % name, 'url': url}
            np_ = HERE / 'nation' / ('%s.json' % slug)
            nt = np_.read_text(encoding='utf-8')
            nj = json.loads(nt)
            if nj['letter'].get('url') != url:
                nj['letter']['url'] = url
                np_.write_text(dump_like(nj, nt), encoding='utf-8')
    sys.path.insert(0, str(HERE))
    import letters_band
    changed = letters_band.run(man, before)
    print('More Letters band: %d Letter pages changed' % len(changed))
    if '--manifest' in sys.argv:
        for r in changed:
            man['pages'][r]['version'] = letters_band.bump(man['pages'][r].get('version'))
    if '--posts' in sys.argv:
        (HERE / 'letters' / 'posts.json').write_text(json.dumps({'about': 'WordPress posts for the Letters built by tools/build_letters.py. Publish each only after the pull request that adds its page is merged (Settings > Perfect Nations Live > Refresh now, then LiteSpeed Cache > Purge All).', 'posts': posts}, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        print('tools/letters/posts.json: %d posts' % len(posts))
    if '--manifest' in sys.argv:
        mpath.write_text(dump_like(man, mtxt), encoding='utf-8')
        print('pages/manifest.json: %d letters' % len([k for k in man['pages'] if k.startswith('pn-letter-')]))


if __name__ == '__main__':
    main()
