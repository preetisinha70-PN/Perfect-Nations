#!/usr/bin/env python3
"""Solutions No. 45 to 50 (12 November 2026): six new Solutions Perfect Nations designs, for the nations whose
standard furthest from reach changed when Energy and Health were re-measured on the use and delivery tests
(pull requests 111 and 112). Nigeria keeps Solution No. 24 (food); the others had no designed Solution.
Each challenge copies the nation's blueprint (coverage, guarantees) exactly. Each proof is a deal already in
data/capital-architecture.json, or the nation's own record with its primary source.
Run once from the repository root: python3 tools/measures/solutions_2026_11_12.py
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SON = ROOT / 'data' / 'state-of-nations.json'
LIB = {it['id']: it for fam in json.loads((ROOT / 'data' / 'capital-architecture.json').read_text())['index']['families']
       for it in fam.get('items', [])}
DATE = '2026-11-12'


def lib(i):
    it = LIB[i]
    return {'name': it['name'], 'where': it['where'], 'year': it['year'], 'figure': it['figure'], 'label': it['label'],
            'source': it['source'], 'url': it['url'], 'own': False}


def nation(slug):
    return json.loads((ROOT / 'data' / ('%s.json' % slug)).read_text())


def far(slug):
    d = nation(slug)
    cv = d['coverage']
    g = next(x for x in d['guarantees'] if x['name'].rstrip('s') == cv['set_by'].rstrip('s'))
    return d['nation'], cv, {'label': g['source'], 'url': g['url']}


def slugify(s):
    s = s.lower().replace('’', '')
    return re.sub(r'[^a-z0-9]+', '-', s).strip('-')


S = []

# 45 Cameroon: the rivers that already carry most of the grid, carried to every home
name, cv, src = far('cameroon')
S.append({
    'no': 45, 'nation': name, 'slug_nation': 'cameroon',
    'title': 'River Power for Every Home',
    'standfirst': 'Rivers already give Cameroon most of its power; guaranteed finance carries that clean power to every home.',
    'figure': cv['gap'], 'caption': 'of the electricity a Cameroonian needs is missing',
    'standards': ['Energy'],
    'challenge': 'Cameroonians use about 251 kWh of electricity a person a year, against the Living Line of 1,000: %s of the electricity a person needs is missing.' % cv['gap'],
    'advises': 'Cameroon should finance the lines, substations and village connections that carry its river power to every home, backed by a development bank guarantee so that private lenders can lend for longer and at lower cost. With super intelligence, river flows, demand and losses on every line can be read as they happen, so each new connection is placed where it lights the most homes for the least money.',
    'how': ['Rivers that already give two thirds of the nation’s power, renewed by rain every year.',
            'Guaranteed long-term loans for lines, substations and village connections.',
            'Clean power in every home, and fewer diesel generators in every town.'],
    'proof': lib('infrastructure-guarantee'),
    'first': 'Map every town and village within reach of the grid, and price its connection.',
    'sources': [src],
})

# 46 Chad: oil revenue stands behind private solar plants
name, cv, src = far('chad')
S.append({
    'no': 46, 'nation': name, 'slug_nation': 'chad',
    'title': 'Oil Behind the Sun',
    'standfirst': 'Oil revenue stands behind private solar plants, so they can be built for N’Djamena and every regional capital.',
    'figure': cv['gap'], 'caption': 'of the electricity a Chadian needs is missing',
    'standards': ['Energy'],
    'challenge': 'Chadians use about 18 kWh of electricity a person a year, against the Living Line of 1,000: %s of the electricity a person needs is missing.' % cv['gap'],
    'advises': 'Chad should invite private producers to build solar and storage plants for N’Djamena and every regional capital, with breach-of-contract cover and a reserve, financed from oil revenue, that stands behind every bill the power company owes them. With super intelligence, sunlight, demand and every bill can be followed plant by plant, so investors can see their risk fall and every town can see its hours of power.',
    'how': ['Oil that earns most of what Chad sells abroad, and sun over 1.26 million square kilometres.',
            'Private solar and storage, made bankable by breach-of-contract cover and a reserve financed from oil revenue.',
            'Power for homes, clinics and water pumps in every regional capital.'],
    'proof': lib('breach-of-contract-cover'),
    'first': 'Size the reserve from oil revenue and offer the first solar and storage plant for N’Djamena.',
    'sources': [src],
})

# 47 Cuba: what Cuba owes its creditors becomes medicine
name, cv, src = far('cuba')
S.append({
    'no': 47, 'nation': name, 'slug_nation': 'cuba',
    'title': 'The Medicine Conversion',
    'standfirst': 'What Cuba owes its creditors becomes medicine on its pharmacy shelves.',
    'figure': cv['gap'], 'caption': 'of the basic list of medicines is not available to Cubans',
    'standards': ['Health'],
    'challenge': 'Only 30%% of the basic list of medicines is available to Cubans, the President of Cuba said in August 2026: %s is not.' % cv['gap'],
    'advises': 'Cuba should ask its official creditors to convert part of what it owes into a medicine fund, building on the counterpart fund it already runs with France, with every purchase audited and published. With super intelligence, stocks can be read pharmacy by pharmacy and shortages seen before they happen, so each order goes where patients are waiting.',
    'how': ['A debt conversion already proven with France, and its own makers of medicines and vaccines.',
            'A debt-for-medicine conversion: part of what Cuba owes becomes an audited medicine fund.',
            'Medicines back on pharmacy shelves, and fewer patients turned away.'],
    'proof': {'name': 'Debt Conversion Fund', 'where': 'Cuba', 'year': '2016', 'figure': '€212M',
              'label': 'of debt to France turned into a fund for development, health among its sectors',
              'source': 'Direction générale du Trésor, France',
              'url': 'https://www.tresor.economie.gouv.fr/Pays/CU/fonds-de-contre-valeur-franco-cubain', 'own': False},
    'first': 'Ask the creditors of the 2015 Paris Club agreement to price a debt-for-medicine conversion.',
    'sources': [src],
})

# 48 Iraq: the gas burned at the oil fields becomes power
name, cv, src = far('iraq')
S.append({
    'no': 48, 'nation': name, 'slug_nation': 'iraq',
    'title': 'Flares to Power',
    'standfirst': 'The gas Iraq burns at its oil fields is captured and turned into power for homes, repaid from the electricity sold.',
    'figure': cv['gap'], 'caption': 'of the electricity Iraq needs is not supplied',
    'standards': ['Energy'],
    'challenge': 'Iraq’s grid produced 24,600 MW in September 2026, against at least 55,000 MW needed for power around the clock: %s of the electricity Iraq needs is not supplied.' % cv['gap'],
    'advises': 'Iraq should finance the capture of the gas now burned at its oil fields and turn it into power, through project finance repaid from the electricity sold, with solar plants built on the same sites. With super intelligence, every flare can be watched from space and every captured cubic metre followed to the grid, so lenders and citizens alike can see wasted gas become power.',
    'how': ['Oil fields among the nine that flare the most gas in the world, and sun in every season.',
            'Project finance for gas capture and power plants, repaid from the electricity sold.',
            'More hours of power in every home, and cleaner air over the oil fields.'],
    'proof': lib('project-finance'),
    'first': 'List the fields where gas is flared and offer each to bidders for capture and power.',
    'sources': [src, {'label': 'World Bank, June 2026', 'url': 'https://www.worldbank.org/en/news/press-release/2026/06/23/global-gas-flaring-rises-energy-security'}],
})

# 49 Palestine: Palestinians abroad and partners finance solar power for Gaza
name, cv, src = far('palestine')
S.append({
    'no': 49, 'nation': name, 'slug_nation': 'palestine',
    'title': 'Sunlight for Gaza',
    'standfirst': 'Palestinians abroad and development partners finance solar power for Gaza’s hospitals, water plants, schools and homes.',
    'figure': cv['gap'], 'caption': 'of Palestinians live in Gaza, where the grid has been down since October 2023',
    'standards': ['Water', 'Energy', 'Health'],
    'challenge': 'Of all Palestinians, %s live in Gaza, where the electricity grid has been down since October 2023.' % cv['gap'],
    'advises': 'Palestine should open a light fund, published in full, through which Palestinians abroad and development partners finance solar power and storage for Gaza’s hospitals, water plants, schools and homes, beginning where the need is greatest. With super intelligence, damage and sunlight can be mapped roof by roof, so every panel is placed where it restores the most hours of power, clean water and care.',
    'how': ['Palestinians abroad who already send home a steady share of the economy, and sun in every season.',
            'A light fund, published in full, pooling diaspora finance and partner grants.',
            'Power for hospitals, water plants, schools and homes, before the grid returns.'],
    'proof': lib('diaspora-bond'),
    'first': 'Open the fund’s public ledger and name the first hospitals and water plants it will power.',
    'sources': [src],
})

# 50 Nigeria: the next sovereign green bond powers markets, clinics and homes (Solution No. 24 stays, for food)
name, cv, src = far('nigeria')
ng = next(r for r in nation('nigeria')['capital']['register'] if r['name'] == 'Sovereign Green Bond, third issuance')
S.append({
    'no': 50, 'nation': name, 'slug_nation': 'nigeria',
    'title': 'The Solar Market Bond',
    'standfirst': 'Nigeria’s next green bond brings solar power to its markets, clinics and homes, state by state.',
    'figure': cv['gap'], 'caption': 'of the electricity a Nigerian needs is missing',
    'standards': ['Energy', 'Livelihood'],
    'challenge': 'Nigerians use about 165 kWh of electricity a person a year, against the Living Line of 1,000: %s of the electricity a person needs is missing.' % cv['gap'],
    'advises': 'Nigeria should dedicate its next sovereign green bond to solar mini-grids and storage for markets, clinics and homes, with private developers matching each connection and the states that open their own electricity markets served first. With super intelligence, rooftops, markets and diesel generators can be mapped from space, so every mini-grid is placed where it replaces the most diesel and serves the most traders.',
    'how': ['Sunlight in every state, and a sovereign green bond market already tested three times.',
            'The next sovereign green bond, dedicated to solar mini-grids and matched by private developers.',
            'Power through the day for markets, clinics and homes, in place of diesel generators.'],
    'proof': {'name': 'Sovereign Green Bond', 'where': 'Nigeria', 'year': '2025', 'figure': ng['amount'],
              'label': 'its third green bond, subscribed almost twice over', 'source': 'Debt Management Office, Nigeria, June 2025',
              'url': ng['url'], 'own': False},
    'first': 'Name the markets, clinics and towns the next green bond will power, state by state.',
    'sources': [src],
})


def entry(s):
    slug = s.pop('slug_nation')
    proof = s['proof']
    sources = s.pop('sources') + [{'label': proof['source'], 'url': proof['url']}]
    seen, uniq = set(), []
    for x in sources:
        if x['url'] not in seen:
            seen.add(x['url'])
            uniq.append(x)
    out = {'no': s['no'], 'kind': 'design', 'slug': '%s-%s' % (slug, slugify(s['title'])), 'nation': s['nation'],
           'blueprint': 'https://perfectnations.com/blueprints/%s/' % slug, 'title': s['title'],
           'kicker': 'Perfect Nations Solution', 'date': DATE, 'standfirst': s['standfirst'], 'figure': s['figure'],
           'caption': s['caption'], 'gap_seen': s['figure'], 'standards': s['standards'], 'challenge': s['challenge'],
           'advises': s['advises'], 'how': s['how'], 'proof': proof, 'first': s['first'], 'sources': uniq}
    return out


def check(e):
    bad = []
    lim = {'title': 60, 'standfirst': 160, 'challenge': 360, 'advises': 520, 'figure': 18, 'caption': 120}
    for k, n in lim.items():
        if len(e[k]) > n:
            bad.append('%s is %d characters (at most %d)' % (k, len(e[k]), n))
    if not re.search(r'\d', e['figure']):
        bad.append('figure has no digit')
    sents = re.split(r'(?<=\.)\s+', e['advises'])
    if len(sents) != 2 or not sents[1].startswith('With super intelligence,'):
        bad.append('advises must be two sentences, the second beginning "With super intelligence,"')
    if e['advises'].startswith('Perfect Nations advises'):
        bad.append('advises begins with "Perfect Nations advises"')
    text = ' '.join([e['title'], e['standfirst'], e['challenge'], e['advises'], e['first'], e['caption']] + e['how'] + [e['proof']['label']])
    if re.search(r'\bpa(y|ys|id|ying)\b', text, re.I):
        bad.append('the word pay')
    if 'FFD' in text or "'" in text:
        bad.append('FFD or a straight apostrophe')
    if re.search(r"\b\w+n’t\b|’(re|ve|ll|d|m)\b|\b(it|that|there|what)’s\b", text, re.I):
        bad.append('a contraction')
    order = ['Food', 'Water', 'Shelter', 'Energy', 'Education', 'Health', 'Livelihood']
    if e['standards'] != sorted(e['standards'], key=order.index):
        bad.append('standards out of order')
    for x in e['sources'] + [e['proof']]:
        if not x['url'].startswith('https://') or re.search(r'[\s"<>]', x['url']):
            bad.append('url %s' % x['url'])
    return bad


son = json.loads(SON.read_text())
have = {x['no'] for x in son['dispatches']}
new = [entry(s) for s in S]
problems = 0
for e in new:
    p = check(e)
    problems += len(p)
    for b in p:
        print('No. %d %s: %s' % (e['no'], e['nation'], b))
if problems:
    raise SystemExit('%d problem(s); nothing written' % problems)
for e in new:
    if e['no'] in have:
        son['dispatches'] = [x for x in son['dispatches'] if x['no'] != e['no']]
son['dispatches'] = sorted(son['dispatches'] + new, key=lambda x: x['no'], reverse=True)
son['updated'] = DATE
SON.write_text(json.dumps(son, indent=1, ensure_ascii=False) + '\n')
for e in new:
    print('No. %d %-10s %-28s %s  (%s)' % (e['no'], e['nation'], e['title'], e['figure'], ', '.join(e['standards'])))
