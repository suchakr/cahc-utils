#!/usr/bin/env python3

from __future__ import annotations

import argparse
import csv
import json
import urllib.parse
import urllib.request
import warnings
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import astropy.units as u
from astropy.coordinates import BarycentricMeanEcliptic, FK5, ICRS, SkyCoord
from astropy.time import Time
from erfa import ErfaWarning


SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent

DEFAULT_CACHE_PATH = REPO_ROOT / "data" / "hip_main_vizier.tsv"
DEFAULT_OUTPUT_SSC = REPO_ROOT / "ssc" / "user-01-pole-stars-over-time.ssc"
DEFAULT_NAME_FAB = Path("/Applications/Stellarium.app/Contents/Resources/stars/hip_gaia3/name.fab")
DEFAULT_MAG_LIMIT = 4.5
DEFAULT_EPOCH_START = -4000
DEFAULT_EPOCH_END = 14000
DEFAULT_EPOCH_STEP = 10
DEFAULT_PREFILTER_BAND_DEG = 12.0
DEFAULT_MAX_SEP_DEG = 7.0
DEFAULT_MAX_RESULTS = 0
HIPPARCOS_CATALOG_ID = "I/239/hip_main"
VIZIER_ASU_TSV_URL = "https://vizier.cds.unistra.fr/viz-bin/asu-tsv"
PRECESSION_CIRCLE_LAT_DEG = 90.0 - 23.4392911
CATALOG_EPOCH = Time(1991.25, format="jyear", scale="tdb")
J2000 = Time(2000.0, format="jyear", scale="tdb")


@dataclass(frozen=True)
class CatalogRow:
    hip: int
    ra_icrs_deg: float
    dec_icrs_deg: float
    pmra_mas_per_year: float
    pmdec_mas_per_year: float
    parallax_mas: float | None
    magnitude: float
    name: str


@dataclass(frozen=True)
class ScanResult:
    hip: int
    year: int
    ra_j2000_deg: float
    dec_j2000_deg: float
    name: str
    min_sep_deg: float
    magnitude: float


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Fetch and cache a normalized Hipparcos subset from Vizier, scan for "
            "stars that come closest to the north celestial pole over time, and emit "
            "a Stellarium .ssc display script."
        )
    )
    parser.add_argument("--cache-path", type=Path, default=DEFAULT_CACHE_PATH)
    parser.add_argument("--output-ssc", type=Path, default=DEFAULT_OUTPUT_SSC)
    parser.add_argument("--name-fab", type=Path, default=DEFAULT_NAME_FAB)
    parser.add_argument("--refresh-cache", action="store_true")
    parser.add_argument("--epoch-start", type=int, default=DEFAULT_EPOCH_START)
    parser.add_argument("--epoch-end", type=int, default=DEFAULT_EPOCH_END)
    parser.add_argument("--epoch-step", type=int, default=DEFAULT_EPOCH_STEP)
    parser.add_argument("--magnitude-limit", type=float, default=DEFAULT_MAG_LIMIT)
    parser.add_argument("--prefilter-band-deg", type=float, default=DEFAULT_PREFILTER_BAND_DEG)
    parser.add_argument("--max-sep-deg", type=float, default=DEFAULT_MAX_SEP_DEG)
    parser.add_argument("--max-results", type=int, default=DEFAULT_MAX_RESULTS)
    return parser


def parse_float(value: str | None) -> float | None:
    if value is None:
        return None
    text = value.strip()
    if not text:
        return None
    try:
        return float(text)
    except ValueError:
        return None


def load_name_map(path: Path) -> dict[int, str]:
    if not path.exists():
        return {}

    mapping: dict[int, str] = {}
    with path.open(encoding="utf-8") as handle:
        for raw_line in handle:
            line = raw_line.strip()
            if not line or line.startswith("#") or "|" not in line:
                continue
            lhs, rhs = line.split("|", 1)
            lhs = lhs.strip()
            rhs = rhs.strip().replace("_", " ")
            if lhs.isdigit() and rhs:
                mapping.setdefault(int(lhs), rhs)
    return mapping


