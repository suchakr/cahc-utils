from __future__ import annotations

import html
import json
from pathlib import Path

from PIL import Image

from jyotisha_2026.paths import LAB_ROOT


SOURCE_ROOT = Path("/Users/sunder/projects/cahc/cahc-utils/stel_scripts/moon-shranga~")
LAB_DIR = LAB_ROOT / "chandra-marga"
STRIPS_DIR = LAB_DIR / "strips"
MANIFEST_PATH = LAB_DIR / "tables" / "strip-manifest.json"
IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".webp"}
WEBP_MAX_WIDTH = 2200
WEBP_QUALITY = 84


MODE_LABELS = {
    "rise-moon-above-8": "Moonrise at Moon altitude +8",
    "set-moon-above-8": "Moonset at Moon altitude +8",
    "set-sun-below-9": "Moonset view at Sun altitude -9",
}

IGNORED_SOURCE_RELS = {
    "rise-moon-above-8/-500/clip04-strip-rise--500-purnima.jpg",
    "rise-moon-above-8/-500/clip04-strip-rise--500-shukla_dwitiya.jpg",
    "rise-moon-above-8/-500/clip04-strip-rise--500-shukla_pratipada.jpg",
    "set-moon-above-8/-500.moon-8alt-prev/clip04-strip-set--500.moon-8-alt-purnima.jpg",
    "set-moon-above-8/-500.moon-8alt-prev/clip04-strip-set--500.moon-8-alt-prev-purnima.jpg",
    "set-moon-above-8/-500.moon-8alt-prev/clip04-strip-set--500.moon-8-alt-shukla_pratipada.jpg",
    "set-moon-above-8/-500.moon-8alt-prev/clip04-strip-set--500.moon-8-alt-prev-shukla_dwitiya.jpg",
    "set-moon-above-8/-500.moon-8alt-prev/clip04-strip-set--500.moon-8-alt-shukla_dwitiya.jpg",
    "set-moon-above-8/-500.moon-8alt-prev/clip04-strip-set--500.moon-8-alt-prev-shukla_pratipada.jpg",
    "set-moon-above-8/-527/clip04-strip-set--527-shukla_pratipada.jpg",
    "set-moon-above-8/-527/brightened~/clip04-strip-set--527-shukla_pratipada.gamma16.jpg",
    "set-moon-above-8/-527/brightened~/clip04-strip-set--527-shukla_pratipada.gamma13.jpg",
    "set-moon-above-8/-527/brightened~/clip04-strip-set--527-shukla_pratipada.shadowlift.jpg",
}

TITHI_META = {
    "Shukla pratipada": ("S1", "Shukla pratipada", 1),
    "Shukla dwitiya": ("S2", "Shukla dwitiya", 2),
    "Purnima": ("S15", "Purnima", 15),
    "Krishna chaturdashi": ("K14", "Krishna chaturdashi", 29),
    "Amavasya": ("K15", "Amavasya", 30),
    "Darsha": ("K15", "Darsha", 30),
}


def selected_sources() -> list[Path]:
    patterns = [
        ("rise-moon-above-8", "**/clip04-strip*.jpg"),
        ("set-moon-above-8", "**/clip04-strip*.jpg"),
        ("set-moon-above-8", "**/*darsha*.jpg"),
        ("set-moon-above-8", "**/*darsha*.jpeg"),
        ("set-sun-below-9", "**/strip-set-sun-below-9*.jpg"),
    ]
    paths: set[Path] = set()
    for mode, pattern in patterns:
        paths.update((SOURCE_ROOT / mode).glob(pattern))
    return sorted(
        path
        for path in paths
        if path.is_file() and path.relative_to(SOURCE_ROOT).as_posix() not in IGNORED_SOURCE_RELS
    )


def event_label(path: Path) -> str:
    stem = path.stem.lower()
    labels = [
        ("shukla_pratipada", "Shukla pratipada"),
        ("shukla_dwitiya", "Shukla dwitiya"),
        ("krishna_chaturdashi", "Krishna chaturdashi"),
        ("purnima", "Purnima"),
        ("poornima", "Purnima"),
        ("amavasya", "Amavasya"),
        ("darsha", "Darsha"),
    ]
    for token, label in labels:
        if token in stem:
            return label
    return path.stem.replace("_", " ").replace("-", " ").title()


def variant_label(path: Path) -> str:
    text = "/".join(path.relative_to(SOURCE_ROOT).parts).lower()
    variants = []
    if "moon-8-alt-prev" in text:
        variants.append("previous Moon +8 run")
    if "moon-8-alt" in text and "moon-8-alt-prev" not in text:
        variants.append("Moon +8 run")
    if "brightened" in text:
        variants.append("brightened")
    if "gamma13" in text:
        variants.append("gamma 1.3")
    if "gamma16" in text:
        variants.append("gamma 1.6")
    if "shadowlift" in text:
        variants.append("shadow lift")
    if not variants and path.name.startswith("clip04"):
        variants.append("clip04 crop")
    return ", ".join(variants) if variants else "strip"


