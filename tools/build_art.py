#!/usr/bin/env python3
"""Build the one-file Art of Nations page (the Perfect Nations Gallery), pages/art-of-nations.html.

    python3 tools/build_art.py

The page is perfectnations.org/perfect-nations-gallery/ (page 16839). Its Elementor Custom HTML widget
already contains the root id pn-art, so the Perfect Nations Live Pages plugin serves this file in its
place. Nothing is pasted.

Two inputs, one output:
  art/catalogue.json               the works: paintings and books, their words, images and links
  art/art-of-nations.template.html the design: style, markup and script, with [[SLOTS]]
  pages/art-of-nations.html        BUILT here; never edit it by hand

To add a painting, add one entry to "paintings" in the catalogue (newest last), raise "version",
run this build, run tools/check_page.py, preview with tools/preview_art.py, raise pn-art in
pages/manifest.json and open a pull request "For approval: Art of Nations vX.Y, [what changed]".
The build refuses: straight apostrophes or contractions in the copy, image URLs outside the Media
Library, a missing field, and any non-ASCII character in the result.
"""
import html
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CAT = ROOT / 'art' / 'catalogue.json'
TPL = ROOT / 'art' / 'art-of-nations.template.html'
OUT = ROOT / 'pages' / 'art-of-nations.html'
MEDIA = 'https://perfectnations.org/wp-content/uploads/'
DEFAULT_STATUS = 'Available by private enquiry'
CONTRACTION = re.compile(r"\b\w+(n['’]t|['’](re|ve|ll|d|m))\b|\b(it|that|there|here|what|who|let)['’]s\b", re.I)
PROBLEMS = []


def esc(s):
    """HTML-escape and turn every non-ASCII character into an entity."""
    return html.escape(str(s), quote=True).encode('ascii', 'xmlcharrefreplace').decode('ascii')


def copy(where, s):
    """Copy a visitor reads: no straight apostrophes, no contractions."""
    s = str(s or '')
    if "'" in s:
        PROBLEMS.append('%s: a straight apostrophe (use ’): %r' % (where, s))
    m = CONTRACTION.search(s)
    if m:
        PROBLEMS.append('%s: a contraction: %r' % (where, m.group(0)))
    return esc(s)


def media(where, url):
    if not isinstance(url, str) or not url.startswith(MEDIA) or re.search(r'[\s"\'<>()]', url):
        PROBLEMS.append('%s: image must be a Media Library URL (%s...): %r' % (where, MEDIA, url))
    return esc(url)


def link(where, url):
    if not isinstance(url, str) or not url.startswith('https://') or re.search(r'[\s"\'<>()]', url):
        PROBLEMS.append('%s: link must start with https:// and hold no quotes, brackets or spaces: %r' % (where, url))
    return esc(url)


def need(obj, where, *keys):
    for k in keys:
        if not obj.get(k):
            PROBLEMS.append('%s: missing "%s"' % (where, k))


def swatch(colours):
    cs = [c for c in colours if re.fullmatch(r'#[0-9A-Fa-f]{6}', c)]
    if not cs:
        return '--sw:#999999'
    step = 100.0 / len(cs)
    stops = ['%s %.2f%% %.2f%%' % (c, i * step, (i + 1) * step) for i, c in enumerate(cs)]
    return '--sw:linear-gradient(90deg,%s)' % ','.join(stops)


def srcset(where, images):
    if any(int(w) > 800 for _, w in images):
        PROBLEMS.append('%s: images lists a copy wider than 768 px; keep larger copies for zoom only' % where)
    parts = []
    for pair in images:
        url, w = pair
        parts.append('%s %dw' % (media(where, url), int(w)))
    return ', '.join(parts)


def pick(images, width):
    """The smallest copy at least `width` wide, else the largest."""
    ok = [p for p in images if int(p[1]) >= width]
    return (min(ok, key=lambda p: int(p[1])) if ok else max(images, key=lambda p: int(p[1])))[0]