def vizier_url() -> str:
    params = {
        "-source": HIPPARCOS_CATALOG_ID,
        "-out": "HIP,RAICRS,DEICRS,Plx,pmRA,pmDE,Vmag",
        "-out.max": "200000",
        "-sort": "HIP",
    }
    return f"{VIZIER_ASU_TSV_URL}?{urllib.parse.urlencode(params)}"


def fetch_vizier_tsv() -> str:
    request = urllib.request.Request(
        vizier_url(),
        headers={"User-Agent": "cahc-utils/user-01-pole-stars-over-time"},
    )
    with urllib.request.urlopen(request, timeout=60) as response:
        return response.read().decode("utf-8")


def parse_vizier_tsv(tsv_text: str) -> list[dict[str, str]]:
    header: list[str] | None = None
    rows: list[dict[str, str]] = []
    required = {"HIP", "RAICRS", "DEICRS", "Plx", "pmRA", "pmDE", "Vmag"}

    for raw_line in tsv_text.splitlines():
        if not raw_line.strip() or raw_line.lstrip().startswith("#"):
            continue

        fields = [field.strip() for field in raw_line.split("\t")]
        if header is None:
            if required.issubset(set(fields)):
                header = fields
            continue

        if not fields or not fields[0].isdigit():
            continue
        if len(fields) < len(header):
            fields.extend([""] * (len(header) - len(fields)))
        rows.append(dict(zip(header, fields[: len(header)])))

    if not rows:
        raise RuntimeError("No Hipparcos rows were parsed from the Vizier response.")

    return rows


def normalize_rows(raw_rows: list[dict[str, str]], name_map: dict[int, str]) -> list[CatalogRow]:
    rows: list[CatalogRow] = []
    for raw in raw_rows:
        hip = int(raw["HIP"])
        ra = parse_float(raw.get("RAICRS"))
        dec = parse_float(raw.get("DEICRS"))
        mag = parse_float(raw.get("Vmag"))
        if hip <= 0 or ra is None or dec is None or mag is None:
            continue
        rows.append(
            CatalogRow(
                hip=hip,
                ra_icrs_deg=ra,
                dec_icrs_deg=dec,
                pmra_mas_per_year=parse_float(raw.get("pmRA")) or 0.0,
                pmdec_mas_per_year=parse_float(raw.get("pmDE")) or 0.0,
                parallax_mas=parse_float(raw.get("Plx")),
                magnitude=mag,
                name=name_map.get(hip, ""),
            )
        )

    if not rows:
        raise RuntimeError("No usable Hipparcos rows were found after normalization.")
    return rows


def write_cache(rows: list[CatalogRow], cache_path: Path) -> None:
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    with cache_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, delimiter="\t")
        writer.writerow(
            [
                "hip",
                "ra_icrs_deg",
                "dec_icrs_deg",
                "pmra_mas_per_year",
                "pmdec_mas_per_year",
                "parallax_mas",
                "magnitude",
                "name",
            ]
        )
        for row in rows:
            writer.writerow(
                [
                    row.hip,
                    f"{row.ra_icrs_deg:.8f}",
                    f"{row.dec_icrs_deg:.8f}",
                    f"{row.pmra_mas_per_year:.6f}",
                    f"{row.pmdec_mas_per_year:.6f}",
                    "" if row.parallax_mas is None else f"{row.parallax_mas:.6f}",
                    f"{row.magnitude:.3f}",
                    row.name,
                ]
            )


def read_cache(cache_path: Path) -> list[CatalogRow]:
    with cache_path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        return [
            CatalogRow(
                hip=int(row["hip"]),
                ra_icrs_deg=float(row["ra_icrs_deg"]),
                dec_icrs_deg=float(row["dec_icrs_deg"]),
                pmra_mas_per_year=float(row["pmra_mas_per_year"]),
                pmdec_mas_per_year=float(row["pmdec_mas_per_year"]),
                parallax_mas=parse_float(row["parallax_mas"]),
                magnitude=float(row["magnitude"]),
                name=row["name"],
            )
            for row in reader
        ]


