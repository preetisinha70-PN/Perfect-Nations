"""The shared generator for the remaining blueprints (waves 2 onward, from 10 November 2026).

Each wave folder holds spec.py (NATIONS, the words and the sourced capital lines written for each nation) and notes.md
(the research). This file reads the World Bank and IMF figures in wb_raw.txt and income.txt, computes the seven standards
on the strict measures of the existing blueprints, and writes data/<slug>.json, tools/nation/<slug>.json and
stewards/<slug>.md. Run: python3 tools/waves/common/gen.py <wave folder> [slugs...]"""
import json, re, sys, importlib.util
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
TODAY = '2026-11-10'
STAMP = '2026-11-10T23:00Z'
WB = 'https://data.worldbank.org/indicator/%s?locations=%s'
IMF = 'https://www.imf.org/external/datamapper/%s@WEO/%s'
MINUS = '−'


# ---------------------------------------------------------------- the figures
def load():
    d, ind, default = {}, None, None
    for line in (HERE / 'wb_raw.txt').read_text(encoding='utf-8').splitlines():
        if line.startswith('## '):
            ind = line[3:].split()[0]
            m = re.search(r'\(all (\d{4})\)', line)
            default = int(m.group(1)) if m else None
            continue
        if not ind or not line.strip():
            continue
        for part in line.split(';'):
            t = part.split()
            if len(t) < 2 or not re.match(r'^[A-Z]{3}$', t[0]):
                continue
            if len(t) >= 3 and re.match(r'^\d{4}$', t[1]):
                d.setdefault(t[0], {})[ind] = (int(t[1]), float(t[2]))
            elif default:
                d.setdefault(t[0], {})[ind] = (default, float(t[1]))
    groups = {'LIC': 'LIC', 'LMC': 'LMIC', 'UMC': 'UMIC', 'HIC': 'HIC'}
    for part in (HERE / 'income.txt').read_text(encoding='utf-8').split(';'):
        t = part.split()
        if len(t) >= 2:
            d.setdefault(t[0], {})['INCOME'] = groups.get(t[1], t[1])
    return d


def r1(x):
    return round(x + 1e-9, 1)


def pct(x, sign=False):
    v = r1(x)
    s = ('%d%%' % abs(v)) if v == int(v) else ('%.1f%%' % abs(v))
    if v < 0:
        return MINUS + s
    return ('+' + s) if sign and v > 0 else s


def num(v):
    v = r1(v)
    return '%d' % v if v == int(v) else '%.1f' % v


def dated(yr):
    return yr <= 2020


# ---------------------------------------------------------------- the seven standards (strict measures)
LINES = {'LIC': ('SI.POV.DDAY', 'US$3.00'), 'LMIC': ('SI.POV.LMIC', 'US$4.20'), 'UMIC': ('SI.POV.UMIC', 'US$8.30'),
         'HIC': ('SI.POV.UMIC', 'US$8.30')}


