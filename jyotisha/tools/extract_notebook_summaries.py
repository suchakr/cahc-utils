"""Extract the first markdown cell from each notebook under this folder
and write a `notebooks-summaries.md` file that can be included in README.

Run from the `jyotisha` directory like:
    python tools/extract_notebook_summaries.py
"""

import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]


def first_markdown(path: Path):
    try:
        nb = json.loads(path.read_text(encoding='utf-8'))
    except Exception:
        return None
    for cell in nb.get('cells', []):
        if cell.get('cell_type') == 'markdown':
            source = ''.join(cell.get('source', []))
            return source.strip()
    return None


def main():
    out = []
    paths = sorted(ROOT.rglob('*.ipynb'))
    for p in paths:
        # skip dot files and directories
        if p.name.startswith('.') or p.is_dir():
            continue
        # skip notebooks if any of [ test, ~ , checkpoint, backup] in path
        if 'tests' in str(p) or '~' in p.name or 'checkpoints' in str(p) or 'backup' in str(p):
            continue
        print(f'Processing: {p}')
        rel = p.relative_to(ROOT)
        summary = first_markdown(p)
        if not summary: summary = f"## TODO "
        filename = rel.name

        # append the filename to the end of  first h2 of the summary in parens
        summary = re.sub(r'^\s*##\s+(.*)', rf'## \1 ({filename})', summary)
        out.append((str(rel), summary))

    dst = ROOT / 'notebooks-summaries.md'
    with dst.open('w', encoding='utf-8') as fh:
        fh.write('# Notebook summaries\n\n')
        for rel, summary in out:
            # fh.write(f'## {rel}\n\n')
            if summary:
                fh.write(summary + '\n\n')
            else:
                fh.write('_No markdown summary found._\n\n')

    print(f'Wrote summaries for {len(out)} notebooks to: {dst}')


if __name__ == '__main__':
    main()
