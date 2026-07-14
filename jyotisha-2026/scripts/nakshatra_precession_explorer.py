from __future__ import annotations

import csv
import json
import math
import re
import subprocess
import warnings
from typing import Any
from dataclasses import dataclass
from pathlib import Path

import astropy.units as u
from astropy.coordinates import BarycentricMeanEcliptic, FK5, SkyCoord
from astropy.time import Time
from astropy.utils import iers

from jyotisha_2026.paths import EXPLORATIONS_ROOT, LAB_ROOT, REPO_ROOT, upstream_dataset_path


iers.conf.auto_download = False
iers.conf.auto_max_age = None
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=RuntimeWarning)

SLUG = "nakshatra-precession-explorer"
TITLE = "Nakshatra Precession Explorer"
SUBTITLE = (
    "Fixed sidereal nakshatra geometry against the drifting seasonal frame, "
    "tested through a shared epoch slider, table view, and projected 2D sky."
)
DEFAULT_EPOCH = -1500
EPOCH_MIN = -5000
EPOCH_MAX = 3000
EPOCH_STEP = 100
ECLIPTIC_BAND_HALF_WIDTH_DEG = 5.0
LUNAR_SYSTEM_LINK_HIP = "HIP 65474"
LUNAR_SYSTEM_LINK_OFFSET_DEG = 180.0
STORIES_ROOT = REPO_ROOT / "stories" / SLUG
COMPILED_STORIES_ROOT = STORIES_ROOT / "compiled"
EPOCH_CACHE_PATH = REPO_ROOT / "tmp" / f"{SLUG}-epoch-states-v1.json"

SKY_CULTURE_ROOT = (REPO_ROOT.parent / "nakshatra_sky_culture" / "vedic_25_codex").resolve()
SKY_CULTURE_DATA_ROOT = (REPO_ROOT.parent / "nakshatra_sky_culture" / "data").resolve()
HIP_MAIN_VIZIER_PATH = (
    REPO_ROOT.parent / "presentations" / "2026-03-23-iks-astro-talk" / "data" / "hip_main_vizier.tsv"
).resolve()

RTUS = [
    ("Vasanta", "#d4aa4d"),
    ("Grishma", "#d38754"),
    ("Varsha", "#6f9fb7"),
    ("Sharat", "#d8c27a"),
    ("Hemanta", "#b07b5d"),
    ("Shishira", "#8da0c9"),
]

SEASON_NAME_MAP = {
    "Vasanta": "वसन्त",
    "Grishma": "ग्रीष्म",
    "Varsha": "वर्षा",
    "Sharat": "शरत्",
    "Hemanta": "हेमन्त",
    "Shishira": "शिशिर",
}

DISPLAY_NAKS_OVERRIDE = {
    "N05-Mrg": "मृगशीर्षा",
    "N07-Pun": "पुनर्वसू",
    "N08-Pus": "पुष्य",
    "N13-Has": "हस्तः",
    "N22-Abi": "अभिजित्",
}

ASTERISM_LINE_OVERRIDE = {
    "N03-Kri": [["HIP 17499", "HIP 17608", "HIP 17847", "HIP 17702", "HIP 17531", "HIP 17499"]],
    "N24-Dha": [["HIP 102281", "HIP 102532", "HIP 101958", "HIP 101769", "HIP 102281"]],
}

SPECIAL_CONSTELLATION_IDS = {
    "CON vedic_25_codex Shim": {"label": "Shiṁśumāra", "native": "शिशुमारः"},
    "CON vedic_25_codex Matsya": {"label": "Matsya", "native": "मत्स्यः"},
}

SPECIAL_STAR_LABELS = {
    "HIP 30438": {"label": "Agastya", "native": "अगस्त्यः"},
}


@dataclass(frozen=True)
class StarPoint:
    hip: str
    label: str
    lon_deg: float
    lat_deg: float
    size_hint: float


def wrap_angle(deg: float) -> float:
    return deg % 360.0


def normalize_hip(value: str) -> str:
    return " ".join(value.split())


def angular_distance_from(start_deg: float, value_deg: float) -> float:
    return (value_deg - start_deg) % 360.0


def longitude_in_span(value_deg: float, start_deg: float, end_deg: float) -> bool:
    value = wrap_angle(value_deg)
    start = wrap_angle(start_deg)
    end = wrap_angle(end_deg)
    if start <= end:
        return start <= value < end
    return value >= start or value < end


def year_label(year: int) -> str:
    if year < 0:
        return f"{abs(year)} BCE"
    if year == 0:
        return "0"
    return f"{year} CE"


def astropy_time(year: int) -> Time:
    return Time(float(year), format="jyear", scale="tt")


def load_meta_rows() -> list[dict[str, str]]:
    with upstream_dataset_path("n28_good_meta.csv").open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def geometry_order_for_meta_index(meta_index_28: int) -> int:
    if meta_index_28 == 22:
        return 28
    if meta_index_28 >= 23:
        return meta_index_28 - 1
    return meta_index_28


def sector_order_for_meta_index(meta_index_28: int) -> int | None:
    if meta_index_28 == 22:
        return None
    if meta_index_28 >= 23:
        return meta_index_28 - 1
    return meta_index_28


def load_asterism_lookup() -> dict[int, dict[str, object]]:
    data = json.loads((SKY_CULTURE_ROOT / "index.json").read_text(encoding="utf-8"))
    lookup: dict[int, dict[str, object]] = {}
    for item in data["asterisms"]:
        if not item["id"].startswith("AST vedic_25_codex N"):
            continue
        order = int(item["id"].split("N", 1)[1])
        lookup[order] = item
    return lookup


def load_codex_payload() -> dict[str, object]:
    return json.loads((SKY_CULTURE_ROOT / "index.json").read_text(encoding="utf-8"))


def load_star_points() -> dict[str, StarPoint]:
    lookup: dict[str, StarPoint] = {}
    j2000_ecliptic = BarycentricMeanEcliptic(equinox=Time("J2000"))

    primary_path = upstream_dataset_path("n83_full_meta_for_-1750.csv")
    with primary_path.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            hip = normalize_hip(row["hip"])
            size_hint = 5.4 if row["tag"] == "rep" else 3.9
            label = row["sname"] or row["gname"]
            lookup[hip] = StarPoint(
                hip=hip,
                label=label,
                lon_deg=float(row["lonJ2000"]),
                lat_deg=float(row["latJ2000"]),
                size_hint=size_hint,
            )

    supplement_path = SKY_CULTURE_DATA_ROOT / "stars_mag6_within_30_declination.csv"
    with supplement_path.open(newline="", encoding="utf-8") as handle:
        for row in csv.reader(handle):
            if len(row) < 10:
                continue
            if row[0] in {"nid", "Naks"}:
                continue
            hip = normalize_hip(row[9])
            if hip in lookup:
                continue
            if not hip.startswith("HIP"):
                continue
            size_hint = 4.6 if row[3] == "1" else 3.6
            coord = SkyCoord(ra=float(row[6]) * u.deg, dec=float(row[7]) * u.deg, frame="icrs").transform_to(j2000_ecliptic)
            lookup[hip] = StarPoint(
                hip=hip,
                label=row[2] if row[2] != "xxx" else row[1].replace("* ", ""),
                lon_deg=float(coord.lon.deg),
                lat_deg=float(coord.lat.deg),
                size_hint=size_hint,
            )

    with HIP_MAIN_VIZIER_PATH.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            hip = f"HIP {row['hip'].strip()}"
            if hip in lookup:
                continue
            coord = SkyCoord(
                ra=float(row["ra_icrs_deg"]) * u.deg,
                dec=float(row["dec_icrs_deg"]) * u.deg,
                frame="icrs",
            ).transform_to(j2000_ecliptic)
            magnitude = float(row["magnitude"]) if row["magnitude"] else 6.0
            if magnitude <= 1.5:
                size_hint = 5.6
            elif magnitude <= 3.0:
                size_hint = 4.8
            elif magnitude <= 4.5:
                size_hint = 4.0
            else:
                size_hint = 3.4
            lookup[hip] = StarPoint(
                hip=hip,
                label=row["name"] or hip,
                lon_deg=float(coord.lon.deg),
                lat_deg=float(coord.lat.deg),
                size_hint=size_hint,
            )
    return lookup


def compute_epoch_states() -> list[dict[str, float | int | str]]:
    states: list[dict[str, float | int | str]] = []
    reference_ecliptic = BarycentricMeanEcliptic(equinox=Time("J2000"))
    for year in range(EPOCH_MIN, EPOCH_MAX + 1, EPOCH_STEP):
        epoch = astropy_time(year)
        vernal = SkyCoord(ra=0 * u.deg, dec=0 * u.deg, frame=FK5(equinox=epoch)).transform_to(reference_ecliptic)
        pole = SkyCoord(ra=0 * u.deg, dec=90 * u.deg, frame=FK5(equinox=epoch)).transform_to(reference_ecliptic)
        vernal_lon = wrap_angle(float(vernal.lon.deg))
        pole_lon = wrap_angle(float(pole.lon.deg))
        pole_lat = float(pole.lat.deg)
        states.append(
            {
                "year": year,
                "label": year_label(year),
                "vernal_equinox_lon_deg": vernal_lon,
                "summer_solstice_lon_deg": wrap_angle(vernal_lon + 90.0),
                "autumnal_equinox_lon_deg": wrap_angle(vernal_lon + 180.0),
                "winter_solstice_lon_deg": wrap_angle(vernal_lon + 270.0),
                "north_pole_lon_deg": pole_lon,
                "north_pole_lat_deg": pole_lat,
                "obliquity_deg": 90.0 - pole_lat,
            }
        )
    return states


