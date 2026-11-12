"""Switch the site address in the repository from perfectnations.org to perfectnations.com.

Run from the repository root:  python3 tools/switch_domain.py [--check]

- Every https://perfectnations.org link, image address and the text "perfectnations.org"
  becomes perfectnations.com, in pages/, data/, figures/, art/, src/, tools/, .github/ and README.md.
- Email addresses stay as they are (anything@perfectnations.org): the mailboxes live on .org.
- Address checks written as regular expressions (perfectnations\\.org) accept both addresses,
  so a page keeps working whichever address it is opened on.
- archive/ (old versions) and wordpress/ (the plugin and its changelog) are left alone.
--check reports what would change and exits 1 if anything still needs switching.
"""
import os, re, sys, json

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKIP_DIRS = {'.git', 'archive', 'wordpress', '__pycache__', 'node_modules', 'probe-out'}
TEXT_EXT = {'.html', '.htm', '.json', '.js', '.css', '.py', '.md', '.txt', '.yml', '.yaml', '.svg', '.xml', '.csv'}
SELF = os.path.abspath(__file__)

REGEX_FORM = re.compile(r'perfectnations\\\.org(?!\|)')          # perfectnations\.org in a JS/py regex
PLAIN_FORM = re.compile(r'(?<![@A-Za-z0-9_.-])perfectnations\.org(?![A-Za-z0-9_-])')

def switch(text):
    text, n1 = REGEX_FORM.subn(r'perfectnations\\.(?:org|com)', text)
    text, n2 = PLAIN_FORM.subn('perfectnations.com', text)
    return text, n1 + n2

def files():
    for d, dirs, names in os.walk(ROOT):
        dirs[:] = [x for x in dirs if x not in SKIP_DIRS]
        for n in names:
            p = os.path.join(d, n)
            if os.path.abspath(p) == SELF or os.path.splitext(n)[1].lower() not in TEXT_EXT:
                continue
            yield p

def main():
    check = '--check' in sys.argv
    changed, total, bad_json = 0, 0, []
    for p in files():
        with open(p, encoding='utf-8', errors='surrogateescape') as f:
            old = f.read()
        new, n = switch(old)
        if not n:
            continue
        changed += 1; total += n
        if check:
            continue
        if p.endswith('.json'):
            try:
                json.loads(new)
            except Exception as e:
                bad_json.append((p, str(e)))
                continue
        with open(p, 'w', encoding='utf-8', errors='surrogateescape', newline='') as f:
            f.write(new)
    rel = lambda p: os.path.relpath(p, ROOT)
    print(('would change' if check else 'changed'), changed, 'files,', total, 'addresses')
    for p, e in bad_json:
        print('NOT CHANGED (JSON would break):', rel(p), e)
    sys.exit(1 if (check and changed) or bad_json else 0)

if __name__ == '__main__':
    main()