def seven(n, w):
    iso, i2, name = n['iso3'], n['iso2'], n.get('in_name') or n['name']
    # 'skip' leaves out an indicator for one nation (a known artefact of the series); the reason goes in the gaps
    x = {k: v for k, v in w.get(iso, {}).items() if k not in n.get('skip', ())}
    g = []
    # Food
    if n.get('food'):
        g.append(dict(n['food'], name='Food'))
    elif 'SN.ITK.MSFI.ZS' in x:
        yr, v = x['SN.ITK.MSFI.ZS']
        g.append({'name': 'Food', 'value': r1(100 - v), 'display': pct(100 - v),
                  'note': 'Not food insecure; %s are moderately or severely food insecure%s' % (pct(v), ', dated' if dated(yr) else ''),
                  'source': 'FAO, %d' % yr, 'url': WB % ('SN.ITK.MSFI.ZS', i2)})
    else:
        g.append({'name': 'Food', 'value': None, 'display': 'Not measured',
                  'note': 'No FAO measure of food insecurity is published for %s' % name, 'source': 'FAO',
                  'url': WB % ('SN.ITK.MSFI.ZS', i2)})
    # Water
    if 'SH.H2O.SMDW.ZS' in x:
        yr, v = x['SH.H2O.SMDW.ZS']
        g.append({'name': 'Water', 'value': r1(v), 'display': pct(v), 'note': 'Safely managed drinking water%s' % (', dated' if dated(yr) else ''),
                  'source': 'WHO/UNICEF, %d' % yr, 'url': WB % ('SH.H2O.SMDW.ZS', i2)})
    elif 'SH.H2O.BASW.ZS' in x:
        yr, v = x['SH.H2O.BASW.ZS']
        g.append({'name': 'Water', 'value': r1(v), 'display': pct(v),
                  'note': 'Basic drinking water; safely managed water is not measured (lenient)%s' % (', dated' if dated(yr) else ''),
                  'source': 'WHO/UNICEF, %d' % yr, 'url': WB % ('SH.H2O.BASW.ZS', i2)})
    else:
        g.append({'name': 'Water', 'value': None, 'display': 'Not measured', 'note': 'No WHO/UNICEF measure of drinking water is published for %s' % name,
                  'source': 'WHO/UNICEF', 'url': WB % ('SH.H2O.SMDW.ZS', i2)})
    # Shelter: the lower of safely managed sanitation and the share of city dwellers outside slums
    san = x.get('SH.STA.SMSS.ZS')
    slum = x.get('EN.POP.SLUM.UR.ZS')
    if san and (not slum or san[1] <= 100 - slum[1]):
        yr, v = san
        tail = ('; %s of city dwellers live in slums' % pct(slum[1])) if slum else ''
        g.append({'name': 'Shelter', 'value': r1(v), 'display': pct(v), 'note': 'Safely managed sanitation%s%s' % (tail, ', dated' if dated(yr) else ''),
                  'source': 'WHO/UNICEF, %d' % yr, 'url': WB % ('SH.STA.SMSS.ZS', i2), 'kind': 'san'})
    elif slum:
        yr, sv = slum
        extra = '' if san else '; safely managed sanitation is not measured'
        g.append({'name': 'Shelter', 'value': r1(100 - sv), 'display': pct(100 - sv),
                  'note': 'City dwellers outside slums; %s live in slums%s%s' % (pct(sv), extra, ', dated' if dated(yr) else ''),
                  'source': 'UN-Habitat, %d' % yr, 'url': WB % ('EN.POP.SLUM.UR.ZS', i2), 'kind': 'slum'})
    else:
        g.append({'name': 'Shelter', 'value': None, 'display': 'Not measured',
                  'note': 'Neither safely managed sanitation nor urban slums is measured for %s' % name, 'source': 'WHO/UNICEF',
                  'url': WB % ('SH.STA.SMSS.ZS', i2)})
    # Energy: clean cooking, with electricity access in the note
    if 'EG.CFT.ACCS.ZS' in x:
        yr, v = x['EG.CFT.ACCS.ZS']
        ev = x.get('EG.ELC.ACCS.ZS')
        tail = ('; %s have electricity' % pct(ev[1])) if ev else ''
        g.append({'name': 'Energy', 'value': r1(v), 'display': pct(v), 'note': '%s cook with clean fuels and technology%s' % (pct(v), tail),
                  'source': 'World Bank, %d' % yr, 'url': WB % ('EG.CFT.ACCS.ZS', i2)})
    elif 'EG.ELC.ACCS.ZS' in x:
        yr, v = x['EG.ELC.ACCS.ZS']
        g.append({'name': 'Energy', 'value': r1(v), 'display': pct(v), 'note': '%s have electricity; clean cooking is not measured (lenient)' % pct(v),
                  'source': 'World Bank, %d' % yr, 'url': WB % ('EG.ELC.ACCS.ZS', i2)})
    else:
        g.append({'name': 'Energy', 'value': None, 'display': 'Not measured', 'note': 'Neither clean cooking nor electricity access is published for %s' % name,
                  'source': 'World Bank', 'url': WB % ('EG.CFT.ACCS.ZS', i2)})
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
        note = ('%s of children read a simple text by the end of primary school' if kind == 'read'
                else '%s of young people complete lower secondary school') % pct(v)
        if dated(yr):
            note += '; %d, dated' % yr
        g.append({'name': 'Education', 'value': r1(v), 'display': num(v), 'note': note, 'source': 'World Bank, %d' % yr, 'url': url, 'kind': kind})
    # Health: the WHO service coverage index
    if 'UHC' in x:
        yr, v = x['UHC']
        g.append({'name': 'Health', 'value': float(v), 'display': '%d' % v, 'note': 'WHO service coverage index', 'source': 'WHO, %d' % yr,
                  'url': 'https://ourworldindata.org/grapher/universal-health-coverage-index?country=~%s' % iso})
    else:
        g.append({'name': 'Health', 'value': None, 'display': 'Not measured', 'note': 'The WHO service coverage index is not published for %s' % name,
                  'source': 'WHO', 'url': 'https://ourworldindata.org/grapher/universal-health-coverage-index'})
    # Livelihoods: above the stricter of the national line and the World Bank line for the income group
    code, line = LINES.get(x.get('INCOME'), LINES['UMIC'])
    opts = []
    if code in x:
        ly, lv = x[code]
        opts.append((lv, ly, 'Above %s a day; %s live below it' % (line, pct(lv)), WB % (code, i2), line))
    if 'SI.POV.NAHC' in x:
        ny, nv = x['SI.POV.NAHC']
        opts.append((nv, ny, 'Above the national poverty line; %s live below it' % pct(nv), WB % ('SI.POV.NAHC', i2), 'the national poverty line'))
    if not opts:
        g.append({'name': 'Livelihoods', 'value': None, 'display': 'Not measured',
                  'note': 'No poverty survey for %s is published by the World Bank' % name, 'source': 'World Bank', 'url': WB % (code, i2)})
        return g
    below, yr, note, url, ln = max(opts, key=lambda t: t[0])
    if dated(yr):
        note += ', dated'
    g.append({'name': 'Livelihoods', 'value': r1(100 - below), 'display': pct(100 - below), 'note': note, 'source': 'World Bank, %d' % yr,
              'url': url, 'line': ln})
    return g