def build_epoch_states() -> list[dict[str, float | int | str]]:
    cache_key = {
        "epoch_min": EPOCH_MIN,
        "epoch_max": EPOCH_MAX,
        "epoch_step": EPOCH_STEP,
        "frame": "BarycentricMeanEcliptic(J2000)/FK5",
        "version": 1,
    }
    if EPOCH_CACHE_PATH.exists():
        try:
            cached = json.loads(EPOCH_CACHE_PATH.read_text(encoding="utf-8"))
            if cached.get("cache_key") == cache_key and isinstance(cached.get("states"), list):
                return cached["states"]
        except json.JSONDecodeError:
            pass

    states = compute_epoch_states()
    EPOCH_CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    EPOCH_CACHE_PATH.write_text(
        json.dumps({"cache_key": cache_key, "states": states}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return states


def build_dataset() -> dict[str, object]:
    meta_rows = load_meta_rows()
    codex_payload = load_codex_payload()
    asterism_lookup = load_asterism_lookup()
    star_lookup = load_star_points()
    sector_width = 360.0 / 27.0
    sector_start = wrap_angle(star_lookup[LUNAR_SYSTEM_LINK_HIP].lon_deg - LUNAR_SYSTEM_LINK_OFFSET_DEG)

    nakshatras: list[dict[str, object]] = []
    referenced_hips: set[str] = set()

    for row in meta_rows:
        meta_index = int(row["nnid"])
        geometry_index = geometry_order_for_meta_index(meta_index)
        sector_index = sector_order_for_meta_index(meta_index)
        asterism = asterism_lookup[geometry_index]

        line_groups: list[list[str]] = []
        for line in asterism["lines"]:
            hips: list[str] = []
            for hip_num in line:
                hip = f"HIP {hip_num}"
                if hip not in star_lookup:
                    continue
                referenced_hips.add(hip)
                hips.append(hip)
            if hips:
                line_groups.append(hips)

        if row["nid"] in ASTERISM_LINE_OVERRIDE:
            line_groups = []
            for line in ASTERISM_LINE_OVERRIDE[row["nid"]]:
                hips = [hip for hip in line if hip in star_lookup]
                if hips:
                    for hip in hips:
                        referenced_hips.add(hip)
                    line_groups.append(hips)

        star_ids = sorted({hip for group in line_groups for hip in group}, key=lambda value: int(value.split()[-1]))
        stars = []
        for hip in star_ids:
            star = star_lookup[hip]
            stars.append(
                {
                    "hip": hip,
                    "label": star.label,
                    "lon_deg": round(star.lon_deg, 3),
                    "lat_deg": round(star.lat_deg, 3),
                    "size_hint": round(star.size_hint, 2),
                }
            )

        if sector_index is None:
            sector_start_lon = None
            sector_end_lon = None
            sector_center_lon = None
            sector_label = "Abhijit"
        else:
            sector_start_lon = wrap_angle(sector_start + (sector_index - 1) * sector_width)
            sector_end_lon = wrap_angle(sector_start_lon + sector_width)
            sector_center_lon = wrap_angle(sector_start_lon + sector_width / 2)
            sector_label = str(sector_index)

        nakshatras.append(
            {
                "meta_index_28": meta_index,
                "sector_index_27": sector_index,
                "geometry_index": geometry_index,
                "nid": row["nid"],
                "enaks": row["enaks"],
                "naks": DISPLAY_NAKS_OVERRIDE.get(row["nid"], row["naks"]),
                "daivata": row["daivata"],
                "marga": row["marga"],
                "veethi": row["veethi"],
                "shape": row["shape"] or "Unspecified",
                "vgj_stars": row["vgj_stars"],
                "proxy": row["proxy"],
                "hip": row["hip"],
                "sector_start_lon_deg": None if sector_start_lon is None else round(sector_start_lon, 3),
                "sector_end_lon_deg": None if sector_end_lon is None else round(sector_end_lon, 3),
                "sector_center_lon_deg": None if sector_center_lon is None else round(sector_center_lon, 3),
                "sector_label": sector_label,
                "asterism_lines": line_groups,
                "stars": stars,
            }
        )

    stars = []
    for hip in sorted(referenced_hips, key=lambda value: int(value.split()[-1])):
        star = star_lookup[hip]
        stars.append(
            {
                "hip": hip,
                "label": star.label,
                "lon_deg": round(star.lon_deg, 3),
                "lat_deg": round(star.lat_deg, 3),
                "size_hint": round(star.size_hint, 2),
            }
        )

    constellation_lookup = {item["id"]: item for item in codex_payload.get("constellations", [])}
    special_figures: list[dict[str, object]] = []
    for constellation_id, label_info in SPECIAL_CONSTELLATION_IDS.items():
        item = constellation_lookup.get(constellation_id)
        if not item:
            continue
        line_groups: list[list[str]] = []
        for line in item["lines"]:
            hips = []
            for hip_num in line:
                hip = f"HIP {hip_num}"
                if hip not in star_lookup:
                    continue
                hips.append(hip)
            if hips:
                line_groups.append(hips)
        star_ids = sorted({hip for group in line_groups for hip in group}, key=lambda value: int(value.split()[-1]))
        if not line_groups or not star_ids:
            continue
        stars_for_figure = []
        for hip in star_ids:
            star = star_lookup[hip]
            stars_for_figure.append(
                {
                    "hip": hip,
                    "label": star.label,
                    "lon_deg": round(star.lon_deg, 3),
                    "lat_deg": round(star.lat_deg, 3),
                    "size_hint": round(star.size_hint, 2),
                }
            )
        special_figures.append(
            {
                "id": constellation_id,
                "label": label_info["label"],
                "native": label_info["native"],
                "lines": line_groups,
                "stars": stars_for_figure,
            }
        )

    special_stars: list[dict[str, object]] = []
    for hip, label_info in SPECIAL_STAR_LABELS.items():
        star = star_lookup.get(hip)
        if not star:
            continue
        special_stars.append(
            {
                "hip": hip,
                "label": label_info["label"],
                "native": label_info["native"],
                "lon_deg": round(star.lon_deg, 3),
                "lat_deg": round(star.lat_deg, 3),
                "size_hint": round(star.size_hint, 2),
            }
        )

    return {
        "meta": {
            "slug": SLUG,
            "title": TITLE,
            "subtitle": SUBTITLE,
            "epoch_min": EPOCH_MIN,
            "epoch_max": EPOCH_MAX,
            "epoch_step": EPOCH_STEP,
            "default_epoch": DEFAULT_EPOCH,
            "ecliptic_band_half_width_deg": ECLIPTIC_BAND_HALF_WIDTH_DEG,
            "sector_width_deg": round(sector_width, 6),
            "sector_start_lon_deg": round(sector_start, 6),
            "lunar_system_link_hip": LUNAR_SYSTEM_LINK_HIP,
            "lunar_system_link_offset_deg": LUNAR_SYSTEM_LINK_OFFSET_DEG,
            "rtus": [{"name": name, "color": color} for name, color in RTUS],
            "season_name_map": SEASON_NAME_MAP,
        },
        "epochs": build_epoch_states(),
        "nakshatras": nakshatras,
        "stars": stars,
        "special_figures": special_figures,
        "special_stars": special_stars,
    }


def load_stories() -> list[dict[str, Any]]:
    if not STORIES_ROOT.exists():
        return []
    command = ["node", str(REPO_ROOT / "scripts" / "compile-vysu.mjs"), SLUG]
    result = subprocess.run(command, cwd=REPO_ROOT, check=True, capture_output=True, text=True)
    return json.loads(result.stdout)



def all_stories(_dataset: dict[str, object]) -> list[dict[str, Any]]:
    # Story inventory is intentionally file-based under stories/<slug>/, not generated here.
    return load_stories()


def browser_vysu_compiler_source() -> str:
    source = (REPO_ROOT / "scripts" / "vysu-compiler.mjs").read_text(encoding="utf-8")
    source = source.replace(
        "export function compileVyomaSutra(source, options = {}) {",
        "compileVyomaSutra = function compileVyomaSutraStage1(source, options = {}) {",
    )
    source = source.replace("export function ", "function ")
    return "// BEGIN VYOMASUTRA COMPILER\n{\n" + source + "\n}\n// END VYOMASUTRA COMPILER"



def page_html(dataset: dict[str, object]) -> str:
    data_json = json.dumps(dataset, ensure_ascii=False)
    stories_json = json.dumps(all_stories(dataset), ensure_ascii=False)
    return f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{TITLE}</title>
    <link rel="stylesheet" href="../shared/css/site.css">
    <script type="importmap">
      {{
        "imports": {{
          "three": "https://unpkg.com/three@0.162.0/build/three.module.js",
          "three/addons/": "https://unpkg.com/three@0.162.0/examples/jsm/"
        }}
      }}
    </script>
    <style>
      .exploration-body .content {{
        width: min(98rem, calc(100vw - 2rem));
        max-width: none;
      }}

      .epoch-strip {{
        display: flex;
        align-items: center;
        flex-wrap: wrap;
        gap: 1rem;
        padding: 0.2rem 0 0.75rem;
      }}

      .epoch-strip label {{
        font-size: 0.92rem;
        color: var(--muted);
        text-transform: uppercase;
        letter-spacing: 0.05em;
      }}

      .epoch-readout {{
        min-width: 7.5rem;
        font-size: 1.05rem;
      }}

      .epoch-slider {{
        flex: 1 1 320px;
        min-width: 220px;
      }}

      .epoch-controls {{
        display: inline-flex;
        align-items: center;
        gap: 0.35rem;
      }}

      .epoch-chip {{
        border: 1px solid var(--line);
        background: rgba(255,255,255,0.55);
        color: var(--ink);
        border-radius: 999px;
        padding: 0.25rem 0.55rem;
        font: inherit;
        font-size: 0.82rem;
        cursor: pointer;
      }}

      .epoch-chip:hover {{
        background: rgba(255,255,255,0.9);
      }}

      .tabs {{
        display: flex;
        gap: 0.25rem;
        padding: 0.7rem 0 0;
      }}

      .tab-button {{
        border: 0;
        border-bottom: 2px solid transparent;
        background: transparent;
        color: var(--muted);
        font: inherit;
        padding: 0.55rem 0.3rem;
        margin-right: 1rem;
        cursor: pointer;
      }}

      .tab-button.active {{
        color: var(--ink);
        border-color: var(--accent);
      }}

      .tab-panel {{
        display: none;
        padding-top: 0.8rem;
      }}

      .tab-panel.active {{
        display: block;
      }}

      .tab-head {{
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 1rem;
        margin-bottom: 0.15rem;
      }}

      .tab-title {{
        margin: 0;
        font-size: 1.5rem;
      }}

      .inline-note {{
        color: var(--muted);
        font-size: 0.95rem;
        line-height: 1.55;
        max-width: 64rem;
        margin: 0.55rem 0 0;
      }}

      .table-wrap {{
        overflow: auto;
      }}

      .marker-strip {{
        display: flex;
        flex-wrap: wrap;
        gap: 0.45rem 0.65rem;
        margin: 0.25rem 0 0.95rem;
      }}

      .marker-pill {{
        display: inline-flex;
        align-items: center;
        gap: 0.35rem;
        padding: 0.25rem 0.48rem;
        border: 1px solid var(--line);
        border-radius: 999px;
        font-size: 0.84rem;
        background: rgba(255,255,255,0.44);
      }}

      .marker-pill.special {{
        border-color: rgba(143, 74, 33, 0.45);
        box-shadow: inset 0 0 0 1px rgba(143, 74, 33, 0.10);
      }}

      .precession-table {{
        width: 100%;
        border-collapse: collapse;
        font-size: 0.95rem;
      }}

      .precession-table th,
      .precession-table td {{
        padding: 0.48rem 0.45rem;
        border-bottom: 1px solid var(--line);
        text-align: left;
        vertical-align: top;
      }}

      .precession-table th {{
        font-size: 0.82rem;
        color: var(--muted);
        letter-spacing: 0.04em;
        text-transform: uppercase;
        position: sticky;
        top: 0;
        background: rgba(246, 241, 232, 0.96);
      }}

      .precession-table tr.selected {{
        background: rgba(143, 74, 33, 0.08);
      }}

      .precession-table tr:hover {{
        background: rgba(143, 74, 33, 0.05);
      }}

      .precession-table tr.season-0 {{
        background: rgba(212, 170, 77, 0.24);
      }}

      .precession-table tr.season-1 {{
        background: rgba(211, 135, 84, 0.22);
      }}

      .precession-table tr.season-2 {{
        background: rgba(111, 159, 183, 0.22);
      }}

      .precession-table tr.season-3 {{
        background: rgba(216, 194, 122, 0.22);
      }}

      .precession-table tr.season-4 {{
        background: rgba(176, 123, 93, 0.22);
      }}

      .precession-table tr.season-5 {{
        background: rgba(141, 160, 201, 0.22);
      }}

      .precession-table tr.marker-row td {{
        border-top: 2px solid rgba(143, 74, 33, 0.4);
        border-bottom: 2px solid rgba(143, 74, 33, 0.4);
      }}

      .minor {{
        color: var(--muted);
        font-size: 0.88rem;
      }}

      .tagline {{
        display: inline-block;
        padding: 0.15rem 0.38rem;
        border: 1px solid var(--line);
        border-radius: 999px;
        font-size: 0.8rem;
        margin-right: 0.25rem;
        margin-bottom: 0.25rem;
        background: rgba(255,255,255,0.45);
      }}

      .sky-toolbar {{
        display: flex;
        flex-wrap: wrap;
        gap: 0.85rem 1.2rem;
        align-items: center;
        padding-bottom: 0.45rem;
      }}

      .sky-toolbar-spacer {{
        flex: 1 1 auto;
      }}

      .guide-inline {{
        display: inline-flex;
        flex-wrap: wrap;
        align-items: center;
        gap: 0.45rem 0.55rem;
      }}

      .guide-button {{
        border-radius: 999px;
        padding: 0.3rem 0.7rem;
        font: inherit;
        font-size: 0.84rem;
        cursor: pointer;
        transition: background 160ms ease, color 160ms ease, border-color 160ms ease;
      }}

      .guide-button.stage {{
        border: 1px solid rgba(73,61,36,0.24);
        background: rgba(255,255,255,0.52);
        color: var(--ink);
      }}

      .guide-button.travel {{
        border: 1px solid rgba(143, 74, 33, 0.32);
        background: rgba(143, 74, 33, 0.10);
        color: #7c411f;
      }}

      .guide-button:hover {{
        background: rgba(255,255,255,0.86);
      }}

      .guide-caption {{
        display: block;
        width: 100%;
        text-align: center;
        color: #7c411f;
        font-size: 1.8rem;
        line-height: 1.2;
        min-height: 2.2rem;
        opacity: 0;
        transition: opacity 340ms ease;
      }}

      .guide-caption.visible {{
        opacity: 1;
      }}

      .debug-panel {{
        position: relative;
        margin: 0;
      }}

      .debug-panel summary {{
        display: inline-flex;
        align-items: center;
        gap: 0.35rem;
        cursor: pointer;
        color: var(--muted);
        font-size: 0.92rem;
        padding: 0.08rem 0;
      }}

      .debug-grid {{
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
        gap: 0.3rem 0.8rem;
      }}

      .debug-popover {{
        display: none;
        position: absolute;
        top: calc(100% + 0.45rem);
        left: 0;
        min-width: 28rem;
        max-width: min(44rem, calc(100vw - 4rem));
        padding: 0.75rem 0.9rem 0.9rem;
        border: 1px solid var(--line);
        border-radius: 14px;
        background: rgba(246, 241, 232, 0.97);
        box-shadow: 0 12px 24px rgba(73, 61, 36, 0.08);
        z-index: 20;
      }}

      .debug-panel[open] .debug-popover {{
        display: block;
      }}

      .debug-subhead {{
        margin-top: 0.7rem;
        color: var(--muted);
        font-size: 0.84rem;
        letter-spacing: 0.04em;
        text-transform: uppercase;
      }}

      .debug-subhead:first-child {{
        margin-top: 0;
      }}

      .debug-actions {{
        display: flex;
        gap: 0.45rem;
        margin-top: 0.45rem;
      }}

      .debug-button {{
        border: 1px solid var(--line);
        background: rgba(255,255,255,0.55);
        color: var(--ink);
        border-radius: 999px;
        padding: 0.18rem 0.5rem;
        font: inherit;
        font-size: 0.8rem;
        cursor: pointer;
      }}

      .debug-toggle {{
        display: inline-flex;
        align-items: center;
        gap: 0.35rem;
        font-size: 0.88rem;
        color: var(--muted);
      }}

      .sky-toggle {{
        display: inline-flex;
        align-items: center;
        gap: 0.32rem;
        color: var(--muted);
        font-size: 0.92rem;
      }}

      .three-toolbar {{
        display: flex;
        flex-wrap: wrap;
        align-items: center;
        gap: 0.7rem 1rem;
        margin: 0.15rem 0 0.7rem;
      }}

      .three-control {{
        display: inline-flex;
        align-items: center;
        gap: 0.45rem;
        color: var(--muted);
        font-size: 0.92rem;
      }}

      .three-story-strip {{
        display: inline-flex;
        align-items: center;
        flex-wrap: wrap;
        gap: 0.38rem;
      }}

      .three-story-search {{
        min-width: 10rem;
        max-width: 16rem;
        border: 1px solid var(--line);
        border-radius: 999px;
        background: rgba(255,255,255,0.66);
        color: var(--ink);
        font: inherit;
        font-size: 0.84rem;
        padding: 0.28rem 0.62rem;
      }}

      .story-search-row {{
        display: flex;
        align-items: center;
        gap: 0.45rem;
        margin: 0.1rem 0 0.45rem;
      }}

      .story-search-row .three-story-search {{
        flex: 1 1 auto;
        min-width: 0;
        max-width: none;
      }}

      .story-mode-label {{
        color: var(--muted);
        font-size: 0.78rem;
        letter-spacing: 0.04em;
        text-transform: uppercase;
        white-space: nowrap;
      }}

      .camera-directive-row {{
        display: flex;
        align-items: center;
        gap: 0.4rem;
        margin-top: 0.45rem;
      }}

      .camera-directive-field {{
        flex: 1 1 auto;
        min-width: 0;
        box-sizing: border-box;
        border: 1px solid var(--line);
        border-radius: 8px;
        background: rgba(255,255,255,0.74);
        color: var(--muted);
        font: 0.76rem/1.2 var(--font-mono);
        padding: 0.45rem 0.55rem;
      }}

      .icon-button {{
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 2.1rem;
        min-width: 2.1rem;
        height: 2.1rem;
        padding: 0;
      }}

      .icon-button svg {{
        width: 1rem;
        height: 1rem;
        stroke: currentColor;
      }}

      .three-story-pill {{
        border: 1px solid rgba(73,61,36,0.22);
        border-radius: 999px;
        background: rgba(255,255,255,0.64);
        color: var(--ink);
        cursor: pointer;
        font: inherit;
        font-size: 0.84rem;
        padding: 0.26rem 0.62rem;
      }}

      .three-story-pill.active {{
        border-color: rgba(143,74,33,0.56);
        background: rgba(211,176,129,0.28);
      }}

      .three-select {{
        border: 1px solid var(--line);
        border-radius: 999px;
        background: rgba(255,255,255,0.72);
        color: var(--ink);
        font: inherit;
        font-size: 0.88rem;
        padding: 0.25rem 0.55rem;
      }}

      .three-debug-panel {{
        position: relative;
        margin-left: auto;
      }}

      .three-debug-popover {{
        min-width: 30rem;
      }}

      .three-workspace {{
        display: grid;
        grid-template-columns: minmax(42rem, 1fr) minmax(360px, 440px);
        gap: 1.25rem;
        align-items: stretch;
      }}

      .three-workspace.dock-collapsed {{
        grid-template-columns: minmax(0, min(76rem, 100%));
        justify-content: center;
      }}

      .three-canvas-column {{
        min-width: 0;
      }}

      .three-container {{
        height: clamp(620px, calc(100vh - 14rem), 860px) !important;
      }}

      .three-dock {{
        border-left: 1px solid var(--line);
        padding-left: 0.9rem;
        min-width: 0;
      }}

      .three-dock.collapsed {{
        display: none;
      }}

      .three-dock-tabs {{
        display: flex;
        gap: 0.3rem;
        margin-bottom: 0.65rem;
      }}

      .three-dock-tab {{
        border: 0;
        border-bottom: 2px solid transparent;
        background: transparent;
        color: var(--muted);
        cursor: pointer;
        font: inherit;
        font-size: 0.92rem;
        padding: 0.15rem 0.25rem 0.25rem;
      }}

      .three-dock-tab.active {{
        color: var(--ink);
        border-bottom-color: var(--accent);
      }}

      .three-dock-panel {{
        display: none;
      }}

      .three-dock-panel.active {{
        display: block;
      }}

      .three-dock-actions {{
        display: flex;
        flex-wrap: wrap;
        gap: 0.45rem;
        margin: 0.45rem 0;
      }}

      .three-story-select {{
        width: 100%;
        box-sizing: border-box;
        border: 1px solid var(--line);
        border-radius: 8px;
        background: rgba(255,255,255,0.72);
        color: var(--ink);
        font: inherit;
        font-size: 0.9rem;
        padding: 0.35rem 0.5rem;
      }}

      .three-story-editor {{
        width: 100%;
        min-height: 24rem;
        margin-top: 0.5rem;
        border: 1px solid var(--line);
        border-radius: 10px;
        background: rgba(255,255,255,0.84);
        color: var(--ink);
        font: 0.8rem/1.42 var(--font-mono);
        padding: 0.7rem 0.8rem;
        resize: vertical;
        box-sizing: border-box;
      }}

      .three-story-editor.vyoma-editor {{
        min-height: 14rem;
      }}

      .three-story-editor.json-editor {{
        min-height: 18rem;
      }}

      .story-subhead {{
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 0.5rem;
        margin-top: 0.75rem;
        color: var(--muted);
        font-size: 0.82rem;
        letter-spacing: 0.04em;
        text-transform: uppercase;
      }}

      .story-help {{
        border: 1px solid var(--line);
        border-radius: 10px;
        background: rgba(255,255,255,0.62);
        margin-top: 0.45rem;
        padding: 0.45rem 0.6rem;
      }}

      .story-help summary {{
        cursor: pointer;
        color: var(--ink);
        font-size: 0.86rem;
      }}

      .story-help pre {{
        white-space: pre-wrap;
        color: var(--muted);
        font: 0.76rem/1.35 var(--font-mono);
        margin: 0.45rem 0 0;
      }}

      .grammar-block {{
        overflow-x: auto;
        border-top: 1px solid var(--line);
        border-bottom: 1px solid var(--line);
        color: var(--muted);
        font: 0.82rem/1.45 var(--font-mono);
        margin: 0.7rem 0 1rem;
        padding: 0.75rem 0.1rem;
        white-space: pre;
      }}

      .three-debug-flags {{
        display: grid;
        grid-template-columns: repeat(2, minmax(0, 1fr));
        gap: 0.4rem 0.8rem;
        margin-top: 0.6rem;
      }}

      .three-debug-flag {{
        display: inline-flex;
        align-items: center;
        gap: 0.42rem;
        color: var(--muted);
        font-size: 0.86rem;
      }}

      .three-debug-textarea {{
        width: 100%;
        min-height: 18rem;
        margin-top: 0.55rem;
        border: 1px solid var(--line);
        border-radius: 10px;
        background: rgba(255,255,255,0.84);
        color: var(--ink);
        font: 0.82rem/1.45 var(--font-mono);
        padding: 0.75rem 0.85rem;
        resize: vertical;
        box-sizing: border-box;
      }}

      .three-debug-status {{
        margin-top: 0.45rem;
        color: var(--muted);
        font-size: 0.82rem;
        min-height: 1.1rem;
      }}

      .three-story-caption {{
        position: absolute;
        inset: 0;
        display: flex;
        align-items: center;
        justify-content: center;
        pointer-events: none;
        color: rgba(255,255,255,0.94);
        font-family: var(--font-display);
        font-size: clamp(2rem, 5vw, 5rem);
        text-shadow: 0 2px 18px rgba(0,0,0,0.65);
        opacity: 0;
        transition: opacity 260ms ease;
        text-align: center;
      }}

      .three-story-caption.visible {{
        opacity: 1;
      }}

      .three-label-layer {{
        position: absolute;
        inset: 0;
        pointer-events: none;
        z-index: 4;
      }}

      .three-story-label {{
        position: absolute;
        transform: translate(-50%, -50%);
        color: rgba(240, 246, 255, 0.94);
        font: 600 0.92rem var(--font-sans);
        text-shadow: 0 1px 8px rgba(0,0,0,0.8);
        white-space: nowrap;
      }}

      .three-view-toolbar {{
        position: absolute;
        right: 0.75rem;
        top: 0.75rem;
        z-index: 4;
        display: inline-flex;
        align-items: center;
        gap: 0.22rem;
        padding: 0.24rem;
        border: 1px solid rgba(255,255,255,0.2);
        border-radius: 999px;
        background: rgba(8,8,16,0.58);
        color: rgba(255,255,255,0.86);
        opacity: 0.16;
        box-shadow: 0 10px 30px rgba(0,0,0,0.22);
        backdrop-filter: blur(10px);
        transition: opacity 220ms ease, background 220ms ease;
      }}

      .three-container:hover .three-view-toolbar {{
        opacity: 0.32;
      }}

      .three-view-toolbar:hover,
      .three-view-toolbar.pinned {{
        opacity: 0.95;
        background: rgba(8,8,16,0.72);
      }}

      .three-view-toolbar-divider {{
        width: 1px;
        height: 1.25rem;
        background: rgba(255,255,255,0.18);
        margin: 0 0.08rem;
      }}

      .three-tool-button {{
        display: inline-flex;
        align-items: center;
        justify-content: center;
        min-width: 2.25rem;
        height: 1.75rem;
        border: 1px solid transparent;
        border-radius: 999px;
        background: transparent;
        color: inherit;
        cursor: pointer;
        font: 700 0.72rem/1 var(--font-sans);
        padding: 0 0.5rem;
        white-space: nowrap;
      }}

      .three-tool-button.icon-only {{
        width: 1.75rem;
        min-width: 1.75rem;
        padding: 0;
      }}

      .three-tool-button svg {{
        width: 0.95rem;
        height: 0.95rem;
        stroke: currentColor;
      }}

      .three-tool-button:hover,
      .three-tool-button:focus-visible {{
        border-color: rgba(255,255,255,0.24);
        background: rgba(255,255,255,0.12);
        outline: none;
      }}

      .three-tool-button.active {{
        border-color: rgba(255,255,255,0.34);
        background: rgba(255,255,255,0.18);
        color: #fff;
      }}

      .three-tool-popover {{
        position: absolute;
        top: calc(100% + 0.45rem);
        right: 0.25rem;
        display: none;
        min-width: 18rem;
        max-width: min(24rem, calc(100vw - 2rem));
        padding: 0.65rem;
        border: 1px solid rgba(255,255,255,0.18);
        border-radius: 8px;
        background: rgba(8,8,16,0.86);
        box-shadow: 0 16px 42px rgba(0,0,0,0.34);
        backdrop-filter: blur(14px);
      }}

      .three-tool-popover.open {{
        display: block;
      }}

      .three-popover-section + .three-popover-section {{
        margin-top: 0.65rem;
        padding-top: 0.55rem;
        border-top: 1px solid rgba(255,255,255,0.12);
      }}

      .three-popover-heading {{
        margin-bottom: 0.4rem;
        color: rgba(255,255,255,0.64);
        font: 700 0.66rem/1 var(--font-sans);
        text-transform: uppercase;
      }}

      .three-popover-grid {{
        display: grid;
        grid-template-columns: repeat(4, minmax(0, 1fr));
        gap: 0.32rem;
      }}

      .three-popover-grid.three-col {{
        grid-template-columns: repeat(3, minmax(0, 1fr));
      }}

      .three-popover-grid.two-col {{
        grid-template-columns: repeat(2, minmax(0, 1fr));
      }}

      .three-popover-button {{
        border: 1px solid rgba(255,255,255,0.14);
        border-radius: 999px;
        background: rgba(255,255,255,0.04);
        color: rgba(255,255,255,0.86);
        cursor: pointer;
        font: 700 0.72rem/1 var(--font-sans);
        height: 1.75rem;
        min-width: 2.25rem;
        padding: 0 0.5rem;
        white-space: nowrap;
      }}

      .three-popover-button:hover,
      .three-popover-button:focus-visible {{
        background: rgba(255,255,255,0.12);
        outline: none;
      }}

      .three-popover-button.active {{
        border-color: rgba(255,255,255,0.34);
        background: rgba(255,255,255,0.20);
        color: #fff;
      }}

      .three-popover-button:disabled {{
        cursor: default;
        opacity: 0.42;
      }}

      .three-time-status {{
        margin-bottom: 0.45rem;
        color: rgba(255,255,255,0.72);
        font: 0.76rem/1.2 var(--font-mono);
        max-width: 100%;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
      }}

      .three-story-status-line {{
        margin-bottom: 0.45rem;
        color: rgba(255,255,255,0.78);
        font: 700 0.76rem/1.2 var(--font-sans);
        max-width: 100%;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
      }}

      .three-container.theater-mode {{
        position: fixed !important;
        inset: 0 !important;
        width: 100vw !important;
        height: 100vh !important;
        z-index: 9999;
        border-radius: 0 !important;
      }}

      .sky-figure {{
        margin: 0;
      }}

      .sky-svg {{
        width: 100%;
        height: auto;
        display: block;
      }}

      .legend-list {{
        display: flex;
        flex-wrap: wrap;
        gap: 0.65rem 1rem;
        margin: 0.8rem 0 0;
        padding: 0;
        list-style: none;
      }}

      .legend-item {{
        display: inline-flex;
        align-items: center;
        gap: 0.45rem;
        color: var(--muted);
        font-size: 0.88rem;
      }}

      .swatch {{
        width: 0.9rem;
        height: 0.9rem;
        border-radius: 999px;
        border: 1px solid rgba(0,0,0,0.08);
      }}

      .explanation-list {{
        margin: 0.4rem 0 0;
        padding-left: 1.1rem;
        line-height: 1.6;
      }}

      @media (max-width: 900px) {{
        .epoch-strip {{
          flex-wrap: wrap;
        }}
        .three-workspace {{
          grid-template-columns: 1fr;
        }}
        .three-workspace.dock-collapsed {{
          grid-template-columns: 1fr;
        }}
        .three-dock {{
          border-left: 0;
          border-top: 1px solid var(--line);
          padding-left: 0;
          padding-top: 0.8rem;
        }}
      }}
    </style>
  </head>
  <body class="exploration-body">
    <main class="content">
      <section class="flat-section">
        <div class="tabs" role="tablist" aria-label="Explorer views">
          <button class="tab-button" type="button" data-tab="table" role="tab" aria-selected="false">Table</button>
          <button class="tab-button" type="button" data-tab="sky" role="tab" aria-selected="false">2D Sky</button>
          <button class="tab-button active" type="button" data-tab="three" role="tab" aria-selected="true">3D Sky</button>
        </div>
      </section>

      <section class="flat-section tab-panel" id="tab-table" role="tabpanel">
        <div class="epoch-strip">
          <label for="epoch-slider-table">Epoch</label>
          <div class="epoch-controls">
            <button class="epoch-chip" type="button" id="play-table">Play</button>
            <button class="epoch-chip" type="button" id="pause-table">Pause</button>
            <button class="epoch-chip" type="button" id="reset-table">Reset</button>
          </div>
          <input class="epoch-slider" id="epoch-slider-table" type="range">
          <div class="epoch-readout" id="epoch-readout-table"></div>
        </div>
        <div class="marker-strip" id="table-marker-strip"></div>
        <div class="table-wrap" id="table-wrap"></div>
        <p class="inline-note">
          Abhijit is kept in the sequence as an asterism, but not as one of the 27 equal ecliptic sectors.
          Seasonal row color reflects the current epoch alignment of each sector center.
        </p>
      </section>

      <section class="flat-section tab-panel" id="tab-sky" role="tabpanel">
        <div class="epoch-strip">
          <label for="epoch-slider-sky">Epoch</label>
          <div class="epoch-controls">
            <button class="epoch-chip" type="button" id="play-sky">Play</button>
            <button class="epoch-chip" type="button" id="pause-sky">Pause</button>
            <button class="epoch-chip" type="button" id="reset-sky">Reset</button>
          </div>
          <input class="epoch-slider" id="epoch-slider-sky" type="range">
          <div class="epoch-readout" id="epoch-readout-sky"></div>
        </div>
        <div class="sky-toolbar">
          <label class="sky-toggle"><input type="checkbox" id="toggle-seasons" checked> Seasons</label>
          <label class="sky-toggle"><input type="checkbox" id="toggle-equator" checked> Equator</label>
          <label class="sky-toggle"><input type="checkbox" id="toggle-sectors" checked> 27 sectors</label>
          <label class="sky-toggle"><input type="checkbox" id="toggle-labels" checked> Nakshatra labels</label>
          <label class="sky-toggle"><input type="checkbox" id="toggle-pole" checked> Precession circle</label>
          <details class="debug-panel" id="trail-debug-panel">
            <summary>More visual toggles</summary>
            <div class="debug-popover">
              <div class="debug-subhead">Polar items visibility</div>
              <div class="debug-grid" id="codex-debug-grid"></div>
              <div class="debug-subhead">Nakṣatra visibility</div>
              <div class="debug-actions">
                <button class="debug-button" type="button" id="visibility-all">Select all</button>
                <button class="debug-button" type="button" id="visibility-none">Deselect all</button>
              </div>
              <div class="debug-grid" id="trail-debug-grid"></div>
            </div>
          </details>
          <span class="sky-toolbar-spacer"></span>
          <span class="guide-inline">
            <button class="guide-button stage" type="button" id="guide-stage">Set Stage</button>
            <button class="guide-button travel" type="button" id="guide-travel">Time Travel</button>
          </span>
        </div>
        <div class="guide-inline">
          <span class="guide-caption" id="guide-caption" aria-live="polite"></span>
        </div>
        <figure class="sky-figure" id="sky-wrap"></figure>
        <ul class="legend-list" id="legend-list"></ul>
        <p class="inline-note">
          In this projected ecliptic view, the pale horizontal band is the ecliptic belt and its center is 0°
          ecliptic latitude. The dashed brown curve is the celestial equator. The stars, nakshatra shapes, and
          27 sectors stay fixed, while the equinoxes, solstices, seasonal belt, equator, and pole position move
          with epoch.
        </p>
      </section>

      <section class="flat-section tab-panel active" id="tab-three" role="tabpanel">
        <div class="epoch-strip">
          <label for="epoch-slider-three">Epoch</label>
          <div class="epoch-controls">
            <button class="epoch-chip" type="button" id="play-three">Play</button>
            <button class="epoch-chip" type="button" id="pause-three">Pause</button>
            <button class="epoch-chip" type="button" id="reset-three">Reset</button>
          </div>
          <input class="epoch-slider" id="epoch-slider-three" type="range">
          <div class="epoch-readout" id="epoch-readout-three"></div>
        </div>
        <div class="three-toolbar">
          <label class="three-control">Light
            <select class="three-select" id="three-light-preset">
              <option value="night" selected>Night</option>
              <option value="twilight">Twilight</option>
              <option value="day">Day</option>
            </select>
          </label>
          <div class="three-story-strip" id="three-story-strip" aria-label="3D stories"></div>
          <button class="debug-button" type="button" id="three-dock-toggle">Hide dock</button>
        </div>
        <div class="three-workspace">
          <div class="three-canvas-column">
            <div class="three-container" id="three-container" style="width:100%; height:600px; background:#111; border-radius:12px; overflow:hidden; position:relative;">
              <div class="three-view-toolbar" id="three-view-toolbar" aria-label="3D view controls">
                <button class="three-tool-button icon-only" type="button" id="three-fullscreen-toggle" title="Fullscreen" aria-label="Fullscreen">
                  <svg viewBox="0 0 24 24" fill="none" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
                    <path d="M8 3H5a2 2 0 0 0-2 2v3"></path>
                    <path d="M16 3h3a2 2 0 0 1 2 2v3"></path>
                    <path d="M8 21H5a2 2 0 0 1-2-2v-3"></path>
                    <path d="M16 21h3a2 2 0 0 0 2-2v-3"></path>
                  </svg>
                </button>
                <span class="three-view-toolbar-divider" aria-hidden="true"></span>
                <button class="three-tool-button active" type="button" id="three-orbit-toggle" title="Click to lock rotation" aria-label="Click to lock rotation" aria-pressed="false">Free</button>
                <button class="three-tool-button" type="button" id="three-more-toggle" title="Show more controls" aria-label="Show more controls" aria-expanded="false">More</button>
                <span class="three-view-toolbar-divider" aria-hidden="true"></span>
                <button class="three-tool-button icon-only" type="button" id="three-toolbar-pin" title="Keep toolbar visible" aria-label="Keep toolbar visible" aria-pressed="false">
                  <svg viewBox="0 0 24 24" fill="none" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
                    <path d="M12 17v5"></path>
                    <path d="M5 17h14"></path>
                    <path d="M7 10h10l-2-7H9z"></path>
                    <path d="M12 10v7"></path>
                  </svg>
                </button>
                <div class="three-tool-popover" id="three-more-drawer" aria-label="More 3D controls">
                  <div class="three-popover-section">
                    <div class="three-popover-heading">Orbit</div>
                    <div class="three-popover-grid three-col">
                      <button class="three-popover-button active" type="button" data-orbit-mode="free" title="Free orbit">Free</button>
                      <button class="three-popover-button" type="button" data-orbit-mode="xy" title="XY plane spin">XY</button>
                      <button class="three-popover-button" type="button" data-orbit-mode="lock" title="Rotation locked">Lock</button>
                    </div>
                  </div>
                  <div class="three-popover-section">
                    <div class="three-popover-heading">View</div>
                    <div class="three-popover-grid">
                      <button class="three-popover-button" type="button" data-view-anchor="home" title="Default composed view">Home</button>
                      <button class="three-popover-button" type="button" data-view-anchor="top" title="Ecliptic north view">Top</button>
                      <button class="three-popover-button" type="button" data-view-anchor="side" title="Ecliptic side view">Side</button>
                      <button class="three-popover-button" type="button" data-view-anchor="pole" title="Current celestial pole view">Pole</button>
                      <button class="three-popover-button" type="button" data-view-anchor="equator" title="Seasonal equator view">Equator</button>
                    </div>
                  </div>
                  <div class="three-popover-section">
                    <div class="three-popover-heading">Scene</div>
                    <div class="three-popover-grid three-col">
                      <button class="three-popover-button" type="button" data-scene-preset="day" title="Day lighting">Day</button>
                      <button class="three-popover-button" type="button" data-scene-preset="twilight" title="Evening lighting">Even</button>
                      <button class="three-popover-button active" type="button" data-scene-preset="night" title="Night lighting">Night</button>
                    </div>
                  </div>
                  <div class="three-popover-section">
                    <div class="three-popover-heading">Layers</div>
                    <div class="three-popover-grid">
                      <button class="three-popover-button" type="button" data-layer-toggle="stars" title="Stars">Stars</button>
                      <button class="three-popover-button" type="button" data-layer-toggle="nakshatras" title="Nakshatra stars and lines">Naks</button>
                      <button class="three-popover-button" type="button" data-layer-toggle="labels" title="Labels">Labels</button>
                      <button class="three-popover-button" type="button" data-layer-toggle="grid" title="Reference grids">Grid</button>
                      <button class="three-popover-button" type="button" data-layer-toggle="sectors" title="Ecliptic sectors">Sectors</button>
                      <button class="three-popover-button" type="button" data-layer-toggle="seasonal" title="Seasonal frame">Seasonal</button>
                      <button class="three-popover-button" type="button" data-layer-toggle="poles" title="Poles and pole path">Poles</button>
                    </div>
                  </div>
                  <div class="three-popover-section">
                    <div class="three-popover-heading">Time</div>
                    <div class="three-time-status" id="three-time-status"></div>
                    <div class="three-popover-grid">
                      <button class="three-popover-button" type="button" data-time-action="step-back" title="Step back">-1</button>
                      <button class="three-popover-button" type="button" data-time-action="reverse" title="Reverse play">Back</button>
                      <button class="three-popover-button" type="button" data-time-action="pause" title="Pause">Pause</button>
                      <button class="three-popover-button" type="button" data-time-action="play" title="Forward play">Play</button>
                      <button class="three-popover-button" type="button" data-time-action="step-forward" title="Step forward">+1</button>
                      <button class="three-popover-button active" type="button" data-time-action="loop" title="Loop at ends">Loop</button>
                    </div>
                    <div class="three-popover-grid" style="margin-top:0.4rem;">
                      <button class="three-popover-button" type="button" data-time-speed="0.25" title="Quarter speed">0.25x</button>
                      <button class="three-popover-button active" type="button" data-time-speed="1" title="Normal speed">1x</button>
                      <button class="three-popover-button" type="button" data-time-speed="4" title="Fast">4x</button>
                      <button class="three-popover-button" type="button" data-time-speed="16" title="Very fast">16x</button>
                    </div>
                  </div>
                  <div class="three-popover-section">
                    <div class="three-popover-heading">Story</div>
                    <div class="three-story-status-line" id="three-toolbar-story-title" title="No story">No story</div>
                    <div class="three-popover-grid">
                      <button class="three-popover-button" type="button" data-story-action="prev" title="Previous story">Prev</button>
                      <button class="three-popover-button" type="button" data-story-action="run" title="Run selected story">Run</button>
                      <button class="three-popover-button" type="button" data-story-action="stop" title="Stop story">Stop</button>
                      <button class="three-popover-button" type="button" data-story-action="next" title="Next story">Next</button>
                    </div>
                  </div>
                </div>
              </div>
              <div id="three-overlay" style="position:absolute; top:1rem; left:1rem; pointer-events:none; color:#eee; font-family:var(--font-mono); font-size:0.8rem; text-shadow: 0 1px 2px rgba(0,0,0,0.8);">
                <span id="three-epoch-label"></span>
              </div>
              <div class="three-label-layer" id="three-label-layer"></div>
              <div class="three-story-caption" id="three-story-caption"></div>
            </div>
          </div>
          <aside class="three-dock collapsed" id="three-dock" aria-label="3D tuning dock">
            <div class="three-dock-tabs" role="tablist" aria-label="3D tuning panels">
              <button class="three-dock-tab active" type="button" data-dock-tab="static">Static</button>
              <button class="three-dock-tab" type="button" data-dock-tab="stories">Stories</button>
            </div>
            <div class="three-dock-panel active" id="three-dock-static">
              <div class="debug-actions">
                <button class="debug-button" type="button" id="three-debug-capture">Capture</button>
                <button class="debug-button" type="button" id="three-debug-apply">Apply</button>
                <button class="debug-button" type="button" id="three-debug-copy">Copy</button>
                <button class="debug-button" type="button" id="three-debug-reset">Reset defaults</button>
              </div>
              <div class="three-debug-flags" id="three-debug-toggles"></div>
              <textarea class="three-debug-textarea" id="three-debug-json" spellcheck="false"></textarea>
              <div class="three-debug-status" id="three-debug-status"></div>
            </div>
            <div class="three-dock-panel" id="three-dock-stories">
              <div class="story-search-row">
                <input class="three-story-search" id="three-story-search" type="search" placeholder="Search stories" aria-label="Search 3D stories">
                <span class="story-mode-label">VyomaSutra</span>
                <button class="debug-button" type="button" id="three-vysu-run">Run VySu</button>
              </div>
              <select class="three-story-select" id="three-story-select"></select>
              <div class="camera-directive-row">
                <input class="camera-directive-field" id="three-camera-directive" type="text" readonly aria-label="Current camera as VyomaSutra" value="camera pos 0,0,0 target 0,0,0 fov 45 over 900">
                <button class="debug-button icon-button" type="button" id="three-camera-grab" title="Grab camera" aria-label="Grab camera">
                  <svg viewBox="0 0 24 24" fill="none" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
                    <path d="M14.5 4l1.5 2h3a2 2 0 0 1 2 2v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h3l1.5-2z"></path>
                    <circle cx="12" cy="13" r="3.5"></circle>
                  </svg>
                </button>
              </div>
              <textarea class="three-story-editor vyoma-editor" id="three-vysu-editor" spellcheck="false"></textarea>
              <details class="story-help" id="three-vysu-help">
                <summary>VyomaSutra help</summary>
                <pre>Short form:
caption "Text" gold size 4 1200:250:350
show eclipticNakSegments ; wait 200 ; rollout naks
flash precessionCircle 1500:
flash thuban ; flash matsya ; hide equator ; flash VE
fullscreen ; wait 500 ; exitFullscreen

Full grammar and examples are below the interpretive notes.</pre>
              </details>
              <div class="three-debug-status" id="three-vysu-status"></div>
              <div class="story-subhead">
                <span>Precession Story JSON</span>
                <span>compiled target</span>
              </div>
              <div class="three-dock-actions">
                <button class="debug-button" type="button" id="three-story-run">Run</button>
                <button class="debug-button" type="button" id="three-story-stop">Stop</button>
                <button class="debug-button" type="button" id="three-story-reset">Reload original</button>
                <button class="debug-button" type="button" id="three-story-copy">Copy</button>
              </div>
              <textarea class="three-story-editor json-editor" id="three-story-editor" spellcheck="false"></textarea>
              <div class="three-debug-status" id="three-story-status"></div>
            </div>
          </aside>
        </div>
        <p class="inline-note">
          Drag to rotate, scroll to zoom. The white grid is the fixed J2000 ecliptic. The drifting seasonal frame (equator, equinoxes) moves relative to the stars.
        </p>
      </section>

      <section class="flat-section">
        <h2>Interpretive Notes</h2>
        <ul class="explanation-list">
          <li>The sidereal layer is fixed: stars, nakshatra shapes, and the 27 equal ecliptic sectors do not move with the slider.</li>
          <li>The tropical seasonal layer drifts: equinoxes, solstices, six rtus, equator alignment, and pole position shift with epoch.</li>
          <li>Precession becomes visible here as changing alignment between these two frames, not as deformation of the nakshatra sky itself.</li>
        </ul>
      </section>

      <section class="flat-section">
        <h2>VyomaSutra Grammar</h2>
        <p class="inline-note">
          VyomaSutra is a forgiving authoring layer for 3D stories. It compiles just-in-time into story JSON; JSON remains the runtime format.
        </p>
        <pre class="grammar-block">statement-list = statement (";" statement)*
comment        = # text, except #RGB and #RRGGBB colors

stage          = stage (blank | night | twilight | day | year NUMBER | epoch NUMBER)*
wait           = wait NUMBER
caption        = (caption | say | title) "TEXT" [duration] [color] [size NUMBER] [fadeIn NUMBER] [fadeOut NUMBER]
visibility     = (show | hide | reveal | rollout | fade) target [mode] [duration] [order]
camera         = camera [pos X,Y,Z] [target X,Y,Z] [fov NUMBER] [duration]
travel         = (travel | epochTravel) FROM to TO [duration] [step NUMBER]
flash          = flash target [duration]
fullscreen     = fullscreen | theater
exit           = exitFullscreen | canvas

duration       = DURATION:FADE_IN:FADE_OUT | DURATION: | NUMBER
mode           = instant | fade | stagger | rollout
order          = ecliptic | reverse-ecliptic | forward | reverse

coarse targets = eclipticGrid, equatorialGrid, eclipticNakSegments, stars, naks, seasonalFrame, poleTrack, overlay
reference      = referencePlanes, eclipticPlane, equatorialPlane, nsAxis, precessionCircle
polar targets  = polarItems, northPolarItems, southPolarItems, NEP, SEP, NP, SP
fine targets   = equator, VE, SS, AE, WS, agastya, thuban, polaris, matsya, sisumara
nak sigils     = $ash sector only, *ash star/stick group, @ash sector plus star/stick group
style          = style target color COLOR alpha %50 fontSize NUMBER starSize NUMBER
grid density   = grid ecliptic 15 blue ; grid equatorial 15 red

Examples:
stage blank night year -1800
caption "Visualize Precession" 1200:250:350
caption "Thuban era" gold size 4 1500:300:300
show eclipticGrid ; wait 200 ; show eclipticNakSegments
grid ecliptic 15 blue ; grid equatorial 15 red
show equatorialGrid ; style equatorialGrid color red alpha %28
rollout stars ; rollout naks
flash @ash 650:
flash thuban ; flash matsya ; flash VE ; hide equator
style naks color #8eaccb alpha .8 fontSize 5
camera pos -147.464,73.504,234.757 target 0,0,0 fov 45 900
travel -3000 to 2000 9000: step 100
fullscreen ; wait 500 ; exitFullscreen</pre>
      </section>
    </main>

    <script id="explorer-data" type="application/json">{data_json}</script>
    <script id="story-data" type="application/json">{stories_json}</script>
    <script>
      const data = JSON.parse(document.getElementById("explorer-data").textContent);
      const epochSliders = [
        document.getElementById("epoch-slider-table"),
        document.getElementById("epoch-slider-sky"),
        document.getElementById("epoch-slider-three"),
      ];
      const epochReadouts = [
        document.getElementById("epoch-readout-table"),
        document.getElementById("epoch-readout-sky"),
        document.getElementById("epoch-readout-three"),
      ];
      const epochButtons = {{
        play: [document.getElementById("play-table"), document.getElementById("play-sky"), document.getElementById("play-three")],
        pause: [document.getElementById("pause-table"), document.getElementById("pause-sky"), document.getElementById("pause-three")],
        reset: [document.getElementById("reset-table"), document.getElementById("reset-sky"), document.getElementById("reset-three")],
      }};
      const tableMarkerStrip = document.getElementById("table-marker-strip");
      const tableWrap = document.getElementById("table-wrap");
      const skyWrap = document.getElementById("sky-wrap");
      const legendList = document.getElementById("legend-list");
      const trailDebugGrid = document.getElementById("trail-debug-grid");
      const codexDebugGrid = document.getElementById("codex-debug-grid");
      const visibilityAllButton = document.getElementById("visibility-all");
      const visibilityNoneButton = document.getElementById("visibility-none");
      const guideStageButton = document.getElementById("guide-stage");
      const guideTravelButton = document.getElementById("guide-travel");
      const guideCaption = document.getElementById("guide-caption");
      const tabButtons = Array.from(document.querySelectorAll(".tab-button"));
      const tabPanels = {{
        table: document.getElementById("tab-table"),
        sky: document.getElementById("tab-sky"),
        three: document.getElementById("tab-three"),
      }};
      const toggles = {{
        seasons: document.getElementById("toggle-seasons"),
        equator: document.getElementById("toggle-equator"),
        sectors: document.getElementById("toggle-sectors"),
        labels: document.getElementById("toggle-labels"),
        pole: document.getElementById("toggle-pole"),
      }};

      const state = {{
        tab: "table",
        selectedMetaIndex: 1,
        epochIndex: Math.max(0, data.epochs.findIndex((epoch) => epoch.year === data.meta.default_epoch)),
        visibleNakshatras: Object.fromEntries(data.nakshatras.map((row) => [row.nid, true])),
        visibleCodex: {{
          "CON vedic_25_codex Shim": true,
          "CON vedic_25_codex Matsya": true,
          "HIP 30438": true,
        }},
        guide: {{
          mode: null,
          step: 0,
          naksVisibleCount: data.nakshatras.length,
          caption: "",
          timer: null,
          flashKey: null,
          flashUntil: 0,
          lastPausedEpochIndex: null,
        }},
      }};
      window.explorerState = state;
      let playTimer = null;

      const sectorRows = data.nakshatras.filter((row) => row.sector_index_27 !== null);
      const TRAVEL_EVENT_DEFS = [
        {{ year: -2800, caption: "2800 BCE · Abhaya Dhruva / Thuban near the pole", flashTarget: "pole-thuban" }},
        {{ year: -1800, caption: "1800 BCE · Maghādi seasonal alignment", flashTarget: "SS" }},
        {{ year: -1300, caption: "1300 BCE · Śraviṣṭhādi takes over", flashTarget: "WS" }},
        {{ year: -1200, caption: "~1250 BCE · Ādityacāra seasonal scheme", flashTarget: "WS" }},
        {{ year: -500, caption: "500 BCE · Ṛtusvabhāva", flashTarget: "seasons" }},
        {{ year: 500, caption: "500 CE · Āryabhaṭa", flashTarget: "VE" }},
        {{ year: 1500, caption: "1500 CE · Matsya Dhruva / Polaris", flashTarget: "pole-polaris" }},
        {{ year: 2000, caption: "2000 CE · Present alignment", flashTarget: "seasons" }},
      ];

      epochSliders.forEach((slider) => {{
        slider.min = "0";
        slider.max = String(data.epochs.length - 1);
        slider.step = "1";
        slider.value = String(state.epochIndex);
      }});

      function wrapAngle(deg) {{
        return ((deg % 360) + 360) % 360;
      }}

      function angleFrom(start, value) {{
        return wrapAngle(value - start);
      }}

      function inSpan(value, start, end) {{
        const v = wrapAngle(value);
        const s = wrapAngle(start);
        const e = wrapAngle(end);
        if (s <= e) {{
          return v >= s && v < e;
        }}
        return v >= s || v < e;
      }}

      function epochState() {{
        return data.epochs[state.epochIndex];
      }}

      function closestEpochIndex(targetYear) {{
        let bestIndex = 0;
        let bestDistance = Number.POSITIVE_INFINITY;
        data.epochs.forEach((epoch, index) => {{
          const distance = Math.abs(epoch.year - targetYear);
          if (distance < bestDistance) {{
            bestIndex = index;
            bestDistance = distance;
          }}
        }});
        return bestIndex;
      }}

      const TRAVEL_EVENTS = TRAVEL_EVENT_DEFS
        .map((event) => ({{ ...event, epochIndex: closestEpochIndex(event.year) }}))
        .sort((left, right) => left.epochIndex - right.epochIndex);

      function seasonInfoAt(longitudeDeg, epoch) {{
        const offset = angleFrom(epoch.vernal_equinox_lon_deg - 30, longitudeDeg);
        const index = Math.floor(offset / 60) % data.meta.rtus.length;
        const season = data.meta.rtus[index];
        return {{
          index,
          name: season.name,
          devanagari: data.meta.season_name_map[season.name] || season.name,
          color: season.color,
        }};
      }}

      function markerEntries(epoch) {{
        return [
          {{ key: "VE", label: "Vernal equinox", lon: epoch.vernal_equinox_lon_deg }},
          {{ key: "SS", label: "Summer solstice", lon: epoch.summer_solstice_lon_deg }},
          {{ key: "AE", label: "Autumnal equinox", lon: epoch.autumnal_equinox_lon_deg }},
          {{ key: "WS", label: "Winter solstice", lon: epoch.winter_solstice_lon_deg }},
        ];
      }}

      function markerTagsForRow(row, epoch) {{
        if (row.sector_start_lon_deg === null) {{
          return ["Asterism only"];
        }}
        return markerEntries(epoch)
          .filter((marker) => inSpan(marker.lon, row.sector_start_lon_deg, row.sector_end_lon_deg))
          .map((marker) => marker.key);
      }}

      function markerNakshatras(epoch) {{
        return markerEntries(epoch).map((marker) => {{
          const hit = sectorRows.find((row) => inSpan(marker.lon, row.sector_start_lon_deg, row.sector_end_lon_deg));
          return {{
            key: marker.key,
            label: marker.label,
            nakshatra: hit ? hit.enaks : "—",
          }};
        }});
      }}

      function bilingualCell(iast, devanagari) {{
        return `<strong>${{iast}}</strong><br><span class="minor">${{devanagari}}</span>`;
      }}

      function singleLineCell(text) {{
        return `<strong>${{text}}</strong>`;
      }}

      function compactPlayStep() {{
        state.epochIndex = state.epochIndex >= data.epochs.length - 1 ? 0 : state.epochIndex + 1;
        render();
      }}

      function startPlay() {{
        stopGuide();
        if (playTimer !== null) return;
        playTimer = window.setInterval(compactPlayStep, 480);
      }}

      function stopPlay() {{
        stopGuide();
        if (playTimer === null) return;
        window.clearInterval(playTimer);
        playTimer = null;
      }}

      function stopGuide(clearCaption = true) {{
        if (state.guide.timer !== null) {{
          window.clearInterval(state.guide.timer);
          state.guide.timer = null;
        }}
        state.guide.mode = null;
        state.guide.step = 0;
        state.guide.naksVisibleCount = data.nakshatras.length;
        state.guide.flashKey = null;
        state.guide.flashUntil = 0;
        state.guide.lastPausedEpochIndex = null;
        if (clearCaption) {{
          state.guide.caption = "";
        }}
      }}

      function setGuideCaption(text) {{
        state.guide.caption = text;
      }}

      function guideLayerState() {{
        if (state.guide.mode === "stage") {{
          return {{
            showStars: true,
            showNakshatras: state.guide.naksVisibleCount > 0,
            naksVisibleCount: state.guide.naksVisibleCount,
            showBelt: state.guide.step >= 2,
            showSectors: state.guide.step >= 2,
            showEquator: state.guide.step >= 3,
            showMarkers: state.guide.step >= 4,
            showSeasons: state.guide.step >= 5,
            showPole: state.guide.step >= 6,
            showCodex: state.guide.step >= 6,
          }};
        }}
        return {{
          showStars: true,
          showNakshatras: true,
          naksVisibleCount: data.nakshatras.length,
          showBelt: true,
          showSectors: true,
          showEquator: true,
          showMarkers: true,
          showSeasons: true,
          showPole: true,
          showCodex: true,
        }};
      }}

      function startSetStage() {{
        stopPlay();
        stopGuide(false);
        state.guide.mode = "stage";
        state.guide.step = 0;
        state.guide.naksVisibleCount = 0;
        setGuideCaption("The fixed star field sets the sidereal stage.");
        renderSky();
        state.guide.timer = window.setInterval(() => {{
          if (state.guide.mode !== "stage") return;
          if (state.guide.step === 0) {{
            state.guide.step = 1;
            state.guide.naksVisibleCount = 1;
            setGuideCaption("Nakshatra line art emerges one by one across the fixed sky.");
          }} else if (state.guide.step === 1) {{
            if (state.guide.naksVisibleCount < data.nakshatras.length) {{
              state.guide.naksVisibleCount += 1;
            }} else {{
              state.guide.step = 2;
              setGuideCaption("The ecliptic belt and 27 sectors establish the zodiacal frame.");
            }}
          }} else if (state.guide.step === 2) {{
            state.guide.step = 3;
            setGuideCaption("The celestial equator appears as a distinct moving frame.");
          }} else if (state.guide.step === 3) {{
            state.guide.step = 4;
            setGuideCaption("Equinoxes and solstices enter as seasonal markers.");
          }} else if (state.guide.step === 4) {{
            state.guide.step = 5;
            setGuideCaption("The six-season belt overlays the fixed nakshatra sky.");
          }} else if (state.guide.step === 5) {{
            state.guide.step = 6;
            setGuideCaption("Pole path, Matsya, Shiṁśumāra, and Agastya complete the scene.");
          }} else {{
            stopGuide(false);
          }}
          renderSky();
        }}, 380);
      }}

      function startTimeTravel() {{
        stopPlay();
        stopGuide(false);
        state.guide.mode = "travel";
        setGuideCaption("");
        renderSky();
        state.guide.timer = window.setInterval(() => {{
          if (state.guide.mode !== "travel") return;
          const now = Date.now();
          const activeEvent = TRAVEL_EVENTS.find((event) => event.epochIndex === state.epochIndex) || null;
          if (activeEvent && state.guide.lastPausedEpochIndex !== state.epochIndex) {{
            state.guide.lastPausedEpochIndex = state.epochIndex;
            state.guide.flashKey = activeEvent.flashTarget;
            state.guide.flashUntil = now + 3600;
            setGuideCaption(activeEvent.caption);
            render();
            return;
          }}
          if (state.guide.flashUntil > now) {{
            renderSky();
            return;
          }}
          if (state.guide.flashKey !== null) {{
            state.guide.flashKey = null;
            setGuideCaption("");
          }}
          state.epochIndex = state.epochIndex >= data.epochs.length - 1 ? 0 : state.epochIndex + 1;
          render();
        }}, 150);
      }}

      function setTab(tabName) {{
        state.tab = tabName;
        tabButtons.forEach((button) => {{
          const active = button.dataset.tab === tabName;
          button.classList.toggle("active", active);
          button.setAttribute("aria-selected", active ? "true" : "false");
        }});
        Object.entries(tabPanels).forEach(([name, panel]) => {{
          panel.classList.toggle("active", name === tabName);
        }});
        if (tabName === "three") {{
          window.dispatchEvent(new Event('resize'));
        }}
        render();
      }}

      function selectNakshatra(metaIndex) {{
        state.selectedMetaIndex = metaIndex;
        render();
      }}

      function formatLon(value) {{
        return value === null ? "-" : `${{value.toFixed(1)}}°`;
      }}

      function renderTable() {{
        const epoch = epochState();
        tableMarkerStrip.innerHTML = markerNakshatras(epoch).map((marker) => `
          <span class="marker-pill special"><strong>${{marker.key}}</strong> ${{marker.nakshatra}}</span>
        `).join("");
        const rowsHtml = data.nakshatras.map((row) => {{
          const season = row.sector_center_lon_deg === null
            ? {{ name: "High north", index: -1 }}
            : seasonInfoAt(row.sector_center_lon_deg, epoch);
          const markers = markerTagsForRow(row, epoch).map((label) => `<span class="tagline">${{label}}</span>`).join("");
          const selectedClass = row.meta_index_28 === state.selectedMetaIndex ? " selected" : "";
          const seasonClass = season.index >= 0 ? ` season-${{season.index}}` : "";
          const markerClass = row.sector_start_lon_deg !== null && markerTagsForRow(row, epoch).some((label) => ["VE", "SS", "AE", "WS"].includes(label))
            ? " marker-row"
            : "";
          return `
            <tr class="${{seasonClass}}${{selectedClass}}${{markerClass}}" data-meta-index="${{row.meta_index_28}}">
              <td>${{row.meta_index_28}}</td>
              <td>${{bilingualCell(row.enaks, row.naks)}}</td>
              <td>${{row.shape}}</td>
              <td>${{singleLineCell(row.marga)}}</td>
              <td>${{singleLineCell(row.veethi)}}</td>
              <td>${{singleLineCell(row.daivata)}}</td>
              <td>${{row.vgj_stars}}</td>
              <td>${{row.proxy}}</td>
              <td>${{row.sector_index_27 === null ? "Abhijit" : row.sector_index_27}}</td>
              <td>${{formatLon(row.sector_start_lon_deg)}} to ${{formatLon(row.sector_end_lon_deg)}}</td>
              <td>${{season.index >= 0 ? singleLineCell(season.name) : "High north"}}</td>
              <td>${{markers || '<span class="minor">-</span>'}}</td>
            </tr>
          `;
        }}).join("");

        tableWrap.innerHTML = `
          <table class="precession-table">
            <thead>
              <tr>
                <th>#</th>
                <th>Nakshatra</th>
                <th>Shape</th>
                <th>Marga</th>
                <th>Veethi</th>
                <th>Devata</th>
                <th>Constituent Taras</th>
                <th>Proxy</th>
                <th>27-sector</th>
                <th>J2000 Longitude</th>
                <th>Season at center</th>
                <th>Epoch markers in sector</th>
              </tr>
            </thead>
            <tbody>${{rowsHtml}}</tbody>
          </table>
        `;

        tableWrap.querySelectorAll("tbody tr").forEach((rowEl) => {{
          rowEl.addEventListener("mouseenter", () => selectNakshatra(Number(rowEl.dataset.metaIndex)));
          rowEl.addEventListener("click", () => selectNakshatra(Number(rowEl.dataset.metaIndex)));
        }});
      }}

      function skyPoint(lonDeg, latDeg, bounds) {{
        const x = bounds.left + (wrapAngle(lonDeg) / 360) * bounds.width;
        const y = bounds.top + ((bounds.maxLat - latDeg) / (bounds.maxLat - bounds.minLat)) * bounds.height;
        return {{ x, y }};
      }}

      function pathForLine(hips, bounds) {{
        const points = hips.map((hip) => {{
          const star = data.stars.find((entry) => entry.hip === hip);
          return star ? skyPoint(star.lon_deg, star.lat_deg, bounds) : null;
        }}).filter(Boolean);
        if (!points.length) {{
          return "";
        }}
        return points.map((point, index) => `${{index === 0 ? "M" : "L"}}${{point.x.toFixed(2)}},${{point.y.toFixed(2)}}`).join(" ");
      }}

      function pathForSpecialLine(hips, specialStarLookup, bounds) {{
        const stars = hips.map((hip) => specialStarLookup[hip]).filter(Boolean);
        if (!stars.length) {{
          return "";
        }}
        let path = "";
        let previous = stars[0];
        let previousPoint = skyPoint(previous.lon_deg, previous.lat_deg, bounds);
        path += `M${{previousPoint.x.toFixed(2)}},${{previousPoint.y.toFixed(2)}}`;

        for (let index = 1; index < stars.length; index += 1) {{
          const current = stars[index];
          const currentPoint = skyPoint(current.lon_deg, current.lat_deg, bounds);
          const delta = current.lon_deg - previous.lon_deg;
          if (Math.abs(delta) <= 180) {{
            path += ` L${{currentPoint.x.toFixed(2)}},${{currentPoint.y.toFixed(2)}}`;
          }} else {{
            const crossesRight = delta < 0;
            const adjustedCurrentLon = crossesRight ? current.lon_deg + 360 : current.lon_deg - 360;
            const seamLon = crossesRight ? 360 : 0;
            const t = (seamLon - previous.lon_deg) / (adjustedCurrentLon - previous.lon_deg);
            const seamLat = previous.lat_deg + (current.lat_deg - previous.lat_deg) * t;
            const seamY = skyPoint(0, seamLat, bounds).y;
            const seamX1 = crossesRight ? bounds.left + bounds.width : bounds.left;
            const seamX2 = crossesRight ? bounds.left : bounds.left + bounds.width;
            path += ` L${{seamX1.toFixed(2)}},${{seamY.toFixed(2)}}`;
            path += ` M${{seamX2.toFixed(2)}},${{seamY.toFixed(2)}}`;
            path += ` L${{currentPoint.x.toFixed(2)}},${{currentPoint.y.toFixed(2)}}`;
          }}
          previous = current;
          previousPoint = currentPoint;
        }}
        return path;
      }}

      function equatorPath(epoch, bounds) {{
        const points = [];
        const step = 3;
        for (let lon = 0; lon < 360; lon += step) {{
          const rel = (lon - epoch.vernal_equinox_lon_deg) * Math.PI / 180;
          const lat = Math.atan(-Math.tan(epoch.obliquity_deg * Math.PI / 180) * Math.sin(rel)) * 180 / Math.PI;
          points.push(skyPoint(lon, lat, bounds));
        }}
        return points.map((point, index) => `${{index === 0 ? "M" : "L"}}${{point.x.toFixed(2)}},${{point.y.toFixed(2)}}`).join(" ");
      }}

      function poleTrackPath(bounds) {{
        return data.epochs.map((epoch, index) => {{
          const point = skyPoint(epoch.north_pole_lon_deg, epoch.north_pole_lat_deg, bounds);
          return `${{index === 0 ? "M" : "L"}}${{point.x.toFixed(2)}},${{point.y.toFixed(2)}}`;
        }}).join(" ");
      }}

      function rtusForEpoch(epoch) {{
        return data.meta.rtus.map((rtu, index) => {{
          const start = wrapAngle(epoch.vernal_equinox_lon_deg - 30 + index * 60);
          const end = wrapAngle(start + 60);
          return {{
            ...rtu,
            start,
            end,
            mid: wrapAngle(start + 30),
          }};
        }});
      }}

      function selectedNakshatra() {{
        return data.nakshatras.find((row) => row.meta_index_28 === state.selectedMetaIndex) || data.nakshatras[0];
      }}

      function renderVisualToggles() {{
        codexDebugGrid.innerHTML = [
          ...data.special_figures.map((figure) => `
            <label class="debug-toggle">
              <input type="checkbox" data-codex-id="${{figure.id}}" ${{state.visibleCodex[figure.id] ? "checked" : ""}}>
              <span>${{figure.label}}</span>
            </label>
          `),
          ...data.special_stars.map((star) => `
            <label class="debug-toggle">
              <input type="checkbox" data-codex-id="${{star.hip}}" ${{state.visibleCodex[star.hip] ? "checked" : ""}}>
              <span>${{star.label}}</span>
            </label>
          `),
        ].join("");
        codexDebugGrid.querySelectorAll("input[type=checkbox]").forEach((input) => {{
          input.addEventListener("change", () => {{
            state.visibleCodex[input.dataset.codexId] = input.checked;
            renderSky();
          }});
        }});

        trailDebugGrid.innerHTML = data.nakshatras.map((row) => `
          <label class="debug-toggle">
            <input type="checkbox" data-nid="${{row.nid}}" ${{state.visibleNakshatras[row.nid] ? "checked" : ""}}>
            <span>${{row.enaks}}</span>
          </label>
        `).join("");
        trailDebugGrid.querySelectorAll("input[type=checkbox]").forEach((input) => {{
          input.addEventListener("change", () => {{
            state.visibleNakshatras[input.dataset.nid] = input.checked;
            renderSky();
          }});
        }});
      }}

      function renderSky() {{
        const epoch = epochState();
        const bounds = {{
          left: 68,
          top: 26,
          width: 1040,
          height: 470,
          minLat: -45,
          maxLat: 80,
        }};
        const selected = selectedNakshatra();
        const rtus = rtusForEpoch(epoch);
        const markers = markerEntries(epoch);
        const specialStarLookup = Object.fromEntries(
          [...data.special_figures.flatMap((figure) => figure.stars), ...data.special_stars].map((star) => [star.hip, star])
        );
        const guideLayers = guideLayerState();
        const flashActive = state.guide.mode === "travel" && state.guide.flashUntil > Date.now();
        const flashStrength = flashActive ? (0.72 + 0.28 * (0.5 + 0.5 * Math.sin(Date.now() / 180))) : 0;
        const flashKey = flashActive ? state.guide.flashKey : null;

        const latGrid = [-30, -15, 0, 15, 30, 45, 60];
        const lonGrid = Array.from({{ length: 13 }}, (_, index) => index * 30);

        const latLines = latGrid.map((lat) => {{
          const y = skyPoint(0, lat, bounds).y;
          return `<line x1="${{bounds.left}}" y1="${{y}}" x2="${{bounds.left + bounds.width}}" y2="${{y}}" stroke="rgba(73,61,36,0.10)" stroke-width="1" />
            <text x="${{bounds.left - 10}}" y="${{y + 4}}" text-anchor="end" font-size="12" fill="rgba(73,61,36,0.64)">${{lat}}°</text>`;
        }}).join("");

        const lonLines = lonGrid.map((lon) => {{
          const x = skyPoint(lon, 0, bounds).x;
          return `<line x1="${{x}}" y1="${{bounds.top}}" x2="${{x}}" y2="${{bounds.top + bounds.height}}" stroke="rgba(73,61,36,0.08)" stroke-width="1" />
            <text x="${{x}}" y="${{bounds.top + bounds.height + 18}}" text-anchor="middle" font-size="12" fill="rgba(73,61,36,0.64)">${{lon}}°</text>`;
        }}).join("");

        const bandTop = skyPoint(0, data.meta.ecliptic_band_half_width_deg, bounds).y;
        const bandBottom = skyPoint(0, -data.meta.ecliptic_band_half_width_deg, bounds).y;

        const seasonRects = toggles.seasons.checked && guideLayers.showSeasons ? rtus.map((rtu) => {{
          const startX = skyPoint(rtu.start, 0, bounds).x;
          const endX = skyPoint(rtu.end, 0, bounds).x;
          const width = endX >= startX ? (endX - startX) : ((bounds.left + bounds.width) - startX);
          const bandOpacity = flashKey === "seasons" ? (0.28 + 0.20 * flashStrength) : 0.30;
          const firstRect = `<rect x="${{startX}}" y="${{bandTop}}" width="${{width}}" height="${{bandBottom - bandTop}}" fill="${{rtu.color}}" fill-opacity="${{bandOpacity}}" />`;
          if (endX >= startX) {{
            return firstRect;
          }}
          return firstRect + `<rect x="${{bounds.left}}" y="${{bandTop}}" width="${{endX - bounds.left}}" height="${{bandBottom - bandTop}}" fill="${{rtu.color}}" fill-opacity="${{bandOpacity}}" />`;
        }}).join("") : "";

        const seasonLabels = toggles.seasons.checked && guideLayers.showSeasons ? rtus.map((rtu) => {{
          const p = skyPoint(rtu.mid, 0, bounds);
          return `<text x="${{p.x}}" y="${{(bandTop + bandBottom) / 2 + 4}}" text-anchor="middle" font-size="12" fill="rgba(73,61,36,0.84)">${{rtu.name}}</text>`;
        }}).join("") : "";

        const yearCaptionPoint = skyPoint(180, 45, bounds);

        const sectors = toggles.sectors.checked && guideLayers.showSectors ? sectorRows.map((row) => {{
          const startX = skyPoint(row.sector_start_lon_deg, 0, bounds).x;
          const centerX = skyPoint(row.sector_center_lon_deg, 0, bounds).x;
          return `
            <line x1="${{startX}}" y1="${{bandTop}}" x2="${{startX}}" y2="${{bandBottom}}" stroke="rgba(73,61,36,0.30)" stroke-width="1" />
            <text x="${{centerX}}" y="${{bandBottom + 16}}" text-anchor="middle" font-size="11" fill="rgba(73,61,36,0.74)">${{row.nid.split("-")[1]}}</text>
          `;
        }}).join("") : "";

        const equator = toggles.equator.checked && guideLayers.showEquator
          ? `<path d="${{equatorPath(epoch, bounds)}}" fill="none" stroke="#8f4a21" stroke-width="1.5" stroke-dasharray="8 6" opacity="0.42" />`
          : "";

        const poleTrack = toggles.pole.checked && guideLayers.showPole
          ? `<path d="${{poleTrackPath(bounds)}}" fill="none" stroke="#6a7b91" stroke-width="1.5" stroke-dasharray="5 6" opacity="0.58" />
             <text x="${{bounds.left + bounds.width - 4}}" y="${{skyPoint(0, 67, bounds).y - 8}}" text-anchor="end" font-size="12" fill="#6a7b91">Precession circle</text>`
          : "";

        const polePoint = toggles.pole.checked && guideLayers.showPole ? (() => {{
          const p = skyPoint(epoch.north_pole_lon_deg, epoch.north_pole_lat_deg, bounds);
          const poleActive = flashKey === "pole-thuban" || flashKey === "pole-polaris";
          const radius = poleActive ? (5.5 + 1.6 * flashStrength) : 5.5;
          const fill = poleActive ? `rgba(68, 86, 108, ${{0.74 + 0.26 * flashStrength}})` : "#44566c";
          return `<circle cx="${{p.x}}" cy="${{p.y}}" r="${{radius}}" fill="${{fill}}" />
            <text x="${{p.x + 10}}" y="${{p.y - 8}}" font-size="12" fill="#44566c">North pole</text>`;
        }})() : "";

        const poleAnchors = toggles.pole.checked && guideLayers.showPole ? (() => {{
          const polarisStar = specialStarLookup["HIP 11767"];
          const thubanStar = specialStarLookup["HIP 68756"];
          if (!polarisStar || !thubanStar) {{
            return "";
          }}
          const polarisPoint = skyPoint(polarisStar.lon_deg, polarisStar.lat_deg, bounds);
          const thubanPoint = skyPoint(thubanStar.lon_deg, thubanStar.lat_deg, bounds);
          const polarisActive = flashKey === "pole-polaris";
          const thubanActive = flashKey === "pole-thuban";
          return `
            <circle cx="${{polarisPoint.x}}" cy="${{polarisPoint.y}}" r="${{polarisActive ? 3.8 + 1.2 * flashStrength : 3.8}}" fill="${{polarisActive ? `rgba(68, 86, 108, ${{0.76 + 0.24 * flashStrength}})` : "#44566c"}}" />
            <text x="${{polarisPoint.x + 8}}" y="${{polarisPoint.y + 16}}" font-size="10" fill="${{polarisActive ? `rgba(68, 86, 108, ${{0.78 + 0.22 * flashStrength}})` : "rgba(68, 86, 108, 0.78)"}}">Matsya Dhruva / Polaris</text>
            <circle cx="${{thubanPoint.x}}" cy="${{thubanPoint.y}}" r="${{thubanActive ? 3.8 + 1.2 * flashStrength : 3.8}}" fill="${{thubanActive ? `rgba(68, 86, 108, ${{0.76 + 0.24 * flashStrength}})` : "#44566c"}}" />
            <text x="${{thubanPoint.x + 8}}" y="${{thubanPoint.y + 14}}" font-size="10" fill="${{thubanActive ? `rgba(68, 86, 108, ${{0.78 + 0.22 * flashStrength}})` : "rgba(68, 86, 108, 0.78)"}}">Abhaya Dhruva / Thuban</text>
          `;
        }})() : "";

        const markerSvg = guideLayers.showMarkers ? markers.map((marker) => {{
          const p = skyPoint(marker.lon, 0, bounds);
          const active = flashKey === marker.key;
          return `
            <circle cx="${{p.x}}" cy="${{p.y}}" r="${{active ? 4.8 + 1.4 * flashStrength : 4.8}}" fill="${{active ? `rgba(143, 74, 33, ${{0.78 + 0.22 * flashStrength}})` : "#8f4a21"}}" />
            <text x="${{p.x}}" y="${{p.y - 12}}" text-anchor="middle" font-size="${{active ? 11.4 : 11}}" fill="${{active ? `rgba(143, 74, 33, ${{0.82 + 0.18 * flashStrength}})` : "#8f4a21"}}">${{marker.key}}</text>
          `;
        }}).join("") : "";

        const codexFigures = guideLayers.showCodex ? data.special_figures.map((figure) => {{
          if (!state.visibleCodex[figure.id]) {{
            return "";
          }}
          const lines = figure.lines.map((line) => {{
            const path = pathForSpecialLine(line, specialStarLookup, bounds);
            if (!path) {{
              return "";
            }}
            return `<path d="${{path}}" fill="none" stroke="#6f86a1" stroke-width="1.15" opacity="0.56" stroke-linejoin="round" stroke-linecap="round" stroke-dasharray="7 5" />`;
          }}).join("");

          const starDots = figure.stars.map((star) => {{
            const point = skyPoint(star.lon_deg, star.lat_deg, bounds);
            const radius = Math.max(1.7, star.size_hint * 0.42);
            return `<circle cx="${{point.x}}" cy="${{point.y}}" r="${{radius}}" fill="#6f86a1" opacity="0.58" />`;
          }}).join("");

          const centroidLon = figure.stars.reduce((sum, star) => sum + star.lon_deg, 0) / figure.stars.length;
          const centroidLat = figure.stars.reduce((sum, star) => sum + star.lat_deg, 0) / figure.stars.length;
          const labelPoint = skyPoint(centroidLon, centroidLat + (figure.id.includes("Shim") ? 2 : -2), bounds);
          const label = `<text x="${{labelPoint.x}}" y="${{labelPoint.y}}" text-anchor="middle" font-size="11" fill="#6a809b">${{figure.label}}</text>`;
          return lines + starDots + label;
        }}).join("") : "";

        const codexSpecialStars = guideLayers.showCodex ? data.special_stars.map((star) => {{
          if (!state.visibleCodex[star.hip]) {{
            return "";
          }}
          const point = skyPoint(star.lon_deg, Math.max(bounds.minLat, star.lat_deg), bounds);
          const withinBounds = star.lat_deg >= bounds.minLat && star.lat_deg <= bounds.maxLat;
          if (withinBounds) {{
            return `
              <circle cx="${{point.x}}" cy="${{point.y}}" r="3.7" fill="#6f86a1" opacity="0.7" />
              <text x="${{point.x + 8}}" y="${{point.y - 8}}" font-size="11" fill="#6a809b">${{star.label}}</text>
            `;
          }}
          const edgeY = bounds.top + bounds.height - 1.5;
          return `
            <path d="M${{point.x - 5}},${{edgeY}} L${{point.x + 5}},${{edgeY}} L${{point.x}},${{edgeY - 8}} Z" fill="#6f86a1" opacity="0.72" />
            <text x="${{point.x}}" y="${{bounds.top + bounds.height + 34}}" text-anchor="middle" font-size="11" fill="#6a809b">${{star.label}}</text>
          `;
        }}).join("") : "";

        const asterismPaths = guideLayers.showNakshatras ? data.nakshatras.map((row, index) => {{
          if (!state.visibleNakshatras[row.nid]) {{
            return "";
          }}
          if (index >= guideLayers.naksVisibleCount) {{
            return "";
          }}
          const selectedRow = row.meta_index_28 === selected.meta_index_28;
          const stroke = selectedRow ? "#8f4a21" : "rgba(48, 52, 61, 0.58)";
          const width = selectedRow ? 2.8 : 1.5;
          const opacity = selectedRow ? 0.96 : 0.72;
          const lines = row.asterism_lines.map((line) => {{
            return `<path d="${{pathForLine(line, bounds)}}" fill="none" stroke="${{stroke}}" stroke-width="${{width}}" opacity="${{opacity}}" stroke-linejoin="round" stroke-linecap="round" />`;
          }}).join("");

          let label = "";
          if (toggles.labels.checked && row.stars.length) {{
            const centroidLon = row.stars.reduce((sum, star) => sum + star.lon_deg, 0) / row.stars.length;
            const centroidLat = row.stars.reduce((sum, star) => sum + star.lat_deg, 0) / row.stars.length;
            const p = skyPoint(centroidLon, centroidLat + 4, bounds);
            const fill = selectedRow ? "#8f4a21" : "rgba(73,61,36,0.40)";
            const size = selectedRow ? 13 : 11;
            label = `<text x="${{p.x}}" y="${{p.y}}" text-anchor="middle" font-size="${{size}}" fill="${{fill}}">${{row.enaks}}</text>`;
          }}
          return lines + label;
        }}).join("") : "";

        const stars = guideLayers.showStars ? data.stars.map((star) => {{
          const point = skyPoint(star.lon_deg, star.lat_deg, bounds);
          const selectedStar = selected.stars.some((entry) => entry.hip === star.hip);
          const radius = selectedStar ? Math.max(2.8, star.size_hint * 0.75) : Math.max(1.9, star.size_hint * 0.58);
          const fill = selectedStar ? "#d98d3d" : "#3f4650";
          const opacity = selectedStar ? 0.95 : 0.72;
          return `<circle cx="${{point.x}}" cy="${{point.y}}" r="${{radius}}" fill="${{fill}}" opacity="${{opacity}}" />`;
        }}).join("") : "";

        const markerHits = markerEntries(epoch)
          .filter((marker) => selected.sector_start_lon_deg !== null && inSpan(marker.lon, selected.sector_start_lon_deg, selected.sector_end_lon_deg))
          .map((marker) => marker.label);
        const selectionInfo = selected.sector_center_lon_deg === null
          ? `Abhijit is shown as an asterism outside the equal-27 sector belt.`
          : markerHits.length
            ? `${{markerHits.join(" and ")}} fall in ${{selected.enaks}} at this epoch.`
            : `${{selected.enaks}} lies in the ${{seasonInfoAt(selected.sector_center_lon_deg, epoch).name}} stretch of the seasonal frame at this epoch.`;

        skyWrap.innerHTML = `
          <svg class="sky-svg" viewBox="0 0 1160 560" role="img" aria-label="Projected nakshatra sky map">
            <rect x="${{bounds.left}}" y="${{bounds.top}}" width="${{bounds.width}}" height="${{bounds.height}}" fill="rgba(255,255,255,0.34)" />
            ${{latLines}}
            ${{lonLines}}
            ${{guideLayers.showBelt ? `<rect x="${{bounds.left}}" y="${{bandTop}}" width="${{bounds.width}}" height="${{bandBottom - bandTop}}" fill="rgba(211, 176, 129, 0.20)" stroke="rgba(73,61,36,0.16)" />` : ""}}
            ${{seasonRects}}
            ${{seasonLabels}}
            ${{sectors}}
            ${{equator}}
            ${{poleTrack}}
            ${{asterismPaths}}
            ${{stars}}
            ${{codexFigures}}
            ${{codexSpecialStars}}
            ${{markerSvg}}
            ${{polePoint}}
            ${{poleAnchors}}
            <text x="${{bounds.left}}" y="16" font-size="13" fill="rgba(73,61,36,0.76)">J2000 ecliptic longitude</text>
            <text x="${{yearCaptionPoint.x}}" y="${{yearCaptionPoint.y}}" text-anchor="middle" font-size="20" fill="rgba(73,61,36,0.28)">${{epoch.label}}</text>
            <text x="10" y="${{bounds.top + bounds.height / 2}}" transform="rotate(-90 10 ${{bounds.top + bounds.height / 2}})" font-size="13" fill="rgba(73,61,36,0.76)">Ecliptic latitude</text>
          </svg>
          <p class="inline-note">
            <strong>${{epoch.label}}</strong>: ${{selectionInfo}}
            The vernal equinox sits near ${{epoch.vernal_equinox_lon_deg.toFixed(1)}}° in this fixed sidereal frame.
          </p>
        `;

        legendList.innerHTML = [
          ...data.meta.rtus.map((rtu) => `<li class="legend-item"><span class="swatch" style="background:${{rtu.color}}"></span>${{rtu.name}}</li>`),
          '<li class="legend-item"><span class="swatch" style="background:rgba(211, 176, 129, 0.20)"></span>Ecliptic belt centered on 0° ecliptic latitude</li>',
          '<li class="legend-item"><span class="swatch" style="background:#8f4a21"></span>Equinox / solstice markers</li>',
          '<li class="legend-item"><span class="swatch" style="background:#8f4a21"></span>Dashed line = celestial equator</li>',
          '<li class="legend-item"><span class="swatch" style="background:#5b728f"></span>Polar items</li>',
          '<li class="legend-item"><span class="swatch" style="background:#44566c"></span>Pole position</li>',
        ].join("");
      }}

      function render() {{
        const epoch = epochState();
        epochReadouts.forEach((readout) => {{
          readout.textContent = `${{epoch.year}} (${{epoch.label}})`;
        }});
        epochSliders.forEach((slider) => {{
          slider.value = String(state.epochIndex);
        }});
        guideCaption.textContent = state.guide.caption;
        guideCaption.classList.toggle("visible", Boolean(state.guide.caption));
        renderTable();
        renderVisualToggles();
        renderSky();
      }}
      window.explorerRender = render;

      epochSliders.forEach((slider) => {{
        slider.addEventListener("input", () => {{
          stopGuide();
          state.epochIndex = Number(slider.value);
          render();
        }});
      }});

      epochButtons.play.forEach((button) => {{
        button.addEventListener("click", startPlay);
      }});
      epochButtons.pause.forEach((button) => {{
        button.addEventListener("click", stopPlay);
      }});
      epochButtons.reset.forEach((button) => {{
        button.addEventListener("click", () => {{
          stopGuide();
          stopPlay();
          state.epochIndex = Math.max(0, data.epochs.findIndex((epoch) => epoch.year === data.meta.default_epoch));
          render();
        }});
      }});

      visibilityAllButton.addEventListener("click", () => {{
        stopGuide();
        data.nakshatras.forEach((row) => {{
          state.visibleNakshatras[row.nid] = true;
        }});
        render();
      }});

      visibilityNoneButton.addEventListener("click", () => {{
        stopGuide();
        data.nakshatras.forEach((row) => {{
          state.visibleNakshatras[row.nid] = false;
        }});
        state.visibleNakshatras[selectedNakshatra().nid] = true;
        render();
      }});

      guideStageButton.addEventListener("click", () => {{
        stopGuide();
        startSetStage();
      }});
      guideTravelButton.addEventListener("click", startTimeTravel);

      tabButtons.forEach((button) => {{
        button.addEventListener("click", () => setTab(button.dataset.tab));
      }});

      Object.values(toggles).forEach((toggle) => {{
        toggle.addEventListener("change", () => {{
          stopGuide();
          renderSky();
        }});
      }});

      render();
    </script>
    <script type="module">
      import * as THREE from 'three';
      import {{ OrbitControls }} from 'three/addons/controls/OrbitControls.js';

      const data = JSON.parse(document.getElementById("explorer-data").textContent);
      const stories = JSON.parse(document.getElementById("story-data").textContent);
      const container = document.getElementById("three-container");
      const threeViewToolbar = document.getElementById("three-view-toolbar");
      const threeFullscreenToggle = document.getElementById("three-fullscreen-toggle");
      const threeOrbitToggle = document.getElementById("three-orbit-toggle");
      const threeMoreToggle = document.getElementById("three-more-toggle");
      const threeMoreDrawer = document.getElementById("three-more-drawer");
      const threeToolbarPin = document.getElementById("three-toolbar-pin");
      const threeOrbitButtons = Array.from(document.querySelectorAll("[data-orbit-mode]"));
      const threeViewAnchorButtons = Array.from(document.querySelectorAll("[data-view-anchor]"));
      const threeLayerButtons = Array.from(document.querySelectorAll("[data-layer-toggle]"));
      const threeTimeButtons = Array.from(document.querySelectorAll("[data-time-action]"));
      const threeTimeSpeedButtons = Array.from(document.querySelectorAll("[data-time-speed]"));
      const threeSceneButtons = Array.from(document.querySelectorAll("[data-scene-preset]"));
      const threeStoryToolbarButtons = Array.from(document.querySelectorAll("[data-story-action]"));
      const threeTimeStatus = document.getElementById("three-time-status");
      const threeToolbarStoryTitle = document.getElementById("three-toolbar-story-title");
      const overlayLabel = document.getElementById("three-epoch-label");
      const storyStrip = document.getElementById("three-story-strip");
      const storyCaption = document.getElementById("three-story-caption");
      const storyLabelLayer = document.getElementById("three-label-layer");
      const threeDock = document.getElementById("three-dock");
      const threeDockToggle = document.getElementById("three-dock-toggle");
      const threeDockResizer = document.getElementById("three-dock-resizer");
      const threeDockTabs = Array.from(document.querySelectorAll(".three-dock-tab"));
      const threeDockPanels = {{
        static: document.getElementById("three-dock-static"),
        stories: document.getElementById("three-dock-stories"),
      }};
      const threeStorySearch = document.getElementById("three-story-search");
      const threeStorySelect = document.getElementById("three-story-select");
      const threeStoryEditor = document.getElementById("three-story-editor");
      const threeStoryStatus = document.getElementById("three-story-status");
      const threeStoryRun = document.getElementById("three-story-run");
      const threeStoryStop = document.getElementById("three-story-stop");
      const threeStoryReset = document.getElementById("three-story-reset");
      const threeStoryCopy = document.getElementById("three-story-copy");
      const threeVysuEditor = document.getElementById("three-vysu-editor");
      const threeVysuLines = document.getElementById("three-vysu-lines");
      const threeVysuFontSize = document.getElementById("three-vysu-font-size");
      const threeVysuRun = document.getElementById("three-vysu-run");
      const threeVysuStatus = document.getElementById("three-vysu-status");
      const threeCameraDirective = document.getElementById("three-camera-directive");
      const threeCameraGrab = document.getElementById("three-camera-grab");
      const threeLightPreset = document.getElementById("three-light-preset");
      const threeDebugJson = document.getElementById("three-debug-json");
      const threeDebugStatus = document.getElementById("three-debug-status");
      const threeDebugCapture = document.getElementById("three-debug-capture");
      const threeDebugApply = document.getElementById("three-debug-apply");
      const threeDebugCopy = document.getElementById("three-debug-copy");
      const threeDebugReset = document.getElementById("three-debug-reset");
      const threeDebugToggles = document.getElementById("three-debug-toggles");

      const R = 100;
      const BAND_HALF = data.meta.ecliptic_band_half_width_deg;
      let scene, camera, renderer, controls;
      let siderealGroup, seasonalGroup;
      let equatorLine, equinoxMarkers, poleDot, southPoleDot, southPoleLabel, nsAxisLine, eclipticPlane, equatorialPlane;
      let eclipticCircle;
      let starPoints;
      const starGroupRefs = [];
      let poleTrackCircle, poleTrackArc, poleTrackLabel;
      let movingPoleLabel = null;
      const eclipticPoleDots = [];
      const eclipticPoleLabels = [];
      const eclipticPoleRefs = [];
      const gridRefs = {{ parallels: [], meridians: [], equatorialParallels: [], equatorialMeridians: [] }};
      const bandRefs = {{ meshes: [], dividers: [], labels: [] }};
      const nakshatraLineRefs = [];
      const nakshatraLabelRefs = [];
      const polarItemRefs = [];
      const seasonalMarkerRefs = [];
      const activeStoryTimers = [];
      let activeStoryId = null;
      let activeStoryFrame = null;
      let storyLabels = {{}};
      let builtEclipticGridStep = null;
      let builtEquatorialGridStep = null;
      const activeTransitionTargets = new Set();
      const activeTransitionObjects = new Set();
      const targetVisibilityOverrides = new Map();
      const focusedPolarTargets = {{ north: new Set(), south: new Set() }};
      const focusedSeasonalTargets = new Set();
      let orbitMode = "free";
      const timeFlow = {{ direction: 0, speed: 1, loop: true, timer: null }};
      const threeDebugUiFields = [
        ["showGrid", "Ecliptic grid"],
        ["showEquatorialGrid", "Equatorial grid"],
        ["showReferencePlanes", "Reference planes"],
        ["showNsAxis", "NS axis"],
        ["showEclipticBand", "Ecliptic band"],
        ["showEclipticDividers", "Sector dividers"],
        ["showEclipticLabels", "Sector labels"],
        ["showEclipticPoles", "Ecliptic poles"],
        ["showStars", "Stars"],
        ["showNakshatraStars", "Nakshatra stars"],
        ["showNakshatraLines", "Nakshatra lines"],
        ["showNakshatraLabels", "Nakshatra labels"],
        ["showPolarItems", "Polar items"],
        ["showNorthPolarItems", "North polar items"],
        ["showSouthPolarItems", "South polar items"],
        ["showPoleTrack", "Precession circle"],
        ["showSeasonalFrame", "Seasonal frame"],
        ["showOverlay", "Overlay caption"],
      ];
      const defaultThreeSettings = {{
        lightPreset: "night",
        epochYear: -1800,
        camera: {{
          position: {{ x: -147.464, y: 73.504, z: 234.757 }},
          target: {{ x: 0, y: 0, z: 0 }},
          fov: 45,
          minDistance: 130,
          maxDistance: 600,
        }},
        grid: {{
          eclipticStepDeg: 30,
          equatorialStepDeg: 30,
          parallelColor: "#667788",
          parallelOpacity: 0.4,
          meridianColor: "#556677",
          meridianOpacity: 0.4,
          equatorialColor: "#884444",
          equatorialOpacity: 0.28,
        }},
        ecliptic: {{
          bandOpacity: 0.18,
          dividerOpacity: 0.32,
          circleColor: "#d4a56a",
          circleOpacity: 0.65,
          sectorLabelSize: 5.0,
          sectorLabelOpacity: 0.72,
          poleLabelSize: 5.0,
          poleLabelOpacity: 0.3,
        }},
        reference: {{
          eclipticPlaneColor: "#d4a56a",
          eclipticPlaneOpacity: 0.045,
          equatorialPlaneColor: "#cc3333",
          equatorialPlaneOpacity: 0.04,
          nsAxisColor: "#a7b4c7",
          nsAxisOpacity: 0.32,
        }},
        stars: {{
          size: 1.4,
          opacity: 0.88,
        }},
        nakshatras: {{
          color: "#8eaccb",
          opacity: 0.88,
          selectedColor: "#d6b27a",
          selectedOpacity: 1.0,
          labelOpacity: 0.5,
          labelSize: 5.0,
        }},
        polarItems: {{
          color: "#6f86a1",
          opacity: 0.55,
          labelOpacity: 0.65,
          starOpacity: 0.72,
          labelSize: 5.0,
        }},
        poleTrack: {{
          color: "#6a7b91",
          opacity: 0.4,
          arcColor: "#8899bb",
          arcOpacity: 0.05,
          dotColor: "#944566",
          trackLabelSize: 4.5,
          trackLabelOpacity: 0.4,
          movingPoleLabelSize: 5.0,
          movingPoleLabelOpacity: 0.7,
        }},
        seasonal: {{
          equatorColor: "#cc3333",
          equatorOpacity: 0.78,
          markerScale: 1.0,
          markerLabelSize: 7.5,
          markerLabelOpacity: 0.8,
        }},
        overlay: {{
          fontSizeRem: 1.8,
          opacity: 1.0,
        }},
        ui: {{
          showGrid: true,
          showEquatorialGrid: false,
          showReferencePlanes: false,
          showEclipticPlane: true,
          showEquatorialPlane: true,
          showNsAxis: false,
          showEclipticBand: true,
          showEclipticDividers: true,
          showEclipticLabels: true,
          showEclipticPoles: true,
          showStars: true,
          showNakshatraStars: true,
          showNakshatraLines: true,
          showNakshatraLabels: true,
          showPolarItems: true,
          showNorthPolarItems: true,
          showSouthPolarItems: true,
          showNEP: true,
          showSEP: true,
          showNP: true,
          showSP: true,
          showPoleTrack: true,
          showSeasonalFrame: true,
          showOverlay: true,
        }},
      }};
      let threeSettings = JSON.parse(JSON.stringify(defaultThreeSettings));

      /* ── helpers ─────────────────────────────────────────── */
      function toCart(lonDeg, latDeg, r) {{
        const lon = lonDeg * Math.PI / 180;
        const lat = latDeg * Math.PI / 180;
        return new THREE.Vector3(
          r * Math.cos(lat) * Math.cos(lon),
          r * Math.sin(lat),
          r * Math.cos(lat) * Math.sin(lon)
        );
      }}

      function circlePoints(latDeg, r, n) {{
        const pts = [];
        for (let i = 0; i <= n; i++) pts.push(toCart(i * 360 / n, latDeg, r));
        return pts;
      }}

      function meridianPoints(lonDeg, r, n) {{
        const pts = [];
        for (let i = 0; i <= n; i++) pts.push(toCart(lonDeg, -90 + i * 180 / n, r));
        return pts;
      }}

      function gridStep(value) {{
        const numeric = Number(value);
        if (!Number.isFinite(numeric)) return 30;
        return Math.min(90, Math.max(5, numeric));
      }}

      function removeObjects(refs, group) {{
        refs.splice(0).forEach((object) => {{
          group.remove(object);
          object.geometry?.dispose?.();
          if (object.material) object.material.dispose?.();
        }});
      }}

      function makeTextSprite(text, opts) {{
        const fontSize = opts.fontSize || 48;
        const canvas = document.createElement('canvas');
        const ctx = canvas.getContext('2d');
        ctx.font = `${{opts.bold ? 'bold ' : ''}}${{fontSize}}px sans-serif`;
        const metrics = ctx.measureText(text);
        const w = Math.ceil(metrics.width) + 12;
        const h = fontSize + 12;
        canvas.width = w;
        canvas.height = h;
        ctx.font = `${{opts.bold ? 'bold ' : ''}}${{fontSize}}px sans-serif`;
        ctx.fillStyle = opts.color || '#ffffff';
        ctx.textBaseline = 'middle';
        ctx.textAlign = 'center';
        ctx.fillText(text, w / 2, h / 2);
        const tex = new THREE.CanvasTexture(canvas);
        tex.minFilter = THREE.LinearFilter;
        const mat = new THREE.SpriteMaterial({{
          map: tex, transparent: true, opacity: opts.opacity || 0.85,
          depthWrite: false, depthTest: false
        }});
        const sprite = new THREE.Sprite(mat);
        // Change: Use absolute world units for height, then scale width proportionally
        const hUnits = opts.size || 8.0; 
        sprite.scale.set(hUnits * w / h, hUnits, 1);
        sprite.userData.aspect = w / h;
        return sprite;
      }}

      function setSpriteHeight(sprite, height) {{
        const aspect = sprite?.userData?.aspect || 1;
        sprite.scale.set(height * aspect, height, 1);
      }}

      function sectorHSL(index) {{
        const h = (index * 360 / 27 + 15) % 360;
        return `hsl(${{h}}, 38%, 52%)`;
      }}

      function sectorHex(index) {{
        const h = (index * 360 / 27 + 15) % 360;
        const c = new THREE.Color();
        c.setHSL(h / 360, 0.38, 0.52);
        return c;
      }}

      function setDebugStatus(text) {{
        if (threeDebugStatus) threeDebugStatus.textContent = text;
      }}

      function setStoryStatus(text) {{
        if (threeStoryStatus) threeStoryStatus.textContent = text;
      }}

      function setVysuStatus(text) {{
        if (threeVysuStatus) threeVysuStatus.textContent = text;
      }}

      function formatCameraNumber(value) {{
        return Number(value || 0).toFixed(3).replace(/\\.?0+$/, "");
      }}

      function currentCameraDirective() {{
        if (!camera || !controls) return "camera pos 0,0,0 target 0,0,0 fov 45 over 900";
        const pos = [camera.position.x, camera.position.y, camera.position.z].map(formatCameraNumber).join(",");
        const target = [controls.target.x, controls.target.y, controls.target.z].map(formatCameraNumber).join(",");
        const fov = formatCameraNumber(camera.fov || 45);
        return `camera pos ${{pos}} target ${{target}} fov ${{fov}} over 900`;
      }}

      async function grabCameraDirective() {{
        const directive = currentCameraDirective();
        if (threeCameraDirective) threeCameraDirective.value = directive;
        try {{
          if (!navigator.clipboard?.writeText) throw new Error("Clipboard unavailable");
          await navigator.clipboard.writeText(directive);
          setVysuStatus("Copied camera directive.");
        }} catch (error) {{
          setVysuStatus("Camera directive ready.");
        }}
      }}

      function cloneSettings(settings) {{
        return JSON.parse(JSON.stringify(settings));
      }}

      function fullscreenIcon(expanded) {{
        return expanded
          ? '<svg viewBox="0 0 24 24" fill="none" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M8 3v3a2 2 0 0 1-2 2H3"></path><path d="M16 3v3a2 2 0 0 0 2 2h3"></path><path d="M8 21v-3a2 2 0 0 0-2-2H3"></path><path d="M16 21v-3a2 2 0 0 1 2-2h3"></path></svg>'
          : '<svg viewBox="0 0 24 24" fill="none" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M8 3H5a2 2 0 0 0-2 2v3"></path><path d="M16 3h3a2 2 0 0 1 2 2v3"></path><path d="M8 21H5a2 2 0 0 1-2-2v-3"></path><path d="M16 21h3a2 2 0 0 0 2-2v-3"></path></svg>';
      }}

      function syncFullscreenButton(expanded) {{
        if (!threeFullscreenToggle) return;
        threeFullscreenToggle.innerHTML = fullscreenIcon(expanded);
        threeFullscreenToggle.title = expanded ? "Exit fullscreen" : "Fullscreen";
        threeFullscreenToggle.setAttribute("aria-label", expanded ? "Exit fullscreen" : "Fullscreen");
      }}

      function applyOrbitMode(mode = orbitMode) {{
        orbitMode = mode;
        threeOrbitButtons.forEach((button) => {{
          const active = button.dataset.orbitMode === orbitMode;
          button.classList.toggle("active", active);
          button.setAttribute("aria-pressed", active ? "true" : "false");
        }});
        if (threeOrbitToggle) {{
          const locked = orbitMode === "lock";
          threeOrbitToggle.textContent = locked ? "Lock" : "Free";
          threeOrbitToggle.classList.toggle("active", !locked);
          threeOrbitToggle.setAttribute("aria-pressed", locked ? "true" : "false");
          threeOrbitToggle.title = locked ? "Click to allow free orbit" : "Click to lock rotation";
          threeOrbitToggle.setAttribute("aria-label", locked ? "Click to allow free orbit" : "Click to lock rotation");
        }}
        if (!controls) return;
        controls.enableRotate = orbitMode !== "lock";
        controls.minAzimuthAngle = -Infinity;
        controls.maxAzimuthAngle = Infinity;
        if (orbitMode === "xy") {{
          const polar = THREE.MathUtils.clamp(controls.getPolarAngle(), 0.001, Math.PI - 0.001);
          controls.minPolarAngle = polar;
          controls.maxPolarAngle = polar;
        }} else {{
          controls.minPolarAngle = 0;
          controls.maxPolarAngle = Math.PI;
        }}
        controls.update();
      }}

      function setMoreDrawer(open) {{
        if (!threeMoreDrawer || !threeMoreToggle) return;
        threeMoreDrawer.classList.toggle("open", open);
        threeMoreToggle.classList.toggle("active", open);
        threeMoreToggle.textContent = open ? "Less" : "More";
        threeMoreToggle.title = open ? "Hide more controls" : "Show more controls";
        threeMoreToggle.setAttribute("aria-label", open ? "Hide more controls" : "Show more controls");
        threeMoreToggle.setAttribute("aria-expanded", open ? "true" : "false");
      }}

      function closeMoreDrawer(force = false) {{
        if (!force && threeViewToolbar?.classList.contains("pinned")) return;
        setMoreDrawer(false);
      }}

      function toggleMoreDrawer() {{
        setMoreDrawer(!threeMoreDrawer?.classList.contains("open"));
      }}

      function layerFlagGroups() {{
        return {{
          stars: ["showStars"],
          nakshatras: ["showNakshatraStars", "showNakshatraLines"],
          labels: ["showNakshatraLabels", "showEclipticLabels"],
          grid: ["showGrid", "showEquatorialGrid"],
          sectors: ["showEclipticBand", "showEclipticDividers", "showEclipticLabels"],
          seasonal: ["showSeasonalFrame"],
          poles: ["showEclipticPoles", "showPolarItems", "showPoleTrack", "showNP", "showSP"],
        }};
      }}

      function syncLayerButtons() {{
        const groups = layerFlagGroups();
        threeLayerButtons.forEach((button) => {{
          const flags = groups[button.dataset.layerToggle] || [];
          const active = flags.length > 0 && flags.every((flag) => threeSettings.ui[flag] !== false);
          button.classList.toggle("active", active);
          button.setAttribute("aria-pressed", active ? "true" : "false");
        }});
      }}

      function setLayerGroup(name) {{
        const flags = layerFlagGroups()[name] || [];
        if (!flags.length) return;
        const active = flags.every((flag) => threeSettings.ui[flag] !== false);
        flags.forEach((flag) => {{
          threeSettings.ui[flag] = !active;
        }});
        applyThreeSettings({{ preserveEpoch: true, preserveCamera: true }});
        syncThreeDebugTogglesFromSettings();
        syncDebugTextareaFromLive();
        syncLayerButtons();
      }}

      function cameraAnchor(anchor) {{
        const target = {{ x: 0, y: 0, z: 0 }};
        const home = cloneSettings(defaultThreeSettings).camera;
        if (anchor === "home") return home;
        if (anchor === "top") return {{ position: {{ x: 0, y: 325, z: 0.1 }}, target, fov: 42 }};
        if (anchor === "side") return {{ position: {{ x: 325, y: 0, z: 0 }}, target, fov: 42 }};
        if (anchor === "pole") {{
          const epoch = data.epochs[window.explorerState?.epochIndex ?? 0] || data.epochs[0];
          const pole = toCart(epoch.north_pole_lon_deg, epoch.north_pole_lat_deg, 325);
          return {{ position: {{ x: pole.x, y: pole.y, z: pole.z }}, target, fov: 42 }};
        }}
        if (anchor === "equator") {{
          const epoch = data.epochs[window.explorerState?.epochIndex ?? 0] || data.epochs[0];
          const point = toCart(epoch.vernal_equinox_lon_deg + 90, 0, 325);
          return {{ position: {{ x: point.x, y: point.y, z: point.z }}, target, fov: 42 }};
        }}
        return home;
      }}

      function flyToCamera(cueCamera, duration = 700) {{
        if (!camera || !controls || !cueCamera) return;
        const startTime = performance.now();
        const startPos = camera.position.clone();
        const startTarget = controls.target.clone();
        const endPos = new THREE.Vector3(
          cueCamera.position?.x ?? camera.position.x,
          cueCamera.position?.y ?? camera.position.y,
          cueCamera.position?.z ?? camera.position.z
        );
        const endTarget = new THREE.Vector3(
          cueCamera.target?.x ?? controls.target.x,
          cueCamera.target?.y ?? controls.target.y,
          cueCamera.target?.z ?? controls.target.z
        );
        const startFov = camera.fov;
        const endFov = cueCamera.fov ?? camera.fov;
        const restoreOrbitMode = orbitMode;
        controls.minPolarAngle = 0;
        controls.maxPolarAngle = Math.PI;
        const tick = (now) => {{
          const t = Math.min(1, (now - startTime) / duration);
          const eased = t < 0.5 ? 2 * t * t : 1 - Math.pow(-2 * t + 2, 2) / 2;
          camera.position.lerpVectors(startPos, endPos, eased);
          controls.target.lerpVectors(startTarget, endTarget, eased);
          camera.fov = startFov + (endFov - startFov) * eased;
          camera.updateProjectionMatrix();
          controls.update();
          if (t < 1) {{
            window.requestAnimationFrame(tick);
          }} else {{
            threeSettings.camera.position = {{
              x: Number(camera.position.x.toFixed(3)),
              y: Number(camera.position.y.toFixed(3)),
              z: Number(camera.position.z.toFixed(3)),
            }};
            threeSettings.camera.target = {{
              x: Number(controls.target.x.toFixed(3)),
              y: Number(controls.target.y.toFixed(3)),
              z: Number(controls.target.z.toFixed(3)),
            }};
            threeSettings.camera.fov = Number(camera.fov.toFixed(3));
            applyOrbitMode(restoreOrbitMode);
            syncDebugTextareaFromLive();
          }}
        }};
        window.requestAnimationFrame(tick);
      }}

      function syncTimeControls() {{
        threeTimeSpeedButtons.forEach((button) => {{
          const active = Number(button.dataset.timeSpeed) === timeFlow.speed;
          button.classList.toggle("active", active);
          button.setAttribute("aria-pressed", active ? "true" : "false");
        }});
        threeTimeButtons.forEach((button) => {{
          const action = button.dataset.timeAction;
          const active = action === "loop" ? timeFlow.loop : (action === "play" && timeFlow.direction > 0) || (action === "reverse" && timeFlow.direction < 0) || (action === "pause" && timeFlow.direction === 0);
          button.classList.toggle("active", active);
          button.setAttribute("aria-pressed", active ? "true" : "false");
        }});
        const epoch = data.epochs[window.explorerState?.epochIndex ?? 0] || data.epochs[0];
        const direction = timeFlow.direction > 0 ? "forward" : timeFlow.direction < 0 ? "backward" : "paused";
        if (threeTimeStatus && epoch) {{
          threeTimeStatus.textContent = `${{epoch.label}} · ${{timeFlow.speed}}x ${{direction}}`;
        }}
      }}

      function stopToolbarTime() {{
        if (timeFlow.timer !== null) {{
          window.clearInterval(timeFlow.timer);
          timeFlow.timer = null;
        }}
        timeFlow.direction = 0;
        syncTimeControls();
      }}

      function stepToolbarTime(delta) {{
        const st = window.explorerState;
        if (!st || typeof window.explorerRender !== "function") return;
        let next = st.epochIndex + delta;
        if (next < 0 || next >= data.epochs.length) {{
          if (!timeFlow.loop) {{
            stopToolbarTime();
            return;
          }}
          next = next < 0 ? data.epochs.length - 1 : 0;
        }}
        st.epochIndex = next;
        window.explorerRender();
        syncTimeControls();
      }}

      function startToolbarTime(direction) {{
        if (timeFlow.timer !== null) {{
          window.clearInterval(timeFlow.timer);
          timeFlow.timer = null;
        }}
        timeFlow.direction = direction;
        const interval = Math.max(60, 480 / timeFlow.speed);
        timeFlow.timer = window.setInterval(() => stepToolbarTime(timeFlow.direction), interval);
        syncTimeControls();
      }}

      function syncSceneButtons() {{
        const preset = threeSettings.lightPreset || "night";
        threeSceneButtons.forEach((button) => {{
          const active = button.dataset.scenePreset === preset;
          button.classList.toggle("active", active);
          button.setAttribute("aria-pressed", active ? "true" : "false");
        }});
      }}

      function applyScenePreset(preset) {{
        if (!preset) return;
        stopStory();
        threeSettings.lightPreset = preset;
        if (threeLightPreset) threeLightPreset.value = preset;
        applyLightPreset();
        syncSceneButtons();
        syncDebugTextareaFromLive();
        setDebugStatus(`Light preset: ${{preset}}`);
      }}

      function selectedStoryContext() {{
        const list = filteredStories();
        const selectedId = threeStorySelect?.value || activeStoryId;
        let index = list.findIndex((story) => story.id === selectedId);
        if (index < 0 && list.length) index = 0;
        return {{ list, index }};
      }}

      function syncStoryControls() {{
        const story = selectedStoryOriginal();
        if (threeToolbarStoryTitle) {{
          const title = story?.title || "No story";
          threeToolbarStoryTitle.textContent = title;
          threeToolbarStoryTitle.title = title;
        }}
        const {{ list }} = selectedStoryContext();
        threeStoryToolbarButtons.forEach((button) => {{
          const action = button.dataset.storyAction;
          button.disabled = !story || (list.length < 2 && (action === "prev" || action === "next"));
          button.classList.toggle("active", Boolean(story && activeStoryId === story.id && action === "run"));
          button.setAttribute("aria-pressed", story && activeStoryId === story.id && action === "run" ? "true" : "false");
        }});
      }}

      function selectToolbarStory(delta) {{
        const {{ list, index }} = selectedStoryContext();
        if (!list.length) {{
          syncStoryControls();
          return null;
        }}
        const next = list[(index + delta + list.length) % list.length];
        if (threeStorySelect) threeStorySelect.value = next.id;
        loadStoryIntoEditors(next);
        setStoryStatus(`Selected ${{next.title}}.`);
        syncStoryControls();
        return next;
      }}

      function runToolbarStory() {{
        try {{
          const story = storyFromEditor();
          runStory(story);
          setStoryStatus(`Running ${{story.title}}.`);
        }} catch (error) {{
          setStoryStatus(`Invalid story: ${{error.message}}`);
        }}
      }}

      const defaultVyomaSutra = `# Visualize axial precession against the fixed nakshatra sky
stage blank night year -1800
camera pos -147.464,73.504,234.757 target 0,0,0

caption "Visualize Precession" 1200:250:350
show eclipticGrid ; wait 200 ; show eclipticNakSegments
wait 200 ; fade stars
wait 100 ; rollout naks
wait 200 ; show seasonalFrame
wait 100 ; show poleTrack
wait 100 ; show overlay

wait 300 ; caption "1800 BCE" 1000:200:300
wait 200 ; travel -1800 to -800 5000: step 100`;

      const vysuTargetAliases = {{
        eclipticgrid: "eclipticGrid",
        eclgrid: "eclipticGrid",
        eclgridwire: "eclipticGrid",
        eclipticnaksegments: "eclipticNakSegments",
        eclipticnakssegments: "eclipticNakSegments",
        naksegments: "eclipticNakSegments",
        nakssegments: "eclipticNakSegments",
        eclipticsegments: "eclipticNakSegments",
        eclipticband: "eclipticBand",
        eclipticdividers: "eclipticDividers",
        sectordividers: "eclipticDividers",
        eclipticlabels: "eclipticLabels",
        sectorlabels: "eclipticLabels",
        eclipticpoles: "eclipticPoles",
        eclipticplane: "eclipticPlane",
        equatorialplane: "equatorialPlane",
        equatorialgrid: "equatorialGrid",
        equatorgrid: "equatorialGrid",
        eqgrid: "equatorialGrid",
        eq: "equatorialGrid",
        referenceplanes: "referencePlanes",
        refs: "referencePlanes",
        nsaxis: "nsAxis",
        axis: "nsAxis",
        nep: "NEP",
        sep: "SEP",
        np: "NP",
        sp: "SP",
        stars: "stars",
        naks: "nakshatras",
        nak: "nakshatras",
        nakshatra: "nakshatras",
        nakshatras: "nakshatras",
        seasonalframe: "seasonalFrame",
        seasons: "seasonalFrame",
        rtus: "seasonalFrame",
        rtu: "seasonalFrame",
        poletrack: "poleTrack",
        polepath: "poleTrack",
        precessioncircle: "poleTrack",
        overlay: "overlay",
        polaritems: "polarItems",
        northpolaritems: "northPolarItems",
        northpolar: "northPolarItems",
        southpolaritems: "southPolarItems",
        southpolar: "southPolarItems",
        precessioncircle: "precessionCircle",
        precession: "precessionCircle",
        equator: "equator",
        ve: "VE",
        ss: "SS",
        ae: "AE",
        ws: "WS",
        agastya: "agastya",
        canopus: "agastya",
        thuban: "thuban",
        abhayadhruva: "thuban",
        polaris: "polaris",
        matsyadhruva: "polaris",
        matsya: "matsya",
        sisumara: "sisumara",
        shishumara: "sisumara",
        shimshumara: "sisumara",
        fullscreen: "fullscreen",
      }};

      function stripVysuComment(line) {{
        let quote = false;
        for (let i = 0; i < line.length; i += 1) {{
          const ch = line[i];
          if (ch === '"') quote = !quote;
          if (!quote && ch === "#") {{
            const hex = line.slice(i + 1).match(/^([0-9a-fA-F]{{3}}|[0-9a-fA-F]{{6}})(\\b|\\s|$)/);
            if (hex) {{
              i += hex[1].length;
              continue;
            }}
            return line.slice(0, i);
          }}
        }}
        return line;
      }}

      function splitVysuStatements(line) {{
        const statements = [];
        let quote = false;
        let start = 0;
        for (let i = 0; i < line.length; i += 1) {{
          const ch = line[i];
          if (ch === '"') quote = !quote;
          if (!quote && ch === ";") {{
            const part = line.slice(start, i).trim();
            if (part) statements.push(part);
            start = i + 1;
          }}
        }}
        const tail = line.slice(start).trim();
        if (tail) statements.push(tail);
        return statements;
      }}

      function tokenizeVysuStatement(statement) {{
        const tokens = [];
        const pattern = /"[^"]*"|\\S+/g;
        let match;
        while ((match = pattern.exec(statement)) !== null) tokens.push(match[0]);
        return tokens;
      }}

      function parseVysuDuration(token) {{
        if (!token) return null;
        const match = String(token).match(/^(\\d+):(\\d*)?(?::(\\d*)?)?$/);
        if (!match) return null;
        const out = {{ duration: Number(match[1]) }};
        if (match[2] !== undefined && match[2] !== "") out.fadeIn = Number(match[2]);
        if (match[3] !== undefined && match[3] !== "") out.fadeOut = Number(match[3]);
        return out;
      }}

      function parseVysuVec3(token) {{
        const parts = String(token || "").split(",").map(Number);
        if (parts.length !== 3 || parts.some((part) => !Number.isFinite(part))) return null;
        return {{ x: parts[0], y: parts[1], z: parts[2] }};
      }}

      function parseVysuAlpha(token) {{
        const raw = String(token || "").trim();
        let value = null;
        if (/^%\\d+(?:\\.\\d+)?$/.test(raw)) value = Number(raw.slice(1)) / 100;
        else if (/^\\d+(?:\\.\\d+)?%$/.test(raw)) value = Number(raw.slice(0, -1)) / 100;
        else if (/^(?:0?\\.\\d+|1(?:\\.0+)?)$/.test(raw)) value = Number(raw);
        else if (/^\\d+(?:\\.\\d+)?$/.test(raw)) {{
          const number = Number(raw);
          if (number <= 1) value = number;
        }}
        return Number.isFinite(value) ? Math.min(1, Math.max(0, value)) : null;
      }}

      function parseVysuColor(token) {{
        const raw = String(token || "").trim();
        if (/^#[0-9a-fA-F]{{3}}(?:[0-9a-fA-F]{{3}})?$/.test(raw)) return raw;
        const named = new Set(["white", "black", "red", "orange", "yellow", "green", "blue", "cyan", "teal", "purple", "magenta", "pink", "gray", "grey", "gold", "brown"]);
        if (named.has(raw.toLowerCase())) return raw.toLowerCase();
        return null;
      }}

      function normalizeVysuTarget(token, warnings, lineNumber) {{
        const raw = String(token || "").trim();
        if (!raw) return null;
        if (/^[$*@]/.test(raw)) return raw;
        const key = raw.replace(/[._-]/g, "").toLowerCase();
        const target = vysuTargetAliases[key] || raw;
        const supported = new Set([
          "eclipticGrid", "equatorialGrid", "referencePlanes", "eclipticPlane", "equatorialPlane", "nsAxis",
          "eclipticNakSegments", "eclipticBand", "eclipticDividers", "eclipticLabels", "eclipticPoles",
          "stars", "nakshatras", "seasonalFrame", "poleTrack", "precessionCircle",
          "overlay", "polarItems", "northPolarItems", "southPolarItems", "NEP", "SEP", "NP", "SP",
          "equator", "VE", "SS", "AE", "WS", "agastya", "thuban", "polaris", "matsya", "sisumara"
        ]);
        if (!supported.has(target)) {{
          warnings.push(`Line ${{lineNumber}}: unsupported target "${{raw}}".`);
          return null;
        }}
        return target;
      }}

      function stylePatchForTarget(target, style) {{
        const patch = {{}};
        const put = (path, value) => {{
          let cursor = patch;
          path.slice(0, -1).forEach((key) => {{
            if (!cursor[key]) cursor[key] = {{}};
            cursor = cursor[key];
          }});
          cursor[path[path.length - 1]] = value;
        }};
        const color = style.color || style.lineColor;
        const alpha = style.alpha ?? style.opacity;
        const fontSize = style.fontSize;
        const pointSize = style.pointSize ?? style.starSize;

        if (target === "eclipticGrid") {{
          if (color) {{
            put(["grid", "parallelColor"], color);
            put(["grid", "meridianColor"], color);
          }}
          if (alpha !== undefined) {{
            put(["grid", "parallelOpacity"], alpha);
            put(["grid", "meridianOpacity"], alpha);
          }}
        }} else if (target === "equatorialGrid") {{
          if (color) put(["grid", "equatorialColor"], color);
          if (alpha !== undefined) put(["grid", "equatorialOpacity"], alpha);
        }} else if (target === "nsAxis") {{
          if (color) put(["reference", "nsAxisColor"], color);
          if (alpha !== undefined) put(["reference", "nsAxisOpacity"], alpha);
        }} else if (target === "eclipticPlane") {{
          if (color) put(["reference", "eclipticPlaneColor"], color);
          if (alpha !== undefined) put(["reference", "eclipticPlaneOpacity"], alpha);
        }} else if (target === "equatorialPlane") {{
          if (color) put(["reference", "equatorialPlaneColor"], color);
          if (alpha !== undefined) put(["reference", "equatorialPlaneOpacity"], alpha);
        }} else if (target === "stars") {{
          if (alpha !== undefined) put(["stars", "opacity"], alpha);
          if (pointSize !== undefined) put(["stars", "size"], pointSize);
        }} else if (target === "nakshatras") {{
          if (color) put(["nakshatras", "color"], color);
          if (alpha !== undefined) put(["nakshatras", "opacity"], alpha);
          if (fontSize !== undefined) put(["nakshatras", "labelSize"], fontSize);
          if (style.labelAlpha !== undefined) put(["nakshatras", "labelOpacity"], style.labelAlpha);
        }} else if (target === "polarItems" || target === "northPolarItems" || target === "southPolarItems") {{
          if (color) put(["polarItems", "color"], color);
          if (alpha !== undefined) put(["polarItems", "opacity"], alpha);
          if (fontSize !== undefined) put(["polarItems", "labelSize"], fontSize);
          if (style.labelAlpha !== undefined) put(["polarItems", "labelOpacity"], style.labelAlpha);
        }} else if (target === "poleTrack" || target === "precessionCircle") {{
          if (color) put(["poleTrack", "color"], color);
          if (alpha !== undefined) put(["poleTrack", "opacity"], alpha);
          if (fontSize !== undefined) put(["poleTrack", "trackLabelSize"], fontSize);
        }} else if (target === "seasonalFrame") {{
          if (color) put(["seasonal", "equatorColor"], color);
          if (alpha !== undefined) put(["seasonal", "equatorOpacity"], alpha);
          if (fontSize !== undefined) put(["seasonal", "markerLabelSize"], fontSize);
          if (style.labelAlpha !== undefined) put(["seasonal", "markerLabelOpacity"], style.labelAlpha);
        }} else if (target === "eclipticNakSegments" || target === "eclipticBand" || target === "eclipticLabels") {{
          if (color) put(["ecliptic", "circleColor"], color);
          if (alpha !== undefined) put(["ecliptic", "circleOpacity"], alpha);
          if (fontSize !== undefined) put(["ecliptic", "sectorLabelSize"], fontSize);
          if (style.labelAlpha !== undefined) put(["ecliptic", "sectorLabelOpacity"], style.labelAlpha);
        }} else if (target === "overlay") {{
          if (alpha !== undefined) put(["overlay", "opacity"], alpha);
          if (fontSize !== undefined) put(["overlay", "fontSizeRem"], fontSize);
        }}
        return Object.keys(patch).length ? patch : null;
      }}

      function gridPatchForVySu(args, warnings, lineNumber) {{
        const kind = String(args[0] || "").toLowerCase();
        const step = Number(args[1]);
        const color = parseVysuColor(args[2]);
        const patch = {{ grid: {{}}, ui: {{}} }};
        if (!Number.isFinite(step)) {{
          warnings.push(`Line ${{lineNumber}}: grid needs a numeric step, e.g. grid ecliptic 15 blue.`);
          return null;
        }}
        if (kind === "ecliptic" || kind === "ecl") {{
          patch.grid.eclipticStepDeg = step;
          if (color) {{
            patch.grid.parallelColor = color;
            patch.grid.meridianColor = color;
          }}
          patch.ui.showGrid = true;
        }} else if (kind === "equatorial" || kind === "equator" || kind === "eq") {{
          patch.grid.equatorialStepDeg = step;
          if (color) patch.grid.equatorialColor = color;
          patch.ui.showEquatorialGrid = true;
        }} else {{
          warnings.push(`Line ${{lineNumber}}: grid kind must be ecliptic or equatorial.`);
          return null;
        }}
        return patch;
      }}

      function compileVyomaSutra(source) {{
        const warnings = [];
        const cues = [];
        const initial = {{ ui: {{}} }};
        let pendingWait = 0;
        let emitted = 0;
        const blankUi = {{
          showGrid: false,
          showEquatorialGrid: false,
          showReferencePlanes: false,
          showEclipticPlane: false,
          showEquatorialPlane: false,
          showNsAxis: false,
          showEclipticBand: false,
          showEclipticDividers: false,
          showEclipticLabels: false,
          showEclipticPoles: false,
          showStars: false,
          showNakshatraStars: false,
          showNakshatraLines: false,
          showNakshatraLabels: false,
          showPolarItems: false,
          showNorthPolarItems: false,
          showSouthPolarItems: false,
          showNEP: false,
          showSEP: false,
          showNP: false,
          showSP: false,
          showPoleTrack: false,
          showSeasonalFrame: false,
          showOverlay: false,
        }};

        const cueTime = () => {{
          if (emitted === 0 && pendingWait === 0) return 0;
          const wait = pendingWait;
          pendingWait = 0;
          return `+${{wait}}`;
        }};
        const addCue = (cue) => {{
          cues.push({{ at: cueTime(), ...cue }});
          emitted += 1;
        }};

        source.split(/\\n/).forEach((line, lineIndex) => {{
          const lineNumber = lineIndex + 1;
          splitVysuStatements(stripVysuComment(line)).forEach((statement) => {{
            const tokens = tokenizeVysuStatement(statement);
            if (tokens.length === 0) return;
            const directive = tokens[0].toLowerCase();
            const args = tokens.slice(1);

            if (directive === "stage") {{
              for (let i = 0; i < args.length; i += 1) {{
                const arg = args[i].toLowerCase();
                if (arg === "blank") Object.assign(initial.ui, blankUi);
                else if (arg === "night" || arg === "twilight" || arg === "day") initial.lightPreset = arg;
                else if (arg === "year" || arg === "epoch") {{
                  const year = Number(args[i + 1]);
                  if (Number.isFinite(year)) {{
                    initial.epochYear = year;
                    i += 1;
                  }} else warnings.push(`Line ${{lineNumber}}: stage ${{arg}} needs a numeric value.`);
                }}
                else warnings.push(`Line ${{lineNumber}}: unknown stage token "${{args[i]}}".`);
              }}
              return;
            }}

            if (directive === "wait") {{
              const wait = Number(args[0]);
              if (Number.isFinite(wait)) pendingWait += wait;
              else warnings.push(`Line ${{lineNumber}}: wait needs milliseconds.`);
              return;
            }}

            if (directive === "grid") {{
              const patch = gridPatchForVySu(args, warnings, lineNumber);
              if (patch) addCue({{ action: "set", state: patch }});
              return;
            }}

            if (directive === "fullscreen" || directive === "theater") {{
              addCue({{ action: "fullscreen" }});
              return;
            }}

            if (directive === "exitfullscreen" || directive === "canvas") {{
              addCue({{ action: "exitFullscreen" }});
              return;
            }}

            if (directive === "caption" || directive === "say" || directive === "title") {{
              const cue = {{ action: "caption", duration: 1500, fadeIn: 300, fadeOut: 300 }};
              for (let index = 0; index < args.length; index += 1) {{
                const arg = args[index];
                if (/^".*"$/.test(arg)) cue.text = arg.slice(1, -1);
                else {{
                  const duration = parseVysuDuration(arg);
                  const alpha = parseVysuAlpha(arg);
                  const color = parseVysuColor(arg);
                  if (duration) Object.assign(cue, duration);
                  else if (/^\\d+$/.test(arg)) cue.duration = Number(arg);
                  else if (["size", "font", "fontsize"].includes(arg.toLowerCase()) && Number.isFinite(Number(args[index + 1]))) {{
                    cue.sizeRem = Number(args[index + 1]);
                    index += 1;
                  }}
                  else if (arg.toLowerCase() === "fadein" && /^\\d+$/.test(args[index + 1] || "")) {{
                    cue.fadeIn = Number(args[index + 1]);
                    index += 1;
                  }}
                  else if (arg.toLowerCase() === "fadeout" && /^\\d+$/.test(args[index + 1] || "")) {{
                    cue.fadeOut = Number(args[index + 1]);
                    index += 1;
                  }}
                  else if (color) cue.color = color;
                  else if (alpha !== null) cue.opacity = alpha;
                }}
              }}
              if (!cue.text) warnings.push(`Line ${{lineNumber}}: caption needs quoted text.`);
              else addCue(cue);
              return;
            }}

            if (["show", "reveal", "rollout", "fade", "hide"].includes(directive)) {{
              const target = normalizeVysuTarget(args[0], warnings, lineNumber);
              if (!target) return;
              const cue = {{ action: directive === "hide" ? "hide" : "reveal", target }};
              if (directive === "rollout" || directive === "fade") cue.mode = directive;
              args.slice(1).forEach((arg) => {{
                const lower = arg.toLowerCase();
                const duration = parseVysuDuration(arg);
                if (duration) cue.duration = duration.duration;
                else if (["instant", "fade", "stagger", "rollout"].includes(lower)) cue.mode = lower;
                else if (["ecliptic", "reverse-ecliptic", "reverse", "forward", "north-to-south", "south-to-north"].includes(lower)) cue.order = lower;
              }});
              addCue(cue);
              return;
            }}

            if (directive === "style") {{
              const target = normalizeVysuTarget(args[0], warnings, lineNumber);
              if (!target) return;
              const style = {{}};
              for (let i = 1; i < args.length; i += 1) {{
                const key = args[i].toLowerCase();
                const next = args[i + 1];
                if (["color", "linecolor"].includes(key)) {{
                  const color = parseVysuColor(next);
                  if (color) {{
                    style[key === "linecolor" ? "lineColor" : "color"] = color;
                    i += 1;
                  }} else warnings.push(`Line ${{lineNumber}}: ${{args[i]}} needs a color.`);
                }} else if (["alpha", "opacity", "labelalpha"].includes(key)) {{
                  const alpha = parseVysuAlpha(next);
                  if (alpha !== null) {{
                    style[key === "labelalpha" ? "labelAlpha" : key] = alpha;
                    i += 1;
                  }} else warnings.push(`Line ${{lineNumber}}: ${{args[i]}} needs alpha like %50 or .5.`);
                }} else if (["fontsize", "font", "starsize", "pointsize"].includes(key)) {{
                  const size = Number(next);
                  if (Number.isFinite(size)) {{
                    if (key === "starsize") style.starSize = size;
                    else if (key === "pointsize") style.pointSize = size;
                    else style.fontSize = size;
                    i += 1;
                  }} else warnings.push(`Line ${{lineNumber}}: ${{args[i]}} needs a numeric size.`);
                }} else if (key === "font+" || key === "font-") {{
                  const delta = Number.isFinite(Number(next)) ? Number(next) : 1;
                  style.fontSize = Math.max(1, (style.fontSize || 5) + (key === "font+" ? delta : -delta));
                  if (Number.isFinite(Number(next))) i += 1;
                }} else {{
                  const color = parseVysuColor(args[i]);
                  const alpha = parseVysuAlpha(args[i]);
                  if (color) style.color = color;
                  else if (alpha !== null) style.alpha = alpha;
                  else warnings.push(`Line ${{lineNumber}}: unsupported style token "${{args[i]}}".`);
                }}
              }}
              const patch = stylePatchForTarget(target, style);
              if (patch) addCue({{ action: "set", state: patch }});
              else warnings.push(`Line ${{lineNumber}}: no supported style knobs for ${{target}}.`);
              return;
            }}

            if (directive === "flash") {{
              const target = normalizeVysuTarget(args[0], warnings, lineNumber);
              if (!target) return;
              const cue = {{ action: "flash", target, duration: 1000 }};
              args.slice(1).forEach((arg) => {{
                const duration = parseVysuDuration(arg);
                if (duration) cue.duration = duration.duration;
                else if (/^\\d+$/.test(arg)) cue.duration = Number(arg);
              }});
              addCue(cue);
              return;
            }}

            if (directive === "camera") {{
              const cue = {{ action: "camera", camera: {{}}, duration: 1000 }};
              for (let i = 0; i < args.length; i += 1) {{
                const lower = args[i].toLowerCase();
                if (lower === "pos" || lower === "position") {{
                  const vec = parseVysuVec3(args[i + 1]);
                  if (vec) {{
                    cue.camera.position = vec;
                    i += 1;
                  }}
                }} else if (lower === "target") {{
                  const vec = parseVysuVec3(args[i + 1]);
                  if (vec) {{
                    cue.camera.target = vec;
                    i += 1;
                  }}
                }} else if (lower === "fov") {{
                  const fov = Number(args[i + 1]);
                  if (Number.isFinite(fov)) {{
                    cue.camera.fov = fov;
                    i += 1;
                  }}
                }} else {{
                  const duration = parseVysuDuration(args[i]);
                  if (duration) cue.duration = duration.duration;
                  else if (/^\\d+$/.test(args[i])) cue.duration = Number(args[i]);
                  else if (i === 0) warnings.push(`Line ${{lineNumber}}: camera preset "${{args[i]}}" is not implemented yet.`);
                }}
              }}
              if (Object.keys(cue.camera).length === 0) warnings.push(`Line ${{lineNumber}}: camera needs pos/target/fov.`);
              else addCue(cue);
              return;
            }}

            if (directive === "travel" || directive === "epochtravel") {{
              const from = Number(args[0]);
              const toIndex = args.findIndex((arg) => arg.toLowerCase() === "to");
              const to = Number(args[toIndex + 1]);
              const cue = {{ action: "epochTravel", from, to, duration: 5000 }};
              args.forEach((arg, index) => {{
                const duration = parseVysuDuration(arg);
                if (duration) cue.duration = duration.duration;
                if (arg.toLowerCase() === "step" && Number.isFinite(Number(args[index + 1]))) cue.step = Number(args[index + 1]);
              }});
              if (!Number.isFinite(from) || toIndex < 0 || !Number.isFinite(to)) warnings.push(`Line ${{lineNumber}}: travel needs "from to to".`);
              else addCue(cue);
              return;
            }}

            warnings.push(`Line ${{lineNumber}}: unknown directive "${{tokens[0]}}".`);
          }});
        }});

        return {{
          story: {{
            id: "vyoma-sutra-scratch",
            title: "VyomaSutra Scratch",
            version: 1,
            initial,
            cues,
          }},
          warnings,
        }};
      }}

      {browser_vysu_compiler_source()}

      function mergeSettings(target, patch) {{
        Object.entries(patch || {{}}).forEach(([key, value]) => {{
          if (value && typeof value === "object" && !Array.isArray(value)) {{
            if (!target[key] || typeof target[key] !== "object" || Array.isArray(target[key])) {{
              target[key] = {{}};
            }}
            mergeSettings(target[key], value);
          }} else {{
            target[key] = value;
          }}
        }});
        return target;
      }}

      function setStoryCaption(text, visible, transitionMs = 260, opts = null) {{
        if (!storyCaption) return;
        storyCaption.style.transitionDuration = `${{Math.max(0, transitionMs)}}ms`;
        storyCaption.textContent = text || "";
        storyCaption.style.color = opts?.color || "";
        storyCaption.style.fontSize = opts?.sizeRem ? `${{opts.sizeRem}}rem` : "";
        storyCaption.classList.toggle("visible", Boolean(visible && text));
      }}

      function clearStoryLabels() {{
        storyLabels = {{}};
        if (storyLabelLayer) storyLabelLayer.innerHTML = "";
      }}

      function applyStoryLabelsPatch(labelsPatch) {{
        if (!labelsPatch || typeof labelsPatch !== "object") return;
        if (Object.keys(labelsPatch).length === 0) {{
          clearStoryLabels();
          return;
        }}
        Object.entries(labelsPatch).forEach(([id, label]) => {{
          if (label === null) delete storyLabels[id];
          else storyLabels[id] = {{ ...(label || {{}}), id }};
        }});
        renderStoryLabels();
      }}

      function storyLabelAnchor(anchor) {{
        const key = String(anchor || "5").toUpperCase();
        return {{
          "1": [16, 84], "2": [50, 84], "3": [84, 84],
          "4": [16, 50], "5": [50, 50], "6": [84, 50],
          "7": [16, 16], "8": [50, 16], "9": [84, 16],
          SW: [16, 84], S: [50, 84], SE: [84, 84],
          W: [16, 50], C: [50, 50], E: [84, 50],
          NW: [16, 16], N: [50, 16], NE: [84, 16],
        }}[key] || [50, 50];
      }}

      function storyTargetObject(target) {{
        if (target === "NP") return poleDot;
        if (target === "SP") return southPoleDot;
        if (["VE", "SS", "AE", "WS"].includes(target)) {{
          return seasonalMarkerRefs.find((entry) => entry.key === target)?.mesh || null;
        }}
        return transitionDescriptorsForTarget(target)?.[0]?.items?.[0]?.object || null;
      }}

      function renderStoryLabels() {{
        if (!storyLabelLayer) return;
        storyLabelLayer.innerHTML = "";
        Object.values(storyLabels).forEach((label) => {{
          const element = document.createElement("div");
          element.className = `three-story-label ${{label.className || ""}}`;
          element.dataset.labelId = label.id;
          element.textContent = label.text || "";
          element.style.color = label.color || "";
          element.style.opacity = label.opacity ?? "";
          element.style.fontSize = label.sizeRem ? `${{label.sizeRem}}rem` : "";
          storyLabelLayer.appendChild(element);
        }});
        updateStoryLabels();
      }}

      function updateStoryLabels() {{
        if (!storyLabelLayer || !camera || !renderer) return;
        storyLabelLayer.querySelectorAll(".three-story-label").forEach((element) => {{
          const label = storyLabels[element.dataset.labelId];
          if (!label) return;
          let x = 50;
          let y = 50;
          let visible = true;
          if (label.mode === "target" && label.target) {{
            const object = storyTargetObject(label.target);
            if (object) {{
              const pos = new THREE.Vector3();
              object.getWorldPosition(pos);
              pos.project(camera);
              visible = pos.z >= -1 && pos.z <= 1;
              x = ((pos.x + 1) / 2) * 100;
              y = ((1 - pos.y) / 2) * 100;
            }} else {{
              visible = false;
            }}
          }} else {{
            [x, y] = storyLabelAnchor(label.screen);
          }}
          element.style.left = `calc(${{x}}% + ${{Number(label.dx || 0)}}px)`;
          element.style.top = `calc(${{y}}% + ${{Number(label.dy || 0)}}px)`;
          element.style.display = visible ? "" : "none";
        }});
      }}

      function stopStory(clearCaption = true) {{
        activeStoryTimers.splice(0).forEach((timer) => window.clearTimeout(timer));
        if (activeStoryFrame !== null) {{
          window.cancelAnimationFrame(activeStoryFrame);
          activeStoryFrame = null;
        }}
        activeStoryId = null;
        activeTransitionTargets.clear();
        activeTransitionObjects.clear();
        targetVisibilityOverrides.clear();
        focusedPolarTargets.north.clear();
        focusedPolarTargets.south.clear();
        focusedSeasonalTargets.clear();
        clearStoryLabels();
        applyOrbitMode();
        if (clearCaption) setStoryCaption("", false);
        if (storyStrip) {{
          storyStrip.querySelectorAll(".three-story-pill").forEach((button) => {{
            button.classList.remove("active");
          }});
        }}
        syncStoryControls();
      }}

      function setThreeFullscreen(enabled) {{
        if (!container) return;
        if (enabled) {{
          if (container.requestFullscreen) {{
            container.requestFullscreen().catch(() => container.classList.add("theater-mode"));
          }} else {{
            container.classList.add("theater-mode");
          }}
        }} else if (document.fullscreenElement === container && document.exitFullscreen) {{
          document.exitFullscreen().catch(() => container.classList.remove("theater-mode"));
        }} else {{
          container.classList.remove("theater-mode");
        }}
        syncFullscreenButton(enabled);
        window.setTimeout(onResize, 80);
      }}

      function applyStoryState(patch) {{
        const labelPatch = patch?.labels;
        const settingsPatch = cloneSettings(patch || {{}});
        if (Object.prototype.hasOwnProperty.call(settingsPatch, "labels")) delete settingsPatch.labels;
        const preserveEpoch = !Object.prototype.hasOwnProperty.call(patch || {{}}, "epochYear");
        const preserveCamera = !(patch || {{}}).camera;
        mergeSettings(threeSettings, settingsPatch);
        applyStoryLabelsPatch(labelPatch);
        if (threeLightPreset && threeSettings.lightPreset) {{
          threeLightPreset.value = threeSettings.lightPreset;
        }}
        applyThreeSettings({{ preserveEpoch, preserveCamera }});
        syncDebugTextareaFromLive();
      }}

      function runCaptionCue(cue) {{
        const fadeIn = cue.fadeIn ?? 250;
        const fadeOut = cue.fadeOut ?? 350;
        const duration = cue.duration ?? 1200;
        const opts = {{ color: cue.color, sizeRem: cue.sizeRem }};
        setStoryCaption(cue.text, false, 0, opts);
        activeStoryTimers.push(window.setTimeout(() => setStoryCaption(cue.text, true, fadeIn, opts), 20));
        activeStoryTimers.push(window.setTimeout(() => setStoryCaption(cue.text, false, fadeOut, opts), Math.max(20, duration - fadeOut)));
      }}

      function runCameraCue(cue) {{
        const cueCamera = cue.camera || cue.state?.camera;
        if (!camera || !controls || !cueCamera) return;
        const duration = cue.duration ?? 1000;
        const startTime = performance.now();
        const startPos = camera.position.clone();
        const startTarget = controls.target.clone();
        const endPos = new THREE.Vector3(
          cueCamera.position?.x ?? camera.position.x,
          cueCamera.position?.y ?? camera.position.y,
          cueCamera.position?.z ?? camera.position.z
        );
        const endTarget = new THREE.Vector3(
          cueCamera.target?.x ?? controls.target.x,
          cueCamera.target?.y ?? controls.target.y,
          cueCamera.target?.z ?? controls.target.z
        );
        if (typeof cueCamera.fov === "number") {{
          camera.fov = cueCamera.fov;
          camera.updateProjectionMatrix();
        }}
        if (typeof cueCamera.minDistance === "number") controls.minDistance = cueCamera.minDistance;
        if (typeof cueCamera.maxDistance === "number") controls.maxDistance = cueCamera.maxDistance;
        const restoreOrbitMode = orbitMode;
        controls.minPolarAngle = 0;
        controls.maxPolarAngle = Math.PI;
        const tick = (now) => {{
          const t = Math.min(1, (now - startTime) / duration);
          const eased = t < 0.5 ? 2 * t * t : 1 - Math.pow(-2 * t + 2, 2) / 2;
          camera.position.lerpVectors(startPos, endPos, eased);
          controls.target.lerpVectors(startTarget, endTarget, eased);
          controls.update();
          if (t < 1 && activeStoryId) {{
            activeStoryFrame = window.requestAnimationFrame(tick);
          }} else {{
            activeStoryFrame = null;
            threeSettings.camera.position = {{
              x: Number(camera.position.x.toFixed(3)),
              y: Number(camera.position.y.toFixed(3)),
              z: Number(camera.position.z.toFixed(3)),
            }};
            threeSettings.camera.target = {{
              x: Number(controls.target.x.toFixed(3)),
              y: Number(controls.target.y.toFixed(3)),
              z: Number(controls.target.z.toFixed(3)),
            }};
            applyOrbitMode(restoreOrbitMode);
            syncDebugTextareaFromLive();
          }}
        }};
        activeStoryFrame = window.requestAnimationFrame(tick);
      }}

      function runEpochTravelCue(cue) {{
        if (!window.explorerState || typeof window.explorerRender !== "function") return;
        const duration = cue.duration ?? 5000;
        const step = cue.step || data.meta.epoch_step || 100;
        const startYear = cue.from;
        const endYear = cue.to;
        const startTime = performance.now();
        let lastApplied = null;
        const tick = (now) => {{
          const t = Math.min(1, (now - startTime) / duration);
          const rawYear = startYear + (endYear - startYear) * t;
          const steppedYear = Math.round(rawYear / step) * step;
          if (steppedYear !== lastApplied) {{
            lastApplied = steppedYear;
            let bestIndex = 0;
            let bestDistance = Number.POSITIVE_INFINITY;
            data.epochs.forEach((epoch, index) => {{
              const distance = Math.abs(epoch.year - steppedYear);
              if (distance < bestDistance) {{
                bestDistance = distance;
                bestIndex = index;
              }}
            }});
            window.explorerState.epochIndex = bestIndex;
            window.explorerRender();
            threeSettings.epochYear = data.epochs[bestIndex].year;
            syncDebugTextareaFromLive();
          }}
          if (t < 1 && activeStoryId) {{
            activeStoryFrame = window.requestAnimationFrame(tick);
          }} else {{
            activeStoryFrame = null;
          }}
        }};
        activeStoryFrame = window.requestAnimationFrame(tick);
      }}

      function runFlashCue(cue) {{
        const descriptors = transitionDescriptorsForTarget(cue.target);
        if (!descriptors.length) return;
        const duration = cue.duration ?? 900;
        const steps = 12;
        const baseScales = new WeakMap();
        descriptors.forEach((entry) => {{
          setTransitionEntryVisible(entry, true);
          entry.items.forEach((item) => {{
            if (item.object.scale) baseScales.set(item.object, item.object.scale.clone());
          }});
        }});
        for (let step = 0; step <= steps; step += 1) {{
          const delay = (duration * step) / steps;
          activeStoryTimers.push(window.setTimeout(() => {{
            const wave = Math.sin((Math.PI * step) / steps);
            descriptors.forEach((entry) => {{
              entry.items.forEach((item) => {{
                setObjectOpacity(item.object, item.opacity + Math.max(0.25, item.opacity) * wave);
                if (item.object.scale) {{
                  const baseScale = baseScales.get(item.object);
                  const scale = 1 + 0.18 * wave;
                  if (baseScale) item.object.scale.copy(baseScale).multiplyScalar(scale);
                }}
              }});
            }});
            if (step === steps) {{
              descriptors.forEach((entry) => {{
                entry.items.forEach((item) => {{
                  setObjectOpacity(item.object, item.opacity);
                  const baseScale = baseScales.get(item.object);
                  if (baseScale) item.object.scale.copy(baseScale);
                }});
              }});
            }}
          }}, delay));
        }}
      }}

      const transitionDefaults = {{
        eclipticGrid: {{ mode: "stagger", order: "default", duration: 1000 }},
        referencePlanes: {{ mode: "fade", order: "default", duration: 700 }},
        eclipticPlane: {{ mode: "fade", order: "default", duration: 700 }},
        equatorialPlane: {{ mode: "fade", order: "default", duration: 700 }},
        nsAxis: {{ mode: "fade", order: "default", duration: 700 }},
        eclipticBand: {{ mode: "fade", order: "ecliptic", duration: 900 }},
        eclipticDividers: {{ mode: "rollout", order: "ecliptic", duration: 1200 }},
        eclipticLabels: {{ mode: "stagger", order: "ecliptic", duration: 1200 }},
        eclipticPoles: {{ mode: "fade", order: "default", duration: 600 }},
        eclipticNakSegments: {{ mode: "rollout", order: "ecliptic", duration: 1300 }},
        stars: {{ mode: "fade", order: "default", duration: 900 }},
        nakshatraStars: {{ mode: "rollout", order: "ecliptic", duration: 1200 }},
        nakshatras: {{ mode: "rollout", order: "ecliptic", duration: 1800 }},
        polarItems: {{ mode: "rollout", order: "default", duration: 1600 }},
        northPolarItems: {{ mode: "rollout", order: "default", duration: 1200 }},
        southPolarItems: {{ mode: "rollout", order: "default", duration: 1200 }},
        poleTrack: {{ mode: "rollout", order: "default", duration: 1100 }},
        precessionCircle: {{ mode: "fade", order: "default", duration: 900 }},
        seasonalFrame: {{ mode: "rollout", order: "default", duration: 1300 }},
        overlay: {{ mode: "fade", order: "default", duration: 500 }},
        default: {{ mode: "fade", order: "default", duration: 800 }},
      }};

      function transitionPatchForTarget(target, visible) {{
        const patches = {{
          eclipticGrid: {{ ui: {{ showGrid: visible }} }},
          equatorialGrid: {{ ui: {{ showEquatorialGrid: visible }} }},
          referencePlanes: {{ ui: {{ showReferencePlanes: visible, showEclipticPlane: visible, showEquatorialPlane: visible }} }},
          eclipticPlane: {{ ui: {{ showReferencePlanes: true, showEclipticPlane: visible }} }},
          equatorialPlane: {{ ui: {{ showReferencePlanes: true, showEquatorialPlane: visible }} }},
          nsAxis: {{ ui: {{ showNsAxis: visible }} }},
          eclipticBand: {{ ui: {{ showEclipticBand: visible }} }},
          eclipticDividers: {{ ui: {{ showEclipticDividers: visible }} }},
          eclipticLabels: {{ ui: {{ showEclipticLabels: visible }} }},
          eclipticPoles: {{ ui: {{ showEclipticPoles: visible }} }},
          NEP: {{ ui: {{ showEclipticPoles: true, showNEP: visible }} }},
          SEP: {{ ui: {{ showEclipticPoles: true, showSEP: visible }} }},
          eclipticNakSegments: {{ ui: {{ showEclipticBand: visible, showEclipticDividers: visible, showEclipticLabels: visible, showEclipticPoles: visible }} }},
          stars: {{ ui: {{ showStars: visible }} }},
          nakshatraStars: {{ ui: {{ showNakshatraStars: visible }} }},
          nakshatras: {{ ui: {{ showNakshatraLines: visible, showNakshatraLabels: visible }} }},
          nakshatraLines: {{ ui: {{ showNakshatraLines: visible }} }},
          nakshatraLabels: {{ ui: {{ showNakshatraLabels: visible }} }},
          polarItems: {{ ui: {{ showPolarItems: visible }} }},
          northPolarItems: {{ ui: {{ showPolarItems: true, showNorthPolarItems: visible }} }},
          southPolarItems: {{ ui: {{ showPolarItems: true, showSouthPolarItems: visible }} }},
          poleTrack: {{ ui: {{ showPoleTrack: visible }} }},
          precessionCircle: {{ ui: {{ showPoleTrack: visible }} }},
          seasonalFrame: {{ ui: {{ showSeasonalFrame: visible }} }},
          equator: {{ ui: {{ showSeasonalFrame: true }} }},
          VE: {{ ui: {{ showSeasonalFrame: true }} }},
          SS: {{ ui: {{ showSeasonalFrame: true }} }},
          AE: {{ ui: {{ showSeasonalFrame: true }} }},
          WS: {{ ui: {{ showSeasonalFrame: true }} }},
          NP: {{ ui: {{ showSeasonalFrame: true, showNP: visible }} }},
          SP: {{ ui: {{ showSeasonalFrame: true, showSP: visible }} }},
          overlay: {{ ui: {{ showOverlay: visible }} }},
        }};
        const polarMatches = polarMatchesForTarget(target);
        if (polarMatches.length) {{
          const regions = new Set(polarMatches.map((entry) => entry.region));
          const patch = visible ? {{ ui: {{ showPolarItems: true }} }} : {{ ui: {{}} }};
          if (visible && regions.has("north")) patch.ui.showNorthPolarItems = true;
          if (visible && regions.has("south")) patch.ui.showSouthPolarItems = true;
          return patch;
        }}
        return patches[target] || null;
      }}

      function setObjectOpacity(object, opacity) {{
        if (!object?.material) return;
        const materials = Array.isArray(object.material) ? object.material : [object.material];
        materials.forEach((material) => {{
          material.transparent = true;
          material.opacity = Math.min(1, Math.max(0, opacity));
          material.needsUpdate = true;
        }});
      }}

      function transitionDescriptor(object, opacity = 1, order = 0) {{
        return {{ items: [{{ object, opacity }}], order }};
      }}

      function transitionGroup(items, order = 0) {{
        return {{ items, order }};
      }}

      function normalizeNakKey(value) {{
        return String(value || "")
          .normalize("NFD")
          .replace(/[\\u0300-\\u036f]/g, "")
          .replace(/[^a-z0-9]/gi, "")
          .toLowerCase();
      }}

      function specialTargetAliases(...values) {{
        const aliases = new Set();
        values.forEach((value) => {{
          const key = normalizeNakKey(value);
          if (key) aliases.add(key);
        }});
        if (aliases.has("convedic25codexshim") || aliases.has("shimsumara") || aliases.has("simsumara")) {{
          aliases.add("sisumara");
          aliases.add("shishumara");
          aliases.add("shimshumara");
        }}
        if (aliases.has("convedic25codexmatsya")) aliases.add("matsya");
        if (aliases.has("agastya") || aliases.has("canopus") || aliases.has("hip30438")) {{
          aliases.add("agastya");
          aliases.add("canopus");
        }}
        if (aliases.has("thuban") || aliases.has("hip68756")) {{
          aliases.add("thuban");
          aliases.add("abhayadhruva");
        }}
        if (aliases.has("polaris") || aliases.has("hip11767")) {{
          aliases.add("polaris");
          aliases.add("matsyadhruva");
        }}
        return Array.from(aliases);
      }}

      const nakAliasMap = new Map();
      data.nakshatras.forEach((row) => {{
        const abbr = normalizeNakKey((row.nid || "").split("-").pop());
        const english = normalizeNakKey(row.enaks);
        const index = String(row.sector_index_27 || row.meta_index_28).padStart(2, "0");
        [abbr, english, `n${{index}}`].forEach((alias) => {{
          if (alias) nakAliasMap.set(alias, row.nid);
        }});
      }});
      Object.entries({{
        pph: "N11-PPhal", uph: "N12-UPhal", pas: "N20-PAsh", uas: "N21-UAsh",
        ppr: "N25-PPros", pbh: "N25-PPros", upr: "N26-UPros", ubh: "N26-UPros",
        abh: "N28-Abh", n28: "N28-Abh",
      }}).forEach(([alias, nid]) => nakAliasMap.set(alias, nid));

      function resolveNakshatraTarget(target) {{
        const raw = String(target || "");
        if (!/^[$*@]/.test(raw)) return null;
        const sigil = raw[0];
        const query = normalizeNakKey(raw.slice(1));
        if (nakAliasMap.has(query)) return {{ sigil, nid: nakAliasMap.get(query) }};
        const matches = Array.from(nakAliasMap.entries()).filter(([alias]) => alias.startsWith(query));
        if (matches.length === 1) return {{ sigil, nid: matches[0][1] }};
        return null;
      }}

      function setTransitionEntryVisible(entry, visible) {{
        entry.items.forEach((item) => {{ item.object.visible = visible; }});
      }}

      function setTransitionEntryOpacity(entry, progress) {{
        entry.items.forEach((item) => setObjectOpacity(item.object, item.opacity * progress));
      }}

      function markTransitionObjects(descriptors, active) {{
        descriptors.forEach((entry) => {{
          entry.items.forEach((item) => {{
            if (active) activeTransitionObjects.add(item.object);
            else activeTransitionObjects.delete(item.object);
          }});
        }});
      }}

      function targetVisible(target) {{
        return targetVisibilityOverrides.get(target) !== false;
      }}

      function isSeasonalLeafTarget(target) {{
        return ["equator", "VE", "SS", "AE", "WS", "NP", "SP"].includes(target);
      }}

      function seasonalTargetVisible(target) {{
        if (focusedSeasonalTargets.size && !focusedSeasonalTargets.has(target)) return false;
        return targetVisible(target);
      }}

      function setFocusedSeasonalTarget(target, visible) {{
        if (visible && isSeasonalLeafTarget(target)) focusedSeasonalTargets.add(target);
      }}

      function clearFocusedSeasonalTarget(target) {{
        if (target === "seasonalFrame") focusedSeasonalTargets.clear();
      }}

      function focusedPolarVisible(entry) {{
        const focused = focusedPolarTargets[entry.region];
        if (!focused || focused.size === 0) return true;
        return (entry.aliases || []).some((alias) => focused.has(alias));
      }}

      function polarMatchesForTarget(target) {{
        return polarItemRefs.filter((entry) => (entry.aliases || []).includes(target));
      }}

      function setFocusedPolarTarget(target, visible) {{
        polarMatchesForTarget(target).forEach((entry) => {{
          const focused = focusedPolarTargets[entry.region];
          (entry.aliases || []).forEach((alias) => {{
            if (visible) focused.add(alias);
            else focused.delete(alias);
          }});
        }});
      }}

      function clearFocusedPolarTarget(target) {{
        if (target === "northPolarItems" || target === "polarItems") focusedPolarTargets.north.clear();
        if (target === "southPolarItems" || target === "polarItems") focusedPolarTargets.south.clear();
      }}

      function aliasesVisible(aliases = []) {{
        return aliases.every((alias) => targetVisible(alias));
      }}

      function polarOpacity(entry) {{
        return entry.kind === "line"
          ? threeSettings.polarItems.opacity
          : entry.kind === "dot"
            ? threeSettings.polarItems.starOpacity
            : threeSettings.polarItems.labelOpacity;
      }}

      function transitionDescriptorsForTarget(target) {{
        const nakTarget = resolveNakshatraTarget(target);
        if (nakTarget) {{
          const items = [];
          if (nakTarget.sigil === "$" || nakTarget.sigil === "@") {{
            nakshatraLineRefs.filter((entry) => entry.nid === nakTarget.nid).forEach((entry) => {{
              items.push({{ object: entry.line, opacity: threeSettings.nakshatras.selectedOpacity }});
            }});
          }}
          if (nakTarget.sigil === "*" || nakTarget.sigil === "@") {{
            starGroupRefs.filter((entry) => entry.nid === nakTarget.nid).forEach((entry) => {{
              items.push({{ object: entry.points, opacity: threeSettings.stars.opacity }});
            }});
          }}
          return items.length ? [transitionGroup(items, 0)] : [];
        }}
        if (target === "eclipticGrid") {{
          return [
            ...gridRefs.parallels.map((line, index) => transitionDescriptor(line, threeSettings.grid.parallelOpacity, index)),
            ...gridRefs.meridians.map((line, index) => transitionDescriptor(line, threeSettings.grid.meridianOpacity, index + gridRefs.parallels.length)),
          ];
        }}
        if (target === "equatorialGrid") {{
          return [
            ...gridRefs.equatorialParallels.map((line, index) => transitionDescriptor(line, threeSettings.grid.equatorialOpacity, index)),
            ...gridRefs.equatorialMeridians.map((line, index) => transitionDescriptor(line, threeSettings.grid.equatorialOpacity, index + gridRefs.equatorialParallels.length)),
          ];
        }}
        if (target === "referencePlanes") {{
          return [
            ...(eclipticPlane ? [transitionDescriptor(eclipticPlane, threeSettings.reference.eclipticPlaneOpacity, 0)] : []),
            ...(equatorialPlane ? [transitionDescriptor(equatorialPlane, threeSettings.reference.equatorialPlaneOpacity, 1)] : []),
          ];
        }}
        if (target === "eclipticPlane") {{
          return eclipticPlane ? [transitionDescriptor(eclipticPlane, threeSettings.reference.eclipticPlaneOpacity, 0)] : [];
        }}
        if (target === "equatorialPlane") {{
          return equatorialPlane ? [transitionDescriptor(equatorialPlane, threeSettings.reference.equatorialPlaneOpacity, 0)] : [];
        }}
        if (target === "nsAxis") {{
          return nsAxisLine ? [transitionDescriptor(nsAxisLine, threeSettings.reference.nsAxisOpacity, 0)] : [];
        }}
        if (target === "eclipticBand") {{
          return [
            ...bandRefs.meshes.map((mesh, index) => transitionDescriptor(mesh, threeSettings.ecliptic.bandOpacity, index)),
            ...(eclipticCircle ? [transitionDescriptor(eclipticCircle, threeSettings.ecliptic.circleOpacity, bandRefs.meshes.length)] : []),
          ];
        }}
        if (target === "eclipticDividers") {{
          return bandRefs.dividers.map((line, index) => transitionDescriptor(line, threeSettings.ecliptic.dividerOpacity, index));
        }}
        if (target === "eclipticLabels") {{
          return bandRefs.labels.map((label, index) => transitionDescriptor(label, threeSettings.ecliptic.sectorLabelOpacity, index));
        }}
        if (target === "eclipticPoles") {{
          return [
            ...eclipticPoleDots.map((dot, index) => transitionDescriptor(dot, 1, index)),
            ...eclipticPoleLabels.map((label, index) => transitionDescriptor(label, threeSettings.ecliptic.poleLabelOpacity, index + eclipticPoleDots.length)),
          ];
        }}
        if (target === "NEP" || target === "SEP") {{
          return eclipticPoleRefs
            .filter((entry) => entry.key === target)
            .map((entry, index) => transitionDescriptor(entry.object, entry.kind === "label" ? threeSettings.ecliptic.poleLabelOpacity : 1, index));
        }}
        if (target === "eclipticNakSegments") {{
          return [
            ...transitionDescriptorsForTarget("eclipticBand"),
            ...transitionDescriptorsForTarget("eclipticDividers"),
            ...transitionDescriptorsForTarget("eclipticLabels"),
            ...transitionDescriptorsForTarget("eclipticPoles"),
          ];
        }}
        if (target === "stars") {{
          return starGroupRefs
            .map((entry) => transitionDescriptor(entry.points, threeSettings.stars.opacity, entry.metaIndex ?? 0))
            .sort((a, b) => a.order - b.order);
        }}
        if (target === "nakshatraStars") {{
          return starGroupRefs
            .filter((entry) => entry.nid !== "__special__")
            .map((entry) => transitionDescriptor(entry.points, threeSettings.stars.opacity, entry.metaIndex ?? 0))
            .sort((a, b) => a.order - b.order);
        }}
        if (target === "nakshatraLines") {{
          return nakshatraLineRefs
            .map((entry) => transitionDescriptor(entry.line, threeSettings.nakshatras.opacity, entry.metaIndex ?? 0))
            .sort((a, b) => a.order - b.order);
        }}
        if (target === "nakshatraLabels") {{
          return nakshatraLabelRefs
            .map((entry) => transitionDescriptor(entry.sprite, threeSettings.nakshatras.labelOpacity, entry.metaIndex ?? 0))
            .sort((a, b) => a.order - b.order);
        }}
        if (target === "nakshatras") {{
          const grouped = new Map();
          nakshatraLineRefs.forEach((entry) => {{
            const orderKey = entry.metaIndex ?? 0;
            if (!grouped.has(orderKey)) grouped.set(orderKey, []);
            grouped.get(orderKey).push({{ object: entry.line, opacity: threeSettings.nakshatras.opacity }});
          }});
          nakshatraLabelRefs.forEach((entry) => {{
            const orderKey = entry.metaIndex ?? 0;
            if (!grouped.has(orderKey)) grouped.set(orderKey, []);
            grouped.get(orderKey).push({{ object: entry.sprite, opacity: threeSettings.nakshatras.labelOpacity }});
          }});
          return Array.from(grouped.entries())
            .sort(([a], [b]) => a - b)
            .map(([orderKey, items]) => transitionGroup(items, orderKey));
        }}
        if (target === "polarItems") {{
          return polarItemRefs.map((entry, index) => {{
            return transitionDescriptor(entry.object, polarOpacity(entry), index);
          }});
        }}
        if (target === "northPolarItems" || target === "southPolarItems") {{
          const region = target === "northPolarItems" ? "north" : "south";
          return polarItemRefs.filter((entry) => entry.region === region).map((entry, index) => {{
            return transitionDescriptor(entry.object, polarOpacity(entry), index);
          }});
        }}
        const polarMatches = polarItemRefs.filter((entry) => (entry.aliases || []).includes(target));
        if (polarMatches.length) {{
          return polarMatches.map((entry, index) => transitionDescriptor(entry.object, polarOpacity(entry), index));
        }}
        if (target === "poleTrack") {{
          return [
            ...(poleTrackCircle ? [transitionDescriptor(poleTrackCircle, threeSettings.poleTrack.opacity, 0)] : []),
            ...(poleTrackArc ? [transitionDescriptor(poleTrackArc, threeSettings.poleTrack.arcOpacity, 1)] : []),
            ...(poleTrackLabel ? [transitionDescriptor(poleTrackLabel, threeSettings.poleTrack.trackLabelOpacity, 2)] : []),
          ];
        }}
        if (target === "precessionCircle") {{
          return poleTrackCircle ? [transitionDescriptor(poleTrackCircle, threeSettings.poleTrack.opacity, 0)] : [];
        }}
        if (target === "seasonalFrame") {{
          return [
            ...(equatorLine ? [transitionDescriptor(equatorLine, threeSettings.seasonal.equatorOpacity, 0)] : []),
            ...(poleDot ? [transitionDescriptor(poleDot, 1, 1)] : []),
            ...(movingPoleLabel ? [transitionDescriptor(movingPoleLabel, threeSettings.poleTrack.movingPoleLabelOpacity, 2)] : []),
            ...seasonalMarkerRefs.flatMap((entry, index) => [
              transitionDescriptor(entry.mesh, 1, index + 3),
              transitionDescriptor(entry.sprite, threeSettings.seasonal.markerLabelOpacity, index + 3.1),
            ]),
          ];
        }}
        if (target === "equator") {{
          return equatorLine ? [transitionDescriptor(equatorLine, threeSettings.seasonal.equatorOpacity, 0)] : [];
        }}
        if (["VE", "SS", "AE", "WS"].includes(target)) {{
          return seasonalMarkerRefs
            .filter((entry) => entry.key === target)
            .flatMap((entry) => [
              transitionDescriptor(entry.mesh, 1, 0),
              transitionDescriptor(entry.sprite, threeSettings.seasonal.markerLabelOpacity, 1),
            ]);
        }}
        if (target === "NP") {{
          return [
            ...(poleDot ? [transitionDescriptor(poleDot, 1, 0)] : []),
            ...(movingPoleLabel ? [transitionDescriptor(movingPoleLabel, threeSettings.poleTrack.movingPoleLabelOpacity, 1)] : []),
          ];
        }}
        if (target === "SP") {{
          return [
            ...(southPoleDot ? [transitionDescriptor(southPoleDot, 1, 0)] : []),
            ...(southPoleLabel ? [transitionDescriptor(southPoleLabel, threeSettings.poleTrack.movingPoleLabelOpacity, 1)] : []),
          ];
        }}
        return [];
      }}

      function setOverlayTransition(visible, progress) {{
        if (!overlayLabel?.parentElement) return;
        overlayLabel.parentElement.style.display = visible || progress > 0 ? "" : "none";
        overlayLabel.parentElement.style.opacity = String((threeSettings.overlay.opacity ?? 1) * progress);
      }}

      function finalizeTransition(target, visible, descriptors = null, hasPatch = false) {{
        activeTransitionTargets.delete(target);
        if (descriptors) markTransitionObjects(descriptors, false);
        if (polarMatchesForTarget(target).length) setFocusedPolarTarget(target, visible);
        clearFocusedPolarTarget(target);
        setFocusedSeasonalTarget(target, visible);
        clearFocusedSeasonalTarget(target);
        targetVisibilityOverrides.set(target, visible);
        const patch = transitionPatchForTarget(target, visible);
        if (patch) mergeSettings(threeSettings, patch);
        applyThreeSettings({{ preserveEpoch: true, preserveCamera: true }});
        syncDebugTextareaFromLive();
      }}

      function runTransitionCue(cue, visible) {{
        const target = cue.target;
        const patch = transitionPatchForTarget(target, visible);
        const defaults = transitionDefaults[target] || transitionDefaults.default;
        const mode = cue.mode || defaults.mode;
        const duration = Number(cue.duration ?? defaults.duration);
        const order = cue.order || defaults.order;
        const direction = cue.direction || (visible ? "forward" : "reverse");
        if (visible && polarMatchesForTarget(target).length) setFocusedPolarTarget(target, true);
        if (visible) clearFocusedPolarTarget(target);
        if (visible) setFocusedSeasonalTarget(target, true);
        if (visible) clearFocusedSeasonalTarget(target);
        activeTransitionTargets.add(target);

        if (target === "overlay") {{
          mergeSettings(threeSettings, patch);
          const steps = mode === "instant" ? 1 : 12;
          for (let step = 0; step <= steps; step += 1) {{
            const delay = steps === 1 ? 0 : (duration * step) / steps;
            activeStoryTimers.push(window.setTimeout(() => {{
              const t = steps === 1 ? 1 : step / steps;
              setOverlayTransition(visible, visible ? t : 1 - t);
              if (step === steps) finalizeTransition(target, visible);
            }}, delay));
          }}
          return;
        }}

        let descriptors = transitionDescriptorsForTarget(target);
        if (!patch && descriptors.length === 0) {{
          activeTransitionTargets.delete(target);
          return;
        }}
        if (direction === "reverse" || order === "reverse-ecliptic") descriptors = descriptors.slice().reverse();
        if (mode === "instant" || descriptors.length === 0) {{
          finalizeTransition(target, visible);
          return;
        }}
        markTransitionObjects(descriptors, true);

        if (visible) {{
          if (patch) mergeSettings(threeSettings, patch);
          applyThreeSettings({{ preserveEpoch: true, preserveCamera: true }});
          descriptors.forEach((entry) => {{
            setTransitionEntryVisible(entry, false);
            setTransitionEntryOpacity(entry, 0);
          }});
        }}

        if (mode === "fade") {{
          const steps = 12;
          descriptors.forEach((entry) => setTransitionEntryVisible(entry, true));
          for (let step = 0; step <= steps; step += 1) {{
            const delay = (duration * step) / steps;
            activeStoryTimers.push(window.setTimeout(() => {{
              const t = step / steps;
              descriptors.forEach((entry) => {{
                const progress = visible ? t : 1 - t;
                setTransitionEntryVisible(entry, progress > 0);
                setTransitionEntryOpacity(entry, progress);
              }});
              if (step === steps) finalizeTransition(target, visible, descriptors);
            }}, delay));
          }}
          return;
        }}

        const staggerSpan = Math.max(0, duration * 0.85);
        const denominator = Math.max(1, descriptors.length - 1);
        descriptors.forEach((entry, index) => {{
          const delay = (staggerSpan * index) / denominator;
          activeStoryTimers.push(window.setTimeout(() => {{
            setTransitionEntryVisible(entry, visible);
            setTransitionEntryOpacity(entry, visible ? 1 : 0);
          }}, delay));
        }});
        activeStoryTimers.push(window.setTimeout(() => finalizeTransition(target, visible, descriptors), duration));
      }}

      function resolveCueTime(token, previousEnd) {{
        if (typeof token === "number") return Math.max(0, token);
        if (typeof token === "string") {{
          const trimmed = token.trim();
          const value = Number(trimmed);
          if (!Number.isFinite(value)) {{
            throw new Error(`Invalid cue time: ${{token}}`);
          }}
          return /^[+-]/.test(trimmed) ? Math.max(0, previousEnd + value) : Math.max(0, value);
        }}
        return previousEnd;
      }}

      function cueDurationForScheduling(cue) {{
        if (Object.prototype.hasOwnProperty.call(cue, "duration")) {{
          const duration = Number(cue.duration);
          return Number.isFinite(duration) ? duration : 0;
        }}
        if (cue.action === "caption") return 1200;
        if (cue.action === "camera") return 1000;
        if (cue.action === "epochTravel") return 5000;
        if (cue.action === "flash") return 900;
        if (cue.action === "reveal" || cue.action === "hide") {{
          const defaults = transitionDefaults[cue.target] || transitionDefaults.default;
          return defaults.duration || 0;
        }}
        return 0;
      }}

      function normalizeStoryCues(story) {{
        const source = story?.cues || [];
        const rawCues = Array.isArray(source)
          ? source
          : Object.entries(source).map(([at, cue]) => ({{ ...(cue || {{}}), at }}));
        let previousEnd = 0;
        return rawCues.map((cue) => {{
          const token = Object.prototype.hasOwnProperty.call(cue, "at")
            ? cue.at
            : Object.prototype.hasOwnProperty.call(cue, "after")
              ? `+${{cue.after}}`
              : "+0";
          const scheduledAt = resolveCueTime(token, previousEnd);
          const duration = cueDurationForScheduling(cue);
          previousEnd = Math.max(previousEnd, scheduledAt + Math.max(0, duration));
          return {{ ...cue, _scheduledAt: scheduledAt }};
        }});
      }}

      function runStory(story) {{
        if (!story) return;
        if (!scene) initThree();
        stopStory();
        activeStoryId = story.id;
        if (storyStrip) {{
          storyStrip.querySelectorAll(".three-story-pill").forEach((button) => {{
            button.classList.toggle("active", button.dataset.storyId === story.id);
          }});
        }}
        if (story.initial) {{
          applyStoryState(cloneSettings(story.initial));
        }}
        normalizeStoryCues(story).forEach((cue) => {{
          const timer = window.setTimeout(() => {{
            if (activeStoryId !== story.id) return;
            if (cue.action === "caption") runCaptionCue(cue);
            if (cue.action === "set") applyStoryState(cue.state);
            if (cue.action === "reveal") runTransitionCue(cue, true);
            if (cue.action === "hide") runTransitionCue(cue, false);
            if (cue.action === "camera") runCameraCue(cue);
            if (cue.action === "epochTravel") runEpochTravelCue(cue);
            if (cue.action === "flash") runFlashCue(cue);
            if (cue.action === "fullscreen") setThreeFullscreen(true);
            if (cue.action === "exitFullscreen") setThreeFullscreen(false);
          }}, cue._scheduledAt);
          activeStoryTimers.push(timer);
        }});
        syncStoryControls();
      }}

      function storySearchText(story) {{
        return [
          story.id,
          story.title,
          story.group,
          ...(Array.isArray(story.tags) ? story.tags : []),
        ].filter(Boolean).join(" ").toLowerCase();
      }}

      function filteredStories() {{
        const query = (threeStorySearch?.value || "").trim().toLowerCase();
        const sorted = stories.slice().sort((a, b) => {{
          const ao = Number.isFinite(Number(a.order)) ? Number(a.order) : 9999;
          const bo = Number.isFinite(Number(b.order)) ? Number(b.order) : 9999;
          return ao - bo || String(a.title).localeCompare(String(b.title));
        }});
        if (!query) return sorted;
        return sorted.filter((story) => storySearchText(story).includes(query));
      }}

      function storyById(id) {{
        return stories.find((story) => story.id === id) || null;
      }}

      function renderStoryPills() {{
        if (!storyStrip) return;
        const featured = filteredStories().filter((story) => story.featured).slice(0, 5);
        storyStrip.innerHTML = featured.map((story) => `
          <button class="three-story-pill" type="button" data-story-id="${{story.id}}">${{story.title}}</button>
        `).join("");
        storyStrip.querySelectorAll(".three-story-pill").forEach((button) => {{
          button.addEventListener("click", () => {{
            const story = stories.find((item) => item.id === button.dataset.storyId);
            if (story && threeStorySelect) threeStorySelect.value = story.id;
            loadStoryIntoEditors(story);
            runStory(story);
            syncStoryControls();
          }});
        }});
      }}

      function storyVysuSource(story) {{
        return story?.vysu || defaultVyomaSutra;
      }}

      function loadStoryIntoEditors(story) {{
        if (!story) return;
        if (threeStoryEditor) threeStoryEditor.value = JSON.stringify(story, null, 2);
        if (threeVysuEditor) threeVysuEditor.value = storyVysuSource(story);
      }}

      function renderStoryEditorOptions() {{
        if (!threeStorySelect || !threeStoryEditor) return;
        const options = filteredStories();
        const previousValue = threeStorySelect.value;
        threeStorySelect.innerHTML = options.map((story) => `
          <option value="${{story.id}}">${{story.title}}</option>
        `).join("");
        const selected = options.find((story) => story.id === previousValue) || options[0] || null;
        if (selected) {{
          threeStorySelect.value = selected.id;
          loadStoryIntoEditors(selected);
          const shown = options.length === stories.length ? `${{stories.length}} story source(s).` : `${{options.length}} of ${{stories.length}} story source(s).`;
          setStoryStatus(shown);
        }} else {{
          threeStoryEditor.value = "";
          if (threeVysuEditor && !threeVysuEditor.value.trim()) threeVysuEditor.value = defaultVyomaSutra;
          setStoryStatus("No build-time stories found.");
        }}
        syncStoryControls();
      }}

      function selectedStoryOriginal() {{
        if (!threeStorySelect) return stories[0] || null;
        return stories.find((story) => story.id === threeStorySelect.value) || stories[0] || null;
      }}

      function storyCueList(story) {{
        const source = story?.cues || [];
        return Array.isArray(source)
          ? source.map((cue, index) => [index, cue])
          : Object.entries(source).map(([at, cue]) => [at, {{ ...(cue || {{}}), at }}]);
      }}

      function validateStoryForEditor(story) {{
        const validActions = new Set(["caption", "set", "reveal", "hide", "camera", "epochTravel", "flash", "fullscreen", "exitFullscreen"]);
        storyCueList(story).forEach(([index, cue]) => {{
          if (!cue || typeof cue !== "object" || Array.isArray(cue)) {{
            throw new Error(`Cue ${{index}} must be an object.`);
          }}
          if (!cue.action) {{
            throw new Error(`Cue ${{index}} is missing action. Camera cues need "action": "camera".`);
          }}
          if (!validActions.has(cue.action)) {{
            throw new Error(`Cue ${{index}} has unknown action "${{cue.action}}".`);
          }}
          if (cue.action === "caption" && !Object.prototype.hasOwnProperty.call(cue, "text")) {{
            throw new Error(`Cue ${{index}} caption needs text.`);
          }}
          if (cue.action === "set" && !cue.state) {{
            throw new Error(`Cue ${{index}} set needs state.`);
          }}
          if ((cue.action === "reveal" || cue.action === "hide") && !cue.target) {{
            throw new Error(`Cue ${{index}} ${{cue.action}} needs target.`);
          }}
          if (cue.action === "flash" && !cue.target) {{
            throw new Error(`Cue ${{index}} flash needs target.`);
          }}
          if (cue.action === "camera" && !cue.camera && !cue.state?.camera) {{
            throw new Error(`Cue ${{index}} camera needs camera.`);
          }}
          if (cue.action === "epochTravel") {{
            ["from", "to", "duration"].forEach((key) => {{
              if (!Object.prototype.hasOwnProperty.call(cue, key)) {{
                throw new Error(`Cue ${{index}} epochTravel needs ${{key}}.`);
              }}
            }});
          }}
        }});
      }}

      function storyFromEditor() {{
        if (!threeStoryEditor) return null;
        const parsed = JSON.parse(threeStoryEditor.value);
        if (!parsed || typeof parsed !== "object" || Array.isArray(parsed)) {{
          throw new Error("Story JSON must be an object.");
        }}
        if (!parsed.id || !parsed.title || (!Array.isArray(parsed.cues) && (!parsed.cues || typeof parsed.cues !== "object"))) {{
          throw new Error("Story needs id, title, and cues.");
        }}
        validateStoryForEditor(parsed);
        return parsed;
      }}

      function setDockTab(tabName) {{
        threeDockTabs.forEach((button) => {{
          button.classList.toggle("active", button.dataset.dockTab === tabName);
        }});
        Object.entries(threeDockPanels).forEach(([name, panel]) => {{
          if (panel) panel.classList.toggle("active", name === tabName);
        }});
      }}

      function captureThreeSettings() {{
        if (!camera || !controls) return cloneSettings(threeSettings);
        return {{
          ...cloneSettings(threeSettings),
          epochYear: data.epochs[window.explorerState?.epochIndex ?? 0]?.year ?? threeSettings.epochYear,
          camera: {{
            ...cloneSettings(threeSettings).camera,
            position: {{
              x: Number(camera.position.x.toFixed(3)),
              y: Number(camera.position.y.toFixed(3)),
              z: Number(camera.position.z.toFixed(3)),
            }},
            target: {{
              x: Number(controls.target.x.toFixed(3)),
              y: Number(controls.target.y.toFixed(3)),
              z: Number(controls.target.z.toFixed(3)),
            }},
            fov: Number(camera.fov.toFixed(3)),
            minDistance: Number(controls.minDistance.toFixed(3)),
            maxDistance: Number(controls.maxDistance.toFixed(3)),
          }},
        }};
      }}

      function syncDebugTextareaFromLive() {{
        if (threeDebugJson) {{
          threeDebugJson.value = JSON.stringify(captureThreeSettings(), null, 2);
        }}
      }}

      function renderThreeDebugToggles() {{
        if (!threeDebugToggles) return;
        threeDebugToggles.innerHTML = threeDebugUiFields
          .map(([key, label]) => `
            <label class="three-debug-flag">
              <input type="checkbox" data-ui-flag="${{key}}">
              <span>${{label}}</span>
            </label>
          `)
          .join("");
        threeDebugToggles.querySelectorAll("input[data-ui-flag]").forEach((input) => {{
          input.addEventListener("change", () => {{
            const key = input.getAttribute("data-ui-flag");
            threeSettings.ui[key] = input.checked;
            applyThreeSettings({{ preserveEpoch: true, preserveCamera: true }});
            syncDebugTextareaFromLive();
            setDebugStatus(`${{input.checked ? "Show" : "Hide"}}: ${{key}}`);
          }});
        }});
      }}

      function syncThreeDebugTogglesFromSettings() {{
        if (!threeDebugToggles) return;
        threeDebugUiFields.forEach(([key]) => {{
          const input = threeDebugToggles.querySelector(`input[data-ui-flag="${{key}}"]`);
          if (input) input.checked = threeSettings.ui[key] !== false;
        }});
      }}

      function applyLightPreset() {{
        if (!scene) return;
        const preset = threeSettings.lightPreset || "night";
        const background = preset === "day" ? 0xdfe8f2 : preset === "twilight" ? 0x1b2436 : 0x080810;
        scene.background = new THREE.Color(background);
      }}

      function applyThreeSettings(options = {{}}) {{
        if (!scene || !camera || !controls) return;
        const preserveEpoch = options.preserveEpoch === true;
        const preserveCamera = options.preserveCamera === true;
        if (!preserveEpoch && typeof threeSettings.epochYear === "number" && window.explorerState && typeof window.explorerRender === "function") {{
          let bestIndex = 0;
          let bestDistance = Number.POSITIVE_INFINITY;
          data.epochs.forEach((epoch, index) => {{
            const distance = Math.abs(epoch.year - threeSettings.epochYear);
            if (distance < bestDistance) {{
              bestDistance = distance;
              bestIndex = index;
            }}
          }});
          window.explorerState.epochIndex = bestIndex;
          window.explorerRender();
        }}
        if (!preserveCamera) {{
          camera.fov = threeSettings.camera.fov;
          camera.position.set(
            threeSettings.camera.position.x,
            threeSettings.camera.position.y,
            threeSettings.camera.position.z
          );
          camera.updateProjectionMatrix();
          controls.target.set(
            threeSettings.camera.target.x,
            threeSettings.camera.target.y,
            threeSettings.camera.target.z
          );
          controls.minDistance = threeSettings.camera.minDistance;
          controls.maxDistance = threeSettings.camera.maxDistance;
        }}
        applyOrbitMode();
        applyLightPreset();
        if (siderealGroup && builtEclipticGridStep !== gridStep(threeSettings.grid.eclipticStepDeg)) {{
          buildSphereGrid();
        }}
        if (seasonalGroup && builtEquatorialGridStep !== gridStep(threeSettings.grid.equatorialStepDeg)) {{
          buildEquatorialGrid();
        }}

        gridRefs.parallels.forEach((line) => {{
          if (activeTransitionObjects.has(line)) return;
          line.material.color.set(threeSettings.grid.parallelColor);
          line.material.opacity = threeSettings.grid.parallelOpacity;
        }});
        gridRefs.meridians.forEach((line) => {{
          if (activeTransitionObjects.has(line)) return;
          line.material.color.set(threeSettings.grid.meridianColor);
          line.material.opacity = threeSettings.grid.meridianOpacity;
        }});
        gridRefs.equatorialParallels.forEach((line) => {{
          if (activeTransitionObjects.has(line)) return;
          line.material.color.set(threeSettings.grid.equatorialColor);
          line.material.opacity = threeSettings.grid.equatorialOpacity;
        }});
        gridRefs.equatorialMeridians.forEach((line) => {{
          if (activeTransitionObjects.has(line)) return;
          line.material.color.set(threeSettings.grid.equatorialColor);
          line.material.opacity = threeSettings.grid.equatorialOpacity;
        }});

        if (eclipticPlane) {{
          eclipticPlane.visible = threeSettings.ui.showReferencePlanes && threeSettings.ui.showEclipticPlane !== false;
          eclipticPlane.material.color.set(threeSettings.reference.eclipticPlaneColor);
          eclipticPlane.material.opacity = threeSettings.reference.eclipticPlaneOpacity;
        }}
        if (equatorialPlane) {{
          equatorialPlane.visible = threeSettings.ui.showReferencePlanes && threeSettings.ui.showEquatorialPlane !== false;
          equatorialPlane.material.color.set(threeSettings.reference.equatorialPlaneColor);
          equatorialPlane.material.opacity = threeSettings.reference.equatorialPlaneOpacity;
        }}
        if (nsAxisLine) {{
          nsAxisLine.visible = threeSettings.ui.showNsAxis;
          nsAxisLine.material.color.set(threeSettings.reference.nsAxisColor);
          nsAxisLine.material.opacity = threeSettings.reference.nsAxisOpacity;
        }}

        bandRefs.meshes.forEach((mesh) => {{
          if (activeTransitionObjects.has(mesh)) return;
          mesh.visible = threeSettings.ui.showEclipticBand;
          mesh.material.opacity = threeSettings.ecliptic.bandOpacity;
        }});
        bandRefs.dividers.forEach((line) => {{
          if (activeTransitionObjects.has(line)) return;
          line.visible = threeSettings.ui.showEclipticDividers;
          line.material.opacity = threeSettings.ecliptic.dividerOpacity;
        }});
        bandRefs.labels.forEach((label) => {{
          if (activeTransitionObjects.has(label)) return;
          label.visible = threeSettings.ui.showEclipticLabels;
          label.material.opacity = threeSettings.ecliptic.sectorLabelOpacity;
          setSpriteHeight(label, threeSettings.ecliptic.sectorLabelSize);
        }});
        eclipticPoleLabels.forEach((label) => {{
          if (activeTransitionObjects.has(label)) return;
          const isSep = label.name === "SEP";
          label.visible = threeSettings.ui.showEclipticPoles && (isSep ? threeSettings.ui.showSEP !== false : threeSettings.ui.showNEP !== false);
          label.material.opacity = threeSettings.ecliptic.poleLabelOpacity;
          setSpriteHeight(label, threeSettings.ecliptic.poleLabelSize);
        }});
        eclipticPoleDots.forEach((dot) => {{
          if (activeTransitionObjects.has(dot)) return;
          const isSep = dot.name === "SEP";
          dot.visible = threeSettings.ui.showEclipticPoles && (isSep ? threeSettings.ui.showSEP !== false : threeSettings.ui.showNEP !== false);
        }});
        if (eclipticCircle) {{
          if (!activeTransitionObjects.has(eclipticCircle)) {{
            eclipticCircle.visible = threeSettings.ui.showEclipticBand;
            eclipticCircle.material.color.set(threeSettings.ecliptic.circleColor);
            eclipticCircle.material.opacity = threeSettings.ecliptic.circleOpacity;
          }}
        }}

        starGroupRefs.forEach((entry) => {{
          if (activeTransitionObjects.has(entry.points)) return;
          entry.points.visible = threeSettings.ui.showStars;
          entry.points.material.size = threeSettings.stars.size;
          entry.points.material.opacity = threeSettings.stars.opacity;
        }});

        if (poleTrackCircle) {{
          poleTrackCircle.visible = threeSettings.ui.showPoleTrack;
          poleTrackCircle.material.color.set(threeSettings.poleTrack.color);
          poleTrackCircle.material.opacity = threeSettings.poleTrack.opacity;
        }}
        if (poleTrackArc) {{
          poleTrackArc.visible = threeSettings.ui.showPoleTrack;
          poleTrackArc.material.color.set(threeSettings.poleTrack.arcColor);
          poleTrackArc.material.opacity = threeSettings.poleTrack.arcOpacity;
        }}
        if (poleTrackLabel) {{
          poleTrackLabel.visible = threeSettings.ui.showPoleTrack;
          poleTrackLabel.material.opacity = threeSettings.poleTrack.trackLabelOpacity;
          setSpriteHeight(poleTrackLabel, threeSettings.poleTrack.trackLabelSize);
        }}
        if (poleDot) {{
          poleDot.visible = threeSettings.ui.showSeasonalFrame && threeSettings.ui.showNP !== false && seasonalTargetVisible("NP");
          poleDot.material.color.set(threeSettings.poleTrack.dotColor);
        }}
        if (movingPoleLabel) {{
          movingPoleLabel.visible = threeSettings.ui.showSeasonalFrame && threeSettings.ui.showNP !== false && seasonalTargetVisible("NP");
          movingPoleLabel.material.opacity = threeSettings.poleTrack.movingPoleLabelOpacity;
          setSpriteHeight(movingPoleLabel, threeSettings.poleTrack.movingPoleLabelSize);
        }}
        if (southPoleDot) {{
          southPoleDot.visible = threeSettings.ui.showSeasonalFrame && threeSettings.ui.showSP !== false && seasonalTargetVisible("SP");
          southPoleDot.material.color.set(threeSettings.poleTrack.dotColor);
        }}
        if (southPoleLabel) {{
          southPoleLabel.visible = threeSettings.ui.showSeasonalFrame && threeSettings.ui.showSP !== false && seasonalTargetVisible("SP");
          southPoleLabel.material.opacity = threeSettings.poleTrack.movingPoleLabelOpacity * 0.72;
          setSpriteHeight(southPoleLabel, threeSettings.poleTrack.movingPoleLabelSize * 0.9);
        }}
        if (equatorLine) {{
          equatorLine.visible = threeSettings.ui.showSeasonalFrame && seasonalTargetVisible("equator");
          equatorLine.material.color.set(threeSettings.seasonal.equatorColor);
          equatorLine.material.opacity = threeSettings.seasonal.equatorOpacity;
        }}
        seasonalMarkerRefs.forEach((entry) => {{
          const markerVisible = threeSettings.ui.showSeasonalFrame && seasonalTargetVisible(entry.key);
          entry.mesh.visible = markerVisible;
          entry.sprite.visible = markerVisible;
          entry.mesh.scale.setScalar(threeSettings.seasonal.markerScale);
          entry.sprite.material.opacity = threeSettings.seasonal.markerLabelOpacity;
          setSpriteHeight(entry.sprite, threeSettings.seasonal.markerLabelSize * threeSettings.seasonal.markerScale);
        }});

        gridRefs.parallels.forEach((line) => {{ if (!activeTransitionObjects.has(line)) line.visible = threeSettings.ui.showGrid; }});
        gridRefs.meridians.forEach((line) => {{ if (!activeTransitionObjects.has(line)) line.visible = threeSettings.ui.showGrid; }});
        gridRefs.equatorialParallels.forEach((line) => {{ if (!activeTransitionObjects.has(line)) line.visible = threeSettings.ui.showEquatorialGrid; }});
        gridRefs.equatorialMeridians.forEach((line) => {{ if (!activeTransitionObjects.has(line)) line.visible = threeSettings.ui.showEquatorialGrid; }});
        if (overlayLabel) {{
          overlayLabel.parentElement.style.display = threeSettings.ui.showOverlay ? "" : "none";
          overlayLabel.parentElement.style.fontSize = `${{threeSettings.overlay.fontSizeRem}}rem`;
          overlayLabel.parentElement.style.opacity = String(threeSettings.overlay.opacity);
        }}

        syncThreeDebugTogglesFromSettings();
        updateThreeState();
      }}

      function updateThreeState() {{
        if (!window.explorerState) return;
        const st = window.explorerState;
        const transitioningNakshatras = activeTransitionTargets.has("nakshatras");
        if (!transitioningNakshatras && !activeTransitionTargets.has("nakshatraLines")) {{
          nakshatraLineRefs.forEach((entry) => {{
            if (activeTransitionObjects.has(entry.line)) return;
            const active = entry.metaIndex === st.selectedMetaIndex;
            const visible = threeSettings.ui.showNakshatraLines && st.visibleNakshatras[entry.nid] !== false;
            entry.line.visible = visible;
            entry.line.material.color.set(active ? threeSettings.nakshatras.selectedColor : threeSettings.nakshatras.color);
            entry.line.material.opacity = visible ? (active ? threeSettings.nakshatras.selectedOpacity : threeSettings.nakshatras.opacity) : 0;
          }});
        }}
        if (!transitioningNakshatras && !activeTransitionTargets.has("nakshatraLabels")) {{
          nakshatraLabelRefs.forEach((entry) => {{
            if (activeTransitionObjects.has(entry.sprite)) return;
            const visible = threeSettings.ui.showNakshatraLabels && st.visibleNakshatras[entry.nid] !== false;
            entry.sprite.visible = visible;
            entry.sprite.material.opacity = visible ? threeSettings.nakshatras.labelOpacity : 0;
            setSpriteHeight(entry.sprite, threeSettings.nakshatras.labelSize);
          }});
        }}
        if (!activeTransitionTargets.has("stars") && !activeTransitionTargets.has("nakshatraStars")) {{
          starGroupRefs.forEach((entry) => {{
            if (activeTransitionObjects.has(entry.points)) return;
            const visible = entry.nid === "__special__"
              ? threeSettings.ui.showStars
              : (threeSettings.ui.showStars || threeSettings.ui.showNakshatraStars) && st.visibleNakshatras[entry.nid] !== false;
            entry.points.visible = visible;
            entry.points.material.opacity = visible ? threeSettings.stars.opacity : 0;
          }});
        }}
        polarItemRefs.forEach((entry) => {{
          const regionVisible = entry.region === "south"
            ? threeSettings.ui.showSouthPolarItems !== false
            : threeSettings.ui.showNorthPolarItems !== false;
          const visible = threeSettings.ui.showPolarItems && regionVisible && focusedPolarVisible(entry) && aliasesVisible(entry.aliases) && st.visibleCodex[entry.id] !== false;
          entry.object.visible = visible;
          if (entry.object.material) {{
            if (entry.kind === "line") entry.object.material.opacity = threeSettings.polarItems.opacity;
            if (entry.kind === "dot") entry.object.material.opacity = threeSettings.polarItems.starOpacity;
            if (entry.kind === "label") {{
              entry.object.material.opacity = threeSettings.polarItems.labelOpacity;
              setSpriteHeight(entry.object, threeSettings.polarItems.labelSize);
            }}
          }}
        }});
        syncLayerButtons();
        syncSceneButtons();
      }}

      /* ── init ────────────────────────────────────────────── */
      function initThree() {{
        scene = new THREE.Scene();
        applyLightPreset();

        camera = new THREE.PerspectiveCamera(
          threeSettings.camera.fov, container.clientWidth / container.clientHeight, 1, 2000
        );
        camera.position.set(
          threeSettings.camera.position.x,
          threeSettings.camera.position.y,
          threeSettings.camera.position.z
        );

        renderer = new THREE.WebGLRenderer({{ antialias: true, alpha: false }});
        renderer.setSize(container.clientWidth, container.clientHeight);
        renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
        container.appendChild(renderer.domElement);

        controls = new OrbitControls(camera, renderer.domElement);
        controls.enableDamping = true;
        controls.dampingFactor = 0.06;
        controls.target.set(
          threeSettings.camera.target.x,
          threeSettings.camera.target.y,
          threeSettings.camera.target.z
        );
        controls.minDistance = threeSettings.camera.minDistance;
        controls.maxDistance = threeSettings.camera.maxDistance;
        controls.enablePan = false;
        applyOrbitMode();

        siderealGroup = new THREE.Group();
        scene.add(siderealGroup);
        seasonalGroup = new THREE.Group();
        scene.add(seasonalGroup);

        buildSphereGrid();
        buildEquatorialGrid();
        buildReferencePrimitives();
        buildEclipticBand();
        buildEclipticCircle();
        buildStars();
        buildNakshatraLines();
        buildNakshatraLabels();
        buildCodexFigures();
        buildSpecialStars();
        buildPoleTrack();
        buildSeasonalFrame();
        applyThreeSettings();
        syncDebugTextareaFromLive();

        window.addEventListener('resize', onResize);
        animate();
      }}

      /* ── A1. Sphere wireframe ───────────────────────────── */
      function buildSphereGrid() {{
        removeObjects(gridRefs.parallels, siderealGroup);
        removeObjects(gridRefs.meridians, siderealGroup);
        const parMat = new THREE.LineBasicMaterial({{ color: new THREE.Color(threeSettings.grid.parallelColor), transparent: true, opacity: threeSettings.grid.parallelOpacity }});
        const merMat = new THREE.LineBasicMaterial({{ color: new THREE.Color(threeSettings.grid.meridianColor), transparent: true, opacity: threeSettings.grid.meridianOpacity }});
        const step = gridStep(threeSettings.grid.eclipticStepDeg);
        builtEclipticGridStep = step;
        for (let lat = -90 + step; lat < 90; lat += step) {{
          if (lat === 0) continue;
          const g = new THREE.BufferGeometry().setFromPoints(circlePoints(lat, R * 0.995, 72));
          const line = new THREE.Line(g, parMat.clone());
          gridRefs.parallels.push(line);
          siderealGroup.add(line);
        }}
        for (let lon = 0; lon < 360; lon += step) {{
          const g = new THREE.BufferGeometry().setFromPoints(meridianPoints(lon, R * 0.995, 72));
          const line = new THREE.Line(g, merMat.clone());
          gridRefs.meridians.push(line);
          siderealGroup.add(line);
        }}
        if (eclipticPoleDots.length > 0) return;
        // ecliptic poles
        const poleMat = new THREE.MeshBasicMaterial({{ color: 0x8899aa }});
        const poleGeom = new THREE.SphereGeometry(1.2, 8, 8);
        const nep = new THREE.Mesh(poleGeom, poleMat);
        nep.name = 'NEP';
        nep.position.copy(toCart(0, 90, R * 0.995));
        eclipticPoleDots.push(nep);
        eclipticPoleRefs.push({{ key: 'NEP', kind: 'dot', object: nep }});
        siderealGroup.add(nep);
        const sep = new THREE.Mesh(poleGeom.clone(), poleMat);
        sep.name = 'SEP';
        sep.position.copy(toCart(0, -90, R * 0.995));
        eclipticPoleDots.push(sep);
        eclipticPoleRefs.push({{ key: 'SEP', kind: 'dot', object: sep }});
        siderealGroup.add(sep);
        const nepLabel = makeTextSprite('NEP', {{ color: '#8899aa', fontSize: 36, size: 7.0, opacity: 0.6 }});
        nepLabel.name = 'NEP';
        nepLabel.position.copy(toCart(15, 85, R * 1.04));
        eclipticPoleLabels.push(nepLabel);
        eclipticPoleRefs.push({{ key: 'NEP', kind: 'label', object: nepLabel }});
        siderealGroup.add(nepLabel);
        const sepLabel = makeTextSprite('SEP', {{ color: '#8899aa', fontSize: 36, size: 7.0, opacity: 0.6 }});
        sepLabel.name = 'SEP';
        sepLabel.position.copy(toCart(15, -85, R * 1.04));
        eclipticPoleLabels.push(sepLabel);
        eclipticPoleRefs.push({{ key: 'SEP', kind: 'label', object: sepLabel }});
        siderealGroup.add(sepLabel);
      }}

      function buildEquatorialGrid() {{
        removeObjects(gridRefs.equatorialParallels, seasonalGroup);
        removeObjects(gridRefs.equatorialMeridians, seasonalGroup);
        const mat = new THREE.LineBasicMaterial({{
          color: new THREE.Color(threeSettings.grid.equatorialColor),
          transparent: true,
          opacity: threeSettings.grid.equatorialOpacity,
        }});
        const step = gridStep(threeSettings.grid.equatorialStepDeg);
        builtEquatorialGridStep = step;
        for (let dec = -90 + step; dec < 90; dec += step) {{
          if (dec === 0) continue;
          const line = new THREE.Line(new THREE.BufferGeometry(), mat.clone());
          line.userData.gridKind = "parallel";
          line.userData.decDeg = dec;
          gridRefs.equatorialParallels.push(line);
          seasonalGroup.add(line);
        }}
        for (let ra = 0; ra < 360; ra += step) {{
          const line = new THREE.Line(new THREE.BufferGeometry(), mat.clone());
          line.userData.gridKind = "meridian";
          line.userData.raDeg = ra;
          gridRefs.equatorialMeridians.push(line);
          seasonalGroup.add(line);
        }}
      }}

      function buildDiscFromRing(points) {{
        const positions = [0, 0, 0];
        points.forEach((point) => positions.push(point.x, point.y, point.z));
        const indices = [];
        for (let i = 1; i < points.length; i += 1) indices.push(0, i, i + 1);
        const geom = new THREE.BufferGeometry();
        geom.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3));
        geom.setIndex(indices);
        geom.computeVertexNormals();
        return geom;
      }}

      function buildReferencePrimitives() {{
        const eclipticGeom = buildDiscFromRing(circlePoints(0, R * 0.985, 144).slice(0, -1));
        eclipticPlane = new THREE.Mesh(eclipticGeom, new THREE.MeshBasicMaterial({{
          color: new THREE.Color(threeSettings.reference.eclipticPlaneColor),
          transparent: true,
          opacity: threeSettings.reference.eclipticPlaneOpacity,
          side: THREE.DoubleSide,
          depthWrite: false,
        }}));
        siderealGroup.add(eclipticPlane);

        equatorialPlane = new THREE.Mesh(new THREE.BufferGeometry(), new THREE.MeshBasicMaterial({{
          color: new THREE.Color(threeSettings.reference.equatorialPlaneColor),
          transparent: true,
          opacity: threeSettings.reference.equatorialPlaneOpacity,
          side: THREE.DoubleSide,
          depthWrite: false,
        }}));
        seasonalGroup.add(equatorialPlane);

        nsAxisLine = new THREE.Line(new THREE.BufferGeometry(), new THREE.LineBasicMaterial({{
          color: new THREE.Color(threeSettings.reference.nsAxisColor),
          transparent: true,
          opacity: threeSettings.reference.nsAxisOpacity,
          depthWrite: false,
        }}));
        seasonalGroup.add(nsAxisLine);
      }}

      /* ── A2. Ecliptic band — colored + labeled sectors ─── */
      function buildEclipticBand() {{
        const sectorRows = data.nakshatras.filter(n => n.sector_index_27 !== null);
        const step = 2;

        sectorRows.forEach((row, idx) => {{
          const lonStart = row.sector_start_lon_deg;
          const lonEnd   = row.sector_end_lon_deg;
          const span = ((lonEnd - lonStart) % 360 + 360) % 360 || (360 / 27);
          const nSteps = Math.max(2, Math.round(span / step));
          const color = sectorHex(idx);

          const positions = [];
          const indices   = [];
          for (let i = 0; i <= nSteps; i++) {{
            const lon = lonStart + (i / nSteps) * span;
            const pTop = toCart(lon,  BAND_HALF, R * 0.998);
            const pBot = toCart(lon, -BAND_HALF, R * 0.998);
            positions.push(pTop.x, pTop.y, pTop.z);
            positions.push(pBot.x, pBot.y, pBot.z);
            if (i < nSteps) {{
              const b = i * 2;
              indices.push(b, b + 1, b + 2, b + 1, b + 3, b + 2);
            }}
          }}
          const geom = new THREE.BufferGeometry();
          geom.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3));
          geom.setIndex(indices);
          geom.computeVertexNormals();
          const mat = new THREE.MeshBasicMaterial({{
            color: color, transparent: true, opacity: threeSettings.ecliptic.bandOpacity,
            side: THREE.DoubleSide, depthWrite: false
          }});
          const mesh = new THREE.Mesh(geom, mat);
          bandRefs.meshes.push(mesh);
          siderealGroup.add(mesh);

          const divPts = [];
          for (let lat = -BAND_HALF; lat <= BAND_HALF; lat += 1) {{
            divPts.push(toCart(lonStart, lat, R * 0.999));
          }}
          const divGeom = new THREE.BufferGeometry().setFromPoints(divPts);
          const divMat = new THREE.LineBasicMaterial({{ color: 0xd4a56a, transparent: true, opacity: threeSettings.ecliptic.dividerOpacity }});
          const divider = new THREE.Line(divGeom, divMat);
          bandRefs.dividers.push(divider);
          siderealGroup.add(divider);

          const midLon = lonStart + span / 2;
          const abbr = row.nid.split('-')[1] || '';
          const label = makeTextSprite(abbr, {{
            color: sectorHSL(idx), fontSize: 36, size: 7.5, opacity: 0.82, bold: true
          }});
          label.position.copy(toCart(midLon, 0, R * 1.025));
          bandRefs.labels.push(label);
          siderealGroup.add(label);
        }});
      }}

      /* ── Ecliptic great circle ──────────────────────────── */
      function buildEclipticCircle() {{
        const pts = circlePoints(0, R * 1.001, 144);
        const geom = new THREE.BufferGeometry().setFromPoints(pts);
        const mat = new THREE.LineBasicMaterial({{ color: new THREE.Color(threeSettings.ecliptic.circleColor), transparent: true, opacity: threeSettings.ecliptic.circleOpacity }});
        eclipticCircle = new THREE.Line(geom, mat);
        siderealGroup.add(eclipticCircle);
      }}

      /* ── Stars ──────────────────────────────────────────── */
      function buildStars() {{
        data.nakshatras.forEach(naks => {{
          if (!naks.stars || naks.stars.length === 0) return;
          const positions = [];
          const colors = [];
          naks.stars.forEach(star => {{
            const p = toCart(star.lon_deg, star.lat_deg, R);
            positions.push(p.x, p.y, p.z);
            colors.push(0.92, 0.92, 1.0);
          }});
          const geom = new THREE.BufferGeometry();
          geom.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3));
          geom.setAttribute('color', new THREE.Float32BufferAttribute(colors, 3));
          const mat = new THREE.PointsMaterial({{
            size: threeSettings.stars.size, vertexColors: true, transparent: true, opacity: threeSettings.stars.opacity, sizeAttenuation: false
          }});
          const points = new THREE.Points(geom, mat);
          starGroupRefs.push({{ nid: naks.nid, metaIndex: naks.meta_index_28, points }});
          siderealGroup.add(points);
        }});
        if (data.special_stars.length > 0) {{
          const positions = [];
          const colors = [];
          data.special_stars.forEach(star => {{
            const p = toCart(star.lon_deg, star.lat_deg, R);
            positions.push(p.x, p.y, p.z);
            colors.push(0.78, 0.86, 1.0);
          }});
          const geom = new THREE.BufferGeometry();
          geom.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3));
          geom.setAttribute('color', new THREE.Float32BufferAttribute(colors, 3));
          const mat = new THREE.PointsMaterial({{
            size: threeSettings.stars.size * 1.15, vertexColors: true, transparent: true, opacity: threeSettings.stars.opacity, sizeAttenuation: true
          }});
          const points = new THREE.Points(geom, mat);
          starGroupRefs.push({{ nid: "__special__", metaIndex: 99, points }});
          siderealGroup.add(points);
        }}
      }}

      /* ── Nakshatra asterism lines ───────────────────────── */
      function buildNakshatraLines() {{
        data.nakshatras.forEach(naks => {{
          naks.asterism_lines.forEach(line => {{
            const pts = [];
            line.forEach(hip => {{
              const star = data.stars.find(s => s.hip === hip);
              if (star) pts.push(toCart(star.lon_deg, star.lat_deg, R * 0.999));
            }});
            if (pts.length > 1) {{
              const geom = new THREE.BufferGeometry().setFromPoints(pts);
              const lineObj = new THREE.Line(geom, new THREE.LineBasicMaterial({{ color: new THREE.Color(threeSettings.nakshatras.color), transparent: true, opacity: threeSettings.nakshatras.opacity }}));
              nakshatraLineRefs.push({{ nid: naks.nid, metaIndex: naks.meta_index_28, line: lineObj }});
              siderealGroup.add(lineObj);
            }}
          }});
        }});
      }}

      /* ── Nakshatra labels ───────────────────────────────── */
      function buildNakshatraLabels() {{
        data.nakshatras.forEach(naks => {{
          if (!naks.stars || naks.stars.length === 0) return;
          const cLon = naks.stars.reduce((s, st) => s + st.lon_deg, 0) / naks.stars.length;
          const cLat = naks.stars.reduce((s, st) => s + st.lat_deg, 0) / naks.stars.length;
          const label = makeTextSprite(naks.enaks, {{
            color: '#99aabb', fontSize: 32, size: 6.5, opacity: threeSettings.nakshatras.labelOpacity
          }});
          label.position.copy(toCart(cLon, cLat + 3, R * 1.03));
          nakshatraLabelRefs.push({{ nid: naks.nid, metaIndex: naks.meta_index_28, sprite: label }});
          siderealGroup.add(label);
        }});
      }}

      /* ── Polar figures ────────────────────────────────────── */
      function buildCodexFigures() {{
        const figMat = new THREE.LineBasicMaterial({{ color: new THREE.Color(threeSettings.polarItems.color), transparent: true, opacity: threeSettings.polarItems.opacity }});
        const figDotMat = new THREE.MeshBasicMaterial({{ color: new THREE.Color(threeSettings.polarItems.color), transparent: true, opacity: threeSettings.polarItems.starOpacity }});
        const figDotGeom = new THREE.SphereGeometry(0.7, 6, 6);

        const specialStarLookup = {{}};
        data.special_figures.forEach(fig => {{
          fig.stars.forEach(s => {{ specialStarLookup[s.hip] = s; }});
        }});
        data.special_stars.forEach(s => {{ specialStarLookup[s.hip] = s; }});

        data.special_figures.forEach(fig => {{
          const avgLat = fig.stars.reduce((a, s) => a + s.lat_deg, 0) / Math.max(1, fig.stars.length);
          const region = avgLat < 0 ? "south" : "north";
          const figAliases = specialTargetAliases(fig.id, fig.label);
          fig.lines.forEach(line => {{
            const pts = [];
            line.forEach(hip => {{
              const s = specialStarLookup[hip];
              if (s) pts.push(toCart(s.lon_deg, s.lat_deg, R * 1.002));
            }});
            if (pts.length > 1) {{
              const geom = new THREE.BufferGeometry().setFromPoints(pts);
              const lineObj = new THREE.Line(geom, figMat.clone());
              polarItemRefs.push({{ id: fig.id, region, kind: "line", object: lineObj, aliases: figAliases }});
              siderealGroup.add(lineObj);
            }}
          }});
          fig.stars.forEach(s => {{
            const dot = new THREE.Mesh(figDotGeom.clone(), figDotMat);
            dot.position.copy(toCart(s.lon_deg, s.lat_deg, R * 1.002));
            polarItemRefs.push({{ id: fig.id, region, kind: "dot", object: dot, aliases: figAliases }});
            siderealGroup.add(dot);
          }});
          const cLon = fig.stars.reduce((a, s) => a + s.lon_deg, 0) / fig.stars.length;
          const cLat = fig.stars.reduce((a, s) => a + s.lat_deg, 0) / fig.stars.length;
          const figName = fig.id.includes('Shim') ? 'Śiśumāra' : fig.id.includes('Matsya') ? 'Matsya' : fig.label;
          const label = makeTextSprite(figName, {{
            color: '#7a94b0', fontSize: 34, size: 8.5, opacity: threeSettings.polarItems.labelOpacity
          }});
          label.position.copy(toCart(cLon, cLat + (fig.id.includes('Shim') ? 3 : -3), R * 1.04));
          polarItemRefs.push({{ id: fig.id, region, kind: "label", object: label, aliases: figAliases }});
          siderealGroup.add(label);
        }});
      }}

      /* ── Special stars (Agastya, Polaris, Thuban) ──────── */
      function buildSpecialStars() {{
        const dotGeom = new THREE.SphereGeometry(1.0, 8, 8);
        const dotMat = new THREE.MeshBasicMaterial({{ color: new THREE.Color(threeSettings.polarItems.color), transparent: true, opacity: threeSettings.polarItems.starOpacity }});

        data.special_stars.forEach(s => {{
          const region = s.lat_deg < 0 ? "south" : "north";
          const aliases = specialTargetAliases(s.hip, s.label);
          const dot = new THREE.Mesh(dotGeom.clone(), dotMat);
          dot.position.copy(toCart(s.lon_deg, s.lat_deg, R * 1.002));
          polarItemRefs.push({{ id: s.hip, region, kind: "dot", object: dot, aliases }});
          siderealGroup.add(dot);
          const label = makeTextSprite(s.label, {{
            color: '#7a94b0', fontSize: 30, size: 7.0, opacity: threeSettings.polarItems.labelOpacity
          }});
          label.position.copy(toCart(s.lon_deg + 3, s.lat_deg - 3, R * 1.04));
          polarItemRefs.push({{ id: s.hip, region, kind: "label", object: label, aliases }});
          siderealGroup.add(label);
        }});

        const specialStarLookup = {{}};
        data.special_figures.forEach(fig => {{
          fig.stars.forEach(s => {{ specialStarLookup[s.hip] = s; }});
        }});

        const poleStarDefs = [
          {{ hip: 'HIP 11767', label: 'Polaris', color: '#5577aa' }},
          {{ hip: 'HIP 68756', label: 'Thuban', color: '#5577aa' }}
        ];
        poleStarDefs.forEach(def => {{
          const s = specialStarLookup[def.hip] || data.stars.find(st => st.hip === def.hip);
          if (!s) return;
          const aliases = specialTargetAliases(def.hip, def.label);
          const psMat = new THREE.MeshBasicMaterial({{ color: new THREE.Color(def.color) }});
          const dot = new THREE.Mesh(dotGeom.clone(), psMat);
          dot.position.copy(toCart(s.lon_deg, s.lat_deg, R * 1.003));
          polarItemRefs.push({{ id: def.hip, region: "north", kind: "dot", object: dot, aliases }});
          siderealGroup.add(dot);
          const label = makeTextSprite(def.label, {{
            color: def.color, fontSize: 28, size: 6.5, opacity: 0.6
          }});
          label.position.copy(toCart(s.lon_deg + 4, s.lat_deg - 3, R * 1.04));
          polarItemRefs.push({{ id: def.hip, region: "north", kind: "label", object: label, aliases }});
          siderealGroup.add(label);
        }});
      }}

      /* ── Precession circle ────────────────────────────────── */
      function buildPoleTrack() {{
        // Full geometric precession circle: small circle at ecliptic lat = 90° − mean obliquity
        const meanObliquity = data.epochs[Math.floor(data.epochs.length / 2)].obliquity_deg || 23.44;
        const precLat = 90 - meanObliquity;
        const fullCirclePts = circlePoints(precLat, R * 1.005, 144);
        const fullGeom = new THREE.BufferGeometry().setFromPoints(fullCirclePts);
        const fullMat = new THREE.LineBasicMaterial({{
          color: new THREE.Color(threeSettings.poleTrack.color),
          transparent: true,
          opacity: threeSettings.poleTrack.opacity,
          depthTest: false,
          depthWrite: false,
        }});
        poleTrackCircle = new THREE.Line(fullGeom, fullMat);
        poleTrackCircle.renderOrder = 22;
        siderealGroup.add(poleTrackCircle);

        // Epoch-sampled arc overlay (brighter, shows covered range)
        const arcPts = data.epochs.map(e => toCart(e.north_pole_lon_deg, e.north_pole_lat_deg, R * 1.006));
        const arcGeom = new THREE.BufferGeometry().setFromPoints(arcPts);
        const arcMat = new THREE.LineBasicMaterial({{
          color: new THREE.Color(threeSettings.poleTrack.arcColor),
          transparent: true,
          opacity: threeSettings.poleTrack.arcOpacity,
          depthTest: false,
          depthWrite: false,
        }});
        poleTrackArc = new THREE.Line(arcGeom, arcMat);
        poleTrackArc.renderOrder = 23;
        siderealGroup.add(poleTrackArc);

        // Label
        const labelPos = toCart(180, precLat + 4, R * 1.05);
        poleTrackLabel = makeTextSprite('Precession Circle', {{
          color: '#8899bb', fontSize: 30, size: 8.5, opacity: 0.6
        }});
        poleTrackLabel.position.copy(labelPos);
        siderealGroup.add(poleTrackLabel);

        // Moving pole dot
        const poleGeom = new THREE.SphereGeometry(1.5, 10, 10);
        const poleMat = new THREE.MeshBasicMaterial({{ color: new THREE.Color(threeSettings.poleTrack.dotColor) }});
        poleDot = new THREE.Mesh(poleGeom, poleMat);
        seasonalGroup.add(poleDot);
        southPoleDot = new THREE.Mesh(poleGeom.clone(), poleMat.clone());
        seasonalGroup.add(southPoleDot);

        const poleLabel = makeTextSprite('North Pole', {{
          color: '#44566c', fontSize: 28, size: 7.0, opacity: 0.7
        }});
        poleLabel.name = 'poleLabel';
        movingPoleLabel = poleLabel;
        seasonalGroup.add(poleLabel);
        southPoleLabel = makeTextSprite('South Pole', {{
          color: '#44566c', fontSize: 26, size: 6.0, opacity: 0.48
        }});
        southPoleLabel.name = 'southPoleLabel';
        seasonalGroup.add(southPoleLabel);
      }}

      /* ── Seasonal frame (red equator + 4 markers) ──────── */
      function buildSeasonalFrame() {{
        const eqGeom = new THREE.BufferGeometry();
        const eqMat = new THREE.LineBasicMaterial({{ color: new THREE.Color(threeSettings.seasonal.equatorColor), transparent: true, opacity: threeSettings.seasonal.equatorOpacity }});
        equatorLine = new THREE.Line(eqGeom, eqMat);
        seasonalGroup.add(equatorLine);

        equinoxMarkers = new THREE.Group();
        seasonalGroup.add(equinoxMarkers);
        const labels = ['VE', 'SS', 'AE', 'WS'];
        const mColors = [0xcc3333, 0xcc8833, 0xcc3333, 0x3388cc];
        labels.forEach((lbl, i) => {{
          const mg = new THREE.SphereGeometry(1.5, 12, 12);
          const mm = new THREE.MeshBasicMaterial({{ color: mColors[i] }});
          const mesh = new THREE.Mesh(mg, mm);
          mesh.name = lbl;
          equinoxMarkers.add(mesh);
          const sprite = makeTextSprite(lbl, {{
            color: '#' + mColors[i].toString(16).padStart(6, '0'),
            fontSize: 36, size: 8.5, opacity: 0.8, bold: true
          }});
          sprite.name = lbl + '_label';
          seasonalMarkerRefs.push({{ key: lbl, mesh, sprite, baseScale: sprite.scale.clone() }});
          equinoxMarkers.add(sprite);
        }});
      }}

      /* ── update drifting frame ──────────────────────────── */
      function updateSeasonalFrame() {{
        const st = window.explorerState;
        if (!st) return;
        const epoch = data.epochs[st.epochIndex];
        const flowText = timeFlow.direction > 0 ? ` · ${{timeFlow.speed}}x forward` : timeFlow.direction < 0 ? ` · ${{timeFlow.speed}}x backward` : "";
        overlayLabel.textContent = `${{epoch.label}}${{flowText}}`;
        syncTimeControls();
        const xAxis = toCart(epoch.vernal_equinox_lon_deg, 0, 1).normalize();
        const zAxis = toCart(epoch.north_pole_lon_deg, epoch.north_pole_lat_deg, 1).normalize();
        const yAxis = new THREE.Vector3().crossVectors(zAxis, xAxis).normalize();
        const equatorialPoint = (raDeg, decDeg, radius) => {{
          const ra = raDeg * Math.PI / 180;
          const dec = decDeg * Math.PI / 180;
          return new THREE.Vector3()
            .addScaledVector(xAxis, Math.cos(dec) * Math.cos(ra))
            .addScaledVector(yAxis, Math.cos(dec) * Math.sin(ra))
            .addScaledVector(zAxis, Math.sin(dec))
            .normalize()
            .multiplyScalar(radius);
        }};
        const updateEquatorialLine = (line) => {{
          const pts = [];
          if (line.userData.gridKind === "parallel") {{
            for (let ra = 0; ra <= 360; ra += 3) pts.push(equatorialPoint(ra, line.userData.decDeg, R * 0.993));
          }} else {{
            for (let dec = -90; dec <= 90; dec += 3) pts.push(equatorialPoint(line.userData.raDeg, dec, R * 0.993));
          }}
          line.geometry.dispose();
          line.geometry = new THREE.BufferGeometry().setFromPoints(pts);
        }};
        gridRefs.equatorialParallels.forEach(updateEquatorialLine);
        gridRefs.equatorialMeridians.forEach(updateEquatorialLine);

        const pts = [];
        for (let lon = 0; lon <= 360; lon += 2) {{
          const rel = (lon - epoch.vernal_equinox_lon_deg) * Math.PI / 180;
          const lat = Math.atan(
            -Math.tan(epoch.obliquity_deg * Math.PI / 180) * Math.sin(rel)
          ) * 180 / Math.PI;
          pts.push(toCart(lon, lat, R * 1.002));
        }}
        equatorLine.geometry.dispose();
        equatorLine.geometry = new THREE.BufferGeometry().setFromPoints(pts);
        if (equatorialPlane) {{
          equatorialPlane.geometry.dispose();
          equatorialPlane.geometry = buildDiscFromRing(pts.slice(0, -1).map((point) => point.clone().multiplyScalar(0.985 / 1.002)));
        }}

        const cardinals = [
          epoch.vernal_equinox_lon_deg,
          epoch.summer_solstice_lon_deg,
          epoch.autumnal_equinox_lon_deg,
          epoch.winter_solstice_lon_deg
        ];
        const labels = ['VE', 'SS', 'AE', 'WS'];
        cardinals.forEach((lonDeg, i) => {{
          const p = toCart(lonDeg, 0, R * 1.006);
          const mesh = equinoxMarkers.getObjectByName(labels[i]);
          if (mesh) mesh.position.copy(p);
          const sprite = equinoxMarkers.getObjectByName(labels[i] + '_label');
          if (sprite) sprite.position.copy(toCart(lonDeg, 4, R * 1.04));
        }});

        if (poleDot) {{
          const pp = toCart(epoch.north_pole_lon_deg, epoch.north_pole_lat_deg, R * 1.006);
          poleDot.position.copy(pp);
          const poleLabel = seasonalGroup.getObjectByName('poleLabel');
          if (poleLabel) poleLabel.position.copy(toCart(epoch.north_pole_lon_deg + 5, epoch.north_pole_lat_deg - 3, R * 1.04));
          const sp = toCart(epoch.north_pole_lon_deg + 180, -epoch.north_pole_lat_deg, R * 1.006);
          if (southPoleDot) southPoleDot.position.copy(sp);
          if (southPoleLabel) southPoleLabel.position.copy(toCart(epoch.north_pole_lon_deg + 185, -epoch.north_pole_lat_deg + 3, R * 1.04));
          if (nsAxisLine) {{
            nsAxisLine.geometry.dispose();
            nsAxisLine.geometry = new THREE.BufferGeometry().setFromPoints([sp, pp]);
          }}
        }}
      }}

      /* ── resize / animate ──────────────────────────────── */
      function onResize() {{
        if (!renderer) return;
        camera.aspect = container.clientWidth / container.clientHeight;
        camera.updateProjectionMatrix();
        renderer.setSize(container.clientWidth, container.clientHeight);
      }}

      function animate() {{
        requestAnimationFrame(animate);
        controls.update();
        updateThreeState();
        updateSeasonalFrame();
        updateStoryLabels();
        renderer.render(scene, camera);
      }}

      function applyThreeSettingsFromTextarea() {{
        if (!threeDebugJson) return;
        try {{
          const parsed = JSON.parse(threeDebugJson.value);
          threeSettings = parsed;
          if (threeLightPreset && threeSettings.lightPreset) {{
            threeLightPreset.value = threeSettings.lightPreset;
          }}
          applyThreeSettings();
          syncDebugTextareaFromLive();
          setDebugStatus("Applied.");
        }} catch (error) {{
          setDebugStatus(`Invalid JSON: ${{error.message}}`);
        }}
      }}

      if (threeLightPreset) {{
        threeLightPreset.value = threeSettings.lightPreset;
        threeLightPreset.addEventListener('change', () => {{
          stopStory();
          threeSettings.lightPreset = threeLightPreset.value;
          applyLightPreset();
          syncDebugTextareaFromLive();
          syncSceneButtons();
          setDebugStatus(`Light preset: ${{threeSettings.lightPreset}}`);
        }});
      }}

      if (threeFullscreenToggle) {{
        syncFullscreenButton(false);
        threeFullscreenToggle.addEventListener("click", () => {{
          const entering = !(document.fullscreenElement === container || container.classList.contains("theater-mode"));
          setThreeFullscreen(entering);
        }});
        document.addEventListener("fullscreenchange", () => {{
          container.classList.toggle("theater-mode", document.fullscreenElement === container);
          syncFullscreenButton(document.fullscreenElement === container);
          onResize();
        }});
      }}

      threeOrbitButtons.forEach((button) => {{
        button.addEventListener("click", () => {{
          applyOrbitMode(button.dataset.orbitMode || "free");
        }});
      }});

      if (threeOrbitToggle) {{
        threeOrbitToggle.addEventListener("click", () => {{
          applyOrbitMode(orbitMode === "lock" ? "free" : "lock");
        }});
      }}

      if (threeMoreToggle) {{
        threeMoreToggle.addEventListener("click", (event) => {{
          event.stopPropagation();
          toggleMoreDrawer();
        }});
      }}

      if (threeMoreDrawer) {{
        threeMoreDrawer.addEventListener("click", (event) => event.stopPropagation());
      }}

      document.addEventListener("click", (event) => {{
        if (threeViewToolbar && !threeViewToolbar.contains(event.target)) {{
          closeMoreDrawer(false);
        }}
      }});

      document.addEventListener("keydown", (event) => {{
        if (event.key === "Escape") closeMoreDrawer(false);
      }});

      threeViewAnchorButtons.forEach((button) => {{
        button.addEventListener("click", () => {{
          if (!scene) initThree();
          threeViewAnchorButtons.forEach((entry) => entry.classList.toggle("active", entry === button));
          flyToCamera(cameraAnchor(button.dataset.viewAnchor));
        }});
      }});

      threeLayerButtons.forEach((button) => {{
        button.addEventListener("click", () => {{
          setLayerGroup(button.dataset.layerToggle);
        }});
      }});

      threeTimeSpeedButtons.forEach((button) => {{
        button.addEventListener("click", () => {{
          timeFlow.speed = Number(button.dataset.timeSpeed) || 1;
          if (timeFlow.direction !== 0) startToolbarTime(timeFlow.direction);
          syncTimeControls();
        }});
      }});

      threeTimeButtons.forEach((button) => {{
        button.addEventListener("click", () => {{
          const action = button.dataset.timeAction;
          if (action === "step-back") {{
            stopToolbarTime();
            stepToolbarTime(-1);
          }} else if (action === "step-forward") {{
            stopToolbarTime();
            stepToolbarTime(1);
          }} else if (action === "reverse") {{
            startToolbarTime(-1);
          }} else if (action === "play") {{
            startToolbarTime(1);
          }} else if (action === "pause") {{
            stopToolbarTime();
          }} else if (action === "loop") {{
            timeFlow.loop = !timeFlow.loop;
            syncTimeControls();
          }}
        }});
      }});

      syncTimeControls();
      syncSceneButtons();

      threeSceneButtons.forEach((button) => {{
        button.addEventListener("click", () => {{
          applyScenePreset(button.dataset.scenePreset);
        }});
      }});

      threeStoryToolbarButtons.forEach((button) => {{
        button.addEventListener("click", () => {{
          const action = button.dataset.storyAction;
          if (action === "prev") {{
            selectToolbarStory(-1);
          }} else if (action === "next") {{
            selectToolbarStory(1);
          }} else if (action === "run") {{
            runToolbarStory();
          }} else if (action === "stop") {{
            stopStory();
            setStoryStatus("Stopped.");
            setVysuStatus("Stopped.");
          }}
        }});
      }});

      if (threeToolbarPin && threeViewToolbar) {{
        threeToolbarPin.addEventListener("click", () => {{
          const pinned = !threeViewToolbar.classList.contains("pinned");
          threeViewToolbar.classList.toggle("pinned", pinned);
          threeToolbarPin.classList.toggle("active", pinned);
          threeToolbarPin.setAttribute("aria-pressed", pinned ? "true" : "false");
          threeToolbarPin.title = pinned ? "Allow toolbar to fade" : "Keep toolbar visible";
          threeToolbarPin.setAttribute("aria-label", pinned ? "Allow toolbar to fade" : "Keep toolbar visible");
        }});
      }}

      if (threeDebugCapture) {{
        threeDebugCapture.addEventListener('click', () => {{
          syncDebugTextareaFromLive();
          setDebugStatus("Captured current view.");
        }});
      }}

      if (threeDebugApply) {{
        threeDebugApply.addEventListener('click', () => {{
          stopStory();
          applyThreeSettingsFromTextarea();
        }});
      }}

      if (threeDebugCopy) {{
        threeDebugCopy.addEventListener('click', async () => {{
          try {{
            await navigator.clipboard.writeText(threeDebugJson.value);
            setDebugStatus("Copied JSON.");
          }} catch (_error) {{
            setDebugStatus("Copy failed.");
          }}
        }});
      }}

      if (threeDebugReset) {{
        threeDebugReset.addEventListener('click', () => {{
          stopStory();
          threeSettings = cloneSettings(defaultThreeSettings);
          if (threeLightPreset) threeLightPreset.value = threeSettings.lightPreset;
          applyThreeSettings();
          syncDebugTextareaFromLive();
          setDebugStatus("Restored defaults.");
        }});
      }}

      if (threeDockToggle && threeDock) {{
        const syncDockLayout = () => {{
          const collapsed = threeDock.classList.contains("collapsed");
          threeDock.closest(".three-workspace")?.classList.toggle("dock-collapsed", collapsed);
          threeDockToggle.textContent = collapsed ? "Show dock" : "Hide dock";
          window.dispatchEvent(new Event("resize"));
        }};
        threeDockToggle.addEventListener("click", () => {{
          threeDock.classList.toggle("collapsed");
          syncDockLayout();
        }});
        syncDockLayout();
      }}

      threeDockTabs.forEach((button) => {{
        button.addEventListener("click", () => setDockTab(button.dataset.dockTab));
      }});

      if (threeStorySelect) {{
        threeStorySelect.addEventListener("change", () => {{
          const story = selectedStoryOriginal();
          if (story && threeStoryEditor) {{
            loadStoryIntoEditors(story);
            setStoryStatus("Loaded build-time story.");
            syncStoryControls();
          }}
        }});
      }}

      if (threeStorySearch) {{
        threeStorySearch.addEventListener("input", () => {{
          renderStoryPills();
          renderStoryEditorOptions();
        }});
      }}

      if (threeStoryRun) {{
        threeStoryRun.addEventListener("click", () => {{
          try {{
            const story = storyFromEditor();
            runStory(story);
            setStoryStatus(`Running ${{story.title}}.`);
            syncStoryControls();
          }} catch (error) {{
            setStoryStatus(`Invalid story: ${{error.message}}`);
          }}
        }});
      }}

      if (threeVysuRun) {{
        threeVysuRun.addEventListener("click", () => {{
          try {{
            const compiled = compileVyomaSutra(threeVysuEditor?.value || "");
            threeStoryEditor.value = JSON.stringify(compiled.story, null, 2);
            validateStoryForEditor(compiled.story);
            runStory(compiled.story);
            const warningText = compiled.warnings.length ? ` Warnings: ${{compiled.warnings.join(" | ")}}` : "";
            setVysuStatus(`Running VyomaSutra.${{warningText}}`);
            setStoryStatus("JSON updated from VyomaSutra.");
            syncStoryControls();
          }} catch (error) {{
            setVysuStatus(`Invalid VyomaSutra: ${{error.message}}`);
          }}
        }});
      }}

      if (threeCameraGrab) {{
        threeCameraGrab.addEventListener("click", () => {{
          if (!scene) initThree();
          grabCameraDirective();
        }});
      }}

      if (threeStoryStop) {{
        threeStoryStop.addEventListener("click", () => {{
          stopStory();
          setStoryStatus("Stopped.");
          setVysuStatus("Stopped.");
          syncStoryControls();
        }});
      }}

      if (threeStoryReset) {{
        threeStoryReset.addEventListener("click", () => {{
          const story = selectedStoryOriginal();
          if (story && threeStoryEditor) {{
            stopStory();
            loadStoryIntoEditors(story);
            setStoryStatus("Reloaded original.");
            setVysuStatus("Reloaded story VyomaSutra.");
            syncStoryControls();
          }}
        }});
      }}

      if (threeStoryCopy) {{
        threeStoryCopy.addEventListener("click", async () => {{
          try {{
            await navigator.clipboard.writeText(threeStoryEditor.value);
            setStoryStatus("Copied story JSON.");
          }} catch (_error) {{
            setStoryStatus("Copy failed.");
          }}
        }});
      }}

      renderStoryPills();
      renderStoryEditorOptions();
      syncStoryControls();
      renderThreeDebugToggles();
      syncThreeDebugTogglesFromSettings();
      syncDebugTextareaFromLive();

      const observer = new IntersectionObserver((entries) => {{
        if (entries[0].isIntersecting && !scene) {{
          initThree();
        }}
      }});
      observer.observe(container);
    </script>

  </body>
