"""Energy re-measured for every blueprint, 12 November 2026 (the Steward-General: "Yes please check all").

1. The use test (approved 19 October 2026, never applied in waves 1 to 7): Energy is the lower of clean cooking
   and electricity used per person against the Living Line of 1,000 kWh a year (Ember, latest year).
2. The delivery test (Cuba, 12 November 2026, now every nation with an official figure): where the nation's own
   ministry, utility or a UN agency publishes how much of national demand the grid actually serves, the lower
   figure counts.
Run: python3 tools/measures/delivery_2026_11_12.py          (prints every change)
     python3 tools/measures/delivery_2026_11_12.py --write  (writes data/<slug>.json and stewards/<slug>.md)
"""
import json, re, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
EMBER = json.loads((ROOT / 'tools/measures/data/ember_kwh_per_person_2026-11-12.json').read_text())
EMBER_URL = EMBER['url']
ISO = {n['slug']: n['iso3'] for n in json.loads((ROOT / 'tools/waves/common/nations.json').read_text())}
EXTRA_ISO = {}  # filled from the World Bank links in each file (locations=XX)

# ---- the delivery test: official figures, each with its source (see the Steward notes for the full citation)
DELIVERY = {
    'lebanon': dict(value=100 / 3, display='33%', source='Ministry of Energy and Water, Dec 2025',
        url='https://energyandwater.gov.lb/ar/details/101089/minister-joe-saddi-s-power-sector-reset-energy-minister-joe-saddi-lays-out-a-hard-line-reform-roadmap-to-rescue-lebanon-s-electricity-sector-from-debt-decay-and-dysfunction-1768810589',
        note='The Minister of Energy: EDL supplies about one third of national demand, and existing plants give 8 to 10 hours a day at best. {cook}% cook with clean fuels (2024)',
        gap_text='Of the electricity Lebanon needs is not supplied by the state grid: EDL meets about one third of national demand.',
        steward='EDL supplies about one third of national demand; existing plants can give 8 to 10 hours of electricity a day at best (Minister of Energy and Water Joe Saddi, ministry website, dated 29 December 2025). 1/3 = 33.3%.'),
    'iraq': dict(value=24600 / 55000 * 100, display='44.7%', source='Ministry of Electricity, Sep 2026',
        url='https://www.iraqinews.com/iraq/iraqs-electricity-shortage-surpasses-35000-megawatts/',
        note='The grid produced 24,600 MW in September 2026, against the 55,000 to 60,000 MW needed for power around the clock. {cook}% cook with clean fuels (2024)',
        gap_text='Of the electricity Iraq needs is not supplied: 24,600 MW against at least 55,000 MW, September 2026.',
        steward='Production 24,600 MW against 55,000 to 60,000 MW needed for 24-hour supply (Ahmed Turki Jiyad, spokesperson of the Ministry of Electricity, IraqiNews, 20 September 2026; the ministry released 24,700 MW for September on 14 September 2026). 24,600 / 55,000 = 44.7%, the lower demand figure, so the gap is not overstated. Peak-season reading.'),
    'syria': dict(value=3000 / 6500 * 100, display='46.2%', source='Petra and Syrian Ministry of Energy, 2026',
        url='https://petra.gov.jo/crm/index.php/en/news/jordan-syria-ink-energy-agreement',
        note='Generation passed 3,000 MW in January 2026, against demand of about 6,500 MW. {cook}% cook with clean fuels (2024)',
        gap_text='Of the electricity Syria needs is not generated: about 3,000 MW against 6,500 MW of demand.',
        steward='Generation rose from 2,500 MW to over 3,000 MW after gas imports from Jordan began on 1 January 2026 (Jordan Minister of Energy, Petra, 26 January 2026); demand about 6,500 MW (Khaled Abu Di, Director-General of the Public Establishment for Electricity Transmission and Distribution, September 2025, https://www.zawya.com/en/projects/utilities/syria-suffers-from-sharp-power-gap-o7k783lk). ASSUMPTION: the 2025 demand figure holds for 2026. 3,000 / 6,500 = 46.2%.'),
    'palestine': dict(value=(1 - 2127034 / 5557096) * 100, display='61.7%', source='OCHA and PCBS, 2026',
        url='https://www.ochaopt.org/content/humanitarian-situation-report-6-march-2026',
        note='The Gaza grid has been down since October 2023 (OCHA), and 38.3% of Palestinians live in Gaza (PCBS, end of 2025). Before the war, 100% had electricity',
        gap_text='Of Palestinians live in Gaza, where the electricity grid has been down since October 2023.',
        steward='"Gaza, where the electricity grid has been down since October 2023" (OCHA, Humanitarian Situation Report, 6 March 2026). Population end of 2025: Palestine 5,557,096, Gaza Strip 2,127,034 (PCBS, https://pcbs.gov.ps/Downloads/book2736.pdf). 1 - 2,127,034 / 5,557,096 = 61.7%. ASSUMPTION: the West Bank grid serves its population.'),
}

