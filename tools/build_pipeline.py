#!/usr/bin/env python3
"""Build the Perfect Nations deal pipeline for funders: data/deal-pipeline.json.

The pipeline is every financeable Solution Perfect Nations has designed, one line each, in one file, so a funder
can see by nation, region, standard and kind of funder where the deals are (the Steward-General, 24 Nov 2026:
"Where is my pipeline of deals stored?"). It adds no fact: every line is copied from an approved file.

  1. The Solutions of State of Nations (data/state-of-nations.json `dispatches`, kind "design"): title, challenge,
     advice, the deal that proves it and its sources.
  2. Each blueprint's lead Solution (data/solutions-by-nation.json): the standard furthest from reach, its gap and
     source, and the instrument of that standard's playbook with its proof. Left out where a Solution of State of
     Nations already covers the same nation and standard.
  3. The three more Solutions of every blueprint (data/more-solutions.json): one each from development banks,
     private investors and corporate partners.

Stage: every line is "Designed" (designed by Perfect Nations from public data). A line becomes a mandate only when
the nation asks; the file says so, and the For Funders page shows it.

Run from the repository root:  python3 tools/build_pipeline.py
Then rebuild the For Funders page (python3 tools/build_funders.py), which counts the pipeline and reads it live.
"""
import json
import re
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / 'data'
ORDER = ['Food', 'Water', 'Shelter', 'Energy', 'Education', 'Health', 'Livelihood']
FINANCE = ['Development banks', 'Private investors', 'Corporate partners']
REGIONS = {'africa': 'Africa', 'americas': 'Americas', 'asia': 'Asia', 'europe': 'Europe',
           'middle-east': 'Middle East', 'oceania': 'Oceania'}
SITE = 'https://perfectnations.com'


def load(name):
    return json.loads((DATA / name).read_text(encoding='utf-8'))


def plain(s):
    return re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', '', s or '')).strip()


def gap_sentence(gap, text):
    """The figure and its caption as one sentence, as on the blueprint ("18.6%" + "Of people in..." reads
    "18.6% of people in...")."""
    t = plain(text)
    if gap and t.startswith('Of '):
        t = 'of ' + t[3:]
    return ((gap + ' ') if gap else '') + t


def https(u):
    return u if isinstance(u, str) and re.match(r'^https://[^\s"\'<>()]+$', u) else ''


