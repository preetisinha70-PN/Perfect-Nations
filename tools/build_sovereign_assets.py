#!/usr/bin/env python3
"""Build the one-file Sovereign Assets page and its live ledger file.

Kept by the Sovereign Assets Steward (skill steward-sovereign-assets).

  python3 tools/build_sovereign_assets.py            count the ledger, write data/sovereign-assets.json
                                                    and pages/sovereign-assets.html, then validate
  python3 tools/build_sovereign_assets.py --data     only refresh data/sovereign-assets.json (the weekly run:
                                                    the page reads this file live, so no pull request)
  python3 tools/build_sovereign_assets.py --check    validate pages/sovereign-assets.html and the data file only

The page is pasted once in WordPress (page 15125, /sovereign-assets/) with root id pn-sov; the Perfect
Nations Live Pages plugin serves pages/sovereign-assets.html in its place. Never edit that file by
hand: edit pages/sovereign-assets-src.html (design) or the "featured" list in
data/sovereign-assets.json (the five assets), then run this script.
"""
import base64
import html
import json
import math
import re
import subprocess
import sys
import tempfile
from datetime import date
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PAGES = ROOT / 'pages'
DATA = ROOT / 'data'
SRC = PAGES / 'sovereign-assets-src.html'
OUT = PAGES / 'sovereign-assets.html'
LEDGER = DATA / 'sovereign-assets.json'
MASK = ROOT / 'assets' / 'home' / 'pn-globe-water-1024.jpg'
NOT_NATIONS = {'state-of-nations', 'ticker', 'sovereign-assets'}
FLAGS = 'https://cdn.jsdelivr.net/npm/flag-icons@7.6.0/flags/1x1/'
UPLOADS = 'https://perfectnations.org/wp-content/uploads/'

# The eight asset classes, each with its colour from the garden painting (art only, never text).
CLASSES = {
    'Water & Rivers': '#5DB5E8', 'Ocean & Coast': '#2350D8', 'Position & Institutions': '#A9C8F5',
    'Beneath the Ground': '#E0352B', 'People': '#F2836B', 'Sun, Wind & Power': '#F2C230',
    'Land & Harvest': '#6FA83C', 'Forest & Wild': '#2FB58C',
}

# Where each nation's lights sit on the golden planet (latitude, longitude of the nation's middle).
# A new nation file needs one line here; the build stops and says so if it is missing.
PLACES = {
    'afghanistan': (33.9, 67.7), 'angola': (-11.2, 17.9), 'bangladesh': (23.7, 90.4), 'barbados': (13.2, -59.5),
    'botswana': (-22.3, 24.7), 'brazil': (-10.3, -53.2), 'burundi': (-3.4, 29.9), 'colombia': (4.6, -74.3),
    'cote-divoire': (7.5, -5.5), 'dr-congo': (-2.9, 23.7), 'ecuador': (-1.8, -78.2), 'egypt': (26.8, 30.8),
    'eswatini': (-26.5, 31.5), 'ethiopia': (9.1, 40.5), 'fiji': (-17.7, 178.1), 'ghana': (7.9, -1.0),
    'india': (21.0, 78.0), 'indonesia': (-2.5, 118.0), 'jamaica': (18.1, -77.3), 'jordan': (31.2, 36.5),
    'kenya': (0.0, 37.9), 'lesotho': (-29.6, 28.2), 'madagascar': (-18.8, 46.9), 'malawi': (-13.3, 34.3),
    'mexico': (23.6, -102.5), 'morocco': (31.8, -7.1), 'mozambique': (-18.7, 35.5), 'namibia': (-22.9, 18.5),
    'nigeria': (9.1, 8.7), 'pakistan': (30.4, 69.3), 'philippines': (12.9, 121.8), 'republic-of-congo': (-0.2, 15.8),
    'rwanda': (-1.9, 29.9), 'senegal': (14.5, -14.5), 'somalia': (5.2, 46.2), 'south-africa': (-30.6, 22.9),
    'south-sudan': (6.9, 31.3), 'sri-lanka': (7.9, 80.8), 'tanzania': (-6.4, 34.9), 'uganda': (1.4, 32.3),
    'ukraine': (48.4, 31.2), 'vietnam': (14.1, 108.3), 'zambia': (-13.1, 27.8), 'zimbabwe': (-19.0, 29.2),
}