NOTED = {  # rationing reported in 2026; no official national share of demand served found on 12 November 2026
    'iran': 'Tavanir rations households and industry in 2026 and reported about 4,200 MW lost to strikes (July 2026); official peak deficit figures conflict (Energy Minister, May 2026: no shortfall; Majlis Research Center: about 13,640 MW at peak).',
    'venezuela': 'Rationing of 4 to 12 hours a day outside Caracas through 2026; Corpoelec has published no schedule and no figure for demand served (record demand 15,625 MW on 10 August 2026).',
    'ukraine': 'Ukrenergo applies hourly outage schedules after strikes on the grid (November 2026); no national figure for demand served is published.',
    'libya': 'GECOL reinstated load shedding in July 2026 (cuts of 10 hours a day and more) and reported a deficit of about 1,000 MW; no dated national figure for demand served was found.',
    'tajikistan': 'Barki Tojik rations households in winter (4 to 5 hours a day in December 2025); no annual figure for demand served is published.',
    'kyrgyzstan': 'Peak-hour limit of 3 kW for households, October 2025 to March 2026, and imports to cover the winter deficit; no figure for demand served is published.',
    'ecuador': 'Scheduled cuts in 2026 were limited to maintenance (up to four hours on two weekends) and to industry in October; household supply was not rationed nationally.',
    'dominican-republic': 'Two national blackouts (November 2025, 23 February 2026) and frequent local cuts; energy not served is a small share of daily demand (OC-SENI).',
}

def pct(v):
    s = ('%.1f' % v).rstrip('0').rstrip('.')
    return s

def iso_of(slug, d):
    if slug in ISO: return ISO[slug]
    m = re.search(r'locations=([A-Z]{2})', json.dumps(d['guarantees']))
    if m:
        import pycountry
        c = pycountry.countries.get(alpha_2=m.group(1))
        return c.alpha_3 if c else None

def clean_cooking(e):
    m = re.match(r'\s*(\d+(?:\.\d+)?)% cook', e.get('note') or '')
    return float(m.group(1)) if m else None

def plan():
    out = {}
    for f in sorted((ROOT / 'data').glob('*.json')):
        d = json.loads(f.read_text())
        if not isinstance(d, dict) or 'guarantees' not in d: continue
        slug = f.stem
        e = next(x for x in d['guarantees'] if x['name'] == 'Energy')
        if slug == 'cuba' or e.get('value') is None or 'kWh' in (e.get('note') or ''):
            continue  # Cuba re-measured this morning; hand-built nations already carry the use test
        cook = clean_cooking(e)
        cur = float(e['value'])
        k = EMBER['by_iso3'].get(iso_of(slug, d) or '', {})
        kwh = k.get('kwh_demand') or k.get('kwh_generation')
        use = min(100.0, kwh / 10) if kwh else None
        new, why = cur, None
        if use is not None and use < cur - 0.05:
            new, why = use, 'use'
        if slug in DELIVERY and DELIVERY[slug]['value'] < new - 0.05:
            new, why = DELIVERY[slug]['value'], 'delivery'
        if why:
            out[slug] = dict(old=cur, new=round(new, 1), why=why, kwh=kwh, kwh_year=k.get('year'), cook=cook if cook is not None else cur)
    return out

if __name__ == '__main__':
    P = plan()
    for s, p in P.items():
        print('%-18s %-8s %5.1f -> %5.1f   kWh %s (%s)' % (s, p['why'], p['old'], p['new'], round(p['kwh']) if p['kwh'] else '-', p['kwh_year']))
    print(len(P), 'nations change')


# ---------------------------------------------------------------- writing (--write)
DEM = None

def demonym(slug, d):
    """The people of the nation as the file already names them, for the Gap sentence."""
    t = (d.get('coverage') or {}).get('gap_text') or ''
    m = re.match(r'Of (?!children|young|city|the )([A-Z][A-Za-z’\' -]+?) (?:lack|live|are|still|cannot|do|who)', t)
    return m.group(1) if m else None

def coverage_for(d, g):
    """The weakest measured standard, Health left out as the wave generator does; returns its name and value."""
    scored = [x for x in g if isinstance(x.get('value'), (int, float)) and x['name'] != 'Health']
    b = min(scored, key=lambda x: x['value'])
    return b['name'], b['value']

def energy_tile(slug, p):
    if p['why'] == 'delivery':
        D = DELIVERY[slug]
        return dict(value=round(D['value'], 1), display=D['display'], note=D['note'].format(cook=pct(p['cook'])), source=D['source'], url=D['url'])
    k = round(p['kwh'])
    return dict(value=p['new'], display=pct(p['new']),
                note='About {:,} kWh of electricity a person a year, against the Living Line of 1,000; {}% cook with clean fuels (2024)'.format(k, pct(p['cook'])),
                source='Ember, %d' % p['kwh_year'], url=EMBER_URL)