def load_or_fetch_catalog(cache_path: Path, refresh_cache: bool, name_map: dict[int, str]) -> tuple[list[CatalogRow], bool]:
    if cache_path.exists() and not refresh_cache:
        return read_cache(cache_path), False

    raw_rows = parse_vizier_tsv(fetch_vizier_tsv())
    rows = normalize_rows(raw_rows, name_map)
    write_cache(rows, cache_path)
    return rows, True


def north_celestial_pole_icrs(obstime: Time) -> SkyCoord:
    return SkyCoord(ra=0 * u.deg, dec=90 * u.deg, frame=FK5(equinox=obstime)).transform_to(ICRS())


def build_star_coords(rows: list[CatalogRow]) -> SkyCoord:
    return SkyCoord(
        ra=np.array([row.ra_icrs_deg for row in rows]) * u.deg,
        dec=np.array([row.dec_icrs_deg for row in rows]) * u.deg,
        pm_ra_cosdec=np.array([row.pmra_mas_per_year for row in rows]) * u.mas / u.yr,
        pm_dec=np.array([row.pmdec_mas_per_year for row in rows]) * u.mas / u.yr,
        frame="icrs",
        obstime=CATALOG_EPOCH,
    )


def prefilter_indices(rows: list[CatalogRow], coords: SkyCoord, magnitude_limit: float, band_deg: float) -> np.ndarray:
    magnitudes = np.array([row.magnitude for row in rows], dtype=float)
    ecliptic = coords.transform_to(BarycentricMeanEcliptic(equinox=J2000))
    offsets = np.abs(ecliptic.lat.deg - PRECESSION_CIRCLE_LAT_DEG)
    return np.where((magnitudes <= magnitude_limit) & (offsets <= band_deg))[0]


def scan_best_epochs(
    rows: list[CatalogRow],
    epoch_start: int,
    epoch_end: int,
    epoch_step: int,
    magnitude_limit: float,
    band_deg: float,
) -> tuple[list[CatalogRow], np.ndarray, np.ndarray]:
    if epoch_end < epoch_start:
        raise ValueError("epoch_end must be greater than or equal to epoch_start")
    if epoch_step <= 0:
        raise ValueError("epoch_step must be positive")

    all_coords = build_star_coords(rows)
    candidate_indices = prefilter_indices(rows, all_coords, magnitude_limit=magnitude_limit, band_deg=band_deg)
    if len(candidate_indices) == 0:
        raise RuntimeError("No stars passed the candidate prefilter. Loosen the magnitude or band settings.")

    candidates = [rows[index] for index in candidate_indices]
    candidate_coords = all_coords[candidate_indices]
    best_sep = np.full(len(candidates), np.inf, dtype=float)
    best_year = np.zeros(len(candidates), dtype=int)

    for year in range(epoch_start, epoch_end + 1, epoch_step):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", category=ErfaWarning)
            obstime = Time(float(year), format="jyear", scale="tdb")
            pole = north_celestial_pole_icrs(obstime)
            moved = candidate_coords.apply_space_motion(new_obstime=obstime)
        separation = moved.separation(pole).deg
        improved = separation < best_sep
        best_sep[improved] = separation[improved]
        best_year[improved] = year

    return candidates, best_year, best_sep