def coverage(n, g):
    name = n.get('in_name') or n['name']
    dem = n.get('of_people') or n.get('demonym') or ('people in %s' % name)
    scored = [x for x in g if isinstance(x.get('value'), (int, float)) and x['name'] != 'Health']
    if not scored:
        return {'set_by': 'Health', 'gap': '', 'gap_text': 'The standards for %s are not yet measured.' % name, 'perfect_capita': 'To set'}
    bind = min(scored, key=lambda x: x['value'])
    v, yr = bind['value'], int(bind['source'].split(', ')[-1])
    old = ', on %d data' % yr if dated(yr) else ''
    k = bind['name']
    if k == 'Food':
        t = 'Of %s are moderately or severely food insecure%s.' % (dem, old)
    elif k == 'Water':
        t = ('Of %s lack safely managed drinking water%s.' if bind['note'].startswith('Safely') else 'Of %s lack even basic drinking water%s.') % (dem, old)
    elif k == 'Shelter':
        t = ('Of %s lack safely managed sanitation%s.' % (dem, old)) if bind.get('kind') == 'san' else ('Of city dwellers in %s live in slums%s.' % (name, old))
    elif k == 'Energy':
        t = ('Of %s still cook without clean fuels%s.' if 'cook' in bind['note'] and bind['note'].index('cook') < 20 else 'Of %s live without electricity%s.') % (dem, old)
    elif k == 'Education':
        t = ('Of children in %s cannot read a simple text by the end of primary school%s.' % (name, old)) if bind.get('kind') == 'read' else (
            'Of young people in %s do not complete lower secondary school%s.' % (name, old))
    else:
        t = ('Of %s live below %s a day%s.' % (dem, bind['line'], old)) if bind.get('line', '').startswith('US$') else (
            'Of %s live below the national poverty line%s.' % (dem, old))
    return {'set_by': 'Livelihood' if k == 'Livelihoods' else k, 'gap': pct(100 - v), 'gap_text': t, 'perfect_capita': 'To set'}