def main():
    son = load('state-of-nations.json')
    sbn = load('solutions-by-nation.json')
    more = load('more-solutions.json')
    bps = {b['slug']: b for b in load('blueprints.json')['open']}
    by_name = {b['name']: b for b in bps.values()}
    plays = {p['standard']: p for p in sbn['standards']}

    def where(slug=None, name=None):
        b = bps.get(slug) if slug else by_name.get(name)
        if not b:
            sys.exit('no open blueprint for %r' % (slug or name))
        return b

    lines, covered = [], set()

    # 1. the Solutions of State of Nations, newest first
    for x in sorted((d for d in son['dispatches'] if d.get('kind') == 'design'), key=lambda d: -d['no']):
        b = where(name=x['nation'])
        std = (x.get('standards') or [''])[0]
        covered.add((b['slug'], std))
        p = x.get('proof') or {}
        src = (x.get('sources') or [{}])[0]
        lines.append({
            'id': 's%02d' % x['no'], 'kind': 'solution', 'no': x['no'],
            'nation': x['nation'], 'slug': b['slug'], 'region': REGIONS[b['region']],
            'standard': std, 'finance': '', 'title': plain(x['title']),
            'challenge': plain(x['challenge']), 'advises': plain(x['advises']),
            'instrument': plain(p.get('name')),
            'proof': {k: plain(p.get(k)) for k in ('where', 'year', 'figure', 'label', 'source')} | {'url': https(p.get('url'))} if p.get('url') else None,
            'source': {'label': plain(src.get('label')), 'url': https(src.get('url'))},
            'url': '%s/state-of-nations/#solution-%02d' % (SITE, x['no']),
            'date': x.get('date', ''),
        })

    # 2. each blueprint's lead Solution, where no Solution of State of Nations covers it
    for n in sbn['nations']:
        std = n.get('standard')
        if not std or (n['slug'], std) in covered or std not in plays:
            continue
        b = where(slug=n['slug'])
        play = plays[std]
        p = play.get('proof') or {}
        aw = n.get('at_work') or {}
        src = n.get('source') or {}
        lines.append({
            'id': '%s-lead' % n['slug'], 'kind': 'lead',
            'nation': n['name'], 'slug': n['slug'], 'region': REGIONS[b['region']],
            'standard': std, 'finance': '', 'title': plain(play.get('head')),
            'challenge': gap_sentence(n.get('gap'), n.get('gap_text')), 'advises': plain(play.get('advises')),
            'instrument': plain(play.get('name')),
            'at_work': ({'name': plain(aw.get('name')), 'amount': plain(aw.get('amount')), 'url': https(aw.get('url'))}
                        if aw.get('name') and https(aw.get('url')) else None),
            'proof': ({k: plain(p.get(k)) for k in ('where', 'year', 'figure', 'label', 'source')} | {'url': https(p.get('url'))}
                      if https(p.get('url')) else None),
            'source': {'label': plain(src.get('label')), 'url': https(src.get('url'))},
            'url': '%s/blueprints/%s/' % (SITE, n['slug']),
        })

    # 3. the three more Solutions of every blueprint
    for slug, v in more['nations'].items():
        b = where(slug=slug)
        for k, c in enumerate(v.get('cards') or [], 1):
            src = c.get('source') or {}
            lines.append({
                'id': '%s-%d' % (slug, k), 'kind': 'more',
                'nation': v['nation'], 'slug': slug, 'region': REGIONS[b['region']],
                # more-solutions.json writes "Livelihoods"; the seven standards say "Livelihood"
                'standard': {'Livelihoods': 'Livelihood'}.get(c['standard'], c['standard']),
                'finance': c['finance'], 'title': plain(c['title']),
                'challenge': plain(c['challenge']), 'advises': plain(c['advises']),
                'source': {'label': plain(src.get('label')), 'url': https(src.get('url'))},
                'url': '%s/blueprints/%s/' % (SITE, slug),
            })

    # checks: every line has a nation, a standard of the seven, a title, a challenge and an https source
    ids = Counter(x['id'] for x in lines)
    dup = [k for k, c in ids.items() if c > 1]
    if dup:
        sys.exit('duplicate pipeline ids: %s' % dup[:5])
    for x in lines:
        if x['standard'] not in ORDER:
            sys.exit('%s: standard %r is not one of the seven' % (x['id'], x['standard']))
        if x['finance'] and x['finance'] not in FINANCE:
            sys.exit('%s: unknown source of finance %r' % (x['id'], x['finance']))
        if not (x['title'] and x['challenge'] and x['source']['url']):
            sys.exit('%s: a title, a challenge and an https source are required' % x['id'])
        for k in [k for k, v in x.items() if v in (None, '')]:
            del x[k]

    nations = sorted({x['slug'] for x in lines})
    count = {
        'lines': len(lines), 'nations': len(nations),
        'by_kind': dict(Counter(x['kind'] for x in lines)),
        'by_standard': {s: sum(1 for x in lines if x['standard'] == s) for s in ORDER},
        'by_finance': {f: sum(1 for x in lines if x.get('finance') == f) for f in FINANCE}
                      | {'Lead and State of Nations Solutions': sum(1 for x in lines if not x.get('finance'))},
        'by_region': {r: sum(1 for x in lines if x['region'] == r) for r in sorted(set(REGIONS.values()))},
        'matrix': {s: {f: sum(1 for x in lines if x['standard'] == s and x.get('finance', '') == f) for f in FINANCE + ['']}
                   for s in ORDER},
    }
    doc = {
        'page': 'deal-pipeline',
        'updated': datetime.now(timezone.utc).strftime('%Y-%m-%d'),
        'about': ('The Perfect Nations deal pipeline: every financeable Solution designed for the 195 blueprints, one line '
                  'each. Built by tools/build_pipeline.py from data/state-of-nations.json, data/solutions-by-nation.json '
                  'and data/more-solutions.json; do not edit by hand. Read by perfectnations.com/for-funders/.'),
        'stage': ('Designed: each line is designed by Perfect Nations from public data. A line becomes a mandate only '
                  'when the nation asks for it.'),
        'count': count,
        'lines': lines,
    }
    (DATA / 'deal-pipeline.json').write_text(json.dumps(doc, indent=1, ensure_ascii=False) + '\n', encoding='utf-8')
    print('data/deal-pipeline.json: %d lines across %d nations %s' % (len(lines), len(nations), dict(count['by_kind'])))


if __name__ == '__main__':
    main()
