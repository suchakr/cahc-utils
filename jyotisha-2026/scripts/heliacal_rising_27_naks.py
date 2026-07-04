from __future__ import annotations

import csv
import json
import math
import warnings
from dataclasses import dataclass
from pathlib import Path

import astropy.units as u
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from astropy.coordinates import AltAz, EarthLocation, FK5, SkyCoord, get_sun
from astropy.time import Time
from astropy.utils import iers

from jyotisha_2026.paths import LAB_ROOT, REPO_ROOT, upstream_dataset_path


iers.conf.auto_download = False
iers.conf.auto_max_age = None
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=RuntimeWarning)

LATITUDE_DEG = 30.0
LONGITUDE_DEG = 0.0
SUN_ALT_THRESHOLD_DEG = -10.0
EPOCHS = [-1500, -1000, -500]
ECLIPTIC_BAND_LAT_DEG = 5.0
ECLIPTIC_OBLIQUITY_DEG_BCE500 = 23.75
SLUG = "heliacal-rising-27-naks"
VGJ_N83_PATH = REPO_ROOT / "data" / "vgj-seasonal-cycle" / "n83_lat_lon_ra_dec_bce2500_ce1000.tsv"
SKY_CULTURE_ROOT = (REPO_ROOT.parent / "nakshatra_sky_culture" / "vedic_25_codex").resolve()

ASTERISM_LINE_OVERRIDE = {
    "N03-Kri": [["HIP 17499", "HIP 17608", "HIP 17847", "HIP 17702", "HIP 17573", "HIP 17531", "HIP 17499"]],
    "N23-Dha": [["HIP 102281", "HIP 102532", "HIP 101958", "HIP 101769", "HIP 102281"]],
}

NID_SHORT_LABELS = {
    "N01-Ash": "Aśv",
    "N02-Bha": "Bha",
    "N03-Kri": "Kṛt",
    "N04-Roh": "Roh",
    "N05-Mrg": "Mṛg",
    "N06-Ard": "Ārd",
    "N07-Pun": "Pun",
    "N08-Pus": "Puṣ",
    "N09-Asl": "Āśl",
    "N10-Mag": "Mag",
    "N11-PPal": "PPh",
    "N12-UPal": "UPh",
    "N13-Has": "Has",
    "N14-Chi": "Cit",
    "N15-Swa": "Svā",
    "N16-Vis": "Viś",
    "N17-Anu": "Anū",
    "N18-Jye": "Jye",
    "N19-Mul": "Mūl",
    "N20-PAsh": "PAṣ",
    "N21-UAsh": "UAṣ",
    "N22-Shr": "Śrvṇ",
    "N23-Dha": "Śrvṣ",
    "N24-Sha": "Śat",
    "N25-PBha": "PPro",
    "N26-UBha": "UPro",
    "N27-Rev": "Rev",
}


@dataclass(frozen=True)
class NakshatraProxy:
    order: int
    nid: str
    enaks: str
    veethi: str
    proxy: str
    ra_j2000_deg: float
    dec_j2000_deg: float


def load_nakshatra_proxies() -> list[NakshatraProxy]:
    meta_path = upstream_dataset_path("nakshatras", "n27_full_meta.csv")
    star_path = upstream_dataset_path("n90_heliacal_rising_times_for_-1700.csv")

    star_lookup: dict[str, tuple[float, float]] = {}
    with star_path.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            gname = row["gname"]
            if gname not in star_lookup:
                star_lookup[gname] = (float(row["raJ2000"]), float(row["decJ2000"]))

    proxies: list[NakshatraProxy] = []
    with meta_path.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            proxy = row["proxy"]
            ra_deg, dec_deg = star_lookup[proxy]
            proxies.append(
                NakshatraProxy(
                    order=int(row["nnid"]),
                    nid=row["nid"],
                    enaks=row["enaks"],
                    veethi=row["veethi"],
                    proxy=proxy,
                    ra_j2000_deg=ra_deg,
                    dec_j2000_deg=dec_deg,
                )
            )
    return proxies


def day_start(year: int, day_offset: int) -> Time:
    return Time(
        {
            "year": year,
            "month": 1,
            "day": 1,
            "hour": 0,
            "minute": 0,
            "second": 0,
        },
        format="ymdhms",
        scale="utc",
    ) + day_offset * u.day


def event_times_for_year(year: int, location: EarthLocation) -> list[Time]:
    minute_grid = np.arange(0, 12 * 60 + 1, 2)
    times_by_day: list[Time] = []
    for day_offset in range(366):
        start = day_start(year, day_offset)
        grid = start + minute_grid * u.min
        altaz = AltAz(obstime=grid, location=location)
        sun_alt = get_sun(grid).transform_to(altaz).alt.deg
        rising = np.where((sun_alt[:-1] < SUN_ALT_THRESHOLD_DEG) & (sun_alt[1:] >= SUN_ALT_THRESHOLD_DEG))[0]
        if len(rising) == 0:
            continue
        idx = int(rising[0])
        alt0 = sun_alt[idx]
        alt1 = sun_alt[idx + 1]
        frac = 0.0 if alt1 == alt0 else (SUN_ALT_THRESHOLD_DEG - alt0) / (alt1 - alt0)
        event_time = grid[idx] + frac * (grid[idx + 1] - grid[idx])
        times_by_day.append(event_time)
    return times_by_day


def rising_azimuth_from_declination(dec_deg: float, latitude_deg: float) -> float:
    ratio = math.sin(math.radians(dec_deg)) / math.cos(math.radians(latitude_deg))
    ratio = max(-1.0, min(1.0, ratio))
    return math.degrees(math.acos(ratio))


def setting_azimuth_from_declination(dec_deg: float, latitude_deg: float) -> float:
    return 360.0 - rising_azimuth_from_declination(dec_deg, latitude_deg)


def compute_results() -> pd.DataFrame:
    proxies = load_nakshatra_proxies()
    location = EarthLocation(lat=LATITUDE_DEG * u.deg, lon=LONGITUDE_DEG * u.deg)
    rows: list[dict[str, object]] = []

    for epoch in EPOCHS:
        event_times = event_times_for_year(epoch, location)
        for proxy in proxies:
            star = SkyCoord(ra=proxy.ra_j2000_deg * u.deg, dec=proxy.dec_j2000_deg * u.deg, frame="icrs")
            altaz = star.transform_to(AltAz(obstime=event_times, location=location))
            altitudes = altaz.alt.deg
            visible_mask = altitudes > 0
            transitions = np.where(visible_mask & ~np.roll(visible_mask, 1))[0]
            if len(transitions) == 0:
                continue

            day_idx = int(transitions[0])
            event_time = event_times[day_idx]
            declination_deg = star.transform_to(FK5(equinox=event_time)).dec.deg
            rows.append(
                {
                    "epoch": epoch,
                    "nnid": proxy.order,
                    "nid": proxy.nid,
                    "enaks": proxy.enaks,
                    "veethi": proxy.veethi,
                    "proxy": proxy.proxy,
                    "event_date_utc": event_time.utc.isot,
                    "jd_utc": float(event_time.jd),
                    "day_of_year": day_idx + 1,
                    "declination_deg": declination_deg,
                    "rising_azimuth_deg": rising_azimuth_from_declination(declination_deg, LATITUDE_DEG),
                    "star_alt_deg_at_sun_minus_10": altitudes[day_idx],
                }
            )

            reversed_altitudes = visible_mask[::-1]
            reversed_transitions = np.where(reversed_altitudes & ~np.roll(reversed_altitudes, 1))[0]
            if len(reversed_transitions) == 0:
                continue
            setting_day_idx = len(event_times) - 1 - int(reversed_transitions[0])
            setting_time = event_times[setting_day_idx]
            setting_declination_deg = star.transform_to(FK5(equinox=setting_time)).dec.deg
            rows[-1].update(
                {
                    "setting_event_date_utc": setting_time.utc.isot,
                    "setting_jd_utc": float(setting_time.jd),
                    "setting_day_of_year": setting_day_idx + 1,
                    "setting_declination_deg": setting_declination_deg,
                    "setting_azimuth_deg": setting_azimuth_from_declination(setting_declination_deg, LATITUDE_DEG),
                    "star_alt_deg_at_setting_sun_minus_10": altitudes[setting_day_idx],
                }
            )

    frame = pd.DataFrame(rows).sort_values(["epoch", "nnid"]).reset_index(drop=True)
    return frame