def build_results(
    candidates: list[CatalogRow],
    best_year: np.ndarray,
    best_sep: np.ndarray,
    max_sep_deg: float,
    max_results: int,
) -> list[ScanResult]:
    shortlisted: list[tuple[CatalogRow, int, float]] = []
    for row, year, min_sep in zip(candidates, best_year.tolist(), best_sep.tolist()):
        if min_sep <= max_sep_deg:
            shortlisted.append((row, int(year), float(min_sep)))

    if not shortlisted:
        raise RuntimeError("No stars met the final separation threshold. Increase --max-sep-deg.")

    if max_results > 0 and len(shortlisted) > max_results:
        shortlisted = sorted(shortlisted, key=lambda item: item[2])[:max_results]

    shortlisted = sorted(shortlisted, key=lambda item: (item[1], item[2], item[0].magnitude))
    results: list[ScanResult] = []

    for row, year, min_sep in shortlisted:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", category=ErfaWarning)
            j2000_coord = (
                SkyCoord(
                    ra=row.ra_icrs_deg * u.deg,
                    dec=row.dec_icrs_deg * u.deg,
                    pm_ra_cosdec=row.pmra_mas_per_year * u.mas / u.yr,
                    pm_dec=row.pmdec_mas_per_year * u.mas / u.yr,
                    frame="icrs",
                    obstime=CATALOG_EPOCH,
                )
                .apply_space_motion(new_obstime=J2000)
                .transform_to(FK5(equinox=J2000))
            )

        results.append(
            ScanResult(
                hip=row.hip,
                year=year,
                ra_j2000_deg=round(float(j2000_coord.ra.deg), 6),
                dec_j2000_deg=round(float(j2000_coord.dec.deg), 6),
                name=row.name,
                min_sep_deg=round(min_sep, 3),
                magnitude=round(row.magnitude, 2),
            )
        )

    return results


def format_results_json(results: list[ScanResult]) -> str:
    payload = [
        [
            result.year,
            result.ra_j2000_deg,
            result.dec_j2000_deg,
            result.hip,
            result.name,
            result.min_sep_deg,
            result.magnitude,
        ]
        for result in results
    ]
    return json.dumps(payload, indent=2, ensure_ascii=False)


