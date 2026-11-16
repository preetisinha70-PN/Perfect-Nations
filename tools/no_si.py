#!/usr/bin/env python3
"""Keep super intelligence and the Stewards off perfectnations.com (Preeti Sinha, President and CEO, 16 Nov 2026).

    "remove all reference to Super intelligence and SI from perfectnations.com. in the about section - just
     profile me. keep the stewards internally for processing at claude but remove the profiles of all stewards
     from all visible pages of perfectnations.com. I am going to single-handedly run perfect nations."

    python3 tools/no_si.py --fix            remove every "With super intelligence, ..." sentence from the data
                                            the pages read and from the content sources that write it
    python3 tools/no_si.py --check [files]  list any mention left in the data and the page files (exit 1 if any)

What it removes: a whole sentence that names super intelligence (the Solutions used to close with one, for
example "With super intelligence, every network can be watched for leaks."). The sentences before it are kept.
Fields that no page shows (the internal "si" notes of a deal or a playbook standard) are left as they are.

The same rule runs in the browser: the blueprint and State of Nations scripts drop any such sentence that a
Steward writes into a data file later, so the site stays clean between reviews.
"""
import glob
import json
import re
import sys

# a sentence that names super intelligence (or SI as a word), with the space before it
SENTENCE = re.compile(
    r"(?:(?<=[.!?])\s+|^\s*)"
    r"(?:[^.!?\"<>]*?)(?:super ?intelligence|superintelligence|\(SI\)|\bSI\b(?![.\-/=]))"
    r"[^\"<>]*?[.!?](?=\s|$|[\"'<\\])",
    re.I)
# anything left that a visitor could read as a reference
MENTION = re.compile(r"(?i:super ?intelligence|superintelligence)|\(SI\)|SI Researcher|(?<![\w=./-])SI(?![\w.=/-])")

# data the pages read (every string field except the internal "si" notes)
DATA = ['data/state-of-nations.json', 'data/solutions-by-nation.json', 'data/more-solutions.json',
        'data/us/states/*.json', 'data/*.json', 'archive/**/*.json', 'figures/*.json']
# Python sources that write that data
SOURCES = ['tools/more/content_*.py', 'tools/measures/*.py']
SKIP_KEYS = {'si'}


def strip_si(text):
    """Remove each sentence that names super intelligence; keep the rest of the text as it was."""
    if not isinstance(text, str) or not MENTION.search(text):
        return text
    out = SENTENCE.sub('', text)
    return out.strip() if out != text else text


def _walk(o, changed):
    if isinstance(o, dict):
        for k in list(o):
            if k in SKIP_KEYS:
                continue
            if isinstance(o[k], str):
                n = strip_si(o[k])
                if n != o[k]:
                    o[k] = n
                    changed.append(1)
            else:
                _walk(o[k], changed)
    elif isinstance(o, list):
        for i, v in enumerate(o):
            if isinstance(v, str):
                n = strip_si(v)
                if n != v:
                    o[i] = n
                    changed.append(1)
            else:
                _walk(v, changed)


def files(patterns):
    seen = []
    for p in patterns:
        for f in sorted(glob.glob(p, recursive=True)):
            if f not in seen and not f.startswith('archive/elementor/'):
                seen.append(f)
    return seen


def fix():
    total = 0
    for f in files(DATA):
        raw = open(f, encoding='utf-8').read()
        try:
            o = json.loads(raw)
        except ValueError:
            continue
        changed = []
        _walk(o, changed)
        if changed:
            ascii_only = all(ord(c) < 128 for c in raw)
            second = raw.split('\n', 2)[1] if raw.count('\n') > 1 else ''
            indent = (len(second) - len(second.lstrip(' '))) or None
            out = json.dumps(o, indent=indent, ensure_ascii=ascii_only)
            open(f, 'w', encoding='utf-8').write(out + ('\n' if raw.endswith('\n') else ''))
            print('%s: %d text(s) cleaned' % (f, len(changed)))
            total += len(changed)
    for f in files(SOURCES):
        src = open(f, encoding='utf-8').read()
        new = re.sub(r"(?<=[.!?])\s+With super intelligence,[^\"'\n]*?[.!?](?=[\"'])", '', src)
        new = re.sub(r"(?<=[.!?])\s+With super intelligence,[^\"'\n]*?[.!?](?=\s)", '', new)
        if new != src:
            open(f, 'w', encoding='utf-8').write(new)
            print('%s: %d sentence(s) removed' % (f, len(MENTION.findall(src)) - len(MENTION.findall(new))))
    print('total data texts cleaned: %d' % total)


def check(paths):
    bad = 0
    for f in paths:
        try:
            src = open(f, encoding='utf-8').read()
        except (OSError, UnicodeDecodeError):
            continue
        if f.endswith('.json'):
            try:
                o = json.loads(src)
            except ValueError:
                o = None
            if o is not None:
                hits = []

                def look(x, key=None):
                    if isinstance(x, dict):
                        for k, v in x.items():
                            if k not in SKIP_KEYS:
                                look(v, k)
                    elif isinstance(x, list):
                        for v in x:
                            look(v, key)
                    elif isinstance(x, str) and MENTION.search(x) and not re.search(r'https?://', x):
                        hits.append('%s: %s' % (key, x[:120]))
                look(o)
                for h in hits:
                    print('%s: %s' % (f, h))
                bad += len(hits)
                continue
        for m in MENTION.finditer(src):
            line = src.count('\n', 0, m.start()) + 1
            text = src[src.rfind('\n', 0, m.start()) + 1:src.find('\n', m.end())]
            if 'NOSI' in text:  # the filter itself (the browser-side copy of this rule)
                continue
            print('%s:%d: %s' % (f, line, src[max(0, m.start() - 60):m.end() + 60].replace('\n', ' ')))
            bad += 1
    return bad


if __name__ == '__main__':
    if '--fix' in sys.argv:
        fix()
    elif '--check' in sys.argv:
        rest = [a for a in sys.argv[1:] if a != '--check'] or files(DATA) + files(['pages/*.html'])
        n = check(rest)
        print('no mention left' if not n else '%d mention(s) left' % n)
        sys.exit(1 if n else 0)
    else:
        print(__doc__)