def load_or_compute_results(table_path: Path) -> pd.DataFrame:
    if table_path.exists():
        return pd.read_csv(table_path)
    frame = compute_results()
    frame.to_csv(table_path, index=False)
    return frame


VEETHI_COLORS = {
    "Go": "#c7aa72",
    "Naga": "#93b86b",
    "Gaja": "#8fb8d6",
    "Airavati": "#d9b07c",
    "Arshabi": "#b7a1d9",
    "Mrga": "#d4cc74",
    "Ajaavika": "#d99b90",
    "Vaishvaanari": "#d8a164",
    "Jaradgavi": "#8eb0a0",
}


def veethi_runs(frame: pd.DataFrame) -> list[tuple[int, int, str]]:
    base = frame[frame["epoch"] == EPOCHS[0]].sort_values("nnid")[["nnid", "veethi"]].reset_index(drop=True)
    runs: list[tuple[int, int, str]] = []
    start = 0
    current = base.iloc[0]["veethi"]
    for idx in range(1, len(base)):
        veethi = base.iloc[idx]["veethi"]
        if veethi != current:
            runs.append((start, idx - 1, current))
            start = idx
            current = veethi
    runs.append((start, len(base) - 1, current))
    return runs


def plot_metric(
    frame: pd.DataFrame,
    metric: str,
    ylabel: str,
    title: str,
    output_path: Path,
    annotate_veethi: bool = False,
) -> None:
    plt.figure(figsize=(18, 8))
    axis = plt.gca()
    if annotate_veethi:
        y_top = 0.965
        for start, end, veethi in veethi_runs(frame):
            axis.axvspan(start - 0.5, end + 0.5, color=VEETHI_COLORS.get(veethi, "#ccb99a"), alpha=0.33, zorder=0)
            axis.text(
                (start + end) / 2,
                y_top,
                veethi,
                transform=axis.get_xaxis_transform(),
                ha="center",
                va="top",
                fontsize=12,
                color="#3f372b",
                zorder=1,
            )
    for epoch in EPOCHS:
        subset = frame[frame["epoch"] == epoch]
        plt.plot(
            subset["enaks"],
            subset[metric],
            marker="o",
            linewidth=2.2,
            markersize=5.5,
            label=f"{epoch}",
            zorder=3,
        )

    if metric == "rising_azimuth_deg":
        axis.axhline(90, color="#8f4a21", linewidth=1.2, alpha=0.25, linestyle="--")
    if metric == "declination_deg":
        axis.axhline(0, color="#8f4a21", linewidth=1.2, alpha=0.25, linestyle="--")

    plt.title(title, fontsize=22)
    plt.xlabel("Nakṣatra", fontsize=20)
    plt.ylabel(ylabel, fontsize=20)
    plt.xticks(rotation=65, ha="right", fontsize=15)
    plt.yticks(fontsize=17)
    plt.grid(True, alpha=0.25)
    plt.legend(title="Epoch", fontsize=16, title_fontsize=16)
    plt.tight_layout()
    plt.savefig(output_path, dpi=180)
    plt.close()


def load_vgj_n83_glyphs(epoch: int = -500) -> pd.DataFrame:
    glyphs = pd.read_csv(VGJ_N83_PATH, sep="\t")
    glyphs = glyphs[(glyphs["year"] == epoch) & (glyphs["nid"] != "N23-Srvs")].copy()
    glyphs["nnid"] = glyphs["nid"].str.extract(r"N(\d+)-").astype(int)
    glyphs["hip"] = glyphs.apply(hip_for_glyph_row, axis=1)
    return glyphs.sort_values(["nnid", "lon", "lat"]).reset_index(drop=True)


def normalize_hip(value: object) -> str:
    text = str(value).strip()
    if text.startswith("HIP"):
        return "HIP " + text.replace("HIP", "", 1).strip()
    return text


def load_glyph_hip_lookup() -> dict[tuple[str, str], str]:
    lookup: dict[tuple[str, str], str] = {}
    with upstream_dataset_path("n83_full_meta_for_-1750.csv").open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            lookup[(row["nid"], row["gname"])] = normalize_hip(row["hip"])
    return lookup


GLYPH_HIP_LOOKUP = load_glyph_hip_lookup()


def hip_for_glyph_row(row: pd.Series) -> str:
    return GLYPH_HIP_LOOKUP.get((str(row["nid"]), str(row["gname"])), "")


def load_asterism_line_lookup() -> dict[int, list[list[str]]]:
    payload = json.loads((SKY_CULTURE_ROOT / "index.json").read_text(encoding="utf-8"))
    lookup: dict[int, list[list[str]]] = {}
    for item in payload["asterisms"]:
        if not item["id"].startswith("AST vedic_25_codex N"):
            continue
        order = int(item["id"].split("N", 1)[1])
        lookup[order] = [[normalize_hip(f"HIP {hip}") for hip in line] for line in item["lines"]]
    return lookup


def metric_ylim(frame: pd.DataFrame, metric: str) -> tuple[float, float]:
    values = frame[metric].dropna()
    lower = float(values.min())
    upper = float(values.max())
    pad = (upper - lower) * 0.05 if upper > lower else 1.0
    return lower - pad, upper + pad