def generate_ssc(
    results: list[ScanResult],
    output_path: Path,
    cache_path: Path,
    rows_fetched: int,
    candidates_scanned: int,
    epoch_start: int,
    epoch_end: int,
    epoch_step: int,
    magnitude_limit: float,
    band_deg: float,
    max_sep_deg: float,
) -> None:
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%SZ")
    data_block = format_results_json(results)
    script = f"""// user-01 · Pole stars over time
// Generated by scripts/user_01_pole_stars_over_time.py on {generated_at}
// Source: Vizier {HIPPARCOS_CATALOG_ID} fetched once and cached locally at {cache_path}
// Method:
//   1. Fetch and normalize the Hipparcos main catalog.
//   2. Prefilter stars by V magnitude <= {magnitude_limit:.2f} and ecliptic-latitude band
//      within ±{band_deg:.1f}° of the north precession circle (~{PRECESSION_CIRCLE_LAT_DEG:.2f}°).
//   3. Scan epochs {epoch_start} to {epoch_end} in {epoch_step}-year steps with Astropy.
//   4. Keep one best-fit row per HIP at its minimum separation from the north celestial pole.
// Data rows use:
//   [year, ra_j2000_deg, dec_j2000_deg, hip, name, min_sep_deg, magnitude]
// Summary:
//   catalog rows cached: {rows_fetched}
//   stars scanned after prefilter: {candidates_scanned}
//   emitted results with min_sep_deg <= {max_sep_deg:.2f}: {len(results)}

var POLE_STARS = {data_block};

var $JD_0 = 1721057.284468;
function BCE(y)  {{ return $JD_0 - (y - 1) * 365.25; }}
function CE(y)   {{ return $JD_0 + y * 365.25; }}
function W(x)    {{ if (!x) x = 0.1; core.wait(x); }}
function toJd(year) {{ return year < 0 ? BCE(-year) : CE(year); }}
function epochStr(year) {{ return year < 0 ? (-year) + " BCE" : year + " CE"; }}

function resetLabels() {{
  LabelMgr.deleteAllLabels();
  MarkerMgr.deleteAllMarkers();
  CustomObjectMgr.removeCustomObjects();
}}

function label(text, x, y, size, color) {{
  var id = LabelMgr.labelScreen(text, x, y, false, size, color);
  LabelMgr.setLabelShow(id, true);
  return id;
}}

function displayName(row) {{
  var name = row[4];
  if (name && name.length > 0) {{
    return name + " (HIP " + row[3] + ")";
  }}
  return "HIP " + row[3];
}}

var _titleLabelId = null;
var _epochLabelId = null;
var _sampleLabelId = null;
var _detailLine1Id = null;
var _detailLine2Id = null;
var _logX = 0;
var _logY = 0;
var _logLineH = 0;

function hideLiveLabels() {{
  if (_epochLabelId !== null) {{ try {{ LabelMgr.setLabelShow(_epochLabelId, false); LabelMgr.deleteLabel(_epochLabelId); }} catch (err) {{}} _epochLabelId = null; }}
  if (_sampleLabelId !== null) {{ try {{ LabelMgr.setLabelShow(_sampleLabelId, false); LabelMgr.deleteLabel(_sampleLabelId); }} catch (err) {{}} _sampleLabelId = null; }}
  if (_detailLine1Id !== null) {{ try {{ LabelMgr.setLabelShow(_detailLine1Id, false); LabelMgr.deleteLabel(_detailLine1Id); }} catch (err) {{}} _detailLine1Id = null; }}
  if (_detailLine2Id !== null) {{ try {{ LabelMgr.setLabelShow(_detailLine2Id, false); LabelMgr.deleteLabel(_detailLine2Id); }} catch (err) {{}} _detailLine2Id = null; }}
}}

function initTourPhase() {{
  var total = POLE_STARS.length;
  _logLineH = Math.max(12, Math.min(16, Math.floor(520 / total)));
  _logX = 80;
  _logY = 208;
  _titleLabelId = label("Pole Stars Over Time", 80, 48, 28, "#22FFFF");
}}

function appendLogRow(row, index) {{
  var rank = (index + 1);
  var rankText = rank < 10 ? "0" + rank : "" + rank;
  var name = row[4];
  if (!name || name.length === 0) {{
    name = "HIP " + row[3];
  }}
  var entry = rankText + ". " + epochStr(row[0]) + "  " + name + "  " + row[5].toFixed(2) + "°";
  label(entry, _logX, _logY, _logLineH, "#CBD5E1");
  _logY += _logLineH + 2;
}}

resetLabels();
core.setGuiVisible(false);
core.setObserverLocation("Kurukshetra, India", "Earth");
LandscapeMgr.setFlagLandscape(false);
LandscapeMgr.setFlagAtmosphere(false);
LandscapeMgr.setFlagFog(false);
ConstellationMgr.setFlagLines(true);
ConstellationMgr.setFlagLabels(false);
ConstellationMgr.setFlagArt(false);
GridLinesMgr.setFlagEquatorGrid(true);
GridLinesMgr.setFlagAzimuthalGrid(false);
GridLinesMgr.setFlagPrecessionCircles(true);
GridLinesMgr.setFlagEclipticLine(false);
GridLinesMgr.setFlagEquatorLine(false);
StelMovementMgr.setEquatorialMount(true);
StelMovementMgr.setFlagTracking(false);

core.setJDay(toJd({results[0].year}));
core.moveToRaDec(0, 89.6, 0);
StelMovementMgr.zoomTo(62, 1.5);
W(1.5);

label("Pole Stars Over Time", 80, 120, 36, "#FFDD88");
label("Precession moves the north celestial pole across the sky.", 80, 176, 20, "#F8FAFC");
label("Astropy scanned the catalog; Stellarium now shows the result.", 80, 208, 20, "#A7F3D0");
W(6);
resetLabels();
initTourPhase();

for (var i = 0; i < POLE_STARS.length; i++) {{
  var row = POLE_STARS[i];
  var year = row[0];
  var hip = row[3];
  var sep = row[5];
  var mag = row[6];
  var objName = "HIP " + hip;

  hideLiveLabels();
  core.setJDay(toJd(year));
  W(0.2);
  core.moveToRaDec(0, 89.6, 0.4);
  W(0.2);

  try {{
    core.selectObjectByName(objName, true);
    W(0.2);
    // Leave a light persistent marker on every visited candidate so the tour builds up on screen.
    MarkerMgr.markerObject(objName, true, "circle", "#93C5FD");
  }} catch (err) {{
  }}

  // Keep the NCP and most of the precession circle in view, with only a gentle zoom pulse.
  StelMovementMgr.zoomTo(56, 1.2);
  W(0.6);
  StelMovementMgr.zoomTo(48, 1.2);

  _epochLabelId = label("Epoch: " + epochStr(year), 80, 92, 22, "#FFD166");
  _sampleLabelId = label("Candidate " + (i + 1) + " / " + POLE_STARS.length, 1040, 56, 16, "#CBD5E1");
  _detailLine1Id = label("Star: " + displayName(row), 80, 124, 18, "#AAFFAA");
  _detailLine2Id = label("Closest pole distance: " + sep.toFixed(2) + "°  |  Magnitude: " + mag.toFixed(2), 80, 154, 18, "#F8FAFC");
  appendLogRow(row, i);
  W(5);
}}

hideLiveLabels();
core.moveToRaDec(0, 89.6, 0.8);
StelMovementMgr.zoomTo(62, 2.0);
label("Precession is the main idea.", 80, _logY + 28, 28, "#FFD166");
label("The pole moves; the best pole-star candidate changes with epoch.", 80, _logY + 66, 18, "#F8FAFC");
label("Astropy is efficient for the scan. Stellarium is clear for the visual story.", 80, _logY + 96, 18, "#A7F3D0");
W(8);
"""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(script, encoding="utf-8")