MONTHS = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October',
          'November', 'December']


def ent(s):
    """HTML-escape and write every character above ASCII as an entity, so the page stays ASCII."""
    s = html.escape(str(s), quote=True).replace('&#x27;', '&#8217;')
    return ''.join(c if ord(c) < 128 else '&#%d;' % ord(c) for c in s)


def long_date(iso):
    y, m, d = (int(x) for x in iso.split('-'))
    return '%d %s %d' % (d, MONTHS[m - 1], y)


def blueprint_urls():
    pages = json.loads((PAGES / 'manifest.json').read_text(encoding='utf-8'))['pages']
    return {k[len('pn-bp-'):]: v['url'] for k, v in pages.items() if k.startswith('pn-bp-')}


def count_ledger():
    """Count every Sovereign Asset card on the open blueprints (data/<nation>.json, assets.items)."""
    urls, nations, missing = blueprint_urls(), [], []
    for f in sorted(DATA.glob('*.json')):
        stem = f.stem
        if stem in NOT_NATIONS:
            continue
        d = json.loads(f.read_text(encoding='utf-8'))
        items = [a for a in ((d.get('assets') or {}).get('items') or []) if a.get('name') and a.get('figure')]
        if not items:
            continue
        if stem not in urls:
            missing.append('%s: no pn-bp-%s entry in pages/manifest.json' % (stem, stem))
            continue
        if stem not in PLACES:
            missing.append('%s: add its latitude and longitude to PLACES in this script' % stem)
            continue
        lat, lon = PLACES[stem]
        lead = items[0]
        top = {'name': lead['name'], 'figure': lead['figure'], 'label': lead.get('label') or '', 'money': bool(lead.get('money'))}
        nations.append({'file': stem, 'name': d.get('nation') or stem, 'url': urls[stem], 'assets': len(items),
                        'lat': lat, 'lon': lon, 'top': top})
    if missing:
        sys.exit('cannot count the ledger:\n  ' + '\n  '.join(missing))
    nations.sort(key=lambda n: n['name'])
    return {'assets': sum(n['assets'] for n in nations), 'nations': len(nations), 'classes': len(CLASSES)}, nations


def refresh_data():
    d = json.loads(LEDGER.read_text(encoding='utf-8'))
    ledger, nations = count_ledger()
    before = json.dumps([d.get('ledger'), d.get('nations'), d.get('classes')], sort_keys=True)
    d['ledger'], d['nations'], d['classes'] = ledger, nations, list(CLASSES)
    if json.dumps([ledger, nations, list(CLASSES)], sort_keys=True) != before:
        d['updated'] = date.today().isoformat()
    check_featured(d.get('featured'))
    LEDGER.write_text(json.dumps(d, indent=2, ensure_ascii=True) + '\n', encoding='utf-8')
    print('data/sovereign-assets.json: %d assets, %d nations, updated %s' % (ledger['assets'], ledger['nations'], d['updated']))
    return d


def check_featured(items):
    if not isinstance(items, list) or len(items) != 5:
        sys.exit('featured must hold exactly five assets')
    for f in items:
        for k in ('cls', 'figure', 'line', 'name', 'nation', 'text', 'source', 'url', 'link', 'image', 'image_small', 'alt'):
            if not isinstance(f.get(k), str) or not f[k].strip():
                sys.exit('featured %r: %s is missing' % (f.get('key'), k))
        if f['cls'] not in CLASSES:
            sys.exit('featured %r: class %r is not one of the eight' % (f.get('key'), f['cls']))
        for k in ('url', 'link', 'image', 'image_small'):
            if not re.match(r'^https://[^\s"\'<>()]+$', f[k]):
                sys.exit('featured %r: %s must be an https link with no quotes, brackets or spaces' % (f.get('key'), k))
        if not f['link'].startswith('https://perfectnations.org/'):
            sys.exit('featured %r: link must lead to a perfectnations.org blueprint' % f.get('key'))
        if not (f['image'].startswith(UPLOADS) and f['image_small'].startswith(UPLOADS)):
            sys.exit('featured %r: pictures come only from the Perfect Nations Media Library' % f.get('key'))
        if not f.get('flags') or not all(re.match(r'^[a-z]{2}$', c) for c in f['flags']):
            sys.exit('featured %r: flags must be two-letter country codes' % f.get('key'))
        for k in ('figure', 'line', 'name', 'nation', 'text', 'source'):
            if "'" in f[k] or '"' in f[k]:
                sys.exit('featured %r: use curly quotation marks in %s' % (f.get('key'), k))