def card(i, p, cat):
    where = 'painting %s' % p.get('slug', i)
    need(p, where, 'slug', 'nation', 'title', 'statement', 'alt', 'spec', 'enquire', 'images', 'zoom', 'colours')
    if PROBLEMS and not p.get('images'):
        return ''
    enquire = link(where, cat['contact'] + '?about=' + p['enquire'])
    buy = link(where, p['buy_url']) if p.get('buy_url') else ''
    price = copy(where, p.get('price', ''))
    status = p.get('status') or DEFAULT_STATUS
    sw = swatch(p['colours'])
    acts = []
    if buy:
        acts.append('<a class="aon-btn aon-btn--sm" href="%s">Buy</a>' % buy)
        acts.append('<a class="aon-btn aon-btn--sm aon-btn--line" href="%s">Enquire</a>' % enquire)
    else:
        acts.append('<a class="aon-btn aon-btn--sm" href="%s">Enquire</a>' % enquire)
    extra = ''
    if price:
        extra += '\n        <p class="aon-price">%s</p>' % price
    if status != DEFAULT_STATUS:
        extra += '\n        <p class="aon-chip">%s</p>' % copy(where, status)
    data = {
        'nation': copy(where, p['nation']), 'title': copy(where, p['title']), 'statement': copy(where, p['statement']),
        'spec': copy(where, p['spec']), 'alt': copy(where, p['alt']), 'zoom': media(where, p['zoom']),
        'src': media(where, pick(p['images'], 768)), 'srcset': srcset(where, p['images']), 'sw': esc(sw[5:]),
        'enquire': enquire, 'buy': buy, 'price': price,
    }
    attrs = ' '.join('data-%s="%s"' % (k, v) for k, v in data.items() if v != '')
    return '''      <article class="aon-card aon-rv" id="aon-%(slug)s" %(attrs)s>
        <a class="aon-frame" href="%(zoom)s" data-open="%(i)d" aria-label="Open %(title)s at full size"><span class="aon-mat"><span class="aon-pic"><img src="%(src)s" srcset="%(srcset)s" sizes="(min-width:1100px) 250px, (min-width:600px) 44vw, 44vw" alt="%(alt)s" width="600" height="600" loading="lazy" decoding="async"></span></span></a>
        <p class="aon-nation"><i class="aon-sw" style="%(sw)s"></i>%(nation)s</p>
        <h3 class="aon-h3">%(title)s</h3>
        <p class="aon-stmt">%(statement)s</p>%(extra)s
        <div class="aon-acts">%(acts)s</div>
      </article>''' % {
        'slug': esc(p['slug']), 'attrs': attrs, 'zoom': data['zoom'], 'i': i, 'title': data['title'],
        'src': media(where, pick(p['images'], 600)), 'srcset': data['srcset'], 'alt': data['alt'], 'sw': esc(sw),
        'nation': data['nation'], 'statement': data['statement'], 'extra': extra, 'acts': ''.join(acts),
    }


def book(b, cat):
    where = 'book %s' % b.get('slug', '?')
    need(b, where, 'slug', 'title', 'tag', 'copy', 'spec', 'status', 'enquire', 'cover', 'cover_alt')
    if not b.get('cover'):
        return ''
    reserve = link(where, cat['contact'] + '?about=' + b['enquire'])
    buy = link(where, b['buy_url']) if b.get('buy_url') else ''
    spec = b['spec'] if b['status'] == b['tag'] else b['spec'] + ' · ' + b['status']
    pages = b.get('pages') or []
    items = ''.join('<li data-src="%s">%s</li>' % (media(where, u), copy(where, c)) for u, c in pages)
    acts = []
    if pages:
        acts.append('<button class="aon-btn aon-btn--sm aon-btn--line" type="button" data-look>Look inside <small>%d</small></button>' % len(pages))
    if buy:
        acts.append('<a class="aon-btn aon-btn--sm" href="%s">Buy</a>' % buy)
    else:
        acts.append('<a class="aon-btn aon-btn--sm" href="%s">Reserve a copy</a>' % reserve)
    price = ('\n          <p class="aon-price" style="color:var(--g)">%s</p>' % copy(where, b['price'])) if b.get('price') else ''
    obj = ('<button class="aon-bk__obj" type="button" data-look aria-label="Look inside %s">' % copy(where, b['title'])) if pages else '<span class="aon-bk__obj">'
    end = '</button>' if pages else '</span>'
    return '''      <article class="aon-bk aon-rv" id="aon-%(slug)s" data-book="%(title)s" data-enquire="%(reserve)s">
        %(obj)s<span class="aon-bk__book"><img src="%(src)s" srcset="%(srcset)s" sizes="(min-width:900px) 230px, 36vw" alt="%(alt)s" width="600" height="600" loading="lazy" decoding="async"></span>%(end)s
        <div class="aon-bk__txt">
          <p class="aon-tag">%(tag)s</p>
          <h3 class="aon-h3">%(title)s</h3>
          <p class="aon-stmt">%(copy)s</p>
          <p class="aon-spec">%(spec)s</p>%(price)s
        </div>
        <div class="aon-acts">%(acts)s</div>
        <ol class="aon-pages" hidden>%(items)s</ol>
      </article>''' % {
        'slug': esc(b['slug']), 'title': copy(where, b['title']), 'reserve': buy or reserve, 'obj': obj, 'end': end,
        'src': media(where, pick(b['cover'], 600)), 'srcset': srcset(where, b['cover']), 'alt': copy(where, b['cover_alt']),
        'tag': copy(where, b['tag']), 'copy': copy(where, b['copy']), 'spec': copy(where, spec), 'price': price,
        'acts': ''.join(acts), 'items': items,
    }


