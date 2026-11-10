"""Wave 1 of the new blueprints (10 November 2026): writes data/<slug>.json, tools/nation/<slug>.json and
stewards/<slug>.md for each nation in spec_*.py, from the World Bank figures in wb_raw.txt and the research in
notes.md. The seven standards follow the strict measures of the existing 44 blueprints."""
import json, math, re, sys, importlib.util
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]  # the repository root
TODAY = '2026-11-10'
STAMP = '2026-11-10T21:00Z'
WB = 'https://data.worldbank.org/indicator/%s?locations=%s'

# ---------------------------------------------------------------- the World Bank figures
def load_wb():
    d, ind = {}, None
    for line in (HERE / 'wb_raw.txt').read_text().splitlines():
        if line.startswith('## '):
            ind = line[3:].split()[0]
            if ind == 'Income':
                ind = 'INCOME'
            elif ind == 'Capitals':
                ind = 'CAP'
            elif ind == 'UHC':
                ind = 'UHC'
            continue
        if not ind or line.startswith('#') or not line.strip():
            continue
        all_year = re.search(r'\(all (\d{4})\)', line)
        body = re.sub(r'\(.*?\)', '', line)
        for part in body.split(';'):
            t = part.split()
            if len(t) < 2 or not re.match(r'^[A-Z]{3}$', t[0]):
                continue
            iso = t[0]
            if ind == 'INCOME':
                d.setdefault(iso, {})['INCOME'] = t[1]
            elif ind == 'CAP':
                d.setdefault(iso, {})['CAP'] = (float(t[-1]), float(t[-2]))  # lat, lng
            elif len(t) >= 3 and re.match(r'^\d{4}$', t[1]):
                d.setdefault(iso, {})[ind] = (int(t[1]), float(t[2]))
            else:
                yr = int(all_year.group(1)) if all_year else {'UHC': 2023, 'AG.LND.AGRI.ZS': 2024, 'AG.LND.FRST.ZS': 2024,
                      'NY.GDP.TOTL.RT.ZS': 2021, 'SP.POP.0014.TO.ZS': 2025, 'ER.H2O.INTR.PC': 2022, 'EG.ELC.RNEW.ZS': 2021,
                      'AG.LND.TOTL.K2': 2024, 'EN.POP.SLUM.UR.ZS': 2022}.get(ind, 2024)
                d.setdefault(iso, {})[ind] = (yr, float(t[1]))
    return d


def r1(x):
    return round(x + 1e-9, 1)


def pct(x):
    v = r1(x)
    return ('%d%%' % v) if v == int(v) else ('%.1f%%' % v)


def dated(yr):
    return yr <= 2020


# ---------------------------------------------------------------- the seven standards (strict measures)
LINES = {'LIC': ('SI.POV.DDAY', 'US$3.00'), 'LMIC': ('SI.POV.LMIC', 'US$4.20'), 'UMIC': ('SI.POV.UMIC', 'US$8.30')}