def energy_gap(slug, p):
    if p['why'] == 'delivery':
        return DELIVERY[slug]['gap_text']
    return 'Of the electricity a person needs is missing: about {:,} kWh a person a year, against the Living Line of 1,000.'.format(round(p['kwh']))

def steward_line(slug, p, tile):
    if p['why'] == 'delivery':
        src = DELIVERY[slug]['steward']
    else:
        src = ('Electricity demand per person {:,} kWh, {} (Ember, Yearly Electricity Data, 2026 release, {}; read through the Our World in Data energy dataset, accessed 12 November 2026). '
               '{:,} / 1,000 = {}%.').format(round(p['kwh']), p['kwh_year'], EMBER_URL, round(p['kwh']), pct(p['new']))
    return src

def write():
    P = plan()
    log = []
    for slug, p in P.items():
        f = ROOT / 'data' / ('%s.json' % slug)
        raw = f.read_text()
        d = json.loads(raw)
        g = d['guarantees']
        e = next(x for x in g if x['name'] == 'Energy')
        before = coverage_for(d, g)
        tile = energy_tile(slug, p)
        e.update(tile)
        after = coverage_for(d, g)
        cov = d['coverage']
        if after[0] == 'Energy':
            cov['set_by'] = 'Energy'
            cov['gap'] = '%s%%' % pct(100 - after[1])
            cov['gap_text'] = energy_gap(slug, p)
            if 'score' in cov:
                cov['score'] = round(after[1], 1)
        d['updated'] = '2026-11-12'
        d['reviewed'] = '2026-11-12T19:00Z'
        indent = 2 if raw.startswith('{\n  "') else 1
        f.write_text(json.dumps(d, indent=indent, ensure_ascii=False) + '\n')
        # the Steward notes
        sf = ROOT / 'stewards' / ('%s.md' % slug)
        if sf.exists():
            t = sf.read_text()
            line = '- **Energy, %s:** %s. %s, %s' % (tile['display'], tile['note'], tile['source'], tile['url'])
            t, n = re.subn(r'^- \*\*Energy, [^*]*:\*\*.*$', lambda m: line, t, count=1, flags=re.M)
            if after[0] == 'Energy':
                t = re.sub(r'^Furthest from reach: .*$', lambda m: 'Furthest from reach: Energy (%s). %s' % (cov['gap'], cov['gap_text']), t, count=1, flags=re.M)
            add = '- 12 November 2026, Energy re-measured (%s test): %s %s' % ('delivery' if p['why'] == 'delivery' else 'use', steward_line(slug, p, tile),
                   ' Energy now sets Coverage.' if after[0] == 'Energy' and before[0] != 'Energy' else '')
            t = t.rstrip('\n') + '\n' + add.rstrip() + '\n' if '## Open gaps' in t else t.rstrip('\n') + '\n\n## Open gaps\n\n' + add.rstrip() + '\n'
            sf.write_text(t)
        # the page words: how Energy is measured, and the source
        nf = ROOT / 'tools' / 'nation' / ('%s.json' % slug)
        if nf.exists():
            nraw = nf.read_text(); nd = json.loads(nraw)
            if p['why'] == 'delivery':
                m = nd['capita']['measures']
                if 'delivery test' not in m:
                    nd['capita']['measures'] = m + (' For %s, the delivery test (12 November 2026): Energy takes the lower of these and the share of national demand the grid actually serves, from %s.'
                                                    % (d['nation'], DELIVERY[slug]['source'].rsplit(',', 1)[0]))
            src = 'Electricity used per person: Ember, Yearly Electricity Data (2026 release), accessed 12 November 2026.' if p['why'] == 'use' else \
                  'Electricity supplied against demand: %s, read 12 November 2026.' % DELIVERY[slug]['source']
            if src not in nd['sources']:
                nd['sources'].append(src)
            ind = 2 if nraw.startswith('{\n  "') else (1 if nraw.startswith('{\n "') else None)
            nf.write_text(json.dumps(nd, indent=ind, ensure_ascii=False) + ('\n' if nraw.endswith('\n') else ''))
        log.append((slug, p['why'], p['old'], tile['value'], before, after))
    for slug, text in NOTED.items():
        sf = ROOT / 'stewards' / ('%s.md' % slug)
        if not sf.exists(): continue
        t = sf.read_text()
        add = '- 12 November 2026, delivery test for Energy: no official national figure for the share of demand served was found, so Energy is unchanged. %s The weekly review looks for one.' % text
        if '12 November 2026, delivery test' in t: continue
        t = t.rstrip('\n') + '\n' + add + '\n' if '## Open gaps' in t else t.rstrip('\n') + '\n\n## Open gaps\n\n' + add + '\n'
        sf.write_text(t)
    for r in log:
        print('%-16s %-8s %5.1f -> %5.1f   furthest %s %.1f -> %s %.1f' % (r[0], r[1], r[2], r[3], r[4][0], r[4][1], r[5][0], r[5][1]))

if __name__ == '__main__' and '--write' in sys.argv:
    write()