def main():
    cat = json.loads(CAT.read_text(encoding='utf-8'))
    tpl = TPL.read_text(encoding='utf-8')
    need(cat, 'catalogue', 'version', 'updated', 'series_total', 'contact', 'paintings')
    link('catalogue contact', cat.get('contact', ''))
    paintings = cat.get('paintings') or []
    total = int(cat.get('series_total') or 195)
    n = len(paintings)
    slugs = [p.get('slug') for p in paintings]
    if len(set(slugs)) != len(slugs):
        PROBLEMS.append('two paintings share a slug: %r' % slugs)
    cards = '\n'.join(card(i, p, cat) for i, p in enumerate(paintings))
    books = '\n'.join(book(b, cat) for b in cat.get('books') or [])
    dots = ''.join('<i class="on is-new"></i>' if k == n - 1 else ('<i class="on"></i>' if k < n else '<i></i>') for k in range(total))
    first = paintings[0] if paintings else {}
    if PROBLEMS:
        sys.exit('The catalogue needs fixing before the page can be built:\n  - ' + '\n  - '.join(PROBLEMS))
    slots = {
        'VERSION': esc(cat['version']), 'DATE': esc(cat['updated']), 'COUNT': str(n), 'COUNT2': '%02d' % n,
        'TOTAL': str(total), 'DOTS': dots, 'CARDS': cards, 'BOOKS': books, 'CONTACT': esc(cat['contact']),
        'FIRST_ZOOM': esc(first['zoom']), 'FIRST_SRC': esc(pick(first['images'], 768)),
        'FIRST_SRCSET': srcset('hero', first['images']), 'FIRST_ALT': esc(first['alt']),
        'FIRST_TITLE': esc(first['title']), 'FIRST_NATION': esc(first['nation']), 'FIRST_SW': esc(swatch(first['colours'])),
    }
    out = tpl
    for k, v in slots.items():
        out = out.replace('[[%s]]' % k, v)
    left = re.findall(r'\[\[[A-Z0-9_]+\]\]', out)
    if left:
        sys.exit('slots left unfilled: %r' % sorted(set(left)))
    first_id = re.search(r'\bid\s*=\s*["\'](pn-[a-z0-9-]+)["\']', out, re.I)
    if not first_id or first_id.group(1) != 'pn-art':
        sys.exit('the first pn- id must be pn-art, found %s' % (first_id.group(1) if first_id else None))
    if re.search(r'\bid\s*=\s*["\']pn-(?!art["\'])', out):
        sys.exit('only the root may use an id starting pn- (the Live Pages plugin reads them)')
    bad = [(i, c) for i, c in enumerate(out) if ord(c) > 126]
    if bad:
        sys.exit('non-ASCII characters in the result: %r' % bad[:5])
    OUT.write_text(out, encoding='utf-8')
    print('%s: v%s, %d paintings, %d books, %d characters' % (OUT.relative_to(ROOT), cat['version'], n, len(cat.get('books') or []), len(out)))


if __name__ == '__main__':
    main()