def plot_metric_a_variant(
    frame: pd.DataFrame,
    metric: str,
    ylabel: str,
    title: str,
    output_path: Path,
    glyphs: pd.DataFrame,
    span_shading_alpha: float = 0.14,
) -> None:
    source_ylim = metric_ylim(frame, metric)
    epoch_frame = frame[frame["epoch"] == -500].sort_values("nnid").reset_index(drop=True)
    epoch_frame["variant_order"] = (epoch_frame["nnid"] - 2) % 27
    epoch_frame = epoch_frame.sort_values("variant_order").reset_index(drop=True)
    colors = plt.colormaps["tab20"](np.linspace(0, 1, 20))

    fig, axis = plt.subplots(figsize=(18, 8), facecolor="white")
    source_ylim = metric_ylim(frame, metric)
    y_span = source_ylim[1] - source_ylim[0]
    display_ylim = (source_ylim[0] - 0.25 * y_span, source_ylim[1])
    glyph_width = 0.8
    glyph_height = 9.0
    label_y = display_ylim[0] + 0.04 * (display_ylim[1] - display_ylim[0])

    if span_shading_alpha > 0:
        for index in range(len(epoch_frame)):
            if index % 2 == 0:
                axis.axvspan(index, index + 1, color="#d8c7a1", alpha=span_shading_alpha, zorder=0)

    for index, row in enumerate(epoch_frame.itertuples()):
        x_center = index + 0.5
        nak_glyph = glyphs[glyphs["nid"] == row.nid].copy()
        if nak_glyph.empty:
            axis.scatter(x_center, getattr(row, metric), c=[colors[int(row.nnid) % len(colors)]], s=100, alpha=0.95, zorder=4)
            continue

        center_lon = float(nak_glyph["lon"].median())
        center_lat = float(nak_glyph["lat"].median())
        lon_delta = (nak_glyph["lon"] - center_lon + 180.0) % 360.0 - 180.0
        lat_delta = nak_glyph["lat"] - center_lat
        lon_span = float(lon_delta.max() - lon_delta.min())
        lat_span = float(lat_delta.max() - lat_delta.min())
        if lon_span > 0:
            nak_glyph["x_plot"] = x_center + (lon_delta - (lon_delta.max() + lon_delta.min()) / 2.0) / lon_span * glyph_width
        else:
            nak_glyph["x_plot"] = x_center
        if lat_span > 0:
            nak_glyph["y_plot"] = getattr(row, metric) + (lat_delta - (lat_delta.max() + lat_delta.min()) / 2.0) / lat_span * glyph_height
        else:
            nak_glyph["y_plot"] = getattr(row, metric)
        color = colors[int(row.nnid) % len(colors)]
        marker = "*" if len(nak_glyph) == 1 else "o"
        size = 187 if len(nak_glyph) == 1 else 100
        axis.scatter(
            nak_glyph["x_plot"],
            nak_glyph["y_plot"],
            c=[color],
            marker=marker,
            s=size,
            alpha=0.95,
            edgecolor="#2c261d",
            linewidth=0.35,
            zorder=4,
        )
        axis.annotate(
            f"{NID_SHORT_LABELS.get(row.nid, row.enaks)}:{len(nak_glyph)}",
            (x_center, getattr(row, metric)),
            xytext=(0, -19 if row.nid == "N19-Mul" else 11),
            textcoords="offset points",
            ha="center",
            va="bottom",
            rotation=90,
            fontsize=15,
            color="purple",
            zorder=5,
        )

    axis.set_title(title, fontsize=22, alpha=0.0)
    axis.set_xlabel("Nakṣatra", fontsize=20)
    axis.set_ylabel(ylabel, fontsize=20)
    axis.set_xlim(0, len(epoch_frame))
    axis.set_ylim(*source_ylim)
    source_yticks = axis.get_yticks()
    axis.set_ylim(*display_ylim)
    axis.set_xticks(range(len(epoch_frame) + 1))
    axis.set_xticklabels([])
    axis.tick_params(axis="x", length=0)
    for index, row in enumerate(epoch_frame.itertuples()):
        axis.text(
            index + 0.5,
            label_y,
            NID_SHORT_LABELS.get(row.nid, row.enaks),
            ha="center",
            va="bottom",
            rotation=90,
            fontsize=22,
            color="#3f372b",
            zorder=5,
        )
    axis.tick_params(axis="y", labelsize=17)
    axis.set_yticks(source_yticks)
    axis.grid(True, alpha=0.25)
    plt.tight_layout()
    plt.savefig(output_path, dpi=180)
    plt.close(fig)


def add_b_variant_positions(
    nak_glyph: pd.DataFrame,
    x_center: float,
    y_center: float,
    glyph_width: float,
    glyph_height: float,
    min_scale: float = 0.38,
    full_scale_span_deg: float = 12.0,
) -> pd.DataFrame:
    positioned = nak_glyph.copy()
    center_lon = float(positioned["lon"].median())
    center_lat = float(positioned["lat"].median())
    lon_delta = (positioned["lon"] - center_lon + 180.0) % 360.0 - 180.0
    lat_delta = positioned["lat"] - center_lat
    lon_centered = lon_delta - (lon_delta.max() + lon_delta.min()) / 2.0
    lat_centered = lat_delta - (lat_delta.max() + lat_delta.min()) / 2.0
    lon_span = float(lon_delta.max() - lon_delta.min())
    lat_span = float(lat_delta.max() - lat_delta.min())
    angular_span = max(lon_span, lat_span, 1.0)
    visual_scale = min(1.0, max(min_scale, angular_span / full_scale_span_deg))
    positioned["x_plot"] = x_center + (lon_centered / angular_span) * glyph_width * visual_scale
    positioned["y_plot"] = y_center + (lat_centered / angular_span) * glyph_height * visual_scale
    return positioned


def sorted_hips_by_fit(hip_to_xy: dict[str, tuple[float, float]]) -> list[str]:
    if len(hip_to_xy) < 2:
        return []
    hips = list(hip_to_xy)
    points = np.array([hip_to_xy[hip] for hip in hips], dtype=float)
    centered = points - points.mean(axis=0)
    if np.allclose(centered, 0):
        return hips
    _, _, vh = np.linalg.svd(centered, full_matrices=False)
    projection = centered @ vh[0]
    return [hip for _, hip in sorted(zip(projection, hips, strict=False))]


def fallback_line_groups(
    hip_to_xy: dict[str, tuple[float, float]],
    source_line_groups: list[list[str]],
) -> list[list[str]]:
    plotted_lines: list[list[str]] = []
    connected_hips: set[str] = set()
    for line_group in source_line_groups:
        drawable = [hip for hip in line_group if hip in hip_to_xy]
        if len(drawable) < 2 or len(set(drawable)) < 2:
            continue
        plotted_lines.append(drawable)
        connected_hips.update(drawable)

    if not plotted_lines:
        fitted = sorted_hips_by_fit(hip_to_xy)
        if len(fitted) >= 2:
            plotted_lines.append(fitted)
            connected_hips.update(fitted)

    for hip in hip_to_xy:
        if hip in connected_hips or len(hip_to_xy) < 2:
            continue
        x0, y0 = hip_to_xy[hip]
        nearest = min(
            (other for other in hip_to_xy if other != hip),
            key=lambda other: (hip_to_xy[other][0] - x0) ** 2 + (hip_to_xy[other][1] - y0) ** 2,
        )
        plotted_lines.append([hip, nearest])
        connected_hips.add(hip)
        connected_hips.add(nearest)

    return plotted_lines


def add_b_reference_guides(axis: plt.Axes, metric: str, display_ylim: tuple[float, float]) -> None:
    if metric == "rising_azimuth_deg":
        reference_y = 90.0
        reference_label = "E"
        lower_label = "N"
        upper_label = "S"
        lower_y = reference_y - 30.0
        upper_y = reference_y + 30.0
    elif metric == "setting_azimuth_deg":
        reference_y = 270.0
        reference_label = "W"
        lower_label = "S"
        upper_label = "N"
        lower_y = reference_y - 30.0
        upper_y = reference_y + 30.0
    elif metric in {"declination_deg", "setting_declination_deg"}:
        reference_y = 0.0
        reference_label = "Eq"
        lower_label = "S"
        upper_label = "N"
        lower_y = display_ylim[0] + 0.5 * (reference_y - display_ylim[0])
        upper_y = reference_y + 0.5 * (display_ylim[1] - reference_y)
    else:
        return

    if not (display_ylim[0] <= reference_y <= display_ylim[1]):
        return

    axis.axhline(reference_y, color="#5e4c34", linewidth=1.25, alpha=0.58, linestyle=(0, (2, 3)), zorder=2)
    axis.annotate(
        reference_label,
        xy=(0, reference_y),
        xytext=(8, 0),
        textcoords="offset points",
        ha="left",
        va="center",
        fontsize=14,
        fontweight="bold",
        color="#4c3f2d",
        zorder=6,
    )

    for label, y_pos in [(lower_label, lower_y), (upper_label, upper_y)]:
        if not (display_ylim[0] <= y_pos <= display_ylim[1]):
            continue
        axis.text(
            0.012,
            y_pos,
            label,
            transform=axis.get_yaxis_transform(),
            ha="left",
            va="center",
            fontsize=14,
            fontweight="bold",
            color="#5e4c34",
            clip_on=True,
            zorder=6,
        )