def land_mask(step=2.5):
    """The land of the golden planet, as rows of bits (1 = land), sampled from the homepage water map."""
    from PIL import Image
    im = Image.open(MASK).convert('L')
    w, h = im.size
    rows, bits = [], []
    lat0 = 90 - step / 2
    for r in range(int(180 / step)):
        lat = lat0 - r * step
        n = max(1, int(math.floor(360 / step * math.cos(math.radians(lat)) + 0.5)))
        rows.append(n)
        for i in range(n):
            lon = -180 + (i + 0.5) * 360 / n
            x = min(w - 1, int((lon + 180) / 360 * w))
            y = min(h - 1, int((90 - lat) / 180 * h))
            bits.append(1 if im.getpixel((x, y)) < 128 else 0)
    raw = bytearray((len(bits) + 7) // 8)
    for k, b in enumerate(bits):
        if b:
            raw[k >> 3] |= 128 >> (k & 7)
    return {'lat0': lat0, 'step': step, 'rows': rows, 'bits': base64.b64encode(bytes(raw)).decode('ascii')}


def render_featured(items):
    out = []
    for i, f in enumerate(items, 1):
        sizes = '(min-width:900px) 820px, (min-width:641px) 92vw, 92vw' if i == 1 else '(min-width:900px) 820px, (min-width:641px) 23vw, 46vw'
        flags = ''.join('<img src="%s%s.svg" alt="" width="24" height="24" loading="lazy" decoding="async">' % (FLAGS, c) for c in f['flags'])
        unit = '<small>%s</small>' % ent(f['unit']) if f.get('unit') else ''
        out.append('''          <article class="sa-sc" id="sa-sc-%(i)d" style="--c:%(c)s;" aria-labelledby="sa-sc-%(i)d-h">
            <div class="sa-sc__ph"><img class="sa-sc__img" src="%(small)s" srcset="%(small)s 768w, %(big)s 1536w" sizes="%(sizes)s" width="1536" height="960" alt="%(alt)s" loading="lazy" decoding="async"><span class="sa-sc__n" aria-hidden="true">%(n)s</span></div>
            <div class="sa-sc__plate">
              <span class="sa-sc__cls">%(cls)s</span>
              <p class="sa-sc__fig"><b>%(fig)s</b>%(unit)s</p>
              <p class="sa-sc__line">%(line)s</p>
              <h3 class="sa-sc__h" id="sa-sc-%(i)d-h"><a href="%(link)s">%(name)s</a></h3>
              <p class="sa-sc__who"><span class="sa-flags">%(flags)s</span><span>%(nation)s</span></p>
              <p class="sa-sc__p">%(text)s</p>
              <p class="sa-sc__act"><a class="sa-go" href="%(link)s">See the blueprint</a></p>
              <small class="sa-sc__src">Source: <a href="%(url)s" target="_blank" rel="noopener noreferrer">%(source)s</a></small>
            </div>
          </article>''' % {
            'i': i, 'n': '%02d' % i, 'c': CLASSES[f['cls']], 'small': ent(f['image_small']), 'big': ent(f['image']),
            'sizes': sizes, 'alt': ent(f['alt']), 'cls': ent(f['cls']), 'fig': ent(f['figure']), 'unit': unit,
            'line': ent(f['line']), 'link': ent(f['link']), 'name': ent(f['name']), 'flags': flags,
            'nation': ent(f['nation']), 'text': ent(f['text']), 'url': ent(f['url']), 'source': ent(f['source'])})
    return '\n'.join(out)


def render_nations(nations):
    return '\n'.join('        <li><a href="%s"><span>%s</span></a></li>' % (ent(n['url']), ent(n['name'])) for n in nations)


def js_json(obj):
    """JSON for an inline script tag: ASCII, and never a closing tag."""
    return json.dumps(obj, ensure_ascii=True, separators=(',', ':')).replace('</', '<\\/')


def build(d):
    sys.path.insert(0, str(ROOT / 'tools'))
    from build_home import seam  # the same painted seams as the homepage
    src = SRC.read_text(encoding='utf-8')
    version = re.search(r'data-v="([0-9.]+)"', src).group(1)
    src = src.split('-->', 1)[1].lstrip('\n')   # the source banner is not served
    seams = (PAGES / 'home-seams.html').read_text(encoding='utf-8').strip()
    ledger = d['ledger']
    seed = {'nations': [{k: n[k] for k in ('name', 'url', 'assets', 'lat', 'lon', 'top')} for n in d['nations']]}
    page = (src.replace('@@SEAMS@@', seams)
               .replace('@@FEATURED@@', render_featured(d['featured']))
               .replace('@@NATIONLIST@@', render_nations(d['nations']))
               .replace('@@SEED@@', js_json(seed))
               .replace('@@LAND@@', js_json(land_mask()))
               .replace('@@ASSETS@@', '{:,}'.format(ledger['assets']))
               .replace('@@NATIONS@@', str(ledger['nations']))
               .replace('@@CLASSES@@', str(ledger['classes']))
               .replace('@@UPDATED@@', long_date(d['updated'])))
    page = re.sub(r'@@SEAM:([a-e])@@', lambda m: seam(m.group(1)), page)
    left = re.findall(r'@@[A-Z:a-z]+@@', page)
    if left:
        sys.exit('tokens left unfilled: %s' % left)
    banner = '''<!-- ===========================================================================
PERFECT NATIONS - SOVEREIGN ASSETS PAGE - THE WHOLE PAGE IN ONE FILE - v%s - built %s
Served live on perfectnations.org/sovereign-assets/ (page 15125) by the Perfect Nations Live Pages
plugin, in place of the code pasted in its one Elementor Custom HTML widget (root id pn-sov).
BUILT by tools/build_sovereign_assets.py from pages/sovereign-assets-src.html (the design) and
data/sovereign-assets.json (the five assets and the ledger, which the page also reads live).
Never edit this file by hand; kept by the Sovereign Assets Steward (skill steward-sovereign-assets).
Palette: Earthrise and ivory grounds, gold only for what a visitor can act on; the colour comes
from the painted seams (Preeti Sinha&#8217;s garden painting) between the Earthrise sections.
=========================================================================== -->
''' % (version, date.today().isoformat())
    page = banner + page
    OUT.write_text(page, encoding='utf-8')
    print('pages/sovereign-assets.html: %d characters' % len(page))


# ---------------------------------------------------------------- the validation suite
VOID = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'source', 'track', 'wbr'}