def year_label(path: Path) -> str:
    rel = path.relative_to(SOURCE_ROOT).parts
    return rel[1] if len(rel) > 1 else ""


def tithi_meta(event: str) -> tuple[str, str, int]:
    return TITHI_META.get(event, ("Other", event, 99))


def year_value(year: str | int) -> int:
    raw = str(year)
    base = raw.split(".", 1)[0]
    try:
        return int(base)
    except ValueError:
        return 0


def year_sort_key(year: int) -> tuple[int, int]:
    if year >= 0:
        return (0, -year)
    return (1, year)


def year_nav_label(year: int) -> str:
    return str(year) if year >= 0 else str(abs(year))


def year_heading(year: int) -> str:
    return f"{abs(year)} BCE" if year < 0 else f"{year} CE"


def group_id(code: str, year: int) -> str:
    era = "ce" if year >= 0 else "bce"
    return f"{code.lower()}-{era}-{abs(year)}"


def webp_target_for(source_rel: Path) -> Path:
    return STRIPS_DIR / source_rel.with_suffix(".webp")


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


def copy_and_manifest() -> list[dict[str, str | int]]:
    STRIPS_DIR.mkdir(parents=True, exist_ok=True)
    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    for old_image in STRIPS_DIR.rglob("*"):
        if old_image.is_file() and old_image.suffix.lower() in IMAGE_SUFFIXES:
            old_image.unlink()

    records: list[dict[str, str | int]] = []
    for source in selected_sources():
        rel = source.relative_to(SOURCE_ROOT)
        target = webp_target_for(rel)
        write_gallery_webp(source, target)

        mode = rel.parts[0]
        record = {
            "mode": mode,
            "mode_label": MODE_LABELS.get(mode, mode.replace("-", " ")),
            "year": year_label(source),
            "event": event_label(source),
            "variant": variant_label(source),
            "filename": target.name,
            "path": str(target.relative_to(LAB_DIR)),
            "size_kb": round(target.stat().st_size / 1024),
        }
        records.append(record)

    records.sort(key=lambda r: (str(r["mode"]), str(r["year"]), str(r["event"]), str(r["path"])))
    MANIFEST_PATH.write_text(json.dumps(records, indent=2) + "\n", encoding="utf-8")
    return records