# ---------------------------------------------------------------- the assets
def auto_assets(n, w):
    iso, i2, name = n['iso3'], n['iso2'], n['name']
    x = w.get(iso, {})
    pop = n['population']
    out = {}
    if 'SP.POP.0014.TO.ZS' in x:
        py, kid = x['SP.POP.0014.TO.ZS']
        out['people'] = {'name': 'The People', 'figure': '%.1fm' % (pop / 1e6) if pop >= 1e6 else '{:,}'.format(pop), 'money': False,
                         'label': 'Citizens, 2025', 'text': n.get('people_text') or '%s are under fifteen: the workforce and the market of the next generation.' % pct(kid),
                         'src': 'World Bank, population 2025 and ages 0 to 14 (%d)' % py}

    def one(key, ind, nm, label, text, src, fig=None):
        if ind not in x:
            return
        yr, v = x[ind]
        out[key] = {'name': nm, 'figure': fig(v) if fig else pct(v), 'money': False, 'label': label % yr,
                    'text': n.get(key + '_text') or text, 'src': src % yr, 'v': v}

    one('farmland', 'AG.LND.AGRI.ZS', 'The Farmland', 'Of the land in agriculture, %d',
        'Land that can feed the nation and earn abroad, valued and financed against its harvest.', 'World Bank, agricultural land (%% of land area), %d')
    one('forest', 'AG.LND.FRST.ZS', 'The Forest', 'Of the land under forest, %d',
        'Standing forest that stores carbon and water, and can earn as it stands.', 'World Bank, forest area (%% of land area), %d')
    one('water', 'ER.H2O.INTR.PC', 'The Fresh Water', 'Renewable fresh water a person, %d',
        'Rain and rivers renewed every year: power, irrigation and drinking water.', 'World Bank, renewable internal freshwater resources per capita, %d',
        fig=lambda v: '{:,} m³'.format(int(round(v))))
    one('ground', 'NY.GDP.TOTL.RT.ZS', 'The Ground', 'Of GDP from natural resource rents, %d',
        'What lies under the land already earns; the task is to turn the rent into lasting assets.', 'World Bank, total natural resources rents (%% of GDP), %d')
    one('grid', 'EG.ELC.RNEW.ZS', 'The Clean Grid', 'Of electricity from renewable sources, %d',
        'Power from water, wind and sun already flows; every new connection can be clean.', 'World Bank, renewable electricity output (%% of total), %d')
    one('land', 'AG.LND.TOTL.K2', 'The Land', 'Land area, %d', 'Territory to farm, power and protect.', 'World Bank, land area, %d',
        fig=lambda v: ('{:,} km²'.format(int(v)) if v < 1e6 else '%.2fM km²' % (v / 1e6)))
    one('minerals', 'NY.GDP.MINR.RT.ZS', 'The Minerals', 'Of GDP from mineral rents, %d',
        'Metals and minerals already earn; the task is to keep more of their value at home.', 'World Bank, mineral rents (%% of GDP), %d')
    one('visitors', 'ST.INT.RCPT.XP.ZS', 'The Visitors', 'Of export earnings from visitors, %d',
        'Visitors already pay for the coast and the culture; their spending can finance what lasts.', 'World Bank, international tourism receipts (%% of total exports), %d')
    one('diaspora', 'BX.TRF.PWKR.DT.GD.ZS', 'The Diaspora', 'Of GDP sent home by citizens abroad, %d',
        'Citizens abroad send home a steady share of the economy: a flow that can back long-term finance.', 'World Bank, personal remittances received (%% of GDP), %d')
    if 'NY.GDP.PETR.RT.ZS' in x or 'NY.GDP.NGAS.RT.ZS' in x:
        oy, ov = x.get('NY.GDP.PETR.RT.ZS', (0, 0.0))
        gy, gv = x.get('NY.GDP.NGAS.RT.ZS', (0, 0.0))
        yr = max(oy, gy)
        out['oilgas'] = {'name': 'The Oil and Gas', 'figure': pct(ov + gv), 'money': False, 'label': 'Of GDP from oil and gas rents, %d' % yr,
                         'text': n.get('oilgas_text') or 'Oil and gas already earn; the task is to turn the rent into assets that outlast it.',
                         'src': 'World Bank, oil rents and natural gas rents (%% of GDP), %d' % yr, 'v': ov + gv}
    return out


