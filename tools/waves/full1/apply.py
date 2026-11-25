#!/usr/bin/env python3
"""Apply wave 1 of the full blueprints (tools/waves/full1/spec.py) to data/<slug>.json and stewards/<slug>.md.

    python3 tools/waves/full1/apply.py            write the changes
    python3 tools/waves/full1/apply.py --check    print the counts only

New register lines go after the last line of the same category, so the four lines a visitor sees first stay as the
Nation Steward chose them; a line already present (same name and source) is not added twice. Enterprises are kept in
the order of the seven standards. Each nation's stewards/<slug>.md gains a section "Full edition, wave 1" with every
new line and its source, and the Open gaps from the spec.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(Path(__file__).resolve().parent))
import spec  # noqa: E402

TODAY = '2026-11-25'
WAVE = ('algeria benin burkina-faso cabo-verde cameroon central-african-republic chad gabon gambia guinea liberia libya mali '
        'mauritania mauritius niger sierra-leone sudan togo tunisia').split()
ORDER = ['Food', 'Water', 'Shelter', 'Energy', 'Education', 'Health', 'Livelihood']


def insert_register(reg, new):
    added = 0
    have = {(x.get('name'), x.get('url')) for x in reg}
    for line in new:
        if (line['name'], line['url']) in have:
            continue
        idx = max([i for i, x in enumerate(reg) if x.get('cat') == line['cat']], default=len(reg) - 1)
        reg.insert(idx + 1, line)
        have.add((line['name'], line['url']))
        added += 1
    return added


def patch(reg, patches):
    done = []
    for prefix, fields in patches:
        for x in reg:
            if x.get('name', '').startswith(prefix):
                x.update(fields)
                done.append(prefix)
                break
        else:
            raise SystemExit('patch target not found: %r' % prefix)
    return done


def steward_section(slug, d, new_reg, new_rec, new_ent, patched):
    L = ['', '## Full edition, wave 1 (25 November 2026)', '',
         'Brief: Project doc claude/full-blueprints-151.md. Researched 25 November 2026; World Bank lines from the '
         'projects API (search.worldbank.org/api/v3, Board approval date and current commitment) and Finances One.', '',
         'Now on the page: %d lines in the record, %d in Capital already committed, %d enterprises, %d Sovereign Assets.' % (
             len(d['capital']['record']), len(d['capital']['register']), len(d['enterprises']['items']), len(d['assets']['items']))]
    if new_rec:
        L += ['', 'Added to the record:', '']
        L += ['- **%s:** %s. %s, %s' % (x['value'], x['text'], x['source'], x['url']) for x in new_rec]
    if new_reg:
        L += ['', 'Added to Capital already committed:', '']
        L += ['- **%s%s:** %s. %s %s' % (x['name'], (' (%s)' % x['amount']) if x['amount'] else '', x['detail'], x['text'], x['url']) for x in new_reg]
    if patched:
        L += ['', 'Amounts or notes filled in on lines already listed: ' + '; '.join(patched) + '.']
    if new_ent:
        L += ['', 'Added to Already working in %s:' % d['nation'], '']
        L += ['- **%s, %s:** %s %s, %s' % (x['standard'], x['name'], x['text'], x['source'], x['url']) for x in new_ent]
    gaps = spec.GAPS.get(slug) or []
    if gaps:
        L += ['', '### Open gaps (wave 1)', ''] + ['- ' + g for g in gaps]
    L += ['', 'Still to come: the interim Nation Portrait (Canva, colours edition) and the Letter to the Nations post in WordPress, published after the pull request is merged.', '']
    return '\n'.join(L)


def main():
    check = '--check' in sys.argv
    rows = []
    for slug in WAVE:
        p = ROOT / 'data' / ('%s.json' % slug)
        txt = p.read_text(encoding='utf-8')
        d = json.loads(txt)
        indent = len(txt.split('\n')[1]) - len(txt.split('\n')[1].lstrip(' '))  # keep the file's own indentation
        cap = d['capital']
        new_reg = [x for x in spec.REGISTER.get(slug, [])]
        n_reg = insert_register(cap['register'], new_reg)
        patched = patch(cap['register'], spec.PATCH.get(slug, []))
        new_rec = spec.RECORD.get(slug, [])
        cap['record'].extend(new_rec)
        new_ent = spec.ENTERPRISES.get(slug, [])
        items = d['enterprises']['items'] + new_ent
        d['enterprises']['items'] = sorted(items, key=lambda x: ORDER.index(x['standard']) if x['standard'] in ORDER else 9)
        if n_reg or new_rec or new_ent or patched:
            d['updated'] = TODAY
        rows.append((slug, len(cap['record']), len(cap['register']), len(d['enterprises']['items']), len(d['assets']['items']), n_reg))
        if not check:
            p.write_text(json.dumps(d, ensure_ascii=False, indent=indent) + '\n', encoding='utf-8')
            if n_reg or new_rec or new_ent or patched:
                sp = ROOT / 'stewards' / ('%s.md' % slug)
                sp.write_text(sp.read_text(encoding='utf-8').rstrip('\n') + '\n' + steward_section(slug, d, new_reg, new_rec, new_ent, patched), encoding='utf-8')
    print('nation                    record register enterprises assets (+register)')
    for r in rows:
        print('%-25s %6d %8d %11d %6d   (+%d)' % r)


if __name__ == '__main__':
    main()
