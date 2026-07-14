from __future__ import annotations

import csv
import html
import json
from dataclasses import dataclass
from pathlib import Path

from PIL import Image

from jyotisha_2026.paths import EXPLORATIONS_ROOT, LAB_ROOT


SOURCE_ROOT = Path("/Users/sunder/projects/cahc/cahc-utils/stel_scripts/moon-shranga~")
SOURCES_PATH = EXPLORATIONS_ROOT / "chandra-marga-sources.tsv"
LAB_DIR = LAB_ROOT / "chandra-marga"
STRIPS_DIR = LAB_DIR / "strips"
SERIES_DIR = LAB_DIR / "series"
MANIFEST_PATH = LAB_DIR / "tables" / "strip-manifest.json"
OLD_SERIES_MANIFEST_PATH = LAB_DIR / "tables" / "series-manifest.json"
IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".webp"}
WEBP_MAX_WIDTH = 2200
WEBP_QUALITY = 84


@dataclass(frozen=True)
class SourceRow:
    id: str
    phase_order: int
    phase_label: str
    view_order: int
    view: str
    condition: str
    year: int
    source_rel: str
    caption: str

    @property
    def source_path(self) -> Path:
        return SOURCE_ROOT / self.source_rel

    @property
    def output_path(self) -> Path:
        return STRIPS_DIR / f"{self.id}.webp"

    @property
    def nav_group(self) -> str:
        return f"{self.view} {self.condition}"

    @property
    def section_title(self) -> str:
        return f"{self.phase_label} · {self.view} · {self.condition} · {year_heading(self.year)}"


def required_text(raw: dict[str, str], field: str) -> str:
    value = raw.get(field, "").strip()
    if not value:
        raise ValueError(f"Missing required field {field!r} in {SOURCES_PATH}")
    return value


def required_int(raw: dict[str, str], field: str) -> int:
    value = required_text(raw, field)
    try:
        return int(value)
    except ValueError as exc:
        raise ValueError(f"Field {field!r} must be an integer: {value!r}") from exc


def read_sources() -> list[SourceRow]:
    with SOURCES_PATH.open(newline="", encoding="utf-8") as file:
        rows = []
        for raw in csv.DictReader(file, delimiter="\t"):
            rows.append(
                SourceRow(
                    id=required_text(raw, "id"),
                    phase_order=required_int(raw, "phase_order"),
                    phase_label=required_text(raw, "phase_label"),
                    view_order=required_int(raw, "view_order"),
                    view=required_text(raw, "view"),
                    condition=required_text(raw, "condition"),
                    year=required_int(raw, "year"),
                    source_rel=required_text(raw, "source_rel"),
                    caption=raw.get("caption", "").strip(),
                )
            )

    ids = [row.id for row in rows]
    duplicate_ids = sorted({id_ for id_ in ids if ids.count(id_) > 1})
    if duplicate_ids:
        raise ValueError(f"Duplicate source ids in {SOURCES_PATH}: {', '.join(duplicate_ids)}")

    missing = [row.source_path for row in rows if not row.source_path.exists()]
    if missing:
        missing_list = "\n".join(str(path) for path in missing)
        raise FileNotFoundError(f"Missing Chandra Marga source images:\n{missing_list}")

    return sorted(rows, key=source_sort_key)


def source_sort_key(row: SourceRow) -> tuple[int, int, tuple[int, int], str]:
    return (row.phase_order, row.view_order, year_sort_key(row.year), row.id)


def year_sort_key(year: int) -> tuple[int, int]:
    return (0, year) if year < 0 else (1, year)


def year_heading(year: int) -> str:
    return f"{abs(year)} BCE" if year < 0 else f"{year} CE"


def year_chip_label(year: int) -> str:
    return f"{abs(year)}" if year < 0 else str(year)


