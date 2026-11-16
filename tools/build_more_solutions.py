#!/usr/bin/env python3
"""
PERFECT NATIONS - THE MORE SOLUTIONS FILE - v1.0 - 2026-11-15 (the Steward-General)

Builds data/more-solutions.json: for every open blueprint, up to three more Solutions, shown as a deck of
stacked cards beside the nation's lead Solution (tools/build_nations.py, v12.9 and later).

  - The standards are chosen here, never by hand: the nation's next gaps after its lead Solution, nearest
    the floor first, from the seven standards its blueprint publishes (data/<slug>.json, guarantees), skipping
    any standard not measured or already at 98 or more.
  - The challenge is written here from the figure and source exactly as the blueprint publishes them
    (CHALLENGE_OVERRIDE for the notes that follow no common pattern).
  - The title, who finances it and the advice are written by the State of Nations Steward in
    tools/more/content_*.py: CONTENT = {slug: [(finance, title, advises), ...]} in the order of the
    standards chosen here. finance is D (development banks), P (private investors) or C (corporate
    partners); a nation with three cards has one of each.

  python3 tools/build_more_solutions.py --brief [slugs]   print what the Steward writes from
  python3 tools/build_more_solutions.py                   write data/more-solutions.json (checks every rule)
"""
import glob
import importlib.util
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / 'data' / 'more-solutions.json'
FINANCE = {'D': 'Development banks', 'P': 'Private investors', 'C': 'Corporate partners'}
MET = 98.0
THE = {'Bahamas', 'Central African Republic', 'Comoros', 'Czech Republic', 'Dominican Republic', 'Gambia', 'Holy See',
       'Maldives', 'Marshall Islands', 'Netherlands', 'Philippines', 'Solomon Islands', 'United Arab Emirates',
       'United Kingdom', 'United States', 'Republic of the Congo'}

# Notes that follow no common pattern: (slug, standard) -> the challenge, figures exactly as published.
CHALLENGE_OVERRIDE = {
    ('afghanistan', 'Health'): 'Afghanistan scores 42 of 100 on the WHO index of essential health service coverage, and women have been barred from medical training since December 2024.',
    ('barbados', 'Livelihoods'): 'In the last poverty survey of Barbados, now dated, 82.5% of people lived above the national poverty line.',
    ('brazil', 'Education'): '48% of children in Brazil could not read a simple text by the end of primary school, in the last data, from 2013.',
    ('cuba', 'Energy'): 'At the evening peak on 10 November 2026, the grid of Cuba could serve 970 of 2,900 MW of demand; the day before, supply was cut for all 24 hours.',
    ('cuba', 'Water'): 'On 3 November 2026, 2,681,770 Cubans, 28.4% of the population, had their piped water cut.',
    ('dr-congo', 'Energy'): 'In DR Congo, 22.5% of people have electricity, about 124 kWh a person a year, and only 5% cook cleanly.',
    ('lebanon', 'Energy'): 'The national power company of Lebanon supplies about one third of national demand, and existing plants give 8 to 10 hours of power a day at best.',
    ('palestine', 'Energy'): 'The Gaza grid has been down since October 2023, and 38.3% of Palestinians live in Gaza.',
    ('syria', 'Energy'): 'Generation in Syria passed 3,000 MW in January 2026, against demand of about 6,500 MW.',
}


def the(n):
    n = n.strip()
    if n.startswith('The '):
        return 'the ' + n[4:]
    return ('the ' + n) if n in THE else n


def cap(s):
    return s[:1].upper() + s[1:]


def num(x):
    return x.rstrip('%')