def ecliptic_declination_deg(lon_deg: np.ndarray, lat_deg: float | np.ndarray = 0.0) -> np.ndarray:
    lon = np.radians(lon_deg)
    lat = np.radians(lat_deg)
    obliquity = math.radians(ECLIPTIC_OBLIQUITY_DEG_BCE500)
    sin_dec = np.sin(lat) * math.cos(obliquity) + np.cos(lat) * math.sin(obliquity) * np.sin(lon)
    return np.degrees(np.arcsin(np.clip(sin_dec, -1.0, 1.0)))


def ecliptic_curve_for_epoch_frame(epoch_frame: pd.DataFrame) -> tuple[np.ndarray, np.ndarray]:
    if len(epoch_frame) < 2:
        return np.array([]), np.array([])
    x_curve = np.linspace(0.5, len(epoch_frame) - 0.5, 900)
    lon_curve = (x_curve - 0.5) * (360.0 / 27.0)
    return x_curve, lon_curve


def azimuth_band_from_declination(metric: str, declination_deg: np.ndarray) -> np.ndarray:
    rise_az = np.array([rising_azimuth_from_declination(float(dec), LATITUDE_DEG) for dec in declination_deg])
    if metric == "setting_azimuth_deg":
        return 360.0 - rise_az
    return rise_az


def add_c_ecliptic_overlay(
    axis: plt.Axes,
    metric: str,
    epoch_frame: pd.DataFrame,
    glyphs: pd.DataFrame,
) -> None:
    x_curve, lon_curve = ecliptic_curve_for_epoch_frame(epoch_frame)
    if len(x_curve) == 0:
        return
    dec_mid = ecliptic_declination_deg(lon_curve, 0.0)
    dec_low = ecliptic_declination_deg(lon_curve, -ECLIPTIC_BAND_LAT_DEG)
    dec_high = ecliptic_declination_deg(lon_curve, ECLIPTIC_BAND_LAT_DEG)
    if metric in {"rising_azimuth_deg", "setting_azimuth_deg"}:
        y_mid = azimuth_band_from_declination(metric, dec_mid)
        y_low = azimuth_band_from_declination(metric, dec_low)
        y_high = azimuth_band_from_declination(metric, dec_high)
        band_label = "ecliptic horizon ±5°"
    elif metric in {"declination_deg", "setting_declination_deg"}:
        y_mid = dec_mid
        y_low = dec_low
        y_high = dec_high
        band_label = "ecliptic ±5°"
    else:
        return

    axis.fill_between(
        x_curve,
        np.minimum(y_low, y_high),
        np.maximum(y_low, y_high),
        color="#6aa6a1",
        alpha=0.16,
        linewidth=0,
        zorder=1,
    )
    axis.plot(
        x_curve,
        y_mid,
        color="#2e7771",
        linewidth=1.55,
        alpha=0.78,
        linestyle=(0, (5, 4)),
        zorder=2.2,
    )
    axis.text(
        x_curve[-1] - 0.2,
        y_mid[-1],
        band_label,
        ha="right",
        va="center",
        fontsize=10,
        color="#2e7771",
        clip_on=True,
        zorder=6,
    )


def bharani_zero_lon(glyphs: pd.DataFrame) -> float:
    bharani = glyphs[glyphs["nid"] == "N02-Bha"]
    if bharani.empty:
        return 0.0
    lon_values = np.radians(bharani["lon"].to_numpy(dtype=float))
    return math.degrees(float(np.angle(np.mean(np.exp(1j * lon_values))) % (2 * math.pi)))


def measured_x_from_lon(lon_deg: pd.Series, zero_lon: float) -> pd.Series:
    sector_width = 360.0 / 27.0
    relative_lon = (lon_deg - zero_lon + 360.0) % 360.0
    return 0.5 + relative_lon / sector_width


def measured_y_for_metric(metric: str, nak_glyph: pd.DataFrame) -> pd.Series:
    if metric in {"declination_deg", "setting_declination_deg"}:
        return nak_glyph["dec"].astype(float)
    if metric == "rising_azimuth_deg":
        return nak_glyph["dec"].astype(float).map(lambda value: rising_azimuth_from_declination(value, LATITUDE_DEG))
    if metric == "setting_azimuth_deg":
        return nak_glyph["dec"].astype(float).map(lambda value: setting_azimuth_from_declination(value, LATITUDE_DEG))
    raise ValueError(f"Unsupported measured metric: {metric}")


def measured_ylim_for_metric(metric: str, frame: pd.DataFrame, glyphs: pd.DataFrame) -> tuple[float, float]:
    if metric in {"declination_deg", "setting_declination_deg"}:
        values = glyphs["dec"].astype(float)
        lower = min(float(values.min()), -ECLIPTIC_OBLIQUITY_DEG_BCE500 - ECLIPTIC_BAND_LAT_DEG)
        upper = max(float(values.max()), ECLIPTIC_OBLIQUITY_DEG_BCE500 + ECLIPTIC_BAND_LAT_DEG)
    elif metric in {"rising_azimuth_deg", "setting_azimuth_deg"}:
        values = measured_y_for_metric(metric, glyphs)
        lower = min(float(values.min()), 90.0 if metric == "rising_azimuth_deg" else 270.0)
        upper = max(float(values.max()), 90.0 if metric == "rising_azimuth_deg" else 270.0)
    else:
        return metric_ylim(frame, metric)
    pad = (upper - lower) * 0.05 if upper > lower else 1.0
    return lower - pad, upper + pad


def plot_metric_stick_variant(
    frame: pd.DataFrame,
    metric: str,
    ylabel: str,
    title: str,
    output_path: Path,
    glyphs: pd.DataFrame,
    asterism_lines: dict[int, list[list[str]]],
    span_shading_alpha: float = 0.14,
    include_ecliptic_overlay: bool = False,
) -> None:
    source_ylim = metric_ylim(frame, metric)
    epoch_frame = frame[frame["epoch"] == -500].sort_values("nnid").reset_index(drop=True)
    epoch_frame["variant_order"] = (epoch_frame["nnid"] - 2) % 27
    epoch_frame = epoch_frame.sort_values("variant_order").reset_index(drop=True)
    colors = plt.colormaps["tab20"](np.linspace(0, 1, 20))

    fig, axis = plt.subplots(figsize=(18, 8), facecolor="white")
    y_span = source_ylim[1] - source_ylim[0]
    display_ylim = (source_ylim[0] - 0.25 * y_span, source_ylim[1])
    glyph_width = 0.82
    glyph_height = 9.2
    label_y = display_ylim[0] + 0.04 * (display_ylim[1] - display_ylim[0])

    if span_shading_alpha > 0:
        for index in range(len(epoch_frame)):
            if index % 2 == 0:
                axis.axvspan(index, index + 1, color="#d8c7a1", alpha=span_shading_alpha, zorder=0)

    if include_ecliptic_overlay:
        add_c_ecliptic_overlay(axis, metric, epoch_frame, glyphs)

    for index, row in enumerate(epoch_frame.itertuples()):
        x_center = index + 0.5
        y_center = getattr(row, metric)
        nak_glyph = glyphs[glyphs["nid"] == row.nid].copy()
        color = colors[int(row.nnid) % len(colors)]
        if nak_glyph.empty:
            axis.scatter(x_center, y_center, c=[color], s=36, alpha=0.95, zorder=4)
            continue

        nak_glyph = add_b_variant_positions(nak_glyph, x_center, y_center, glyph_width, glyph_height)
        hip_to_xy = {
            hip: (float(x_plot), float(y_plot))
            for hip, x_plot, y_plot in zip(nak_glyph["hip"], nak_glyph["x_plot"], nak_glyph["y_plot"], strict=False)
            if hip
        }
        line_groups = fallback_line_groups(
            hip_to_xy,
            ASTERISM_LINE_OVERRIDE.get(row.nid, asterism_lines.get(int(row.nnid), [])),
        )
        for line_group in line_groups:
            points = [hip_to_xy[hip] for hip in line_group if hip in hip_to_xy]
            if len(points) < 2 or len(set(points)) < 2:
                continue
            axis.plot(
                [point[0] for point in points],
                [point[1] for point in points],
                color="#3f372b",
                linewidth=1.15,
                alpha=0.72,
                solid_capstyle="round",
                solid_joinstyle="round",
                zorder=3,
            )

        marker = "*" if len(nak_glyph) == 1 else "o"
        size = 67 if len(nak_glyph) == 1 else 36
        axis.scatter(
            nak_glyph["x_plot"],
            nak_glyph["y_plot"],
            c=[color],
            marker=marker,
            s=size,
            alpha=0.95,
            edgecolor="#2c261d",
            linewidth=0.35,
            zorder=4,
        )

    axis.set_title(title, fontsize=22, alpha=0.0)
    axis.set_xlabel("Nakṣatra", fontsize=20)
    axis.set_ylabel(ylabel, fontsize=20)
    axis.set_xlim(0, len(epoch_frame))
    axis.set_ylim(*source_ylim)
    source_yticks = axis.get_yticks()
    axis.set_ylim(*display_ylim)
    add_b_reference_guides(axis, metric, display_ylim)
    axis.set_xticks(range(len(epoch_frame) + 1))
    axis.set_xticklabels([])
    axis.tick_params(axis="x", length=0)
    for index, row in enumerate(epoch_frame.itertuples()):
        nak_glyph = glyphs[glyphs["nid"] == row.nid]
        axis.text(
            index + 0.5,
            label_y,
            f"{NID_SHORT_LABELS.get(row.nid, row.enaks)}:{len(nak_glyph)}",
            ha="center",
            va="bottom",
            rotation=90,
            fontsize=18,
            color="#3f372b",
            zorder=5,
        )
    axis.tick_params(axis="y", labelsize=17)
    axis.set_yticks(source_yticks)
    axis.grid(True, alpha=0.25)
    plt.tight_layout()
    plt.savefig(output_path, dpi=180)
    plt.close(fig)


