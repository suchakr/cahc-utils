# tools/scan_requirements.py
# Simple scanner that looks for import statements in .py and .ipynb files
# and writes a suggested package list. Conservative — manual review recommended.

import re
import json
from pathlib import Path
from collections import Counter

ROOT = Path(__file__).resolve().parents[1]  # points to cahc-utils/jyotisha
INCLUDE_EXTS = ['.py', '.ipynb']
IMPORT_RE = re.compile(r'^\s*(?:from|import)\s+([A-Za-z0-9_\.]+)')


def extract_from_py(text):
    pkgs = []
    for line in text.splitlines():
        m = IMPORT_RE.match(line)
        if m:
            name = m.group(1).split('.')[0]
            pkgs.append(name)
    return pkgs


def extract_from_ipynb(path):
    pkgs = []
    try:
        nb = json.loads(path.read_text(encoding='utf-8'))
    except Exception:
        return pkgs
    for cell in nb.get('cells', []):
        if cell.get('cell_type') == 'code':
            src = ''.join(cell.get('source', []))
            pkgs.extend(extract_from_py(src))
    return pkgs


def main():
    files = []
    for p in ROOT.rglob('*'):
        if p.suffix in INCLUDE_EXTS:
            files.append(p)
    counter = Counter()
    for f in files:
        if f.suffix == '.py':
            text = f.read_text(encoding='utf-8')
            pkgs = extract_from_py(text)
        else:
            pkgs = extract_from_ipynb(f)
        counter.update(pkgs)
    stdlike = set([
        'sys','os','re','math','json','datetime','pathlib','typing',
        'collections','itertools','functools','statistics','time','io'
    ])
    candidates = [p for p,count in counter.most_common() if p not in stdlike and len(p) > 1]
    out_path = ROOT / 'requirements-suggested.txt'
    with out_path.open('w', encoding='utf-8') as fh:
        for p in candidates:
            fh.write(p + '\n')
    print(f"Scanned {len(files)} files. Suggested package names written to: {out_path}")
    print("Top candidates (name:count):")
    for p,count in counter.most_common()[:50]:
        if p not in stdlike and len(p) > 1:
            print(f"  {p}: {count}")


if __name__ == '__main__':
    main()