def seven(n, w):
    iso, i2, name = n['iso3'], n['iso2'], n['name']
    x = w[iso]
    g = []
    # Food
    if n.get('food'):
        g.append(dict(n['food'], name='Food'))
    elif 'SN.ITK.MSFI.ZS' in x:
        yr, v = x['SN.ITK.MSFI.ZS']
        g.append({'name': 'Food', 'value': r1(100 - v), 'display': pct(100 - v),
                  'note': 'Not food insecure; %s are moderately or severely food insecure' % pct(v),
                  'source': 'FAO, %d' % yr, 'url': WB % ('SN.ITK.MSFI.ZS', i2)})
    else:
        g.append({'name': 'Food', 'value': None, 'display': 'Not measured',
                  'note': 'No FAO measure of food insecurity is published for %s' % name,
                  'source': 'FAO', 'url': WB % ('SN.ITK.MSFI.ZS', i2)})
    # Water
    if 'SH.H2O.SMDW.ZS' in x:
        yr, v = x['SH.H2O.SMDW.ZS']
        g.append({'name': 'Water', 'value': r1(v), 'display': pct(v), 'note': 'Safely managed drinking water',
                  'source': 'WHO/UNICEF, %d' % yr, 'url': WB % ('SH.H2O.SMDW.ZS', i2)})
    else:
        yr, v = x['SH.H2O.BASW.ZS']
        g.append({'name': 'Water', 'value': r1(v), 'display': pct(v),
                  'note': 'Basic drinking water; safely managed water is not measured (lenient)',
                  'source': 'WHO/UNICEF, %d' % yr, 'url': WB % ('SH.H2O.BASW.ZS', i2)})
    # Shelter: the lower of safely managed sanitation and the share of city dwellers outside slums
    sy, sv = x['EN.POP.SLUM.UR.ZS']
    out = 100 - sv
    if 'SH.STA.SMSS.ZS' in x and x['SH.STA.SMSS.ZS'][1] <= out:
        yr, v = x['SH.STA.SMSS.ZS']
        g.append({'name': 'Shelter', 'value': r1(v), 'display': pct(v),
                  'note': 'Safely managed sanitation; %s of city dwellers live in slums' % pct(sv),
                  'source': 'WHO/UNICEF, %d' % yr, 'url': WB % ('SH.STA.SMSS.ZS', i2)})
    else:
        extra = '' if 'SH.STA.SMSS.ZS' in x else '; safely managed sanitation is not measured'
        g.append({'name': 'Shelter', 'value': r1(out), 'display': pct(out),
                  'note': 'City dwellers outside slums; %s live in slums%s' % (pct(sv), extra),
                  'source': 'UN-Habitat, %d' % sy, 'url': WB % ('EN.POP.SLUM.UR.ZS', i2)})
    # Energy: clean cooking (electricity per person is not published for these nations), with access in the note
    yr, v = x['EG.CFT.ACCS.ZS']
    ey, ev = x['EG.ELC.ACCS.ZS']
    g.append({'name': 'Energy', 'value': r1(v), 'display': pct(v),
              'note': '%s cook with clean fuels and technology; %s have electricity' % (pct(v), pct(ev)),
              'source': 'World Bank, %d' % yr, 'url': WB % ('EG.CFT.ACCS.ZS', i2)})
    # Education: the lower of children reading by the end of primary and lower-secondary completion
    cands = []
    if 'SE.LPV.PRIM' in x:
        yr, lp = x['SE.LPV.PRIM']
        cands.append((100 - lp, yr, 'read', WB % ('SE.LPV.PRIM', i2)))
    if 'SE.SEC.CMPT.LO.ZS' in x:
        yr, c = x['SE.SEC.CMPT.LO.ZS']
        cands.append((min(c, 100), yr, 'complete', WB % ('SE.SEC.CMPT.LO.ZS', i2)))
    if not cands:
        g.append({'name': 'Education', 'value': None, 'display': 'Not measured',
                  'note': 'Neither learning outcomes nor lower-secondary completion is published for %s' % name,
                  'source': 'World Bank', 'url': WB % ('SE.SEC.CMPT.LO.ZS', i2)})
    else:
        v, yr, kind, url = min(cands, key=lambda t: t[0])
        if kind == 'read':
            note = '%s of children read a simple text by the end of primary school' % pct(v)
        else:
            note = '%s of young people complete lower secondary school' % pct(v)
        if dated(yr):
            note += '; %d, dated' % yr
        g.append({'name': 'Education', 'value': r1(v), 'display': '%.1f' % r1(v) if r1(v) != int(r1(v)) else '%d' % r1(v),
                  'note': note, 'source': 'World Bank, %d' % yr, 'url': url, 'kind': kind})
    # Health: the WHO service coverage index
    yr, v = x['UHC']
    g.append({'name': 'Health', 'value': float(v), 'display': '%d' % v, 'note': 'WHO service coverage index',
              'source': 'WHO, %d' % yr, 'url': 'https://ourworldindata.org/grapher/universal-health-coverage-index?country=~%s' % iso})
    # Livelihoods: above the stricter of the national line and the World Bank line for the income group
    code, line = LINES[x['INCOME']]
    if code not in x and 'SI.POV.NAHC' not in x:
        g.append({'name': 'Livelihoods', 'value': None, 'display': 'Not measured',
                  'note': 'No poverty survey for %s is published by the World Bank' % name,
                  'source': 'World Bank', 'url': WB % (code, i2)})
        return g
    ly, lv = x[code]
    ny, nv = x['SI.POV.NAHC']
    if lv >= nv:
        v, yr, note, url = 100 - lv, ly, 'Above %s a day; %s live below it' % (line, pct(lv)), WB % (code, i2)
    else:
        v, yr, note, url = 100 - nv, ny, 'Above the national poverty line; %s live below it' % pct(nv), WB % ('SI.POV.NAHC', i2)
    if dated(yr):
        note += ', dated'
    g.append({'name': 'Livelihoods', 'value': r1(v), 'display': pct(v), 'note': note, 'source': 'World Bank, %d' % yr, 'url': url,
              'below': 100 - v, 'line': line if lv >= nv else 'the national poverty line'})
    return g