def plot_metric_b_variant(
    frame: pd.DataFrame,
    metric: str,
    ylabel: str,
    title: str,
    output_path: Path,
    glyphs: pd.DataFrame,
    asterism_lines: dict[int, list[list[str]]],
    span_shading_alpha: float = 0.14,
) -> None:
    plot_metric_stick_variant(
        frame=frame,
        metric=metric,
        ylabel=ylabel,
        title=title,
        output_path=output_path,
        glyphs=glyphs,
        asterism_lines=asterism_lines,
        span_shading_alpha=span_shading_alpha,
        include_ecliptic_overlay=False,
    )


def plot_metric_c_variant(
    frame: pd.DataFrame,
    metric: str,
    ylabel: str,
    title: str,
    output_path: Path,
    glyphs: pd.DataFrame,
    asterism_lines: dict[int, list[list[str]]],
    span_shading_alpha: float = 0.14,
) -> None:
    plot_metric_stick_variant(
        frame=frame,
        metric=metric,
        ylabel=ylabel,
        title=title,
        output_path=output_path,
        glyphs=glyphs,
        asterism_lines=asterism_lines,
        span_shading_alpha=span_shading_alpha,
        include_ecliptic_overlay=True,
    )


def plot_metric_d_variant(
    frame: pd.DataFrame,
    metric: str,
    ylabel: str,
    title: str,
    output_path: Path,
    glyphs: pd.DataFrame,
    asterism_lines: dict[int, list[list[str]]],
    span_shading_alpha: float = 0.14,
) -> None:
    source_ylim = measured_ylim_for_metric(metric, frame, glyphs)
    epoch_frame = frame[frame["epoch"] == -500].sort_values("nnid").reset_index(drop=True)
    epoch_frame["variant_order"] = (epoch_frame["nnid"] - 2) % 27
    epoch_frame = epoch_frame.sort_values("variant_order").reset_index(drop=True)
    colors = plt.colormaps["tab20"](np.linspace(0, 1, 20))

    fig, axis = plt.subplots(figsize=(18, 8), facecolor="white")
    y_span = source_ylim[1] - source_ylim[0]
    display_ylim = (source_ylim[0] - 0.25 * y_span, source_ylim[1])
    label_y = display_ylim[0] + 0.04 * (display_ylim[1] - display_ylim[0])
    zero_lon = bharani_zero_lon(glyphs)

    if span_shading_alpha > 0:
        for index in range(len(epoch_frame)):
            if index % 2 == 0:
                axis.axvspan(index, index + 1, color="#d8c7a1", alpha=span_shading_alpha, zorder=0)

    add_c_ecliptic_overlay(axis, metric, epoch_frame, glyphs)

    glyph_width = 0.82
    glyph_height = 9.2
    for index, row in enumerate(epoch_frame.itertuples()):
        nak_glyph = glyphs[glyphs["nid"] == row.nid].copy()
        color = colors[int(row.nnid) % len(colors)]
        if nak_glyph.empty:
            continue

        nak_glyph["x_plot"] = measured_x_from_lon(nak_glyph["lon"].astype(float), zero_lon)
        nak_glyph["y_plot"] = measured_y_for_metric(metric, nak_glyph)
        visible_glyph = nak_glyph[(nak_glyph["x_plot"] >= 0.0) & (nak_glyph["x_plot"] <= len(epoch_frame))].copy()
        if visible_glyph.empty:
            continue

        hip_to_xy = {
            hip: (float(x_plot), float(y_plot))
            for hip, x_plot, y_plot in zip(visible_glyph["hip"], visible_glyph["x_plot"], visible_glyph["y_plot"], strict=False)
            if hip
        }
        topology_glyph = add_b_variant_positions(
            nak_glyph,
            x_center=index + 0.5,
            y_center=getattr(row, metric),
            glyph_width=glyph_width,
            glyph_height=glyph_height,
        )
        topology_hip_to_xy = {
            hip: (float(x_plot), float(y_plot))
            for hip, x_plot, y_plot in zip(topology_glyph["hip"], topology_glyph["x_plot"], topology_glyph["y_plot"], strict=False)
            if hip in hip_to_xy
        }
        line_groups = fallback_line_groups(
            topology_hip_to_xy,
            ASTERISM_LINE_OVERRIDE.get(row.nid, asterism_lines.get(int(row.nnid), [])),
        )
        for line_group in line_groups:
            points = [hip_to_xy[hip] for hip in line_group if hip in hip_to_xy]
            if len(points) < 2 or len(set(points)) < 2:
                continue
            axis.plot(
                [point[0] for point in points],
                [point[1] for point in points],
                color="#3f372b",
                linewidth=1.0,
                alpha=0.62,
                solid_capstyle="round",
                solid_joinstyle="round",
                zorder=3,
            )

        marker = "*" if len(visible_glyph) == 1 else "o"
        size = 58 if len(visible_glyph) == 1 else 28
        axis.scatter(
            visible_glyph["x_plot"],
            visible_glyph["y_plot"],
            c=[color],
            marker=marker,
            s=size,
            alpha=0.95,
            edgecolor="#2c261d",
            linewidth=0.32,
            zorder=4,
        )

    axis.set_title(title, fontsize=22, alpha=0.0)
    axis.set_xlabel("Nakṣatra", fontsize=20)
    axis.set_ylabel(ylabel, fontsize=20)
    axis.set_xlim(0, len(epoch_frame))
    axis.set_ylim(*source_ylim)
    source_yticks = axis.get_yticks()
    axis.set_ylim(*display_ylim)
    add_b_reference_guides(axis, metric, display_ylim)
    axis.set_xticks(range(len(epoch_frame) + 1))
    axis.set_xticklabels([])
    axis.tick_params(axis="x", length=0)
    for index, row in enumerate(epoch_frame.itertuples()):
        nak_glyph = glyphs[glyphs["nid"] == row.nid]
        axis.text(
            index + 0.5,
            label_y,
            f"{NID_SHORT_LABELS.get(row.nid, row.enaks)}:{len(nak_glyph)}",
            ha="center",
            va="bottom",
            rotation=90,
            fontsize=18,
            color="#3f372b",
            zorder=5,
        )
    axis.tick_params(axis="y", labelsize=17)
    axis.set_yticks(source_yticks)
    axis.grid(True, alpha=0.25)
    plt.tight_layout()
    plt.savefig(output_path, dpi=180)
    plt.close(fig)