def print_summary(results: list[ScanResult], cache_path: Path, ssc_path: Path, rows_fetched: int, candidates_scanned: int, fetched_now: bool) -> None:
    print(f"Catalog cache: {cache_path}")
    print(f"Generated SSC: {ssc_path}")
    print(f"Catalog rows available: {rows_fetched}")
    print(f"Candidate stars scanned after prefilter: {candidates_scanned}")
    print()
    print("Emitted rows:")
    for result in results:
        name = result.name if result.name else f"HIP {result.hip}"
        print(
            f"  {result.year:>6}  |  {name:<18}  |  HIP {result.hip:>6}  |  "
            f"sep {result.min_sep_deg:>5.2f} deg  |  Vmag {result.magnitude:>4.2f}"
        )
    print()
    if fetched_now:
        print("Fetched fresh Hipparcos data from Vizier and wrote the local cache.")
    else:
        print("Used the existing local Hipparcos cache.")


def main() -> int:
    args = build_parser().parse_args()
    name_map = load_name_map(args.name_fab)
    rows, fetched_now = load_or_fetch_catalog(args.cache_path, args.refresh_cache, name_map)
    candidates, best_year, best_sep = scan_best_epochs(
        rows=rows,
        epoch_start=args.epoch_start,
        epoch_end=args.epoch_end,
        epoch_step=args.epoch_step,
        magnitude_limit=args.magnitude_limit,
        band_deg=args.prefilter_band_deg,
    )
    results = build_results(
        candidates=candidates,
        best_year=best_year,
        best_sep=best_sep,
        max_sep_deg=args.max_sep_deg,
        max_results=args.max_results,
    )
    generate_ssc(
        results=results,
        output_path=args.output_ssc,
        cache_path=args.cache_path,
        rows_fetched=len(rows),
        candidates_scanned=len(candidates),
        epoch_start=args.epoch_start,
        epoch_end=args.epoch_end,
        epoch_step=args.epoch_step,
        magnitude_limit=args.magnitude_limit,
        band_deg=args.prefilter_band_deg,
        max_sep_deg=args.max_sep_deg,
    )
    print_summary(
        results=results,
        cache_path=args.cache_path,
        ssc_path=args.output_ssc,
        rows_fetched=len(rows),
        candidates_scanned=len(candidates),
        fetched_now=fetched_now,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