def coverage(n, g):
    name, dem = n['name'], n.get('of_people') or ('people in %s' % n['name'])
    scored = [x for x in g if isinstance(x.get('value'), (int, float))]
    bind = min(scored, key=lambda x: x['value'] if x['name'] != 'Health' else 999)
    v, yr = bind['value'], int(bind['source'].split(', ')[-1])
    gap = pct(100 - v)
    old = ', on %d data' % yr if dated(yr) else ''
    k = bind['name']
    if k == 'Food':
        t = 'Of %s are moderately or severely food insecure%s.' % (dem, old)
    elif k == 'Water':
        t = 'Of %s lack safely managed drinking water%s.' % (dem, old) if 'Safely' in bind['note'] else 'Of %s lack even basic drinking water%s.' % (dem, old)
    elif k == 'Shelter':
        t = ('Of %s lack safely managed sanitation%s.' % (dem, old)) if 'sanitation;' in bind['note'] and bind['note'].startswith('Safely') else ('Of city dwellers in %s live in slums%s.' % (name, old))
    elif k == 'Energy':
        t = 'Of %s still cook without clean fuels%s.' % (dem, old)
    elif k == 'Education':
        t = ('Of children in %s cannot read a simple text by the end of primary school%s.' % (name, old)) if bind.get('kind') == 'read' else ('Of young people in %s do not complete lower secondary school%s.' % (name, old))
    else:
        t = 'Of %s live below %s a day%s.' % (dem, bind.get('line'), old) if bind.get('line', '').startswith('US$') else 'Of %s live below the national poverty line%s.' % (dem, old)
    return {'set_by': 'Livelihood' if k == 'Livelihoods' else k, 'gap': gap, 'gap_text': t, 'perfect_capita': 'To set'}


# ---------------------------------------------------------------- the assets (World Bank figures, plus the nation's own)
def wb_assets(n, w):
    iso, i2, name = n['iso3'], n['iso2'], n['name']
    x = w[iso]
    pop = n['population']
    out = {}
    py, kid = x['SP.POP.0014.TO.ZS']
    out['people'] = {'name': 'The People', 'figure': '%.1fm' % (pop / 1e6) if pop >= 1e6 else '{:,}'.format(pop), 'money': False,
                     'label': 'Citizens, 2025', 'text': '%s are under fifteen: the workforce and the market of the next generation.' % pct(kid),
                     'src': 'World Bank, World Development Indicators: population 2025, ages 0 to 14 (%d)' % py}
    yr, v = x['AG.LND.AGRI.ZS']
    out['farmland'] = {'name': 'The Farmland', 'figure': pct(v), 'money': False, 'label': 'Of the land in agriculture, %d' % yr,
                       'text': n.get('farm_text') or 'Land that can feed the nation and earn abroad, valued and financed against its harvest.',
                       'src': 'World Bank, agricultural land (%% of land area), %d' % yr, 'v': v}
    yr, v = x['AG.LND.FRST.ZS']
    out['forest'] = {'name': 'The Forest', 'figure': pct(v), 'money': False, 'label': 'Of the land under forest, %d' % yr,
                     'text': n.get('forest_text') or 'Standing forest that stores carbon and water, and can earn as it stands.',
                     'src': 'World Bank, forest area (%% of land area), %d' % yr, 'v': v}
    yr, v = x['ER.H2O.INTR.PC']
    out['water'] = {'name': 'The Fresh Water', 'figure': '{:,} m³'.format(int(round(v))), 'money': False,
                    'label': 'Renewable fresh water a person, %d' % yr,
                    'text': n.get('water_text') or 'Rain and rivers renewed every year: power, irrigation and drinking water.',
                    'src': 'World Bank, renewable internal freshwater resources per capita, %d' % yr, 'v': v}
    yr, v = x['NY.GDP.TOTL.RT.ZS']
    out['ground'] = {'name': 'The Ground', 'figure': pct(v), 'money': False, 'label': 'Of GDP from natural resource rents, %d' % yr,
                     'text': n.get('ground_text') or 'What lies under the land already earns; the task is to turn the rent into lasting assets.',
                     'src': 'World Bank, total natural resources rents (%% of GDP), %d' % yr, 'v': v}
    yr, v = x['EG.ELC.RNEW.ZS']
    out['grid'] = {'name': 'The Clean Grid', 'figure': pct(v), 'money': False, 'label': 'Of electricity from renewable sources, %d' % yr,
                   'text': n.get('grid_text') or 'Power from water and sun already flows; every new connection can be clean.',
                   'src': 'World Bank, renewable electricity output (%% of total), %d' % yr, 'v': v}
    yr, v = x['AG.LND.TOTL.K2']
    out['land'] = {'name': 'The Land', 'figure': '{:,} km²'.format(int(v)) if v < 1e6 else '%.2fM km²' % (v / 1e6), 'money': False,
                   'label': 'Land area, %d' % yr, 'text': n.get('land_text') or 'Territory to farm, mine, power and protect.',
                   'src': 'World Bank, land area, %d' % yr, 'v': v}
    return out