def clean_generated_assets() -> None:
    for old_manifest in (OLD_SERIES_MANIFEST_PATH,):
        if old_manifest.exists():
            old_manifest.unlink()

    for generated_root in (STRIPS_DIR, SERIES_DIR):
        if not generated_root.exists():
            continue
        for image in generated_root.rglob("*"):
            if image.is_file() and image.suffix.lower() in IMAGE_SUFFIXES:
                image.unlink()

        for directory in sorted(
            (path for path in generated_root.rglob("*") if path.is_dir()),
            key=lambda path: len(path.parts),
            reverse=True,
        ):
            try:
                directory.rmdir()
            except OSError:
                pass


def write_gallery_webp(source: Path, target: Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    with Image.open(source) as image:
        image = image.convert("RGB")
        if image.width > WEBP_MAX_WIDTH:
            scale = WEBP_MAX_WIDTH / image.width
            image = image.resize(
                (WEBP_MAX_WIDTH, round(image.height * scale)),
                Image.Resampling.LANCZOS,
            )
        image.save(target, "WEBP", quality=WEBP_QUALITY, method=6)


def build_assets(rows: list[SourceRow]) -> list[dict[str, str | int]]:
    STRIPS_DIR.mkdir(parents=True, exist_ok=True)
    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    clean_generated_assets()

    records: list[dict[str, str | int]] = []
    for row in rows:
        write_gallery_webp(row.source_path, row.output_path)
        records.append(
            {
                "id": row.id,
                "phase_order": row.phase_order,
                "phase_label": row.phase_label,
                "view_order": row.view_order,
                "view": row.view,
                "condition": row.condition,
                "year": row.year,
                "source_rel": row.source_rel,
                "caption": row.caption,
                "path": str(row.output_path.relative_to(LAB_DIR)),
                "size_kb": round(row.output_path.stat().st_size / 1024),
            }
        )

    MANIFEST_PATH.write_text(json.dumps(records, indent=2) + "\n", encoding="utf-8")
    return records


def render_nav(rows: list[SourceRow]) -> str:
    phases = []
    for row in rows:
        phase_key = (row.phase_order, row.phase_label)
        if phase_key not in phases:
            phases.append(phase_key)

    columns = []
    for row in rows:
        column_key = (row.view_order, row.nav_group)
        if column_key not in columns:
            columns.append(column_key)
    columns.sort()

    header_cells = "".join(
        f'<div class="matrix-cell matrix-head">{html.escape(label)}</div>'
        for _, label in columns
    )

    body_rows = []
    for _phase_order, phase_label in phases:
        cells = []
        for view_order, _column_label in columns:
            matches = [
                row
                for row in rows
                if row.phase_label == phase_label and row.view_order == view_order
            ]
            if matches:
                links = "".join(
                    f'<a class="year-chip" href="#{html.escape(row.id)}" data-target="{html.escape(row.id)}" '
                    f'title="{html.escape(row.section_title)}">{html.escape(year_chip_label(row.year))}</a>'
                    for row in sorted(matches, key=lambda row: year_sort_key(row.year))
                )
            else:
                links = '<span class="empty-cell">—</span>'
            cells.append(f'<div class="matrix-cell">{links}</div>')
        body_rows.append(
            f"""
          <div class="matrix-row">
            <div class="matrix-phase">{html.escape(phase_label)}</div>
            {''.join(cells)}
          </div>"""
        )

    return f"""
        <div class="nav-matrix" id="nav-matrix" style="--matrix-columns: {len(columns)}">
          <div class="matrix-row matrix-header">
            <div class="matrix-phase matrix-head"></div>
            {header_cells}
          </div>
{''.join(body_rows)}
        </div>"""


def render_sections(rows: list[SourceRow]) -> str:
    sections = []
    current_phase = None
    for row in rows:
        if row.phase_label != current_phase:
            if current_phase is not None:
                sections.append("        </section>")
            current_phase = row.phase_label
            sections.append(
                f"""
        <section class="phase-section" aria-labelledby="phase-{html.escape(row.phase_label.lower().replace(" ", "-"))}">
          <h2 id="phase-{html.escape(row.phase_label.lower().replace(" ", "-"))}">{html.escape(row.phase_label)}</h2>"""
            )

        image_path = html.escape(str(row.output_path.relative_to(LAB_DIR)))
        caption = f'<p class="caption">{html.escape(row.caption)}</p>' if row.caption else ""
        sections.append(
            f"""
          <article class="strip-item" id="{html.escape(row.id)}">
            <h3>{html.escape(row.section_title)}</h3>
            <span class="strip-label" hidden>{html.escape(row.section_title)}</span>
            <img class="asset-preview strip-preview" src="{image_path}" alt="{html.escape(row.section_title)} lunar strip" loading="lazy" decoding="async">
            {caption}
          </article>"""
        )

    if current_phase is not None:
        sections.append("        </section>")

    return "\n".join(sections)


def render_gallery(rows: list[SourceRow]) -> str:
    nav = render_nav(rows)
    sections = render_sections(rows)
    initial_title = html.escape(rows[0].section_title if rows else "Chandra Marga")

    return f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Chandra Marga</title>
    <link rel="stylesheet" href="../shared/css/site.css">
    <style>
      html {{
        scroll-behavior: smooth;
        scroll-padding-top: 4.4rem;
      }}
      .content {{
        max-width: 1160px;
      }}
      .intro {{
        padding-bottom: 0.55rem;
      }}
      .intro h1 {{
        margin-bottom: 0.35rem;
      }}
      .intro .lede {{
        max-width: 58rem;
        font-size: 1rem;
        line-height: 1.5;
      }}
      .chandra-strip-nav {{
        position: sticky;
        top: 0;
        z-index: 5;
        margin: 0 calc(50% - 50vw) 0.75rem;
        border-top: 1px solid var(--line);
        border-bottom: 1px solid var(--line);
        background: rgba(255, 251, 244, 0.97);
        backdrop-filter: blur(8px);
      }}
      .chandra-strip-nav-inner {{
        max-width: 1160px;
        margin: 0 auto;
        padding: 0.42rem 1.25rem;
      }}
      .nav-topline {{
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 1rem;
        min-height: 2.2rem;
      }}
      .chandra-brand {{
        color: var(--ink);
        font-weight: 700;
        text-decoration: none;
        white-space: nowrap;
      }}
      .current-strip-label {{
        min-width: 0;
        flex: 1;
        color: var(--muted);
        font-size: 0.95rem;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
      }}
      .nav-actions {{
        display: flex;
        align-items: center;
        gap: 0.45rem;
        white-space: nowrap;
      }}
      .nav-toggle {{
        border: 1px solid var(--line);
        border-radius: 999px;
        background: rgba(255, 255, 255, 0.62);
        color: var(--ink);
        padding: 0.24rem 0.62rem;
        font: inherit;
        font-size: 0.9rem;
        text-decoration: none;
        cursor: pointer;
      }}
      .current-strip-label.label-changing {{
        animation: label-change 360ms ease-out;
      }}
      @keyframes label-change {{
        0% {{
          color: var(--accent);
          opacity: 0.48;
          transform: translateY(0.28rem);
        }}
        70% {{
          color: var(--accent);
          opacity: 1;
          transform: translateY(0);
        }}
        100% {{
          color: var(--muted);
        }}
      }}
      .nav-matrix {{
        display: none;
        gap: 0.18rem;
        min-width: min(720px, 100%);
        overflow-x: auto;
        padding-top: 0.34rem;
      }}
      .nav-expanded .nav-matrix {{
        display: grid;
      }}
      .matrix-row {{
        display: grid;
        grid-template-columns: minmax(92px, 0.8fr) repeat(var(--matrix-columns), minmax(118px, 1fr));
        gap: 0.18rem;
        align-items: stretch;
      }}
      .matrix-phase,
      .matrix-cell {{
        min-height: 2rem;
        padding: 0.32rem 0.38rem;
        border-bottom: 1px solid rgba(73, 61, 36, 0.12);
      }}
      .matrix-phase {{
        font-weight: 700;
      }}
      .matrix-head {{
        color: var(--muted);
        font-size: 0.86rem;
        font-weight: 700;
      }}
      .matrix-cell {{
        display: flex;
        align-items: center;
        gap: 0.28rem;
        flex-wrap: wrap;
      }}
      .year-chip {{
        display: inline-flex;
        align-items: center;
        justify-content: center;
        min-width: 2.8rem;
        border: 1px solid var(--line);
        border-radius: 999px;
        padding: 0.18rem 0.48rem;
        background: rgba(255, 255, 255, 0.64);
        text-decoration: none;
        font-size: 0.88rem;
        transition:
          background 180ms ease,
          border-color 180ms ease,
          box-shadow 180ms ease,
          color 180ms ease,
          transform 180ms ease;
      }}
      .year-chip:hover {{
        background: rgba(255, 255, 255, 0.96);
      }}
      .year-chip.active {{
        background: var(--accent);
        border-color: var(--accent);
        color: #fff;
        box-shadow: 0 0 0 3px rgba(151, 92, 35, 0.16);
        transform: translateY(-1px);
      }}
      .empty-cell {{
        color: var(--muted);
      }}
      .phase-section {{
        padding: 0.4rem 0 0.65rem;
      }}
      .phase-section + .phase-section {{
        border-top: 1px solid var(--line);
      }}
      .phase-section h2 {{
        margin: 0 0 0.55rem;
        font-size: 1.32rem;
      }}
      .strip-item {{
        scroll-margin-top: 4.6rem;
        margin: 0 0 1.05rem;
      }}
      .strip-item h3 {{
        margin: 0 0 0.32rem;
        font-size: 1rem;
        color: var(--muted);
        font-weight: 700;
      }}
      .strip-preview {{
        background: #111;
        border: 1px solid var(--line);
      }}
      .caption {{
        margin: 0.32rem 0 0;
        color: var(--muted);
        font-size: 0.94rem;
        line-height: 1.45;
      }}
      .page-footer {{
        border-top: 1px solid var(--line);
        padding-top: 0.75rem;
      }}
      @media (max-width: 760px) {{
        html {{
          scroll-padding-top: 5rem;
        }}
        .chandra-strip-nav-inner {{
          padding: 0.36rem 0.75rem;
        }}
        .nav-topline {{
          gap: 0.55rem;
        }}
        .chandra-brand {{
          display: none;
        }}
        .current-strip-label {{
          font-size: 0.88rem;
        }}
        .matrix-row {{
          grid-template-columns: minmax(78px, 0.7fr) repeat(var(--matrix-columns), minmax(104px, 1fr));
        }}
        .matrix-phase,
        .matrix-cell {{
          padding: 0.26rem 0.28rem;
        }}
        .strip-item {{
          scroll-margin-top: 5.2rem;
        }}
      }}
    </style>
  </head>
  <body class="exploration-body">
    <main class="content" id="top">
      <section class="flat-section intro">
        <p class="eyebrow">Exploration</p>
        <h1>Chandra Marga</h1>
        <p class="lede">Curated lunar strip views from the moon-shrunga Stellarium workflow, organized by phase and observing condition.</p>
      </section>

      <nav class="chandra-strip-nav" aria-label="Chandra Marga strip jumps">
        <div class="chandra-strip-nav-inner">
          <div class="nav-topline">
            <a class="chandra-brand" href="#top">Chandra Marga</a>
            <div class="current-strip-label" id="current-strip-label">{initial_title}</div>
            <div class="nav-actions">
              <button class="nav-toggle" id="nav-toggle" type="button" aria-expanded="false" aria-controls="nav-matrix">Index</button>
            </div>
          </div>
{nav}
        </div>
      </nav>

{sections}

      <footer class="flat-section page-footer">
        <p class="small-note">Source curation is managed in <code>explorations/chandra-marga-sources.tsv</code>.</p>
      </footer>
    </main>
    <script>
      const nav = document.querySelector(".chandra-strip-nav");
      const navToggle = document.getElementById("nav-toggle");
      const currentLabel = document.getElementById("current-strip-label");
      const chips = Array.from(document.querySelectorAll(".year-chip"));
      const sectionsById = new Map(
        Array.from(document.querySelectorAll(".strip-item")).map((section) => [section.id, section])
      );

      function setExpanded(expanded) {{
        nav.classList.toggle("nav-expanded", expanded);
        navToggle.setAttribute("aria-expanded", String(expanded));
        navToggle.textContent = expanded ? "Close" : "Index";
      }}

      function setCurrent(section) {{
        if (!section || section.dataset.current === "true") return;
        sectionsById.forEach((candidate) => {{
          candidate.dataset.current = candidate === section ? "true" : "false";
        }});
        const label = section.querySelector(".strip-label")?.textContent || section.querySelector("h3")?.textContent || "Chandra Marga";
        if (currentLabel.textContent !== label) {{
          currentLabel.classList.remove("label-changing");
          void currentLabel.offsetWidth;
          currentLabel.textContent = label;
          currentLabel.classList.add("label-changing");
        }}
        chips.forEach((chip) => chip.classList.toggle("active", chip.dataset.target === section.id));
      }}

      currentLabel.addEventListener("animationend", () => {{
        currentLabel.classList.remove("label-changing");
      }});

      function currentSectionFromViewport() {{
        const sections = Array.from(sectionsById.values());
        const navBottom = nav.getBoundingClientRect().bottom;
        const probeY = Math.min(window.innerHeight * 0.42, navBottom + 180);
        const containing = sections.find((section) => {{
          const rect = section.getBoundingClientRect();
          return rect.top <= probeY && rect.bottom > probeY;
        }});
        if (containing) return containing;

        return sections
          .map((section) => {{
            const rect = section.getBoundingClientRect();
            return {{ section, distance: Math.abs(rect.top - probeY) }};
          }})
          .sort((a, b) => a.distance - b.distance)[0]?.section;
      }}

      let pendingCurrentUpdate = false;
      function queueCurrentUpdate() {{
        if (pendingCurrentUpdate) return;
        pendingCurrentUpdate = true;
        requestAnimationFrame(() => {{
          pendingCurrentUpdate = false;
          setCurrent(currentSectionFromViewport());
        }});
      }}

      navToggle.addEventListener("click", () => {{
        setExpanded(!nav.classList.contains("nav-expanded"));
        queueCurrentUpdate();
      }});

      chips.forEach((chip) => {{
        chip.addEventListener("click", (event) => {{
          event.preventDefault();
          const section = sectionsById.get(chip.dataset.target);
          if (!section) return;
          setExpanded(false);
          window.history.pushState(null, "", `#${{section.id}}`);
          section.scrollIntoView({{ behavior: "smooth", block: "start" }});
          setCurrent(section);
        }});
      }});

      const initialSection = sectionsById.get(window.location.hash.replace("#", "")) || sectionsById.values().next().value;
      if (initialSection) setCurrent(initialSection);
      window.addEventListener("scroll", queueCurrentUpdate, {{ passive: true }});
      window.addEventListener("resize", queueCurrentUpdate);
      window.addEventListener("load", queueCurrentUpdate);
    </script>
  </body>
</html>
"""


def main() -> None:
    rows = read_sources()
    records = build_assets(rows)
    (LAB_DIR / "index.html").write_text(render_gallery(rows), encoding="utf-8")
    print(f"copied={len(records)}")
    print(f"sources={SOURCES_PATH}")
    print(f"manifest={MANIFEST_PATH}")
    print(f"page={LAB_DIR / 'index.html'}")


if __name__ == "__main__":
    main()