# ---------------------------------------------------------------- the record and the hero figures
def auto_lines(n, w):
    iso, i2 = n['iso3'], n['iso2']
    x = w.get(iso, {})
    rec, st = {}, {}
    if 'IMF.GGXWDG_NGDP' in x:
        yr, v = x['IMF.GGXWDG_NGDP']
        rec['debt'] = {'value': pct(v), 'money': False, 'text': 'General government gross debt, share of GDP, %d' % yr,
                       'source': 'IMF, WEO Oct 2026', 'url': IMF % ('GGXWDG_NGDP', iso)}
        st['debt'] = {'value': pct(v), 'label': 'Public debt, share of GDP, %d' % yr}
    if 'IMF.NGDP_RPCH' in x:
        yr, v = x['IMF.NGDP_RPCH']
        rec['growth'] = {'value': pct(v), 'money': False, 'text': 'Real GDP growth projected for %d' % yr,
                         'source': 'IMF, WEO Oct 2026', 'url': IMF % ('NGDP_RPCH', iso)}
        st['growth'] = {'value': pct(v), 'label': 'Growth projected for %d, IMF' % yr}
    if 'BX.TRF.PWKR.DT.GD.ZS' in x:
        yr, v = x['BX.TRF.PWKR.DT.GD.ZS']
        rec['remit'] = {'value': pct(v), 'money': False, 'text': 'Remittances received from citizens abroad, share of GDP, %d' % yr,
                        'source': 'World Bank, %d' % yr, 'url': WB % ('BX.TRF.PWKR.DT.GD.ZS', i2)}
        st['remit'] = {'value': pct(v), 'label': 'Remittances, share of GDP, %d' % yr}
    if 'ST.INT.RCPT.XP.ZS' in x:
        yr, v = x['ST.INT.RCPT.XP.ZS']
        rec['tourism'] = {'value': pct(v), 'money': False, 'text': 'Tourism receipts, share of export earnings, %d' % yr,
                          'source': 'World Bank, %d' % yr, 'url': WB % ('ST.INT.RCPT.XP.ZS', i2)}
        st['tourism'] = {'value': pct(v), 'label': 'Tourism, share of exports, %d' % yr}
    if 'NY.GDP.PCAP.CD' in x:
        yr, v = x['NY.GDP.PCAP.CD']
        st['gdppc'] = {'value': '${:,}'.format(int(round(v))), 'label': 'Income a person, %d' % yr}
    return rec, st


# ---------------------------------------------------------------- outlines
_GEO = None


def outline_for(n):
    global _GEO
    if not n.get('ne'):
        return []
    if _GEO is None:
        _GEO = json.loads(Path('/tmp/pn-libs/node_modules/three-globe/example/country-polygons/ne_110m_admin_0_countries.geojson').read_text())
    f = next(f for f in _GEO['features'] if f['properties']['ADMIN'] == n['ne'])
    geo = f['geometry']
    rnd = lambda ring: [[round(a, 6), round(b, 6)] for a, b in ring]
    if geo['type'] == 'Polygon':
        return [{'type': 'Polygon', 'coordinates': [rnd(r) for r in geo['coordinates']]}]
    return [{'type': 'MultiPolygon', 'coordinates': [[rnd(r) for r in p] for p in geo['coordinates']]}]


def centroid(n, o):
    if not o:
        return n['lat'], n['lng']
    polys = o[0]['coordinates'] if o[0]['type'] == 'MultiPolygon' else [o[0]['coordinates']]
    best = max(polys, key=lambda p: len(p[0]))  # the largest landmass, so the globe faces the nation
    A = cx = cy = 0.0
    r = best[0]
    for (x0, y0), (x1, y1) in zip(r, r[1:] + r[:1]):
        c = x0 * y1 - x1 * y0
        A += c; cx += (x0 + x1) * c; cy += (y0 + y1) * c
    A /= 2
    if abs(A) < 1e-9:
        return n['lat'], n['lng']
    return round(cy / (6 * A), 4), round(cx / (6 * A), 4)


# ---------------------------------------------------------------- the page words
CODESIGNER = ('Everyone who shares a vision, a voice or an enterprise here becomes a <b>Co-designer of Perfect %s</b>: one of a '
              'community of selfless people, at home and abroad, building a nation where every citizen has a decent life.')
MEASURES = ('Strict measures. Food: share not moderately or severely food insecure (FAO). Water: safely managed drinking water where '
            'measured; where it is not, basic water, marked as such. Shelter: the lower of safely managed sanitation and the share '
            'outside urban slums. Energy: the lower of electricity per person against 1,000 kWh and clean cooking; where electricity '
            'per person is not published, clean cooking. Education: the lower of children reading by the end of primary school and '
            'lower-secondary completion. Health: WHO service coverage index. Livelihood: share above the stricter of the national '
            'poverty line and the World Bank line for the nation’s income group (US$8.30 a day for high-income nations). Each figure links to its source.')