# ---------------------------------------------------------------- outlines
def outline_for(n):
    if n.get('small'):
        return []
    g = json.loads(Path('/tmp/pn-libs/node_modules/three-globe/example/country-polygons/ne_110m_admin_0_countries.geojson').read_text())
    f = next(f for f in g['features'] if f['properties']['ADMIN'] == n['ne'])
    geo = f['geometry']
    rnd = lambda ring: [[round(a, 6), round(b, 6)] for a, b in ring]
    if geo['type'] == 'Polygon':
        return [{'type': 'Polygon', 'coordinates': [rnd(r) for r in geo['coordinates']]}]
    return [{'type': 'MultiPolygon', 'coordinates': [[rnd(r) for r in p] for p in geo['coordinates']]}]


def centroid(n):
    if n.get('latlng'):
        return n['latlng']
    o = outline_for(n)
    polys = o[0]['coordinates'] if o[0]['type'] == 'MultiPolygon' else [o[0]['coordinates']]
    A = cx = cy = 0.0
    for p in polys:
        r = p[0]
        for (x0, y0), (x1, y1) in zip(r, r[1:] + r[:1]):
            c = x0 * y1 - x1 * y0
            A += c; cx += (x0 + x1) * c; cy += (y0 + y1) * c
    A /= 2
    return round(cy / (6 * A), 4), round(cx / (6 * A), 4)


# ---------------------------------------------------------------- the page words
CODESIGNER = ('Everyone who shares a vision, a voice or an enterprise here becomes a <b>Co-designer of Perfect %s</b>: one of a '
              'community of selfless people, at home and abroad, building a nation where every citizen has a decent life.')
MEASURES = ('Strict measures. Food: share not moderately or severely food insecure (FAO). Water: safely managed drinking water where '
            'measured; where it is not, basic water, marked as such. Shelter: the lower of safely managed sanitation and the share '
            'outside urban slums. Energy: the lower of electricity per person against 1,000 kWh and clean cooking; where electricity '
            'per person is not published, clean cooking. Education: the lower of children reading by the end of primary school and '
            'lower-secondary completion. Health: WHO service coverage index. Livelihood: share above the stricter of the national '
            'poverty line and the World Bank line for the nation’s income group. Each figure links to its source.')


def page_words(n, cov, lat, lng):
    name = n['name']
    bind = cov['set_by']
    return {
        'slug': n['slug'], 'name': name, 'root': 'pn-bp-' + n['slug'],
        'eyebrow': 'National Blueprint · One of 195',
        'people': 'Where %s and Co-designers design the nation they want to live in.' % n['demonym'],
        'codesigner': CODESIGNER % name,
        'edition': 'first',
        'letter': {'paras': [n['letter']], 'quote': '“%s”' % n['quote'], 'url': ''},
        'mandates': {'moves': [
            ['The five sovereign assets on this page, walked through.',
             '%s, the standard furthest from reach, and the Gap, explained.' % bind,
             'The instruments that could close the Gap, shortlisted.', 'The path to market, outlined.'],
            ['The ledger tested against your ministries’ own data.', 'Each of the seven standards costed in local prices.',
             'One financing structure, drawn with your team.', 'A term sheet and the partners to approach.'],
            ['A full sovereign asset ledger, valued and verified.', 'Perfect Capita set and agreed with government, with a monitoring plan.',
             'The full structure: legal form, credit enhancement, guarantees and pricing.',
             'Taken to investors and development partners, through to close.']],
            'terms': 'For the Government of %s, its development partners and investors. Scope and fees are agreed in writing before any work begins.' % (n.get('gov') or name)},
        'capita': {'pc_text': 'The yearly cost, per person, of lifting everyone above the Living Line in all seven basic living standards, set with %s in its own prices.' % name,
                   'price_text': 'Perfect Capita times the population: the national bill, each year.',
                   'est': 'Perfect Nations estimate, to be confirmed with %s. Figures marked dated rest on surveys more than five years old; lenient measures are marked as such.' % name,
                   'measures': MEASURES},
        'voices': {'local': 'We are looking for the people with real stories from %s: the leaders who built something that works, and the keepers of local knowledge who know how their communities live, cope and thrive.' % name},
        'close_lead': 'Share your vision, suggest a guest, or write to us. Every message receives a personal reply.',
        'sources': n['sources'],
        'globe': {'lat': lat, 'lng': lng, 'outline': outline_for(n)},
    }


