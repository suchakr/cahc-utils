from __future__ import annotations

import csv
import json
import math
import warnings
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


def build_epoch_states() -> list[dict[str, float | int | str]]:
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


def page_html(dataset: dict[str, object]) -> str:
    data_json = json.dumps(dataset, ensure_ascii=False)
    return f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{TITLE}</title>
    <link rel="stylesheet" href="../shared/css/site.css">
    <style>
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
      }}
    </style>
  </head>
  <body class="exploration-body">
    <main class="content">
      <section class="flat-section">
        <div class="tabs" role="tablist" aria-label="Explorer views">
          <button class="tab-button active" type="button" data-tab="table" role="tab" aria-selected="true">Table</button>
          <button class="tab-button" type="button" data-tab="sky" role="tab" aria-selected="false">2D Sky</button>
        </div>
      </section>

      <section class="flat-section tab-panel active" id="tab-table" role="tabpanel">
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
          <label class="sky-toggle"><input type="checkbox" id="toggle-pole" checked> Pole track</label>
          <details class="debug-panel" id="trail-debug-panel">
            <summary>More visual toggles</summary>
            <div class="debug-popover">
              <div class="debug-subhead">Codex figures</div>
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

      <section class="flat-section">
        <h2>Interpretive Notes</h2>
        <ul class="explanation-list">
          <li>The sidereal layer is fixed: stars, nakshatra shapes, and the 27 equal ecliptic sectors do not move with the slider.</li>
          <li>The tropical seasonal layer drifts: equinoxes, solstices, six rtus, equator alignment, and pole position shift with epoch.</li>
          <li>Precession becomes visible here as changing alignment between these two frames, not as deformation of the nakshatra sky itself.</li>
        </ul>
      </section>
    </main>

    <script id="explorer-data" type="application/json">{data_json}</script>
    <script>
      const data = JSON.parse(document.getElementById("explorer-data").textContent);
      const epochSliders = [
        document.getElementById("epoch-slider-table"),
        document.getElementById("epoch-slider-sky"),
      ];
      const epochReadouts = [
        document.getElementById("epoch-readout-table"),
        document.getElementById("epoch-readout-sky"),
      ];
      const epochButtons = {{
        play: [document.getElementById("play-table"), document.getElementById("play-sky")],
        pause: [document.getElementById("pause-table"), document.getElementById("pause-sky")],
        reset: [document.getElementById("reset-table"), document.getElementById("reset-sky")],
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
             <text x="${{bounds.left + bounds.width - 4}}" y="${{skyPoint(0, 67, bounds).y - 8}}" text-anchor="end" font-size="12" fill="#6a7b91">Pole track</text>`
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
        }}).join("");

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
          '<li class="legend-item"><span class="swatch" style="background:#5b728f"></span>Codex figures</li>',
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
  </body>
</html>
"""


def write_outputs(dataset: dict[str, object]) -> None:
    page_root = LAB_ROOT / SLUG
    page_root.mkdir(parents=True, exist_ok=True)
    (page_root / "index.html").write_text(page_html(dataset), encoding="utf-8")


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
- short interpretive notes explaining the fixed-versus-drifting-frame model

## Open Questions

- whether the equal-27 sector anchor should remain tied to the current sky-culture link-star convention or be overridden by a repo-specific convention later
- what epoch range and slider granularity should be preferred for later passes
- how much of the current 2D rendering logic should be reused directly when the Three.js sphere is revived
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