def challenge(slug, name, g):
    if (slug, g['name']) in CHALLENGE_OVERRIDE:
        return CHALLENGE_OVERRIDE[(slug, g['name'])]
    st, note, disp = g['name'], (g.get('note') or '').strip(), num(str(g.get('display') or ''))
    N = the(name)
    yr = re.search(r'\b(19|20)\d\d\b', note)
    when = (' in %s' % yr.group(0)) if yr and 'dated' in note else ''
    try:
        v = float(g['value'])
    except (TypeError, ValueError):
        return None
    if st == 'Food':
        m = re.search(r'([\d.]+)% are moderately or severely food insecure', note)
        if m:
            return '%s%% of people in %s are moderately or severely food insecure%s.' % (m.group(1), N, when)
        m = re.search(r'([\d.]+)% are undernourished', note)
        if m:
            return '%s%% of people in %s are undernourished, and food insecurity is not yet measured.' % (m.group(1), N)
    if st == 'Water':
        if note.startswith('Safely managed drinking water'):
            return ('Only %s%% of people in %s use safely managed drinking water%s.' % (disp, N, when)) if v < 90 else \
                   ('%s still falls short of safe water for all: %s%% use safely managed drinking water%s.' % (cap(N), disp, when))
        if note.startswith('Basic drinking water') or note.startswith('Basic water'):
            if v >= 90:
                return 'Not every home in %s has safe water: %s%% of people have basic drinking water%s, and safely managed water is not yet measured.' % (N, disp, when)
            return 'Only %s%% of people in %s have basic drinking water%s, and safely managed water is not yet measured.' % (disp, N, when)
    if st == 'Shelter':
        m = re.match(r'Safely managed sanitation(?:; ([\d.]+)% of city dwellers live in slums)?', note)
        if m:
            s = ('Only %s%% of people in %s use safely managed sanitation%s' % (disp, N, when)) if v < 90 else \
                ('Not every home in %s has safe sanitation: %s%% of people use safely managed sanitation%s' % (N, disp, when))
            if m.group(1) and float(m.group(1)) >= 1:
                s += ', and %s%% of city dwellers live in slums' % m.group(1)
            return s + '.'
        m = re.search(r'([\d.]+)% (?:of city dwellers )?live in slums', note)
        if m and ('City dwellers outside slums' in note or 'Outside urban slums' in note):
            return '%s%% of city dwellers in %s live in slums%s.' % (m.group(1), N, when)
    if st == 'Energy':
        m = re.match(r'([\d.]+)% cook with clean fuels and technology(?:; ([\d.]+)% have electricity)?', note)
        if m:
            if m.group(2) and float(m.group(2)) < 100:
                if float(m.group(2)) < float(m.group(1)):
                    return 'Only %s%% of people in %s have electricity, though %s%% cook with clean fuels and technology.' % (m.group(2), N, m.group(1))
                return 'In %s, %s%% of people have electricity and only %s%% cook with clean fuels and technology.' % (N, m.group(2), m.group(1))
            return ('Only %s%% of people in %s cook with clean fuels and technology.' % (m.group(1), N)) if float(m.group(1)) < 90 else \
                   ('Not every home in %s cooks cleanly: %s%% of people cook with clean fuels and technology.' % (N, m.group(1)))
        m = re.match(r'About ([\d,.]+) kWh(?: of electricity)? a person a year, against (?:the Living Line of )?([\d,]+)(?:; ([\d.]+)% cook (?:with clean fuels|cleanly))?', note)
        if m:
            s = 'People in %s use about %s kWh of electricity a year, against the Living Line of %s kWh' % (N, m.group(1), m.group(2))
            if m.group(3):
                s += ', and %s%% cook with clean fuels' % m.group(3)
            return s + '.'
    if st == 'Education':
        m = re.match(r'([\d.]+)% of children read a simple text by the end of primary school', note)
        if m:
            return ('Only %s%% of children in %s can read a simple text by the end of primary school%s.' % (m.group(1), N, when)) if float(m.group(1)) < 90 else \
                   ('Not every child in %s reads by the end of primary school: %s%% can read a simple text%s.' % (N, m.group(1), when))
        m = re.match(r'([\d.]+)% (?:of young people )?complete lower secondary school', note)
        if m:
            return ('Only %s%% of young people in %s complete lower secondary school%s.' % (m.group(1), N, when)) if float(m.group(1)) < 90 else \
                   ('Not every young person in %s finishes school: %s%% complete lower secondary%s.' % (N, m.group(1), when))
        if note.startswith('Lower-secondary completion'):
            return '%s%% of young people in %s complete lower secondary school, and reading is not yet measured.' % (disp, N)
    if st == 'Health':
        if note in ('WHO service coverage index', 'UHC service coverage index'):
            return '%s scores %s of 100 on the WHO index of essential health service coverage.' % (cap(N), disp)
    if st == 'Livelihoods':
        m = re.match(r'Above the national poverty line; ([\d.]+)% live below it', note)
        if m:
            return '%s%% of people in %s live below the national poverty line%s.' % (m.group(1), N, when)
        m = re.match(r'Above US\$([\d.]+) a day; ([\d.]+)% live below it', note)
        if m:
            return '%s%% of people in %s live on less than US$%s a day%s.' % (m.group(2), N, m.group(1), when)
    return None


def nations():
    man = json.loads((ROOT / 'pages' / 'manifest.json').read_text(encoding='utf-8'))
    return sorted(k[6:] for k in man['pages'] if k.startswith('pn-bp-'))


def lead_of(d, son):
    for x in son.get('dispatches', []):
        if x.get('kind') == 'design' and x.get('nation') == d['nation']:
            st = x.get('standards') or []
            if isinstance(st, str):
                st = re.findall(r"'([A-Za-z]+)'", st)
            if st:
                return 'Livelihoods' if st[0] == 'Livelihood' else st[0]
    st = (d.get('coverage') or {}).get('set_by')
    return 'Livelihoods' if st == 'Livelihood' else st