def main():
    w = load_wb()
    specs = []
    for f in sorted(HERE.glob('spec_*.py')):
        sp = importlib.util.spec_from_file_location(f.stem, f)
        m = importlib.util.module_from_spec(sp)
        sp.loader.exec_module(m)
        specs.extend(m.NATIONS)
    only = set(sys.argv[1:])
    for n in specs:
        if only and n['slug'] not in only:
            continue
        iso = n['iso3']
        n['population'] = int(w[iso]['SP.POP.TOTL'][1])
        g = seven(n, w)
        cov = coverage(n, g)
        A = wb_assets(n, w)
        items = []
        for a in n['assets']:
            if isinstance(a, str):
                a = dict(A[a])
            items.append({k: a[k] for k in ('name', 'figure', 'money', 'label', 'text') if k in a})
        for x in g:
            x.pop('kind', None); x.pop('below', None); x.pop('line', None)
        d = {
            'nation': n['name'], 'page_version': '1.0', 'updated': TODAY,
            'steward': {'name': n['steward'], 'role': 'Nation Steward of %s' % n['name']},
            'population': n['population'],
            'hero': {'lead': n['lead'], 'stats': n['stats']},
            'capital': {'heading': n['cap_heading'], 'record': n['record'], 'register': n['register']},
            'assets': {'heading': 'Five assets no balance sheet counts.', 'items': items},
            'enterprises': {'heading': 'Already working in %s.' % n['name'], 'items': []},
            'coverage': cov, 'guarantees': g, 'newswire': n['newswire'], 'dispatches': [],
            'checked': STAMP, 'reviewed': STAMP,
        }
        for x in d['newswire']:
            dt = x['date']
            y, mo, dd = dt.split('-')
            x.setdefault('label', '%d %s %s' % (int(dd), ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'][int(mo) - 1], y))
            x.setdefault('highlight', '')
        lat, lng = centroid(n)
        p = page_words(n, cov, lat, lng)
        (REPO / 'data' / ('%s.json' % n['slug'])).write_text(json.dumps(d, indent=1, ensure_ascii=False) + '\n', encoding='utf-8')
        (REPO / 'tools' / 'nation' / ('%s.json' % n['slug'])).write_text(json.dumps(p, ensure_ascii=False) + '\n', encoding='utf-8')
        # the Nation Steward's notes: sources and facts only
        L = ['# %s: notes of the Nation Steward' % n['name'], '',
             '%s, AI Nation Steward of %s. Public notes: sources and facts only.' % (n['steward'], n['name']), '',
             'First edition: 10 November 2026 (wave 1 of the remaining 151 nations). The weekly review adds the register, the Newswire and the enterprises.', '',
             '## The seven standards', '']
        for x in g:
            L.append('- **%s, %s:** %s. %s, %s' % (x['name'], x['display'], x['note'], x['source'], x['url']))
        L += ['', 'Furthest from reach: %s (%s). %s' % (cov['set_by'], cov['gap'], cov['gap_text']), '', '## The Sovereign Assets', '']
        for a in n['assets']:
            if isinstance(a, str):
                a = A[a]
            L.append('- **%s, %s:** %s. %s' % (a['name'], a['figure'], a['label'], a.get('src', '')))
        L += ['', '## The record and the register', '']
        for r in n['record']:
            L.append('- **%s:** %s. %s, %s' % (r['value'], r['text'], r['source'], r['url']))
        for r in n['register']:
            L.append('- **%s (%s):** %s %s' % (r['name'], r.get('amount') or 'no amount', r.get('text', ''), r['url']))
        L += ['', '## Open gaps', ''] + ['- %s' % s for s in n.get('gaps', [])] + ['']
        (REPO / 'stewards' / ('%s.md' % n['slug'])).write_text('\n'.join(L), encoding='utf-8')
        print('%-26s pop %10s  bind %-10s %s  assets %d  record %d  register %d  wire %d' % (
            n['slug'], '{:,}'.format(n['population']), cov['set_by'], cov['gap'], len(items), len(n['record']), len(n['register']), len(n['newswire'])))


if __name__ == '__main__':
    main()