class Walk(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=False)
        self.stack, self.errors, self.ids, self.text, self.scripts, self.styles = [], [], {}, [], [], []
        self.raw = None

    def handle_starttag(self, tag, attrs):
        self.text.append(' ')
        a = dict(attrs)
        if 'id' in a:
            self.ids[a['id']] = self.ids.get(a['id'], 0) + 1
        if tag == 'script' and 'src' in a:
            self.errors.append('static script src: %s' % a['src'])
        if tag in VOID:
            return
        self.stack.append(tag)
        if tag in ('script', 'style'):
            self.raw = (tag, a.get('type', ''), [])

    def handle_startendtag(self, tag, attrs):
        a = dict(attrs)
        if 'id' in a:
            self.ids[a['id']] = self.ids.get(a['id'], 0) + 1

    def handle_endtag(self, tag):
        self.text.append(' ')
        if tag in VOID:
            return
        if self.raw and tag == self.raw[0]:
            body = ''.join(self.raw[2])
            (self.scripts if tag == 'script' else self.styles).append((self.raw[1], body))
            self.raw = None
        if not self.stack or self.stack[-1] != tag:
            self.errors.append('tag mismatch: </%s> while open %s' % (tag, self.stack[-3:]))
            if tag in self.stack:
                while self.stack and self.stack.pop() != tag:
                    pass
            return
        self.stack.pop()

    def handle_charref(self, name):
        self.handle_data('&#%s;' % name)

    def handle_entityref(self, name):
        self.handle_data('&%s;' % name)

    def handle_data(self, data):
        if self.raw:
            self.raw[2].append(data)
        elif self.stack and self.stack[-1] not in ('svg', 'symbol', 'g', 'defs'):
            self.text.append(data)