def build_summary(frame: pd.DataFrame) -> str:
    az = frame.pivot(index="enaks", columns="epoch", values="rising_azimuth_deg")
    dec = frame.pivot(index="enaks", columns="epoch", values="declination_deg")
    set_az = frame.pivot(index="enaks", columns="epoch", values="setting_azimuth_deg")

    az_shift = (az[-500] - az[-1500]).sort_values()
    dec_shift = (dec[-500] - dec[-1500]).sort_values()
    set_az_shift = (set_az[-500] - set_az[-1500]).sort_values()

    northmost = az.loc[:, -1500].idxmin()
    southmost = az.loc[:, -1500].idxmax()
    westmost_set = set_az.loc[:, -1500].idxmin()
    eastmost_set = set_az.loc[:, -1500].idxmax()
    strongest_az = az_shift.abs().sort_values(ascending=False).head(3)
    strongest_dec = dec_shift.abs().sort_values(ascending=False).head(3)
    strongest_set_az = set_az_shift.abs().sort_values(ascending=False).head(3)
    strongest_az_text = ", ".join(f"{name} {value:+.2f}°" for name, value in strongest_az.items())
    strongest_dec_text = ", ".join(f"{name} {value:+.2f}°" for name, value in strongest_dec.items())
    strongest_set_az_text = ", ".join(f"{name} {value:+.2f}°" for name, value in strongest_set_az.items())

    lines = [
        "# Summary",
        "",
        f"- Computed for latitude {LATITUDE_DEG:.0f}°N with symmetric heliacal criteria: first morning rise and last evening setting with the Sun at -10° altitude.",
        f"- In the -1500 series, the northernmost rising azimuth is {northmost}, while the southernmost is {southmost}.",
        f"- In the -1500 setting series, the westernmost setting azimuth is {westmost_set}, while the easternmost is {eastmost_set}.",
        f"- Largest azimuth shifts from -1500 to -500 are {strongest_az_text}.",
        f"- Largest setting-azimuth shifts from -1500 to -500 are {strongest_set_az_text}.",
        f"- Largest declination shifts from -1500 to -500 are {strongest_dec_text}.",
        "- The rise/set expansion is geometrically constrained: for a fixed latitude and flat horizon, setting azimuth is largely the complementary horizon expression of the same declination signal, and rise/set declination will often look nearly identical.",
        "- The table includes UTC ISO timestamps and Julian Dates so the event moments can be reused directly in Stellarium or related tools.",
    ]
    return "\n".join(lines) + "\n"


def summary_markdown_to_html(summary_md: str) -> str:
    html_parts: list[str] = []
    in_list = False
    for raw_line in summary_md.splitlines():
        line = raw_line.strip()
        if not line:
            if in_list:
                html_parts.append("</ul>")
                in_list = False
            continue
        if line.startswith("# "):
            if in_list:
                html_parts.append("</ul>")
                in_list = False
            html_parts.append(f"<h3>{line[2:]}</h3>")
            continue
        if line.startswith("- "):
            if not in_list:
                html_parts.append("<ul>")
                in_list = True
            html_parts.append(f"<li>{line[2:]}</li>")
            continue
        if line.startswith("  - "):
            if not in_list:
                html_parts.append("<ul>")
                in_list = True
            html_parts.append(f"<li>{line[4:]}</li>")
            continue
        if in_list:
            html_parts.append("</ul>")
            in_list = False
        html_parts.append(f"<p>{line}</p>")
    if in_list:
        html_parts.append("</ul>")
    return "".join(html_parts)


def preview_table_html(frame: pd.DataFrame) -> str:
    preview = frame.loc[
        :,
        [
            "epoch",
            "enaks",
            "event_date_utc",
            "jd_utc",
            "rising_azimuth_deg",
            "setting_event_date_utc",
            "setting_jd_utc",
            "setting_azimuth_deg",
        ],
    ].copy()
    preview["jd_utc"] = preview["jd_utc"].map(lambda value: f"{value:.6f}")
    preview["setting_jd_utc"] = preview["setting_jd_utc"].map(lambda value: f"{value:.6f}")
    preview["rising_azimuth_deg"] = preview["rising_azimuth_deg"].map(lambda value: f"{value:.2f}")
    preview["setting_azimuth_deg"] = preview["setting_azimuth_deg"].map(lambda value: f"{value:.2f}")
    preview = preview.head(12)
    return preview.to_html(index=False, border=0)