def choose(slug, son):
    d = json.loads((ROOT / 'data' / ('%s.json' % slug)).read_text(encoding='utf-8'))
    lead = lead_of(d, son)
    picks = []
    for g in sorted((g for g in d.get('guarantees') or [] if g.get('name') != lead), key=lambda g: (g.get('value') is None, g.get('value') or 0)):
        if g.get('value') is None or float(g['value']) >= MET or not g.get('url', '').startswith('https://'):
            continue
        ch = challenge(slug, d['nation'], g)
        picks.append({'standard': g['name'], 'value': g['value'], 'note': g.get('note'), 'challenge': ch,
                      'source': {'label': g.get('source') or 'Source', 'url': g['url']}})
        if len(picks) == 3:
            break
    return d, lead, picks


def brief(slugs):
    son = json.loads((ROOT / 'data' / 'state-of-nations.json').read_text(encoding='utf-8'))
    for slug in slugs:
        d, lead, picks = choose(slug, son)
        assets = (d.get('assets') or {}).get('items') or []
        reg = (d.get('capital') or {}).get('register') or []
        print('## %s | %s | lead: %s' % (slug, d['nation'], lead))
        print('   assets: ' + '; '.join('%s (%s)' % (a.get('name'), (a.get('label') or '')[:40]) for a in assets[:5]))
        for p in picks:
            print('   - %s: %s' % (p['standard'], p['challenge'] or ('NO PATTERN: ' + (p['note'] or ''))))


def load_content():
    content = {}
    for f in sorted(glob.glob(str(ROOT / 'tools' / 'more' / 'content_*.py'))):
        spec = importlib.util.spec_from_file_location(Path(f).stem, f)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        for k, v in mod.CONTENT.items():
            assert k not in content, 'written twice: ' + k
            content[k] = v
    return content


def curly(s):
    return re.sub(r"(?<=\w)'(?=\w)", '’', s)


def check(slug, title, adv):
    errs = []
    if len(title) > 60:
        errs.append('title over 60')
    if len(adv) > 520:
        errs.append('advice over 520 (%d)' % len(adv))
    if re.search(r'super ?intelligence|\bSI\b', adv, re.I):
        errs.append('the advice names super intelligence; the site never does (Preeti Sinha, 16 Nov 2026)')
    if re.search(r"\bpay(s|ing|ment)?\b|FFD|n't|\b(I'm|it's|don't)\b", adv, re.I):
        errs.append('forbidden word')
    if re.search(r'\d', adv):
        errs.append('no figures in the advice')
    if adv.startswith('Perfect Nations advises'):
        errs.append('must not begin "Perfect Nations advises"')
    return ['%s: %s: %s' % (slug, title, e) for e in errs]


def build():
    son = json.loads((ROOT / 'data' / 'state-of-nations.json').read_text(encoding='utf-8'))
    content = load_content()
    out, errs, titles = {}, [], {}
    for slug in nations():
        if slug not in content:
            continue
        d, lead, picks = choose(slug, son)
        cards = content[slug]
        if len(cards) != len(picks):
            errs.append('%s: %d cards written for %d standards' % (slug, len(cards), len(picks)))
            continue
        fins = [c[0] for c in cards]
        if len(cards) == 3 and sorted(fins) != ['C', 'D', 'P']:
            errs.append('%s: one card each for D, P and C' % slug)
        rows = []
        for p, (fin, title, adv) in zip(picks, cards):
            if not p['challenge']:
                errs.append('%s %s: no challenge pattern' % (slug, p['standard']))
                continue
            title, adv = curly(title.strip()), curly(adv.strip())
            errs += check(slug, title, adv)
            if title.lower() in titles:
                errs.append('%s: title also used for %s: %s' % (slug, titles[title.lower()], title))
            titles[title.lower()] = slug
            rows.append({'standard': p['standard'], 'finance': FINANCE[fin], 'title': title,
                         'challenge': curly(p['challenge']), 'source': p['source'], 'advises': adv})
        out[slug] = {'nation': d['nation'], 'lead': lead, 'cards': rows}
    if errs:
        sys.exit('\n'.join(errs))
    OUT.write_text(json.dumps({'updated': '2026-11-15', 'note': 'Built by tools/build_more_solutions.py; do not edit by hand.',
                               'nations': out}, indent=1, ensure_ascii=False) + '\n', encoding='utf-8')
    print('%d nations, %d cards -> %s' % (len(out), sum(len(v['cards']) for v in out.values()), OUT.relative_to(ROOT)))


if __name__ == '__main__':
    a = sys.argv[1:]
    if a and a[0] == '--brief':
        brief(a[1:] or nations())
    else:
        build()