WDI = ('World Bank, World Development Indicators (API), accessed 10 November 2026: population and ages 0 to 14, 2025; land area and '
       'agricultural and forest land; renewable fresh water per person, 2022; natural resource, oil, gas and mineral rents, 2021; '
       'renewable electricity output, 2021; tourism receipts; personal remittances; electricity access and clean cooking.')
STD = ('The seven standards: FAO food insecurity, WHO/UNICEF JMP water and sanitation, UN-Habitat urban slums, World Bank clean cooking, '
       'learning poverty and lower-secondary completion, and poverty headcounts (all via the World Bank); WHO UHC service coverage index, 2023.')
IMFS = 'IMF, World Economic Outlook, October 2026 (DataMapper, accessed 10 November 2026): general government gross debt, 2025, and real GDP growth projected for 2026.'


def page_words(n, cov, lat, lng, outline):
    name = n['name']
    nin = n.get('in_name') or name
    return {
        'slug': n['slug'], 'name': name, 'root': 'pn-bp-' + n['slug'],
        'eyebrow': 'National Blueprint · One of 195',
        'people': 'Where %s and Co-designers design the nation they want to live in.' % (n.get('people_word') or n['demonym']),
        'codesigner': CODESIGNER % name,
        'edition': 'first',
        'letter': {'paras': [n['letter']], 'quote': '“%s”' % n['quote'], 'url': ''},
        'mandates': {'moves': [
            ['The five sovereign assets on this page, walked through.',
             ('%s, the standard furthest from reach, and the Gap, explained.' % cov['set_by']) if cov.get('gap') else
             'The seven standards measured with your own data, and the Gap, found.',
             'The instruments that could close the Gap, shortlisted.', 'The path to market, outlined.'],
            ['The ledger tested against your ministries’ own data.', 'Each of the seven standards costed in local prices.',
             'One financing structure, drawn with your team.', 'A term sheet and the partners to approach.'],
            ['A full sovereign asset ledger, valued and verified.', 'Perfect Capita set and agreed with government, with a monitoring plan.',
             'The full structure: legal form, credit enhancement, guarantees and pricing.',
             'Taken to investors and development partners, through to close.']],
            'terms': 'For %s, its development partners and investors. Scope and fees are agreed in writing before any work begins.' % (n.get('gov') or 'the Government of %s' % nin)},
        'capita': {'pc_text': 'The yearly cost, per person, of lifting everyone above the Living Line in all seven basic living standards, set with %s in its own prices.' % nin,
                   'price_text': 'Perfect Capita times the population: the national bill, each year.',
                   'est': 'Perfect Nations estimate, to be confirmed with %s. Figures marked dated rest on surveys more than five years old; lenient measures are marked as such.' % nin,
                   'measures': MEASURES},
        'voices': {'local': 'We are looking for the people with real stories from %s: the leaders who built something that works, and the keepers of local knowledge who know how their communities live, cope and thrive.' % nin},
        'close_lead': 'Share your vision, suggest a guest, or write to us. Every message receives a personal reply.',
        'sources': [WDI, STD, IMFS] + n.get('sources', []),
        'globe': {'lat': lat, 'lng': lng, 'outline': outline},
    }