def css_errors(css):
    import tinycss2
    errs = []

    def walk(nodes):
        for n in nodes:
            if n.type == 'error':
                errs.append('%s at line %s' % (n.message, n.source_line))
            elif n.type == 'qualified-rule':
                for dcl in tinycss2.parse_declaration_list(n.content):
                    if dcl.type == 'error':
                        errs.append('%s at line %s' % (dcl.message, dcl.source_line))
            elif n.type == 'at-rule' and n.content is not None:
                walk(tinycss2.parse_rule_list(n.content))
    walk(tinycss2.parse_stylesheet(css, skip_whitespace=True, skip_comments=True))
    return errs


def validate(page):
    errors = []
    bad = [(i, c) for i, c in enumerate(page) if ord(c) > 126 or (ord(c) < 32 and c not in '\n\t\r')]
    if bad:
        errors.append('non-ASCII characters: %r' % bad[:5])
    first = re.search(r'\bid\s*=\s*["\'](pn-[a-z0-9-]+)["\']', page, re.I)
    if not first or first.group(1) != 'pn-sov':
        errors.append('the first pn- id must be pn-sov, found %s' % (first.group(1) if first else None))
    if 'backdrop-filter' in page:
        errors.append('backdrop-filter is not allowed')
    w = Walk()
    w.feed(page)
    w.close()
    errors += w.errors
    if w.stack:
        errors.append('tags left open: %s' % w.stack)
    errors += ['duplicate id: %s' % k for k, v in w.ids.items() if v > 1]
    for _, css in w.styles:
        if re.search(r'</?\w+', css):
            errors.append('a tag-like sequence inside CSS (WordPress rejects it): %s' % re.search(r'</?\w+', css).group(0))
        errors += ['CSS: ' + e for e in css_errors(css)]
    for typ, js in w.scripts:
        if typ == 'application/json':
            try:
                json.loads(js)
            except ValueError as e:
                errors.append('inline JSON: %s' % e)
            continue
        with tempfile.NamedTemporaryFile('w', suffix='.js', delete=False) as t:
            t.write(js)
        r = subprocess.run(['node', '--check', t.name], capture_output=True, text=True)
        if r.returncode:
            errors.append('node --check: %s' % r.stderr.strip()[:400])
    copy = html.unescape(''.join(w.text))
    if "'" in copy:
        errors.append('straight apostrophe in copy: %r' % copy[max(0, copy.index("'") - 40):copy.index("'") + 20])
    m = re.search(r"(n[’']t|[’'](re|ve|ll|m|d))\b|\b(it|that|there|what|let|here|who)[’']s\b", copy, re.I)
    if m:
        errors.append('contraction in copy: %r' % m.group(0))
    for u in re.findall(r'(?:src|href|srcset)="([^"]+)"', page):
        for part in u.split(','):
            url = part.strip().split(' ')[0]
            if url.startswith('http:'):
                errors.append('http link (use https): %s' % url)
    for u in re.findall(r'<img[^>]+src="([^"]+)"', page):
        if not (u.startswith(UPLOADS) or u.startswith(FLAGS)):
            errors.append('picture from outside the Media Library: %s' % u)
    return errors


def main():
    args = sys.argv[1:]
    if '--check' in args:
        d = json.loads(LEDGER.read_text(encoding='utf-8'))
        check_featured(d.get('featured'))
    else:
        d = refresh_data()
        if '--data' in args:
            return
        build(d)
    errors = validate(OUT.read_text(encoding='utf-8'))
    if errors:
        print('VALIDATION FAILED:\n  ' + '\n  '.join(errors))
        sys.exit(1)
    print('validation passed: ASCII, root pn-sov first, CSS parses, no tag in CSS, scripts pass node --check, '
          'tags balance, ids unique, no backdrop-filter, no static script src, no straight apostrophes or contractions, '
          'pictures only from the Media Library')


if __name__ == '__main__':
    main()
