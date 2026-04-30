from __future__ import annotations

import argparse
import re
from pathlib import Path

from jyotisha_2026.paths import EXPLORATIONS_ROOT, LAB_ROOT


def slugify(text: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return slug or "exploration"


def write_if_missing(path: Path, content: str) -> bool:
    if path.exists():
        return False
    path.write_text(content, encoding="utf-8")
    return True


def brief_content(title: str, slug: str) -> str:
    return f"""# {title}

Slug: `{slug}`
Status: draft

## Question

State the exact question being investigated.

## Inputs

- upstream datasets
- site assumptions
- epoch assumptions
- proxy or representative-star assumptions

## Outputs

- plot(s)
- table(s)
- short narration

## Open Questions

- question 1
- question 2
"""


def lab_index_content(title: str, slug: str) -> str:
    return f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{title}</title>
    <link rel="stylesheet" href="../shared/css/site.css">
  </head>
  <body>
    <header class="hero">
      <div class="hero-inner">
        <p class="eyebrow">Exploration</p>
        <h1>{title}</h1>
        <p class="lede">
          This page is scaffolded and ready for plots, tables, and narration.
        </p>
      </div>
    </header>

    <main class="content">
      <section class="panel">
        <h2>Status</h2>
        <p>Scaffold created for <code>{slug}</code>.</p>
      </section>

      <section class="panel">
        <h2>Planned Outputs</h2>
        <p>Add generated plots, export tables, and short interpretation notes here.</p>
        <p><a href="../index.html">Back to lab index</a></p>
      </section>
    </main>
  </body>
</html>
"""


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("title")
    parser.add_argument("--slug")
    args = parser.parse_args()

    title = args.title.strip()
    slug = args.slug or slugify(title)

    brief_path = EXPLORATIONS_ROOT / f"{slug}.md"
    lab_dir = LAB_ROOT / slug
    plots_dir = lab_dir / "plots"
    tables_dir = lab_dir / "tables"
    narration_dir = lab_dir / "narration"
    lab_index = lab_dir / "index.html"

    lab_dir.mkdir(parents=True, exist_ok=True)
    plots_dir.mkdir(exist_ok=True)
    tables_dir.mkdir(exist_ok=True)
    narration_dir.mkdir(exist_ok=True)

    brief_created = write_if_missing(brief_path, brief_content(title, slug))
    page_created = write_if_missing(lab_index, lab_index_content(title, slug))

    print(f"slug={slug}")
    print(f"brief={'created' if brief_created else 'exists'}:{brief_path}")
    print(f"page={'created' if page_created else 'exists'}:{lab_index}")
    print("next=add script, generate outputs, update lab/index.html")


if __name__ == "__main__":
    main()