def label_date(dt):
    y, mo, dd = dt.split('-')
    return '%d %s %s' % (int(dd), ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'][int(mo) - 1], y)


def build(n, w, wave):
    iso = n['iso3']
    x = w.get(iso, {})
    n['population'] = int(n.get('population') or x.get('SP.POP.TOTL', (0, 0))[1])
    g = seven(n, w)
    cov = coverage(n, g)
    cov.update(n.get('coverage') or {})
    A = auto_assets(n, w)
    rec_auto, st_auto = auto_lines(n, w)
    items, notes_assets = [], []
    for a in n['assets']:
        if isinstance(a, str):
            a = dict(A[a])
        items.append({k: a[k] for k in ('name', 'figure', 'money', 'label', 'text') if k in a})
        notes_assets.append(a)
    record = [dict(rec_auto[r]) if isinstance(r, str) else r for r in n['record'] if not isinstance(r, str) or r in rec_auto]
    stats = [dict(st_auto[s]) if isinstance(s, str) else s for s in n['stats'] if not isinstance(s, str) or s in st_auto]
    for gg in g:
        gg.pop('kind', None); gg.pop('line', None)
    wire = []
    for it in sorted(n['newswire'], key=lambda i: i['date'], reverse=True):
        it = dict(it)
        it.setdefault('label', label_date(it['date']))
        it.setdefault('highlight', '')
        wire.append(it)
    d = {
        'nation': n['name'], 'page_version': '1.0', 'updated': TODAY,
        'steward': {'name': n['steward'], 'role': 'Nation Steward of %s' % n['name']},
        'population': n['population'],
        'hero': {'lead': n['lead'], 'stats': stats[:3]},
        'capital': {'heading': n['cap_heading'], 'record': record, 'register': n['register']},
        'assets': {'heading': '%s assets no balance sheet counts.' % ['No', 'One', 'Two', 'Three', 'Four', 'Five', 'Six'][min(len(items), 6)], 'items': items},
        'enterprises': {'heading': 'Already working in %s.' % (n.get('in_name') or n['name']), 'items': []},
        'coverage': cov, 'guarantees': g, 'newswire': wire, 'dispatches': [],
        'checked': STAMP, 'reviewed': STAMP,
    }
    outline = outline_for(n)
    lat, lng = centroid(n, outline)
    p = page_words(n, cov, lat, lng, outline)
    (REPO / 'data' / ('%s.json' % n['slug'])).write_text(json.dumps(d, indent=1, ensure_ascii=False) + '\n', encoding='utf-8')
    (REPO / 'tools' / 'nation' / ('%s.json' % n['slug'])).write_text(json.dumps(p, ensure_ascii=False) + '\n', encoding='utf-8')
    L = ['# %s: notes of the Nation Steward' % n['name'], '',
         '%s, AI Nation Steward of %s. Public notes: sources and facts only.' % (n['steward'], n['name']), '',
         'First edition: %s (%s of the remaining nations). The weekly review adds the enterprises, more of the capital already committed and the Newswire.' % ('10 November 2026', wave), '',
         '## The seven standards', '']
    for gg in g:
        L.append('- **%s, %s:** %s. %s, %s' % (gg['name'], gg['display'], gg['note'], gg['source'], gg['url']))
    L += ['', 'Furthest from reach: %s (%s). %s' % (cov['set_by'], cov['gap'], cov['gap_text']), '', '## The Sovereign Assets', '']
    for a in notes_assets:
        L.append('- **%s, %s:** %s. %s' % (a['name'], a['figure'], a['label'], a.get('src', '')))
    L += ['', '## The record and Capital already committed', '']
    for r in record:
        L.append('- **%s:** %s. %s, %s' % (r['value'], r['text'], r['source'], r['url']))
    for r in n['register']:
        L.append('- **%s (%s):** %s %s' % (r['name'], r.get('amount') or 'no amount', r.get('text', ''), r['url']))
    L += ['', '## Open gaps', ''] + ['- %s' % s for s in n.get('gaps', [])] + ['']
    (REPO / 'stewards' / ('%s.md' % n['slug'])).write_text('\n'.join(L), encoding='utf-8')
    return d, cov, g


def main():
    wave_dir = Path(sys.argv[1]).resolve()
    only = set(sys.argv[2:])
    w = load()
    base = {n['slug']: n for n in json.loads((HERE / 'nations.json').read_text(encoding='utf-8'))}
    sp = importlib.util.spec_from_file_location('spec', wave_dir / 'spec.py')
    m = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(m)
    for s in m.NATIONS:
        if only and s['slug'] not in only:
            continue
        n = dict(base[s['slug']])
        n.update(s)
        d, cov, g = build(n, w, getattr(m, 'WAVE', wave_dir.name))
        print('%-32s pop %13s  bind %-11s %-6s assets %d record %d register %d wire %d' % (
            n['slug'], '{:,}'.format(n['population']), cov['set_by'], cov['gap'], len(d['assets']['items']), len(d['capital']['record']),
            len(d['capital']['register']), len(d['newswire'])))


if __name__ == '__main__':
    main()