def render_gallery(records: list[dict[str, str | int]]) -> str:
    sorted_records = sorted(
        records,
        key=lambda record: (
            tithi_meta(str(record["event"]))[2],
            year_sort_key(year_value(record["year"])),
            str(record["mode"]),
            str(record["variant"]),
            str(record["path"]),
        ),
    )

    grouped_records: dict[tuple[str, int], list[dict[str, str | int]]] = {}
    group_labels: dict[tuple[str, int], str] = {}
    for record in sorted_records:
        code, label, _ = tithi_meta(str(record["event"]))
        year = year_value(record["year"])
        key = (code, year)
        grouped_records.setdefault(key, []).append(record)
        group_labels[key] = label

    tithi_nav_groups = []
    for code, _label, order in sorted(set(tithi_meta(str(record["event"])) for record in records), key=lambda item: item[2]):
        years = sorted(
            {year for group_code, year in grouped_records if group_code == code},
            key=year_sort_key,
        )
        if not years:
            continue
        links = " ".join(
            f'<a href="#{group_id(code, year)}">{html.escape(year_nav_label(year))}</a>'
            for year in years
        )
        tithi_nav_groups.append(
            f'<div class="tithi-nav-group"><span>{html.escape(code)}</span>{links}</div>'
        )
    tithi_nav = "".join(tithi_nav_groups)

    group_sections = []
    for key, group in grouped_records.items():
        code, year = key
        cards = []
        for record in group:
            path = html.escape(str(record["path"]))
            title = html.escape(f'{record["year"]} - {record["event"]}')
            meta = html.escape(f'{record["mode_label"]} - {record["variant"]}')
            filename = html.escape(str(record["filename"]))
            cards.append(
                f"""
          <article class="strip-item">
            <div class="strip-title-row">
              <h3>{title}</h3>
              <a href="{path}">Open</a>
            </div>
            <p class="small-note">{meta}</p>
            <a href="{path}"><img class="asset-preview strip-preview" src="{path}" alt="{title} lunar strip" loading="lazy" decoding="async"></a>
            <p class="small-note">{filename} - {record["size_kb"]} KB</p>
          </article>"""
            )
        group_sections.append(
            f"""
        <section class="strip-group" id="{html.escape(group_id(code, year))}">
          <h3>{html.escape(code)} · {html.escape(group_labels[key])} · {html.escape(year_heading(year))}</h3>
          <div class="strip-grid">
{''.join(cards)}
          </div>
        </section>"""
        )

    table_rows = []
    for record in sorted_records:
        table_rows.append(
            "    <tr>"
            f"<td>{html.escape(str(record['mode_label']))}</td>"
            f"<td>{html.escape(str(record['year']))}</td>"
            f"<td>{html.escape(str(record['event']))}</td>"
            f"<td>{html.escape(str(record['variant']))}</td>"
            f"<td><a href=\"{html.escape(str(record['path']))}\">{html.escape(str(record['filename']))}</a></td>"
            "</tr>"
        )

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
        scroll-padding-top: 4rem;
      }}
      .chandra-strip-nav {{
        position: sticky;
        top: 0;
        z-index: 5;
        margin: 0.7rem calc(50% - 50vw) 0;
        border-top: 1px solid var(--line);
        border-bottom: 1px solid var(--line);
        background: rgba(255, 251, 244, 0.96);
        backdrop-filter: blur(8px);
      }}
      .chandra-strip-nav-inner {{
        max-width: 1120px;
        margin: 0 auto;
        padding: 0.58rem 1.25rem 0.52rem;
        display: flex;
        align-items: center;
        gap: 1rem;
        min-width: 0;
      }}
      .chandra-brand {{
        color: var(--ink);
        font-weight: 700;
        text-decoration: none;
        white-space: nowrap;
      }}
      .tithi-nav {{
        display: flex;
        align-items: center;
        gap: 0.75rem;
        overflow-x: auto;
        min-width: 0;
        flex: 1;
        padding-bottom: 0.08rem;
      }}
      .tithi-nav-group {{
        display: inline-flex;
        align-items: baseline;
        gap: 0.32rem;
        white-space: nowrap;
        color: var(--muted);
        font-size: 0.95rem;
      }}
      .tithi-nav-group span {{
        color: var(--ink);
        font-weight: 700;
      }}
      .tithi-nav-group a,
      .manifest-link {{
        text-decoration: none;
      }}
      .strip-grid {{
        display: grid;
        grid-template-columns: 1fr;
        gap: 1rem;
      }}
      .strip-group {{
        scroll-margin-top: 4rem;
        padding: 0.3rem 0 1rem;
      }}
      .strip-group + .strip-group {{
        border-top: 1px solid var(--line);
        padding-top: 1rem;
      }}
      .strip-group h3 {{
        margin: 0 0 0.75rem;
        font-size: 1.12rem;
      }}
      .strip-item {{
        padding-bottom: 1rem;
        border-bottom: 1px solid var(--line);
      }}
      .strip-title-row {{
        display: flex;
        align-items: baseline;
        justify-content: space-between;
        gap: 1rem;
      }}
      .strip-title-row h3 {{
        margin: 0;
        font-size: 1.12rem;
      }}
      .strip-preview {{
        background: #111;
        border: 1px solid var(--line);
      }}
      code {{
        overflow-wrap: anywhere;
      }}
    </style>
  </head>
  <body class="exploration-body">
    <main class="content" id="top">
      <section class="flat-section">
        <p class="eyebrow">Exploration</p>
        <h1>Chandra Marga</h1>
        <p class="lede">
          A self-contained gallery for lunar crescent strip images generated by the
          chandra-marga event pipeline and rendered through Stellarium.
        </p>
      </section>

      <section class="flat-section">
        <h2>Reading Notes</h2>
        <ul>
          <li>Moon-altitude strips fix the Moon near +8 degrees and compare crescent visibility across selected tithis.</li>
          <li>The Sun-altitude strip fixes twilight at Sun altitude -9 degrees for the Shukla pratipada series.</li>
        </ul>
      </section>

      <nav class="chandra-strip-nav" aria-label="Chandra Marga strip jumps">
        <div class="chandra-strip-nav-inner">
          <a class="chandra-brand" href="#top">Chandra Marga</a>
          <div class="tithi-nav">
            {tithi_nav}
          </div>
          <a class="manifest-link" href="#manifest">Manifest</a>
        </div>
      </nav>

      <section class="flat-section">
        <div class="section-title-row">
          <h2>Lunar Strips</h2>
          <a href="tables/strip-manifest.json">Manifest JSON</a>
        </div>
{''.join(group_sections)}
      </section>

      <section class="flat-section" id="manifest">
        <h2>Manifest Preview</h2>
        <div class="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Mode</th>
                <th>Year Tag</th>
                <th>Event</th>
                <th>Variant</th>
                <th>File</th>
              </tr>
            </thead>
            <tbody>
{chr(10).join(table_rows)}
            </tbody>
          </table>
        </div>
      </section>
    </main>
  </body>
</html>
"""


def main() -> None:
    records = copy_and_manifest()
    (LAB_DIR / "index.html").write_text(render_gallery(records), encoding="utf-8")
    print(f"copied={len(records)}")
    print(f"manifest={MANIFEST_PATH}")
    print(f"page={LAB_DIR / 'index.html'}")


if __name__ == "__main__":
    main()