def write_page(summary_html: str, table_html: str) -> None:
    page_path = LAB_ROOT / SLUG / "index.html"
    page_path.write_text(
        f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>27 Nakshatra Heliacal Rising</title>
    <link rel="stylesheet" href="../shared/css/site.css">
  </head>
  <body class="exploration-body">
    <main class="content">
      <section class="flat-section">
        <h2>Azimuth</h2>
        <p class="small-note">At fixed latitude, setting azimuth is largely the complementary horizon expression of the same declination signal driving rising azimuth.</p>
        <div class="comparison-grid">
          <div>
            <h3>Rising</h3>
            <p><img class="asset-preview" src="plots/rising-azimuth-by-nakshatra.png" alt="Rising azimuth by nakshatra and epoch"></p>
          </div>
          <div>
            <h3>Setting</h3>
            <p><img class="asset-preview" src="plots/setting-azimuth-by-nakshatra.png" alt="Setting azimuth by nakshatra and epoch"></p>
          </div>
        </div>
      </section>

      <section class="flat-section">
        <h2>Declination</h2>
        <p class="small-note">Rise and set declination are expected to be very close here, because declination is primarily a property of the star at the event date rather than a separate horizon-side measurement.</p>
        <div class="comparison-grid">
          <div>
            <h3>Rising</h3>
            <p><img class="asset-preview" src="plots/rising-declination-by-nakshatra.png" alt="Rising declination by nakshatra and epoch"></p>
          </div>
          <div>
            <h3>Setting</h3>
            <p><img class="asset-preview" src="plots/setting-declination-by-nakshatra.png" alt="Setting declination by nakshatra and epoch"></p>
          </div>
        </div>
      </section>

      <section class="flat-section">
        <h2>Azimuth A Variant</h2>
        <p class="small-note">Single-epoch -500 view. Each nakshatra is shown as its VGJ-style star cluster centered on the computed azimuth point; no trend or fitted lines are drawn.</p>
        <div class="comparison-grid">
          <div>
            <h3>Rising-A</h3>
            <p><img class="asset-preview" src="plots/rising-a-azimuth-by-nakshatra.png" alt="Rising-A azimuth astrograph variant"></p>
          </div>
          <div>
            <h3>Setting-A</h3>
            <p><img class="asset-preview" src="plots/setting-a-azimuth-by-nakshatra.png" alt="Setting-A azimuth astrograph variant"></p>
          </div>
        </div>
      </section>

      <section class="flat-section">
        <h2>Azimuth B Variant</h2>
        <p class="small-note">Single-epoch -500 view. The A-style star clusters are redrawn with smaller dots, Stellarium skyculture stick figures, and bottom labels showing nakshatra plus star count.</p>
        <div class="comparison-grid">
          <div>
            <h3>Rising-B</h3>
            <p><img class="asset-preview" src="plots/rising-b-azimuth-by-nakshatra.png" alt="Rising-B azimuth astrograph variant"></p>
          </div>
          <div>
            <h3>Setting-B</h3>
            <p><img class="asset-preview" src="plots/setting-b-azimuth-by-nakshatra.png" alt="Setting-B azimuth astrograph variant"></p>
          </div>
        </div>
      </section>

      <section class="flat-section">
        <h2>Azimuth C Variant</h2>
        <p class="small-note">B-style star clusters with a projected horizon-azimuth envelope for the ecliptic and its ±5° latitude band at 30°N.</p>
        <div class="comparison-grid">
          <div>
            <h3>Rising-C</h3>
            <p><img class="asset-preview" src="plots/rising-c-azimuth-by-nakshatra.png" alt="Rising-C azimuth astrograph variant with ecliptic horizon band"></p>
          </div>
          <div>
            <h3>Setting-C</h3>
            <p><img class="asset-preview" src="plots/setting-c-azimuth-by-nakshatra.png" alt="Setting-C azimuth astrograph variant with ecliptic horizon band"></p>
          </div>
        </div>
      </section>

      <section class="flat-section">
        <h2>Azimuth D Variant</h2>
        <p class="small-note">Measured variant. Individual stars are positioned by their -500 ecliptic longitude and declination-derived horizon azimuth, against the same Bharani-zero ecliptic band.</p>
        <div class="comparison-grid">
          <div>
            <h3>Rising-D</h3>
            <p><img class="asset-preview" src="plots/rising-d-azimuth-by-nakshatra.png" alt="Rising-D measured azimuth variant with ecliptic horizon band"></p>
          </div>
          <div>
            <h3>Setting-D</h3>
            <p><img class="asset-preview" src="plots/setting-d-azimuth-by-nakshatra.png" alt="Setting-D measured azimuth variant with ecliptic horizon band"></p>
          </div>
        </div>
      </section>

      <section class="flat-section">
        <h2>Declination A Variant</h2>
        <p class="small-note">Single-epoch -500 view. The same star-cluster convention is centered on the computed declination point for each nakshatra.</p>
        <div class="comparison-grid">
          <div>
            <h3>Rising-A</h3>
            <p><img class="asset-preview" src="plots/rising-a-declination-by-nakshatra.png" alt="Rising-A declination astrograph variant"></p>
          </div>
          <div>
            <h3>Setting-A</h3>
            <p><img class="asset-preview" src="plots/setting-a-declination-by-nakshatra.png" alt="Setting-A declination astrograph variant"></p>
          </div>
        </div>
      </section>

      <section class="flat-section">
        <h2>Declination B Variant</h2>
        <p class="small-note">Single-epoch -500 view. The B convention uses the same bounded star-span scaling for dots and stick figures.</p>
        <div class="comparison-grid">
          <div>
            <h3>Rising-B</h3>
            <p><img class="asset-preview" src="plots/rising-b-declination-by-nakshatra.png" alt="Rising-B declination astrograph variant"></p>
          </div>
          <div>
            <h3>Setting-B</h3>
            <p><img class="asset-preview" src="plots/setting-b-declination-by-nakshatra.png" alt="Setting-B declination astrograph variant"></p>
          </div>
        </div>
      </section>

      <section class="flat-section">
        <h2>Declination C Variant</h2>
        <p class="small-note">B-style star clusters with the ecliptic declination curve and its ±5° ecliptic-latitude band.</p>
        <div class="comparison-grid">
          <div>
            <h3>Rising-C</h3>
            <p><img class="asset-preview" src="plots/rising-c-declination-by-nakshatra.png" alt="Rising-C declination astrograph variant with ecliptic band"></p>
          </div>
          <div>
            <h3>Setting-C</h3>
            <p><img class="asset-preview" src="plots/setting-c-declination-by-nakshatra.png" alt="Setting-C declination astrograph variant with ecliptic band"></p>
          </div>
        </div>
      </section>

      <section class="flat-section">
        <h2>Declination D Variant</h2>
        <p class="small-note">Measured variant. Individual stars are positioned by their -500 ecliptic longitude and true declination, making distance to the ecliptic band directly readable.</p>
        <div class="comparison-grid">
          <div>
            <h3>Rising-D</h3>
            <p><img class="asset-preview" src="plots/rising-d-declination-by-nakshatra.png" alt="Rising-D measured declination variant with ecliptic band"></p>
          </div>
          <div>
            <h3>Setting-D</h3>
            <p><img class="asset-preview" src="plots/setting-d-declination-by-nakshatra.png" alt="Setting-D measured declination variant with ecliptic band"></p>
          </div>
        </div>
      </section>

      <section class="flat-section">
        <h2>Azimuth by Veethi</h2>
        <div class="comparison-grid">
          <div>
            <h3>Rising</h3>
            <p><img class="asset-preview" src="plots/rising-azimuth-by-nakshatra-veethi.png" alt="Rising azimuth by nakshatra and veethi"></p>
          </div>
          <div>
            <h3>Setting</h3>
            <p><img class="asset-preview" src="plots/setting-azimuth-by-nakshatra-veethi.png" alt="Setting azimuth by nakshatra and veethi"></p>
          </div>
        </div>
      </section>

      <section class="flat-section">
        <h2>Declination by Veethi</h2>
        <div class="comparison-grid">
          <div>
            <h3>Rising</h3>
            <p><img class="asset-preview" src="plots/rising-declination-by-nakshatra-veethi.png" alt="Rising declination by nakshatra and veethi"></p>
          </div>
          <div>
            <h3>Setting</h3>
            <p><img class="asset-preview" src="plots/setting-declination-by-nakshatra-veethi.png" alt="Setting declination by nakshatra and veethi"></p>
          </div>
        </div>
      </section>

      <section class="flat-section">
        <div class="section-title-row">
          <h2>Table Preview</h2>
        </div>
        <div class="table-wrap">
          {table_html}
        </div>
        <p class="small-note">Preview truncated to the first 12 rows. Use the CSV link above for the full table.</p>
      </section>

      <section class="flat-section">
        <h2>Narration</h2>
        {summary_html}
      </section>
    </main>
  </body>
</html>
""",
        encoding="utf-8",
    )


def main() -> None:
    out_dir = LAB_ROOT / SLUG
    plots_dir = out_dir / "plots"
    tables_dir = out_dir / "tables"
    narration_dir = out_dir / "narration"
    plots_dir.mkdir(parents=True, exist_ok=True)
    tables_dir.mkdir(parents=True, exist_ok=True)
    narration_dir.mkdir(parents=True, exist_ok=True)

    frame = load_or_compute_results(tables_dir / "heliacal-rising-27-naks.csv")
    glyphs = load_vgj_n83_glyphs(-500)
    asterism_lines = load_asterism_line_lookup()

    plot_metric(
        frame,
        metric="rising_azimuth_deg",
        ylabel="Rising Azimuth (deg from north)",
        title="27 Nakshatra Heliacal Rising: Rising Azimuth at 30°N",
        output_path=plots_dir / "rising-azimuth-by-nakshatra.png",
    )
    plot_metric(
        frame,
        metric="rising_azimuth_deg",
        ylabel="Rising Azimuth (deg from north)",
        title="27 Nakshatra Heliacal Rising: Rising Azimuth at 30°N with Veethi Bands",
        output_path=plots_dir / "rising-azimuth-by-nakshatra-veethi.png",
        annotate_veethi=True,
    )
    plot_metric(
        frame,
        metric="setting_azimuth_deg",
        ylabel="Setting Azimuth (deg from north)",
        title="27 Nakshatra Heliacal Setting: Setting Azimuth at 30°N",
        output_path=plots_dir / "setting-azimuth-by-nakshatra.png",
    )
    plot_metric(
        frame,
        metric="setting_azimuth_deg",
        ylabel="Setting Azimuth (deg from north)",
        title="27 Nakshatra Heliacal Setting: Setting Azimuth at 30°N with Veethi Bands",
        output_path=plots_dir / "setting-azimuth-by-nakshatra-veethi.png",
        annotate_veethi=True,
    )
    plot_metric_a_variant(
        frame,
        metric="rising_azimuth_deg",
        ylabel="Rising Azimuth (deg from north)",
        title="Rising-A Azimuth: -500 Nakshatra Astrograph Variant",
        output_path=plots_dir / "rising-a-azimuth-by-nakshatra.png",
        glyphs=glyphs,
    )
    plot_metric_a_variant(
        frame,
        metric="setting_azimuth_deg",
        ylabel="Setting Azimuth (deg from north)",
        title="Setting-A Azimuth: -500 Nakshatra Astrograph Variant",
        output_path=plots_dir / "setting-a-azimuth-by-nakshatra.png",
        glyphs=glyphs,
    )
    plot_metric_b_variant(
        frame,
        metric="rising_azimuth_deg",
        ylabel="Rising Azimuth (deg from north)",
        title="Rising-B Azimuth: -500 Nakshatra Astrograph Variant",
        output_path=plots_dir / "rising-b-azimuth-by-nakshatra.png",
        glyphs=glyphs,
        asterism_lines=asterism_lines,
    )
    plot_metric_b_variant(
        frame,
        metric="setting_azimuth_deg",
        ylabel="Setting Azimuth (deg from north)",
        title="Setting-B Azimuth: -500 Nakshatra Astrograph Variant",
        output_path=plots_dir / "setting-b-azimuth-by-nakshatra.png",
        glyphs=glyphs,
        asterism_lines=asterism_lines,
    )
    plot_metric_c_variant(
        frame,
        metric="rising_azimuth_deg",
        ylabel="Rising Azimuth (deg from north)",
        title="Rising-C Azimuth: -500 Nakshatra Astrograph Variant with Ecliptic Band",
        output_path=plots_dir / "rising-c-azimuth-by-nakshatra.png",
        glyphs=glyphs,
        asterism_lines=asterism_lines,
    )
    plot_metric_c_variant(
        frame,
        metric="setting_azimuth_deg",
        ylabel="Setting Azimuth (deg from north)",
        title="Setting-C Azimuth: -500 Nakshatra Astrograph Variant with Ecliptic Band",
        output_path=plots_dir / "setting-c-azimuth-by-nakshatra.png",
        glyphs=glyphs,
        asterism_lines=asterism_lines,
    )
    plot_metric_d_variant(
        frame,
        metric="rising_azimuth_deg",
        ylabel="Rising Azimuth (deg from north)",
        title="Rising-D Azimuth: -500 Measured Nakshatra Variant with Ecliptic Band",
        output_path=plots_dir / "rising-d-azimuth-by-nakshatra.png",
        glyphs=glyphs,
        asterism_lines=asterism_lines,
    )
    plot_metric_d_variant(
        frame,
        metric="setting_azimuth_deg",
        ylabel="Setting Azimuth (deg from north)",
        title="Setting-D Azimuth: -500 Measured Nakshatra Variant with Ecliptic Band",
        output_path=plots_dir / "setting-d-azimuth-by-nakshatra.png",
        glyphs=glyphs,
        asterism_lines=asterism_lines,
    )
    plot_metric(
        frame,
        metric="declination_deg",
        ylabel="Declination (deg)",
        title="27 Nakshatra Heliacal Rising: Declination at Heliacal Event",
        output_path=plots_dir / "rising-declination-by-nakshatra.png",
    )
    plot_metric(
        frame,
        metric="declination_deg",
        ylabel="Declination (deg)",
        title="27 Nakshatra Heliacal Rising: Declination at Heliacal Event with Veethi Bands",
        output_path=plots_dir / "rising-declination-by-nakshatra-veethi.png",
        annotate_veethi=True,
    )
    plot_metric(
        frame,
        metric="setting_declination_deg",
        ylabel="Declination (deg)",
        title="27 Nakshatra Heliacal Setting: Declination at Heliacal Event",
        output_path=plots_dir / "setting-declination-by-nakshatra.png",
    )
    plot_metric(
        frame,
        metric="setting_declination_deg",
        ylabel="Declination (deg)",
        title="27 Nakshatra Heliacal Setting: Declination at Heliacal Event with Veethi Bands",
        output_path=plots_dir / "setting-declination-by-nakshatra-veethi.png",
        annotate_veethi=True,
    )
    plot_metric_a_variant(
        frame,
        metric="declination_deg",
        ylabel="Declination (deg)",
        title="Rising-A Declination: -500 Nakshatra Astrograph Variant",
        output_path=plots_dir / "rising-a-declination-by-nakshatra.png",
        glyphs=glyphs,
    )
    plot_metric_a_variant(
        frame,
        metric="setting_declination_deg",
        ylabel="Declination (deg)",
        title="Setting-A Declination: -500 Nakshatra Astrograph Variant",
        output_path=plots_dir / "setting-a-declination-by-nakshatra.png",
        glyphs=glyphs,
    )
    plot_metric_b_variant(
        frame,
        metric="declination_deg",
        ylabel="Declination (deg)",
        title="Rising-B Declination: -500 Nakshatra Astrograph Variant",
        output_path=plots_dir / "rising-b-declination-by-nakshatra.png",
        glyphs=glyphs,
        asterism_lines=asterism_lines,
    )
    plot_metric_b_variant(
        frame,
        metric="setting_declination_deg",
        ylabel="Declination (deg)",
        title="Setting-B Declination: -500 Nakshatra Astrograph Variant",
        output_path=plots_dir / "setting-b-declination-by-nakshatra.png",
        glyphs=glyphs,
        asterism_lines=asterism_lines,
    )
    plot_metric_c_variant(
        frame,
        metric="declination_deg",
        ylabel="Declination (deg)",
        title="Rising-C Declination: -500 Nakshatra Astrograph Variant with Ecliptic Band",
        output_path=plots_dir / "rising-c-declination-by-nakshatra.png",
        glyphs=glyphs,
        asterism_lines=asterism_lines,
    )
    plot_metric_c_variant(
        frame,
        metric="setting_declination_deg",
        ylabel="Declination (deg)",
        title="Setting-C Declination: -500 Nakshatra Astrograph Variant with Ecliptic Band",
        output_path=plots_dir / "setting-c-declination-by-nakshatra.png",
        glyphs=glyphs,
        asterism_lines=asterism_lines,
    )
    plot_metric_d_variant(
        frame,
        metric="declination_deg",
        ylabel="Declination (deg)",
        title="Rising-D Declination: -500 Measured Nakshatra Variant with Ecliptic Band",
        output_path=plots_dir / "rising-d-declination-by-nakshatra.png",
        glyphs=glyphs,
        asterism_lines=asterism_lines,
    )
    plot_metric_d_variant(
        frame,
        metric="setting_declination_deg",
        ylabel="Declination (deg)",
        title="Setting-D Declination: -500 Measured Nakshatra Variant with Ecliptic Band",
        output_path=plots_dir / "setting-d-declination-by-nakshatra.png",
        glyphs=glyphs,
        asterism_lines=asterism_lines,
    )

    summary_md = build_summary(frame)
    (narration_dir / "summary.md").write_text(summary_md, encoding="utf-8")
    summary_html = summary_markdown_to_html(summary_md)
    table_html = preview_table_html(frame)
    write_page(summary_html, table_html)


if __name__ == "__main__":
    main()