</html>
"""


def split_page_assets(page_text: str) -> tuple[str, str, str]:
    """Emit inspectable generated assets while keeping file:// viewing functional."""
    style_start = page_text.index("    <style>\n")
    style_body_start = style_start + len("    <style>\n")
    style_end = page_text.index("    </style>\n", style_body_start)
    css_text = page_text[style_body_start:style_end]
    page_text = (
        page_text[:style_start]
        + '    <link rel="stylesheet" href="./assets/css/explorer.css">\n'
        + page_text[style_end + len("    </style>\n") :]
    )

    module_start = page_text.index('    <script type="module">\n')
    module_body_start = module_start + len('    <script type="module">\n')
    module_end = page_text.index("    </script>\n", module_body_start)
    module_text = page_text[module_body_start:module_end]
    return page_text, css_text, module_text


def write_outputs(dataset: dict[str, object]) -> None:
    page_root = LAB_ROOT / SLUG
    page_root.mkdir(parents=True, exist_ok=True)
    js_root = page_root / "assets" / "js"
    css_root = page_root / "assets" / "css"
    js_root.mkdir(parents=True, exist_ok=True)
    css_root.mkdir(parents=True, exist_ok=True)
    index_html, css_text, three_module = split_page_assets(page_html(dataset))
    (page_root / "index.html").write_text(index_html, encoding="utf-8")
    (css_root / "explorer.css").write_text(css_text, encoding="utf-8")
    (js_root / "three-explorer.js").write_text(three_module, encoding="utf-8")
    (js_root / "vysu-compiler.mjs").write_text(
        (REPO_ROOT / "scripts" / "vysu-compiler.mjs").read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    story_match = re.search(
        r'(<script id="story-data" type="application/json">)(.*?)(</script>)',
        index_html,
        re.DOTALL,
    )
    if story_match:
        (page_root / "stories.json").write_text(story_match.group(2) + "\n", encoding="utf-8")


def update_lab_index() -> None:
    path = LAB_ROOT / "index.html"
    text = path.read_text(encoding="utf-8")
    new_button = """          <button
            class="exploration-link active"
            type="button"
            data-title="Nakshatra Precession Explorer"
            data-slug="nakshatra-precession-explorer"
            data-path="nakshatra-precession-explorer/index.html"
            data-description="Joined 27/28 nakshatra metadata and 2D precession view with a shared epoch slider."
          >
            <span class="exploration-title">Nakshatra Precession Explorer</span>
            <span class="exploration-meta">Fixed sidereal geometry against the drifting seasonal frame</span>
          </button>
"""
    old_active = 'class="exploration-link active"'
    if "nakshatra-precession-explorer" not in text:
        text = text.replace(old_active, 'class="exploration-link"', 1)
        marker = '        <nav class="exploration-list" aria-label="Explorations">\n'
        text = text.replace(marker, marker + new_button, 1)
        text = text.replace(
            '<h2 id="viewer-title">27 Nakshatra Heliacal Rising</h2>',
            '<h2 id="viewer-title">Nakshatra Precession Explorer</h2>',
        )
        text = text.replace(
            "Rising azimuth and declination of the ordered 27 nakshatra proxies across the epochs\n              -1500, -1000, and -500 at 30°N.",
            "Joined 27/28 nakshatra metadata and a projected precession view of the drifting seasonal frame.",
        )
        text = text.replace(
            'src="heliacal-rising-27-naks/index.html"',
            'src="nakshatra-precession-explorer/index.html"',
        )
    path.write_text(text, encoding="utf-8")


def update_brief() -> None:
    path = EXPLORATIONS_ROOT / f"{SLUG}.md"
    path.write_text(
        """# Nakshatra Precession Explorer

Slug: `nakshatra-precession-explorer`
Status: implemented
Story PRD: [vyoma-sutra-prd.md](../stories/nakshatra-precession-explorer/vyoma-sutra-prd.md)

## Question

How can precessional time be shown clearly by separating the fixed sidereal nakshatra framework from the drifting seasonal framework, while joining textual nakshatra metadata with constituent-star geometry?

## Conceptual Model

- The sidereal frame is fixed:
  - stars
  - nakshatra asterism shapes
  - 27 equal nakshatra sectors on the ecliptic
  - Abhijit as an additional asterism, not one of the 27 equal sectors
- The seasonal frame drifts with epoch:
  - equinoxes
  - solstices
  - six rtus
  - equator relative to the ecliptic
  - pole position around the ecliptic pole
- Precession is therefore shown as changing alignment between the fixed sidereal frame and the drifting seasonal frame.

## Inputs

- `../datasets/n28_good_meta.csv` as the metadata spine for names, shape labels, proxies, constituent-star text, and related properties
- `../datasets/n83_full_meta_for_-1750.csv` as the main J2000 star-position source for nakshatra constituent stars
- `../nakshatra_sky_culture/vedic_25_codex/index.json` for nakshatra asterism line geometry
- `../nakshatra_sky_culture/data/stars_mag6_within_30_declination.csv` as an Abhijit coordinate supplement
- 27 equal ecliptic sectors anchored from the lunar-system link star in the sky-culture JSON
- Abhijit represented explicitly as an asterism overlay outside the equal-27 sector scheme
- epoch as a shared state variable controlled by a slider

## Outputs

- joined exploration dataset combining nakshatra metadata and asterism geometry
- epoch slider shared by all current views
- `Table` view with seasonal alignment cues and marker-in-sector annotations
- `2D Sky` view with stars, nakshatra shapes, ecliptic band, 27 sectors, Abhijit, equator, seasonal belt, equinoxes, solstices, and pole position
- `3D Sky` view as the live development baseline for the same fixed-versus-drifting model
- build-time 3D stories authored as `stories/nakshatra-precession-explorer/*.vysu` and compiled to `stories/nakshatra-precession-explorer/compiled/*.json`
- top 3D story pills sourced from `# featured: true` metadata, capped at five visible matches with search for larger story sets
- generated CSS in `lab/nakshatra-precession-explorer/assets/css/explorer.css` and an inspectable copy of the inline 3D runtime in `assets/js/three-explorer.js`
- short interpretive notes explaining the fixed-versus-drifting-frame model

## Maintenance Notes

- `scripts/nakshatra_precession_explorer.py` remains the generator for dataset, HTML, and generated 3D assets.
- `scripts/compile_stories.py nakshatra-precession-explorer` is the fast story-only path; it does not import astropy and replaces the existing lab page story payload from current story sources.
- `lab/nakshatra-precession-explorer/index.html` is generated and should not be hand-edited; CSS lives in `assets/css/explorer.css`, while the 3D module remains inline for `file://` and is also copied to `assets/js/three-explorer.js` for inspection.
- Story grammar and target vocabulary should be updated in `stories/nakshatra-precession-explorer/SKILL.md` and `vyoma-sutra-prd.md` before matching code changes.
- Use `netlify dev --dir lab` from the `jyotisha-2026` repo root for local review; `file://` viewing is secondary.

## Open Questions

- whether the equal-27 sector anchor should remain tied to the current sky-culture link-star convention or be overridden by a repo-specific convention later
- what epoch range and slider granularity should be preferred for later passes
- how far the 3D story layer should go before adding browser-side story authoring
""",
        encoding="utf-8",
    )


def main() -> None:
    dataset = build_dataset()
    write_outputs(dataset)
    update_lab_index()
    update_brief()


if __name__ == "__main__":
    main()
