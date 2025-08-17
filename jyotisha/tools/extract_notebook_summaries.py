"""Extract the first markdown cell from each notebook under this folder
and write a `notebooks-summaries.md` file that can be included in README.

Run from the `jyotisha` directory like:
    python tools/extract_notebook_summaries.py
"""

import json
from pathlib import Path

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
        rel = p.relative_to(ROOT)
        summary = first_markdown(p)
        out.append((str(rel), summary))

    dst = ROOT / 'notebooks-summaries.md'
    with dst.open('w', encoding='utf-8') as fh:
        fh.write('# Notebook summaries (first markdown cell)\n\n')
        for rel, summary in out:
            fh.write(f'## {rel}\n\n')
            if summary:
                fh.write(summary + '\n\n')
            else:
                fh.write('_No markdown summary found._\n\n')

    print(f'Wrote summaries for {len(out)} notebooks to: {dst}')


if __name__ == '__main__':
    main()
