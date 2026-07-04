from __future__ import annotations

import html
import json
import re
from dataclasses import dataclass
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.interpolate import interp1d

from jyotisha_2026.paths import LAB_ROOT, REPO_ROOT


SLUG = "vgj-seasonal-cycle"
TITLE = "VGJ Seasonal Nakshatra Cycle"
DATA_ROOT = REPO_ROOT / "data" / SLUG
OUT_ROOT = LAB_ROOT / SLUG
PLOTS_DIR = OUT_ROOT / "plots"
TABLES_DIR = OUT_ROOT / "tables"
NARRATION_DIR = OUT_ROOT / "narration"
SKY_CULTURE_ROOT = (REPO_ROOT.parent / "nakshatra_sky_culture" / "vedic_25_codex").resolve()

SEED_FILES = {
    "divisions": "n27_lon_divisions.csv",
    "n83": "n83_lat_lon_ra_dec_bce2500_ce1000.tsv",
    "n83_mag": "n83_mag.tsv",
    "base": "n27_base_Feb24_bce2500_to_ce0500.tsv",
    "feb20_delta": "n27_delta_Feb20_bce2500_to_ce0500.tsv",
    "shr_dha_delta": "n27_delta_shr_dha_bce2500_to_ce0500.tsv",
    "abhyankar_delta": "n27_delta_abhyankar_bce2500_to_ce0500.tsv",
}

ASHADHA_PATCH_NIDS = {"N20-PAsh", "N21-UAsh"}
SHR_DHA_NIDS = {"N22-Shr", "N23-Dha"}
ABHYANKAR_NIDS = {"N10-Mag", "N13-Has", "N18-Jye", "N19-Mul", "N20-PAsh", "N21-UAsh", "N24-Sha", "N27-Rev"}
SEASONAL_NIDS = ["N27-Rev", "N04-Roh", "N05-Mrg", "N09-Asl", "N13-Has", "N14-Chi", "N18-Jye", "N22-Shr", "N23-Dha"]
STAR_FIELD_EPOCHS = [-1500, -1000, -500]
ASTERISM_LINE_OVERRIDE = {
    "N03-Kri": [["HIP 17499", "HIP 17608", "HIP 17847", "HIP 17702", "HIP 17531", "HIP 17499"]],
    "N23-Dha": [["HIP 102281", "HIP 102532", "HIP 101958", "HIP 101769", "HIP 102281"]],
}
PLOT_COLORS = {
    "N27 base": "#7b3f1d",
    "N83 stars": "#2f6f73",
    "Seasonal 9": "#9166a8",
    "Base": "#7b3f1d",
    "Base shifted": "#c8322c",
    "Ādityacāra: 27 proxy": "#7b3f1d",
    "Ṛtusvabhāva: 27 proxy": "#c8322c",
    "Ṛtusvabhāva: 9 seasonal": "#9166a8",
    "Shr/Dha sensitivity": "#2f6f73",
    "Abhyankar-style": "#b06b23",
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
class SeriesSpec:
    key: str
    label: str
    frame: str
    frame_df: pd.DataFrame


def read_seed(name: str) -> pd.DataFrame:
    path = DATA_ROOT / SEED_FILES[name]
    sep = "\t" if path.suffix == ".tsv" else ","
    return pd.read_csv(path, sep=sep)


def normalize_hip(value: str) -> str:
    return " ".join(str(value).split())


def nid_order(nid: str) -> int:
    match = re.match(r"N(\d+)-", str(nid))
    return int(match.group(1)) if match else 999


def geometry_order_for_vgj_nid(nid: str) -> int:
    order = nid_order(nid)
    return order + 1 if order >= 22 else order


def load_asterism_lines_by_nid() -> dict[str, list[list[str]]]:
    data = json.loads((SKY_CULTURE_ROOT / "index.json").read_text(encoding="utf-8"))
    lines_by_geometry_order: dict[int, list[list[str]]] = {}
    for item in data["asterisms"]:
        if not str(item["id"]).startswith("AST vedic_25_codex N"):
            continue
        geometry_order = int(str(item["id"]).split("N", 1)[1])
        lines_by_geometry_order[geometry_order] = [
            [f"HIP {hip_num}" for hip_num in line]
            for line in item.get("lines", [])
        ]

    lines_by_nid: dict[str, list[list[str]]] = {}
    for order in range(1, 28):
        nid = next((key for key in NID_SHORT_LABELS if nid_order(key) == order), "")
        if not nid:
            continue
        lines_by_nid[nid] = lines_by_geometry_order.get(geometry_order_for_vgj_nid(nid), [])
    lines_by_nid.update(ASTERISM_LINE_OVERRIDE)
    return lines_by_nid


def circular_delta_deg(value: float, target: float) -> float:
    return (value - target + 180.0) % 360.0 - 180.0


def circular_abs_deg(value: float, target: float) -> float:
    return abs(circular_delta_deg(value, target))


def interval_error_deg(value: float, start: float, end: float) -> float:
    span = (end - start) % 360.0
    position = (value - start) % 360.0
    if position <= span:
        return 0.0
    return min(circular_abs_deg(value, start), circular_abs_deg(value, end))


def load_divisions() -> pd.DataFrame:
    divisions = read_seed("divisions").copy()
    divisions["order"] = divisions["nid"].map(nid_order)
    divisions = divisions.sort_values("order").reset_index(drop=True)
    divisions["label"] = divisions["nid"].str.replace(r"^N\d+-", "", regex=True)
    divisions["r_eq"] = divisions["Eq"].shift(1)
    divisions.loc[0, "r_eq"] = divisions.loc[len(divisions) - 1, "Eq"]
    divisions["l_eq"] = divisions["Eq"]
    divisions["r_rtus"] = (divisions["r_eq"] - 350.0) % 360.0
    divisions["l_rtus"] = (divisions["l_eq"] - 350.0) % 360.0
    return divisions


def with_boundary_errors(frame: pd.DataFrame, divisions: pd.DataFrame) -> pd.DataFrame:
    merged = frame.merge(
        divisions[["nid", "order", "label", "r_eq", "l_eq", "r_rtus", "l_rtus"]],
        on="nid",
        how="left",
    )
    merged["order"] = merged["order"].fillna(merged["nid"].map(nid_order))
    merged["label"] = merged["label"].fillna(merged["nid"].str.replace(r"^N\d+-", "", regex=True))
    merged["err_eq_deg"] = [
        interval_error_deg(row.lon, row.r_eq, row.l_eq) for row in merged.itertuples()
    ]
    merged["err_rtus_deg"] = [
        interval_error_deg(row.lon, row.r_rtus, row.l_rtus) for row in merged.itertuples()
    ]
    merged["inside_eq"] = merged["err_eq_deg"].eq(0.0)
    merged["inside_rtus"] = merged["err_rtus_deg"].eq(0.0)
    return merged.sort_values(["year", "order", "gname"]).reset_index(drop=True)


def replace_nids(base: pd.DataFrame, replacement: pd.DataFrame, nids: set[str]) -> pd.DataFrame:
    years = sorted(set(base["year"]).intersection(set(replacement["year"])))
    base_keep = base[~base["nid"].isin(nids) & base["year"].isin(years)]
    repl_keep = replacement[replacement["nid"].isin(nids) & replacement["year"].isin(years)]
    return pd.concat([base_keep, repl_keep], ignore_index=True).sort_values(["year", "nid"])


def build_scenarios(divisions: pd.DataFrame) -> dict[str, pd.DataFrame]:
    base_raw = read_seed("base")
    feb20 = read_seed("feb20_delta")
    shr_dha = read_seed("shr_dha_delta")
    abhyankar = read_seed("abhyankar_delta")

    base = replace_nids(base_raw, feb20, ASHADHA_PATCH_NIDS)
    sensitivity = replace_nids(base, shr_dha, SHR_DHA_NIDS)
    abhyankar_nids = ABHYANKAR_NIDS | SHR_DHA_NIDS
    abhyankar_style = replace_nids(base, pd.concat([shr_dha, abhyankar], ignore_index=True), abhyankar_nids)

    return {
        "base": with_boundary_errors(base, divisions),
        "sensitivity": with_boundary_errors(sensitivity, divisions),
        "abhyankar": with_boundary_errors(abhyankar_style, divisions),
    }


def build_n83(divisions: pd.DataFrame) -> pd.DataFrame:
    n83 = read_seed("n83")
    mag = read_seed("n83_mag")[["nid", "gname", "mag"]]
    n83 = n83.merge(mag, on=["nid", "gname"], how="left")
    hip_lookup_path = REPO_ROOT.parent / "datasets" / "n83_full_meta_for_-1750.csv"
    if hip_lookup_path.exists():
        hip_lookup = pd.read_csv(hip_lookup_path)[["nid", "gname", "hip"]].copy()
        hip_lookup["hip"] = hip_lookup["hip"].map(normalize_hip)
        n83 = n83.merge(hip_lookup, on=["nid", "gname"], how="left")
    else:
        n83["hip"] = ""
    n83["mag"] = n83["mag"].fillna(4.8)
    return with_boundary_errors(n83, divisions)


def aggregate_error(frame: pd.DataFrame, value_col: str, label: str, frame_label: str) -> pd.DataFrame:
    grouped = (
        frame.groupby("year", as_index=False)
        .agg(mean_error_deg=(value_col, "mean"), median_error_deg=(value_col, "median"), inside_count=(value_col, lambda s: int((s == 0).sum())), n=("nid", "count"))
        .sort_values("year")
    )
    grouped["series"] = label
    grouped["frame"] = frame_label
    return grouped


def best_window(series: pd.DataFrame) -> tuple[int, float, int, int, int]:
    best = series.loc[series["mean_error_deg"].idxmin()]
    threshold = float(best["mean_error_deg"]) + 1.0
    near = series[series["mean_error_deg"] <= threshold].sort_values("year")
    return (
        int(best["year"]),
        float(best["mean_error_deg"]),
        int(near["year"].min()),
        int(near["year"].max()),
        int(len(near)),
    )


def plot_error_curves(curves: list[pd.DataFrame], title: str, output_path: Path, ylabel: str = "Mean boundary error (deg)") -> None:
    plt.figure(figsize=(14, 7.6))
    axis = plt.gca()
    for index, curve in enumerate(curves):
        label = str(curve["series"].iloc[0])
        color = PLOT_COLORS.get(label, None)
        linestyle = ":" if "N83" in label else "--" if "Seasonal" in label else "-"
        marker = "o" if len(curve) <= 12 else None
        axis.plot(
            curve["year"],
            curve["mean_error_deg"],
            linewidth=2.6,
            linestyle=linestyle,
            marker=marker,
            markersize=5.5,
            color=color,
            label=label,
        )
        best_year, best_error, start, end, _ = best_window(curve)
        axis.scatter([best_year], [best_error], s=70, color=color, zorder=4)
        offset_options = [(22, 28), (28, -38), (-72, 22), (-80, -34)]
        axis.annotate(
            f"{best_year}\n{best_error:.2f}°",
            xy=(best_year, best_error),
            xytext=offset_options[index % len(offset_options)],
            textcoords="offset points",
            fontsize=10,
            color=color or "#2d2a24",
            arrowprops={
                "arrowstyle": "-",
                "color": color or "#777777",
                "alpha": 0.45,
                "linewidth": 0.9,
            },
        )
        axis.axvspan(start, end, color=color or "#999999", alpha=0.06)

    axis.axvline(-1500, color="#000000", linewidth=1.0, alpha=0.12)
    axis.axvline(-1000, color="#000000", linewidth=1.0, alpha=0.12)
    axis.grid(True, alpha=0.24)
    axis.set_title(title, fontsize=20)
    axis.set_xlabel("Epoch year", fontsize=15)
    axis.set_ylabel(ylabel, fontsize=15)
    axis.tick_params(axis="both", labelsize=12)
    axis.legend(title="Frame", fontsize=12, title_fontsize=12)
    plt.tight_layout()
    plt.savefig(output_path, dpi=180)
    plt.close()


def legacy_axis_style(axis: plt.Axes, ymax: float = 15.0) -> None:
    major_xticks = np.arange(-2500, 501, 250)
    major_yticks = np.arange(0, 36, 5)
    axis.set_xticks(major_xticks)
    axis.set_yticks(major_yticks)
    axis.set_xticklabels([str(x) for x in major_xticks], rotation=0, fontsize=18)
    axis.set_yticklabels([f"{int(y)}°" for y in major_yticks], rotation=0, fontsize=18)
    axis.set_ylim(0, ymax)
    axis.set_xlim(-2500, 500)
    axis.minorticks_on()
    axis.yaxis.grid(which="major", linestyle="-", linewidth=1.1, color="gray", alpha=0.75)
    axis.yaxis.grid(which="minor", linestyle=":", linewidth=0.75, color="gray", alpha=0.65)
    axis.xaxis.grid(which="major", linestyle="-", linewidth=1.1, color="gray", alpha=0.75)
    axis.xaxis.grid(which="minor", linestyle=":", linewidth=0.75, color="gray", alpha=0.65)
    axis.set_xlabel("")
    axis.set_ylabel("")
    axis.set_facecolor("white")


def plot_fig1_epoch_error(
    n27_curve: pd.DataFrame,
    n83_curve: pd.DataFrame,
    seasonal_curve: pd.DataFrame,
    rtus_curve: pd.DataFrame,
    output_path: Path,
) -> None:
    fig, axis = plt.subplots(figsize=(25, 10), facecolor="white")
    ylim = 15
    n83_plot = n83_curve[(n83_curve["mean_error_deg"] <= ylim) & (n83_curve["year"] <= -250)]
    n27_plot = n27_curve[(n27_curve["mean_error_deg"] <= ylim) & (n27_curve["year"] <= -250)]
    seasonal_plot = seasonal_curve[
        (seasonal_curve["mean_error_deg"] <= ylim) & (seasonal_curve["year"] <= -250)
    ]
    rtus_plot = rtus_curve[(rtus_curve["mean_error_deg"] <= ylim) & (rtus_curve["year"] >= -1500)]

    axis.plot(n83_plot["year"], n83_plot["mean_error_deg"], "--", color="green", linewidth=2.0)
    axis.plot(n27_plot["year"], n27_plot["mean_error_deg"], "-", color="green", linewidth=2.4)
    axis.plot(seasonal_plot["year"], seasonal_plot["mean_error_deg"], "-.", color="green", linewidth=2.4)
    axis.plot(rtus_plot["year"], rtus_plot["mean_error_deg"], "-", color="red", linewidth=2.4)

    axis.annotate("83 STARS", (-1250, 12.0), fontsize=24, color="black")
    axis.plot([-900, -750], [12.25, 12.25], linestyle="--", linewidth=3, color="black")
    axis.annotate("27 NAKṢATRA", (-1250, 11.0), fontsize=24, color="black")
    axis.plot([-800, -650], [11.25, 11.25], linestyle="-", linewidth=3, color="black")
    axis.annotate("9 SEASONAL NAKṢATRA", (-1250, 10.0), fontsize=24, color="black")
    axis.plot([-550, -450], [10.25, 10.25], linestyle="-.", linewidth=3, color="black")
    axis.annotate("ṚTUSVABHĀVA", (0, 8.3), fontsize=28, color="red")
    axis.annotate("ĀDITYACĀRA", (-2450, 11.0), fontsize=28, color="green")
    axis.annotate("YEAR", (-2453, 0.2), fontsize=24, color="black")
    axis.annotate("POSITION ERROR", (-2475, 3.0), fontsize=24, color="black", rotation=90)
    legacy_axis_style(axis, ymax=15)
    plt.tight_layout()
    plt.savefig(output_path, dpi=180, bbox_inches="tight")
    plt.close(fig)


def plot_fig2_sensitivity(
    sensitivity_curve: pd.DataFrame,
    seasonal_curve: pd.DataFrame,
    abhyankar_curve: pd.DataFrame,
    output_path: Path,
) -> None:
    fig, axis = plt.subplots(figsize=(25, 10), facecolor="white")
    axis.plot(sensitivity_curve["year"], sensitivity_curve["mean_error_deg"], "-", color="green", linewidth=2.4)
    axis.plot(seasonal_curve["year"], seasonal_curve["mean_error_deg"], "-.", color="green", linewidth=3.0)
    axis.plot(abhyankar_curve["year"], abhyankar_curve["mean_error_deg"], ":", color="green", linewidth=4.0)
    axis.annotate("27 NAKṢATRA", (-1500, 11.0), fontsize=24, color="black")
    axis.plot([-1050, -900], [11.25, 11.25], linestyle="-", linewidth=3, color="black")
    axis.annotate("9 SEASONAL NAKṢATRA", (-1500, 10.0), fontsize=24, color="black")
    axis.plot([-800, -650], [10.25, 10.25], linestyle="-.", linewidth=3, color="black")
    axis.annotate("ABHYANKAR'S YOGATĀRĀ", (-1500, 9.0), fontsize=24, color="black")
    axis.plot([-750, -600], [9.25, 9.25], linestyle=":", linewidth=3, color="black")
    axis.annotate("ĀDITYACĀRA", (-2450, 12.5), fontsize=28, color="green")
    axis.annotate("YEAR", (-2453, 0.2), fontsize=24, color="black")
    axis.annotate("POSITION ERROR", (-2475, 2.8), fontsize=24, color="black", rotation=90)
    legacy_axis_style(axis, ymax=15)
    plt.tight_layout()
    plt.savefig(output_path, dpi=180, bbox_inches="tight")
    plt.close(fig)


def short_nid_label(nid: str) -> str:
    nid = str(nid)
    key = re.sub(r"^N\d+-", "", nid)
    return NID_SHORT_LABELS.get(nid, key)


def nakshatra_tick_positions() -> np.ndarray:
    return np.arange(0, 360, 360 / 27)


def stacked_degree_minute_label(value: float) -> str:
    total_minutes = int(round(value * 60))
    degrees = total_minutes // 60
    minutes = total_minutes % 60
    return f"{degrees}$^\\circ$\n{minutes:02d}$^\\prime$"


def not_a_knot_cubic_interp(x_values: np.ndarray, y_values: np.ndarray, x_new: np.ndarray) -> np.ndarray:
    order = np.argsort(x_values)
    xs = np.asarray(x_values, dtype=float)[order]
    ys = np.asarray(y_values, dtype=float)[order]
    keep = np.concatenate([[True], np.diff(xs) > 1e-9])
    xs = xs[keep]
    ys = ys[keep]
    count = len(xs)
    if count < 4:
        return np.interp(x_new, xs, ys)

    h = np.diff(xs)
    matrix = np.zeros((count, count))
    rhs = np.zeros(count)

    matrix[0, 0] = -h[1]
    matrix[0, 1] = h[0] + h[1]
    matrix[0, 2] = -h[0]
    for idx in range(1, count - 1):
        matrix[idx, idx - 1] = h[idx - 1]
        matrix[idx, idx] = 2 * (h[idx - 1] + h[idx])
        matrix[idx, idx + 1] = h[idx]
        rhs[idx] = 6 * ((ys[idx + 1] - ys[idx]) / h[idx] - (ys[idx] - ys[idx - 1]) / h[idx - 1])
    matrix[-1, -3] = -h[-1]
    matrix[-1, -2] = h[-2] + h[-1]
    matrix[-1, -1] = -h[-2]

    second = np.linalg.solve(matrix, rhs)
    x_new = np.asarray(x_new, dtype=float)
    interval = np.searchsorted(xs, x_new, side="right") - 1
    interval = np.clip(interval, 0, count - 2)
    x0 = xs[interval]
    x1 = xs[interval + 1]
    y0 = ys[interval]
    y1 = ys[interval + 1]
    m0 = second[interval]
    m1 = second[interval + 1]
    span = x1 - x0
    left = x1 - x_new
    right = x_new - x0
    return (
        m0 * left**3 / (6 * span)
        + m1 * right**3 / (6 * span)
        + (y0 - m0 * span**2 / 6) * left / span
        + (y1 - m1 * span**2 / 6) * right / span
    )


def plot_fig3_n83_lon_lat(
    n83: pd.DataFrame,
    epoch: int,
    output_path: Path,
    start_lon: float = 330.0,
    show_month_season_guides: bool = True,
    show_rtusvabhava_label: bool = True,
    label_actual_longitudes: bool = True,
    guide_origin: str = "actual",
    show_fitted_line: bool = True,
    show_nakshatra_connection: bool = False,
    show_astrographs: bool = False,
    show_moon_path_band: bool = False,
    highlight_single_stars: bool = False,
    longitude_label_x: float = 3.5,
    longitude_label_y: float = -36.8,
    month_label_y_offset: float = 0.0,
    civil_month_label_y_offset: float = 0.0,
    season_guide_y_offset: float = 0.0,
    ylim: tuple[float, float] = (-38.0, 38.0),
    yticks: np.ndarray | None = None,
    figsize: tuple[float, float] = (25.0, 10.0),
    nak_label_fontsize: float = 20.0,
    month_label_fontsize: float = 16.0,
    season_label_fontsize: float = 18.0,
    tick_label_fontsize: float = 22.0,
    axis_label_fontsize: float = 21.0,
    latitude_label_fontsize: float = 22.0,
) -> None:
    frame = n83[n83["year"] == epoch].copy()
    frame = frame[frame["nid"] != "N23-Srvs"].copy()
    frame["plot_lon"] = (frame["lon"] - start_lon) % 360.0
    frame = frame.sort_values(["order", "plot_lon", "lat"])
    fig, axis = plt.subplots(figsize=figsize, facecolor="white")
    if show_moon_path_band:
        axis.axhspan(-5, 5, color="#7a7a7a", alpha=0.12, zorder=0)
    colors = plt.colormaps["tab20"](np.linspace(0, 1, 20))
    single_star_nids: set[str] = set()
    if highlight_single_stars:
        single_star_nids = set(frame.groupby("nid")["gname"].count().loc[lambda counts: counts == 1].index)
    dot_frame = frame[~frame["nid"].isin(single_star_nids)]
    point_colors = [colors[int(order) % len(colors)] for order in dot_frame["order"]]
    axis.scatter(dot_frame["plot_lon"], dot_frame["lat"], c=point_colors, s=100, alpha=0.82)
    if highlight_single_stars:
        single_stars = frame[frame["nid"].isin(single_star_nids)]
        single_star_colors = [colors[int(order) % len(colors)] for order in single_stars["order"]]
        axis.scatter(
            single_stars["plot_lon"],
            single_stars["lat"],
            c=single_star_colors,
            edgecolor="#2c261d",
            marker="*",
            s=187,
            linewidth=0.35,
            alpha=0.82,
            zorder=5,
        )

    if show_astrographs:
        asterism_lines_by_nid = load_asterism_lines_by_nid()
        point_lookup = {
            normalize_hip(row.hip): (float(row.plot_lon), float(row.lat))
            for row in frame.dropna(subset=["hip"]).itertuples()
            if normalize_hip(row.hip)
        }
        for nid, line_groups in asterism_lines_by_nid.items():
            for line in line_groups:
                points = [point_lookup[hip] for hip in line if hip in point_lookup]
                if len(points) < 2:
                    continue
                x_values = np.asarray([point[0] for point in points], dtype=float)
                y_values = np.asarray([point[1] for point in points], dtype=float)
                if x_values.max() - x_values.min() > 180:
                    x_values = np.where(x_values < 180, x_values + 360, x_values)
                color = "#243746" if nid != "N15-Swa" else "#7a3f98"
                axis.plot(
                    x_values,
                    y_values,
                    color=color,
                    linewidth=1.35,
                    alpha=0.56,
                    solid_capstyle="round",
                    solid_joinstyle="round",
                    zorder=2,
                )
                axis.plot(
                    x_values - 360,
                    y_values,
                    color=color,
                    linewidth=1.35,
                    alpha=0.56,
                    solid_capstyle="round",
                    solid_joinstyle="round",
                    zorder=2,
                )

    n27_mean = (
        frame.groupby(["nid", "order"], as_index=False)
        .agg(plot_lon=("plot_lon", "median"), lat=("lat", "median"), cnt=("gname", "count"))
        .sort_values("plot_lon")
    )
    if show_nakshatra_connection:
        connection = n27_mean.sort_values("plot_lon")
        connection_lon_series = connection["plot_lon"].copy()
        if 14 in connection_lon_series.index:
            connection_lon_series.loc[14] = connection_lon_series.loc[14] + 10
        connection_lat_series = connection["lat"].copy()
        connection_order = np.argsort(connection_lon_series.to_numpy())
        connection_lon = connection_lon_series.to_numpy()[connection_order]
        connection_lat = connection_lat_series.to_numpy()[connection_order]
        connection_x = np.arange(connection_lon.min(), connection_lon.max(), 1)
        connection_y = interp1d(connection_lon, connection_lat, kind="cubic")(connection_x)
        axis.plot(
            connection_x,
            connection_y,
            color="#5c5c5c",
            linewidth=2.0,
            linestyle=(0, (2, 5)),
            alpha=0.48,
            zorder=1,
        )

    lon_lat_label_adjustments = {
        "N15-Swa": {"x": 0.0, "y": -13.0},
        "N22-Shr": {"x": -3.0, "y": -13.0},
        "N23-Dha": {"x": 3.0, "y": -13.0},
    }
    for row in n27_mean.itertuples():
        label = f"{short_nid_label(row.nid)}:{row.cnt}"
        adjustment = lon_lat_label_adjustments.get(row.nid, {})
        x_offset = adjustment.get("x", 0.0)
        y_offset = adjustment.get("y", 10 if row.lat >= 0 else -10)
        axis.annotate(
            label,
            (row.plot_lon + x_offset, row.lat + y_offset),
            fontsize=nak_label_fontsize,
            color="purple",
            va="center",
            ha="center",
            rotation=90,
        )

    if show_month_season_guides:
        vedic_months = "madhu mādhava śuci śukra nabhaḥ nabhasya iṣa ūrja sahas sahasya tapas tapasya".split()
        civil_months = "caitra vaiśākha jyeṣṭha āṣāḍha śrāvaṇa bhādrapada āśvayuja kārtika mārgaśira pauṣa māgha phālguna".split()
        guide_shift = start_lon if guide_origin == "actual" else 0.0
        for lon, vedic, civil in zip(np.linspace(0, 330, 12), vedic_months, civil_months):
            text_x = (lon + 345 - guide_shift) % 360
            axis.annotate(vedic.upper(), (text_x, -31.2 + month_label_y_offset), fontsize=month_label_fontsize, color="blue", ha="center", va="top")
            axis.annotate(civil.upper(), (text_x, -34.0 + month_label_y_offset + civil_month_label_y_offset), fontsize=month_label_fontsize, color="black", ha="center", va="top")

        rtu_spans = [
            ("vasanta", 330.0, 30.0),
            ("grīṣma", 30.0, 90.0),
            ("varṣā", 90.0, 150.0),
            ("śarat", 150.0, 210.0),
            ("hemanta", 210.0, 270.0),
            ("śiśira", 270.0, 330.0),
        ]
        for label, start, end in rtu_spans:
            start_x = (start - guide_shift) % 360
            end_x = (end - guide_shift) % 360
            mid_x = ((start + ((end - start) % 360) / 2.0) - guide_shift) % 360
            text_y = (32.0 if guide_origin == "display" else 30.0) + season_guide_y_offset
            if guide_origin == "display" and end < start:
                mid_x = ((start + 15.0) - guide_shift) % 360
            axis.plot(
                [start_x, start_x],
                [20 + season_guide_y_offset, 38 + season_guide_y_offset],
                linestyle="-.",
                linewidth=3,
                color="#4c4c4c",
            )
            axis.plot(
                [end_x, end_x],
                [20 + season_guide_y_offset, 38 + season_guide_y_offset],
                linestyle="-.",
                linewidth=3,
                color="#4c4c4c",
            )
            axis.annotate(label.upper(), (mid_x, text_y), fontsize=season_label_fontsize, color="black", ha="center", va="center")
            if guide_origin == "display" and end < start:
                wrapped_mid_x = (((end - start) % 360) / 4.0 - guide_shift) % 360
                axis.annotate(
                    label.upper(),
                    (wrapped_mid_x, text_y),
                    fontsize=season_label_fontsize,
                    color="black",
                    ha="center",
                    va="center",
                )

    if show_fitted_line:
        smooth = n27_mean.sort_values("plot_lon")
        smooth_lon_series = smooth["plot_lon"].copy()
        if 14 in smooth_lon_series.index:
            smooth_lon_series.loc[14] = smooth_lon_series.loc[14] + 10
        smooth_lat_series = smooth["lat"].copy()
        smooth_order = np.argsort(smooth_lon_series.to_numpy())
        smooth_lon = smooth_lon_series.to_numpy()[smooth_order]
        smooth_lat = smooth_lat_series.to_numpy()[smooth_order]
        smooth_x = np.arange(smooth_lon.min(), smooth_lon.max(), 1)
        smooth_y = interp1d(smooth_lon, smooth_lat, kind="cubic")(smooth_x)
        axis.plot(smooth_x, smooth_y, linewidth=2.0, color="olive")
    axis.axhline(0, color="#4c4c4c", linewidth=1.4)
    axis.axhline(-30, color="#4c4c4c", linewidth=1.0, alpha=0.5)
    axis.axhline(30, color="#4c4c4c", linewidth=1.0, alpha=0.5)
    axis.set_xlim(0, 360)
    axis.set_ylim(*ylim)
    xspan = np.linspace(0, 360, 13)
    yspan = yticks if yticks is not None else np.linspace(-30, 30, 7)
    axis.set_xticks(xspan)
    if label_actual_longitudes:
        xtick_labels = [f"{int((x + start_lon) % 360)}°" for x in xspan]
    else:
        xtick_labels = [f"{int(x)}°" for x in xspan]
    axis.set_xticklabels(xtick_labels, fontsize=tick_label_fontsize)
    axis.set_yticks(yspan)
    axis.set_yticklabels([f"{int(y)}°" for y in yspan], fontsize=tick_label_fontsize)
    axis.annotate("LONGITUDE", (longitude_label_x, longitude_label_y), fontsize=axis_label_fontsize, color="black", va="center", ha="center")
    axis.annotate("LATITUDE", (4.6, -15), fontsize=latitude_label_fontsize, color="black", va="bottom", ha="center", rotation=90)
    if show_rtusvabhava_label:
        axis.annotate(f"ṚTUSVABHĀVA\n({epoch})", (220, 20), fontsize=30, color="red", ha="left")
    axis.set_xlabel("")
    axis.set_ylabel("")
    axis.grid(True)
    plt.tight_layout()
    plt.savefig(output_path, dpi=180, bbox_inches="tight")
    plt.close(fig)


def plot_fig3a_n83_ra_dec(
    n83: pd.DataFrame,
    epoch: int,
    output_path: Path,
    show_rtus_label: bool = True,
) -> None:
    frame = n83[n83["year"] == epoch].copy()
    frame = frame[frame["nid"] != "N23-Srvs"].copy()
    frame["ra_plot"] = frame["ra"].where(frame["ra"] >= 0, frame["ra"] + 360)
    frame = frame.sort_values(["order", "ra_plot", "dec"])
    fig, axis = plt.subplots(figsize=(25, 10), facecolor="white")
    colors = plt.colormaps["tab20"](np.linspace(0, 1, 20))
    point_colors = [colors[int(order) % len(colors)] for order in frame["order"]]
    axis.scatter(frame["ra_plot"], frame["dec"], c=point_colors, s=100, alpha=0.82)

    n27_mean = (
        frame.groupby(["nid", "order"], as_index=False)
        .agg(ra_plot=("ra_plot", "median"), dec=("dec", "median"), cnt=("gname", "count"))
        .sort_values("ra_plot")
    )
    for row in n27_mean.itertuples():
        label = f"{short_nid_label(row.nid)}:{row.cnt}"
        y_offset = 10 if row.dec >= 0 else -10
        if row.nid == "N19-Mul":
            y_offset = 12
        axis.annotate(
            label,
            (row.ra_plot, row.dec + y_offset),
            fontsize=20,
            color="purple",
            va="center",
            ha="center",
            rotation=90,
        )

    vedic_months = "madhu mādhava śuci śukra nabhaḥ nabhasya iṣa ūrja sahas sahasya tapas tapasya".split()
    civil_months = "caitra vaiśākha jyeṣṭha āṣāḍha śrāvaṇa bhādrapada āśvayuja kārtika mārgaśira pauṣa māgha phālguna".split()
    for ra_value, vedic, civil in zip(np.linspace(0, 330, 12), vedic_months, civil_months):
        text_x = (ra_value + 15) % 360
        axis.annotate(vedic.upper(), (text_x, -49), fontsize=16, color="blue", ha="center", va="top")
        axis.annotate(civil.upper(), (text_x, -54), fontsize=16, color="black", ha="center", va="top")

    rtu_labels = ["vasanta", "grīṣma", "varṣā", "śarat", "hemanta", "śiśira"]
    for rtu_ra, label in zip(np.linspace(0, 300, 6), rtu_labels):
        axis.plot([rtu_ra, rtu_ra], [38, 58], linestyle="-.", linewidth=3, color="#4c4c4c")
        axis.plot([rtu_ra + 60, rtu_ra + 60], [38, 58], linestyle="-.", linewidth=3, color="#4c4c4c")
        axis.annotate(label.upper(), (rtu_ra + 30, 49), fontsize=18, color="black", ha="center", va="center")

    smooth = n27_mean.sort_values("ra_plot")
    smooth_ra = smooth["ra_plot"].to_numpy()
    smooth_dec = smooth["dec"].to_numpy()
    smooth_x = np.arange(smooth_ra.min(), smooth_ra.max(), 1)
    smooth_y = interp1d(smooth_ra, smooth_dec, kind="cubic")(smooth_x)
    axis.plot(smooth_x, smooth_y, linewidth=2.0, color="olive")
    axis.axhline(0, color="#4c4c4c", linewidth=1.4)
    axis.set_xlim(0, 360)
    axis.set_ylim(-59, 59)
    xspan = np.arange(0, 361, 30)
    yspan = np.arange(-40, 41, 20)
    axis.set_xticks(xspan)
    axis.set_xticklabels([f"{int(x)}°" for x in xspan], fontsize=22)
    axis.set_yticks(yspan)
    axis.set_yticklabels([f"{int(y)}°" for y in yspan], fontsize=22)
    axis.annotate("DECLINATION", (4.6, -25), fontsize=22, color="black", va="bottom", ha="center", rotation=90)
    if show_rtus_label:
        axis.annotate(f"ṚTUSVABHĀVA\n({epoch})", (220, 28), fontsize=30, color="red", ha="left")
    axis.set_xlabel("RIGHT ASCENSION", fontsize=20, labelpad=18, loc="left")
    axis.set_ylabel("")
    axis.grid(True)
    fig.subplots_adjust(bottom=0.16, top=0.96, left=0.055, right=0.985)
    plt.savefig(output_path, dpi=180, bbox_inches="tight")
    plt.close(fig)


def plot_star_field(n83: pd.DataFrame, x_col: str, y_col: str, output_path: Path, title: str, xlabel: str, ylabel: str) -> None:
    fig, axes = plt.subplots(len(STAR_FIELD_EPOCHS), 1, figsize=(18, 11.4), sharex=False)
    for axis, epoch in zip(axes, STAR_FIELD_EPOCHS):
        subset = n83[n83["year"] == epoch].copy()
        sizes = np.clip((5.3 - subset["mag"]) ** 2 * 12, 16, 140)
        axis.scatter(subset[x_col], subset[y_col], s=sizes, c=subset["order"], cmap="viridis", alpha=0.78, edgecolor="#2c261d", linewidth=0.25)
        for row in subset[subset["gname"].isin(["α Tau", "α Leo", "α Sco", "β Del", "β Aqr"])].itertuples():
            axis.annotate(row.gname, (getattr(row, x_col), getattr(row, y_col)), xytext=(4, 4), textcoords="offset points", fontsize=8)
        axis.axhline(0, color="#8f4a21", linewidth=1.0, alpha=0.25, linestyle="--")
        if x_col == "lon":
            for guide in nakshatra_tick_positions():
                axis.axvline(guide, color="#000000", linewidth=0.5, alpha=0.08)
            axis.set_xlim(0, 360)
            clusters = (
                subset.groupby(["nid", "order"], as_index=False)
                .agg(lon=("lon", "median"), lat=("lat", "median"))
                .sort_values("order")
            )
            for row in clusters.itertuples():
                axis.annotate(
                    short_nid_label(row.nid),
                    (row.lon, row.lat),
                    xytext=(0, 8 if row.lat >= 0 else -11),
                    textcoords="offset points",
                    ha="center",
                    va="bottom" if row.lat >= 0 else "top",
                    fontsize=8,
                    color="#5f2f7e",
                    bbox={
                        "boxstyle": "round,pad=0.12",
                        "facecolor": "white",
                        "edgecolor": "none",
                        "alpha": 0.62,
                    },
                )
            ticks = nakshatra_tick_positions()
            axis.set_xticks(ticks)
            axis.set_xticklabels([stacked_degree_minute_label(tick) for tick in ticks], fontsize=7.5)
        axis.set_title(f"{epoch}", fontsize=14, loc="left")
        axis.grid(True, alpha=0.16)
        axis.set_ylabel(ylabel, fontsize=11)
        axis.set_xlabel(xlabel, fontsize=11)
    fig.suptitle(title, fontsize=19)
    plt.tight_layout()
    plt.savefig(output_path, dpi=180)
    plt.close()


def plot_bound_fit(frame: pd.DataFrame, output_path: Path) -> None:
    counts = (
        frame.groupby("year", as_index=False)
        .agg(inside_eq=("inside_eq", "sum"), inside_rtus=("inside_rtus", "sum"), n=("nid", "count"))
        .sort_values("year")
    )
    years = counts["year"].to_numpy()
    max_count = int(counts["n"].max())
    fig, axes = plt.subplots(2, 1, figsize=(16, 10.5), sharex=True)

    def draw_panel(axis: plt.Axes, values: np.ndarray, title: str, color: str) -> None:
        axis.bar(
            years,
            values,
            width=38,
            color=color,
            alpha=0.16,
            edgecolor=color,
            linewidth=0.7,
            label="sampled years",
        )
        smooth_x = np.arange(years.min(), years.max() + 1, 1)
        smooth_y = interp1d(years, values, kind="cubic")(smooth_x)
        axis.plot(smooth_x, smooth_y, color=color, linewidth=2.8, label="smoothed count")
        axis.scatter(years, values, color=color, s=42, zorder=3)
        for year, value in zip(years, values):
            axis.annotate(
                f"{int(value)}",
                (year, value),
                xytext=(0, 6),
                textcoords="offset points",
                ha="center",
                va="bottom",
                fontsize=8,
                color="#3d2b1f",
            )
        axis.axhline(max_count, color="#2f2b24", linestyle="--", linewidth=1.0, alpha=0.28)
        axis.set_ylim(0, max_count + 2)
        axis.set_title(title, fontsize=16, loc="left")
        axis.set_ylabel("Representatives inside bound", fontsize=12)
        axis.grid(True, axis="y", alpha=0.26)
        axis.grid(True, axis="x", which="major", alpha=0.14)
        axis.legend(fontsize=10, loc="upper right")

    draw_panel(
        axes[0],
        counts["inside_eq"].to_numpy(),
        "Ādityacāra: representatives inside equal nakshatra divisions",
        "#7b3f1d",
    )
    draw_panel(
        axes[1],
        counts["inside_rtus"].to_numpy(),
        "Ṛtusvabhāva: representatives inside shifted seasonal divisions",
        "#2f6f73",
    )

    axes[-1].set_xlim(years.min() - 80, years.max() + 80)
    major_ticks = np.arange(-2500, 501, 250)
    minor_ticks = np.arange(-2500, 501, 100)
    axes[-1].set_xticks(major_ticks)
    axes[-1].set_xticklabels([str(int(tick)) for tick in major_ticks], fontsize=11)
    axes[-1].set_xticks(minor_ticks, minor=True)
    axes[-1].set_xticklabels([str(int(tick)) for tick in minor_ticks], minor=True, rotation=90, fontsize=7)
    axes[-1].tick_params(axis="x", which="minor", pad=18, length=2)
    axes[-1].set_xlabel("Epoch year", fontsize=15)
    fig.suptitle("Nakshatra Bound Fit: Base Representatives Inside Their Assigned Divisions", fontsize=20)
    plt.subplots_adjust(bottom=0.16, left=0.08, right=0.98, top=0.9, hspace=0.28)
    plt.savefig(output_path, dpi=180)
    plt.close()


def plot_month_cycle(divisions: pd.DataFrame, output_path: Path) -> pd.DataFrame:
    months = [
        "Madhu", "Madhava", "Sukra", "Suci", "Nabhas", "Nabhasya",
        "Isa", "Urja", "Sahas", "Sahasya", "Tapas", "Tapasya",
    ]
    civil_months = [
        "Chaitra", "Vaishakha", "Jyeshtha", "Ashadha", "Shravana", "Bhadrapada",
        "Ashvayuja", "Kartika", "Margashira", "Pausha", "Magha", "Phalguna",
    ]
    seasons = ["Vasanta", "Grisma", "Varsa", "Sarad", "Hemanta", "Sisira"]
    rows = []
    for idx, (month, civil_month) in enumerate(zip(months, civil_months)):
        start = idx * 30.0
        mid = start + 15.0
        rows.append(
            {
                "month_index": idx + 1,
                "month": month,
                "civil_month": civil_month,
                "season": seasons[idx // 2],
                "start_lon_deg": start,
                "mid_lon_deg": mid,
            }
        )
    month_df = pd.DataFrame(rows)

    fig, axis = plt.subplots(figsize=(14, 4.6))
    for row in month_df.itertuples():
        axis.barh(0, 30, left=row.start_lon_deg, height=0.42, color="#d7b596" if row.month_index % 2 else "#b8c5a7", edgecolor="#4b3b28", linewidth=0.6)
        axis.text(
            row.mid_lon_deg,
            0,
            f"{row.month}\n{row.civil_month}",
            ha="center",
            va="center",
            fontsize=8.5,
            linespacing=1.2,
        )
    for row in divisions.itertuples():
        axis.axvline(row.l_eq, color="#7b3f1d", alpha=0.25, linewidth=0.8)
        if row.order in {1, 4, 7, 10, 13, 16, 19, 22, 25}:
            axis.text(row.l_eq, 0.36, row.label, rotation=65, ha="left", va="bottom", fontsize=8, color="#4f4536")
    for guide in range(0, 361, 90):
        axis.axvline(guide, color="#000000", alpha=0.18, linestyle="--", linewidth=1.0)
    axis.set_xlim(0, 360)
    axis.set_ylim(-0.6, 0.75)
    axis.set_yticks([])
    axis.set_xlabel("Ecliptic longitude (deg)", fontsize=12)
    axis.set_title("Solar Transit / Twelve-Month Cycle Staged Against Nakshatra Bounds", fontsize=18)
    plt.tight_layout()
    plt.savefig(output_path, dpi=180)
    plt.close()
    return month_df


def markdown_to_html(markdown: str) -> str:
    parts: list[str] = []
    in_list = False
    for raw in markdown.splitlines():
        line = raw.strip()
        if not line:
            if in_list:
                parts.append("</ul>")
                in_list = False
            continue
        if line.startswith("# "):
            if in_list:
                parts.append("</ul>")
                in_list = False
            parts.append(f"<h3>{html.escape(line[2:])}</h3>")
        elif line.startswith("- "):
            if not in_list:
                parts.append("<ul>")
                in_list = True
            parts.append(f"<li>{html.escape(line[2:])}</li>")
        else:
            if in_list:
                parts.append("</ul>")
                in_list = False
            parts.append(f"<p>{html.escape(line)}</p>")
    if in_list:
        parts.append("</ul>")
    return "\n".join(parts)


def table_preview(frame: pd.DataFrame, columns: list[str] | None = None, rows: int = 10) -> str:
    preview = frame if columns is None else frame.loc[:, columns]
    return preview.head(rows).to_html(index=False, border=0, classes="preview-table")


def image_html(src: str, alt: str) -> str:
    return f'<p><img class="asset-preview" src="{src}" alt="{html.escape(alt)}"></p>'


def section_image_html(src_item: str | tuple[str, str, str], alt: str) -> str:
    if isinstance(src_item, tuple):
        label, src, note = src_item
        note_html = f'<p class="small-note">{html.escape(note)}</p>' if note else ""
        return f"""<div class="chart-item">
          <h3>{html.escape(label)}</h3>
          {note_html}
          {image_html(src, f"{alt} {label}")}
        </div>"""
    return image_html(src_item, alt)


def build_summary(minima: pd.DataFrame, windows: pd.DataFrame, source_files: pd.DataFrame) -> str:
    base = minima[(minima["series"] == "Base") & (minima["frame"] == "Ādityacāra/equal")].iloc[0]
    seasonal = minima[(minima["series"] == "Seasonal 9") & (minima["frame"] == "Ādityacāra/equal")].iloc[0]
    n83 = minima[(minima["series"] == "N83 stars") & (minima["frame"] == "Ādityacāra/equal")].iloc[0]
    abhy = minima[(minima["series"] == "Abhyankar-style") & (minima["frame"] == "Ādityacāra/equal")].iloc[0]
    base_win = windows[(windows["series"] == "Base") & (windows["frame"] == "Ādityacāra/equal")].iloc[0]
    lines = [
        "# Summary",
        "",
        f"- Base 27-proxy fit reaches its lowest mean boundary error near {int(base.best_year)} with {base.best_mean_error_deg:.2f} degrees mean error.",
        f"- The strongest base window, defined as within 1 degree of that minimum, spans {int(base_win.window_start_year)} to {int(base_win.window_end_year)}.",
        f"- The nine seasonal representatives are most compact near {int(seasonal.best_year)} with {seasonal.best_mean_error_deg:.2f} degrees mean error.",
        f"- The coarse 83-star family has its best sampled epoch at {int(n83.best_year)}; because the seed is sampled every 500 years, this is a broad qualitative check rather than a fine minimum.",
        f"- Abhyankar-style substitutions move the scenario minimum to {int(abhy.best_year)} with {abhy.best_mean_error_deg:.2f} degrees mean error, so representative choice remains a visible sensitivity.",
        "- The solar month-cycle panel is staged from the vendored nakshatra-bound seed and is explicitly not an Astropy-regenerated transit calculation.",
        f"- The source-file table lists {len(source_files)} local seed files used for this Stage 1 reconstruction.",
        "- Qualitative validation: the reproduced chart family keeps the expected broad BCE minimum window and preserves the interpretability of the representative-star sensitivity comparisons.",
    ]
    return "\n".join(lines) + "\n"


def source_files_table() -> pd.DataFrame:
    roles = {
        "n27_lon_divisions.csv": "canonical seed",
        "n83_lat_lon_ra_dec_bce2500_ce1000.tsv": "canonical seed",
        "n83_mag.tsv": "validation-only",
        "n27_base_Feb24_bce2500_to_ce0500.tsv": "canonical seed",
        "n27_delta_Feb20_bce2500_to_ce0500.tsv": "canonical patch seed",
        "n27_delta_shr_dha_bce2500_to_ce0500.tsv": "canonical scenario seed",
        "n27_delta_abhyankar_bce2500_to_ce0500.tsv": "canonical scenario seed",
    }
    rows = []
    for filename, role in roles.items():
        path = DATA_ROOT / filename
        rows.append(
            {
                "file": filename,
                "role": role,
                "local_path": f"data/{SLUG}/{filename}",
                "rows": len(pd.read_csv(path, sep="\t" if path.suffix == ".tsv" else ",")),
            }
        )
    return pd.DataFrame(rows)


def write_page(summary_html: str, tables: dict[str, pd.DataFrame]) -> None:
    sections = [
        (
            "Fig. 1. Yearly variation of the nakshatra location error Ey in the seasonal solar zodiac of VGJ.",
            "plots/epoch-error-curves.png",
            [
                "The green curves (....83 stars; ___ 27 proxy stars; -.-.-. 9 seasonal nakshatra) refer to the Ādityacāra data of the 11th Section of VGJ.",
                "The 83 constituent and the 27 proxy stars are as per Table 1.",
                "Errors for the nine seasonal nakshatra boundaries remain near zero in the strongest-fit window.",
                "The red curve stages the Ṛtusvabhāva comparison from the local shifted-boundary seed.",
            ],
            "Process note: regenerated from local seed tables; no process labels are placed inside the chart.",
        ),
        (
            "Fig. 2. Error sensitivity for possible identification of Vedic star śraviṣṭhā as β Aquari and śravaṇa as β Delphini.",
            "plots/identification-sensitivity.png",
            [
                "The readjusted 27 proxy stars and the yogatāras of Abhyankar lead to almost the same broad result for the error minimum.",
                "Errors for the nine seasonal nakshatra boundaries remain near zero in the strongest-fit window.",
            ],
            "Process note: scenario rows are local replacements over the base 27-proxy table.",
        ),
        (
            "Fig.3. Twelve month (madhu-tapasya) or (caitra-phālguna) sun’s transit in 500 BCE as per the Ṛtusvabhāva (59th aṅga) of VGJ.",
            [
                ("Chart 1", "plots/fig3-rtusvabhava-500-lon-lat.png", "Original reproduction with the older longitude origin and the smooth visualization curve."),
                ("Chart 2", "plots/fig3-lon-lat-zero-clean.png", "Bharaṇī-relative longitude origin with the seasonal and month guides retained."),
                ("Chart 3", "plots/fig3-lon-lat-zero-astrographs.png", "Bharaṇī-relative astrograph version preserving the earlier dotted nakshatra-connection guide."),
                ("Chart 3A", "plots/fig3-lon-lat-zero-astrographs-readable.png", "Readable older-style aspect variant of Chart 3: no smooth or dotted curve; astrographs and labels are enlarged."),
                ("Chart 4", "plots/fig3-lon-lat-zero-astrographs-prof-variant.png", "Presentation variant with no dotted guide and star markers for single-star nakshatras."),
                ("Chart 4A", "plots/fig3-lon-lat-zero-astrographs-prof-readable.png", "Readable older-style aspect variant of Chart 4, retaining the single-star marker convention."),
                ("Chart 4B", "plots/fig3-lon-lat-zero-astrographs-prof-readable-ash360.png", "Chart 4A styling in the source longitude frame: Aśvinī sits just before 360° and Bharaṇī falls naturally between 0° and 15°."),
            ],
            [
                "Chart 1 preserves the older smooth visualization curve for comparison with the original ṛtusvabhāva-style figure.",
                "It can be verified that all the twelve nakshatra named in the VGJ text would have been visible sometime in the specified months.",
                "The second chart below uses the same longitude/latitude field with the x-axis shifted so the first Bharaṇī star sits near 0.5°, while keeping the Madhu/Caitra and season guide lines but omitting the red -500 Ṛtusvabhāva label.",
                "The third chart is the same Bharaṇī-relative field without the fitted line; nakshatra astrographs use the same HIP-defined asterism line geometry as the Nakshatra Precession Explorer where those stars are present in the VGJ N83 table.",
                "The fourth chart is a presentation variant of the third: the dotted nakshatra-connection line is removed, single-star nakshatras including Citrā and Svātī use small star markers, and the latitude scale is modestly compressed.",
                "Charts 3A and 4A respond to the older ṛtusvabhāva comparison: broader lettering, shorter aspect, Bharaṇī-relative zero point, and no smooth or dotted curve.",
                "Chart 4B keeps the Chart 4A styling but uses the source longitude frame so Aśvinī sits just before 360° and Bharaṇī falls naturally between 0° and 15°.",
            ],
            "Process note: Fig. 3 images are reproduced from the local N83 longitude/latitude seed for -500; Charts 2 through 4A use a Bharaṇī-relative longitude origin, while Chart 4B uses the source longitude frame.",
        ),
        (
            "Fig. 3A. RA/Dec view of the same 500 BCE Ṛtusvabhāva star field.",
            [
                "plots/fig3a-rtusvabhava-500-ra-dec-no-label.png",
                "plots/fig3a-rtusvabhava-500-ra-dec.png",
            ],
            [
                "The same month and season annotations are placed on the right-ascension axis.",
                "Negative RA values are wrapped into 0-360 degrees so Bharaṇī begins the visual sequence at the left.",
            ],
            "Process note: generated from the same local N83 RA/Dec seed for -500.",
        ),
        (
            "Plot of Nakshatra locations in their respective divisions",
            "plots/nakshatra-bound-fit.png",
            ["Red-band-style emphasis is summarized here as the strongest epoch range for representatives inside their assigned divisions."],
            "Process note: Stage 1 uses a compact count curve rather than the full legacy band plot.",
        ),
        (
            "Seasons per Ādityacāra",
            "plots/solar-month-cycle.png",
            [
                "Śraviṣṭhā to Revatī half, Rohiṇī to the end, and the remaining seasonal ranges are shown against the same nakshatra frame.",
            ],
            "Process note: this is a seed-derived schematic companion to the notebook season dial.",
        ),
    ]
    star_sections = [
        ("N83 longitude/latitude, selected epochs", "plots/n83-lon-lat-fields.png"),
        ("N83 RA/Dec, selected epochs", "plots/n83-ra-dec-fields.png"),
        ("Ādityacāra and Ṛtusvabhāva boundary frames", "plots/rtusvabhava-error-curves.png"),
    ]
    plot_html = "\n".join(
        f"""<section class="flat-section">
        <h2>{html.escape(title)}</h2>
        <ul class="small-note">
          {"".join(f"<li>{html.escape(item)}</li>" for item in notes)}
        </ul>
        {"".join(section_image_html(src_item, title) for src_item in ([src] if isinstance(src, str) else src))}
        <p class="small-note">{html.escape(process_note)}</p>
      </section>"""
        for title, src, notes, process_note in sections
    )
    star_html = "\n".join(
        f"""<div class="supporting-chart">
        <h3>{html.escape(title)}</h3>
        <p><img class="asset-preview" src="{src}" alt="{html.escape(title)}"></p>
      </div>"""
        for title, src in star_sections
    )

    page = f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{TITLE}</title>
    <link rel="stylesheet" href="../shared/css/site.css">
  </head>
  <body class="exploration-body">
    <main class="content">
      <section class="flat-section">
        <p class="eyebrow">Exploration</p>
        <h1>{TITLE}</h1>
        <p class="lede">Seed-derived reproduction and enhancement of the VGJ seasonal nakshatra chart family.</p>
      </section>

      {plot_html}

      <section class="flat-section">
        <h2>Additional Stage 1 Views</h2>
        <p class="small-note">These are supporting static views generated from the same local seed tables.</p>
        <div class="supporting-chart-stack">
          {star_html}
        </div>
      </section>

      <section class="flat-section">
        <h2>Minima</h2>
        <div class="table-wrap">{table_preview(tables["minima"], rows=12)}</div>
      </section>

      <section class="flat-section">
        <h2>Epoch Windows</h2>
        <div class="table-wrap">{table_preview(tables["windows"], rows=12)}</div>
      </section>

      <section class="flat-section">
        <h2>Scenario Rows</h2>
        <div class="table-wrap">{table_preview(tables["scenarios"], rows=8)}</div>
      </section>

      <section class="flat-section">
        <h2>Source Files</h2>
        <div class="table-wrap">{table_preview(tables["source_files"], rows=10)}</div>
      </section>

      <section class="flat-section">
        <h2>Narration</h2>
        {summary_html}
      </section>
    </main>
  </body>
</html>
"""
    (OUT_ROOT / "index.html").write_text(page, encoding="utf-8")


def main() -> None:
    PLOTS_DIR.mkdir(parents=True, exist_ok=True)
    TABLES_DIR.mkdir(parents=True, exist_ok=True)
    NARRATION_DIR.mkdir(parents=True, exist_ok=True)

    divisions = load_divisions()
    scenarios = build_scenarios(divisions)
    n83 = build_n83(divisions)
    base = scenarios["base"]
    seasonal = base[base["nid"].isin(SEASONAL_NIDS)].copy()

    n27_curve = aggregate_error(base, "err_eq_deg", "N27 base", "Ādityacāra/equal")
    n83_curve = aggregate_error(n83, "err_eq_deg", "N83 stars", "Ādityacāra/equal")
    seasonal_curve = aggregate_error(seasonal, "err_eq_deg", "Seasonal 9", "Ādityacāra/equal")
    rtus_base_curve = aggregate_error(base, "err_rtus_deg", "Base shifted", "Ṛtusvabhāva shifted")
    plot_fig1_epoch_error(
        n27_curve,
        n83_curve,
        seasonal_curve,
        rtus_base_curve,
        PLOTS_DIR / "epoch-error-curves.png",
    )

    sensitivity_curves = [
        aggregate_error(scenarios["base"], "err_eq_deg", "Base", "Ādityacāra/equal"),
        aggregate_error(scenarios["sensitivity"], "err_eq_deg", "Shr/Dha sensitivity", "Ādityacāra/equal"),
        aggregate_error(scenarios["abhyankar"], "err_eq_deg", "Abhyankar-style", "Ādityacāra/equal"),
    ]
    seasonal_sensitivity_curve = aggregate_error(
        scenarios["sensitivity"][scenarios["sensitivity"]["nid"].isin(SEASONAL_NIDS)],
        "err_eq_deg",
        "Seasonal 9",
        "Ādityacāra/equal",
    )
    plot_fig2_sensitivity(
        sensitivity_curves[1],
        seasonal_sensitivity_curve,
        sensitivity_curves[2],
        PLOTS_DIR / "identification-sensitivity.png",
    )

    rtus_curves = [
        aggregate_error(base, "err_eq_deg", "Base", "Ādityacāra/equal"),
        rtus_base_curve.copy(),
        aggregate_error(seasonal, "err_rtus_deg", "Seasonal 9", "Ṛtusvabhāva shifted"),
    ]
    rtus_curves[0]["series"] = "Ādityacāra: 27 proxy"
    rtus_curves[1]["series"] = "Ṛtusvabhāva: 27 proxy"
    rtus_curves[2]["series"] = "Ṛtusvabhāva: 9 seasonal"
    plot_error_curves(rtus_curves, "Ādityacāra and Ṛtusvabhāva Boundary Frames", PLOTS_DIR / "rtusvabhava-error-curves.png")

    plot_fig3_n83_lon_lat(n83, -500, PLOTS_DIR / "fig3-rtusvabhava-500-lon-lat.png")
    bharani_first_lon = float(
        n83[(n83["year"] == -500) & (n83["nid"] == "N02-Bha")]["lon"].min()
    )
    plot_fig3_n83_lon_lat(
        n83,
        -500,
        PLOTS_DIR / "fig3-lon-lat-zero-clean.png",
        start_lon=bharani_first_lon - 0.5,
        show_month_season_guides=True,
        show_rtusvabhava_label=False,
        label_actual_longitudes=False,
        guide_origin="display",
    )
    plot_fig3_n83_lon_lat(
        n83,
        -500,
        PLOTS_DIR / "fig3-lon-lat-zero-astrographs.png",
        start_lon=bharani_first_lon - 0.5,
        show_month_season_guides=True,
        show_rtusvabhava_label=False,
        label_actual_longitudes=False,
        guide_origin="display",
        show_fitted_line=False,
        show_nakshatra_connection=True,
        show_astrographs=True,
        show_moon_path_band=True,
        longitude_label_x=180.0,
        longitude_label_y=-50.8,
        month_label_y_offset=-8.0,
        civil_month_label_y_offset=-2.0,
        season_guide_y_offset=10.0,
        ylim=(-55, 55),
        yticks=np.arange(-30, 31, 10),
    )
    readable_fig3_kwargs = {
        "figsize": (22.5, 7.3),
        "nak_label_fontsize": 24.0,
        "month_label_fontsize": 18.0,
        "season_label_fontsize": 21.0,
        "tick_label_fontsize": 24.0,
        "axis_label_fontsize": 24.0,
        "latitude_label_fontsize": 24.0,
    }
    plot_fig3_n83_lon_lat(
        n83,
        -500,
        PLOTS_DIR / "fig3-lon-lat-zero-astrographs-readable.png",
        start_lon=bharani_first_lon - 0.5,
        show_month_season_guides=True,
        show_rtusvabhava_label=False,
        label_actual_longitudes=False,
        guide_origin="display",
        show_fitted_line=False,
        show_nakshatra_connection=False,
        show_astrographs=True,
        show_moon_path_band=True,
        longitude_label_x=180.0,
        longitude_label_y=-50.8,
        month_label_y_offset=-8.0,
        civil_month_label_y_offset=-2.0,
        season_guide_y_offset=10.0,
        ylim=(-55, 55),
        yticks=np.arange(-30, 31, 10),
        **readable_fig3_kwargs,
    )
    plot_fig3_n83_lon_lat(
        n83,
        -500,
        PLOTS_DIR / "fig3-lon-lat-zero-astrographs-prof-variant.png",
        start_lon=bharani_first_lon - 0.5,
        show_month_season_guides=True,
        show_rtusvabhava_label=False,
        label_actual_longitudes=False,
        guide_origin="display",
        show_fitted_line=False,
        show_nakshatra_connection=False,
        show_astrographs=True,
        show_moon_path_band=True,
        highlight_single_stars=True,
        longitude_label_x=180.0,
        longitude_label_y=-46.8,
        month_label_y_offset=-2.8,
        civil_month_label_y_offset=-2.0,
        season_guide_y_offset=9.0,
        ylim=(-50, 50),
        yticks=np.arange(-30, 31, 10),
    )
    plot_fig3_n83_lon_lat(
        n83,
        -500,
        PLOTS_DIR / "fig3-lon-lat-zero-astrographs-prof-readable.png",
        start_lon=bharani_first_lon - 0.5,
        show_month_season_guides=True,
        show_rtusvabhava_label=False,
        label_actual_longitudes=False,
        guide_origin="display",
        show_fitted_line=False,
        show_nakshatra_connection=False,
        show_astrographs=True,
        show_moon_path_band=True,
        highlight_single_stars=True,
        longitude_label_x=180.0,
        longitude_label_y=-46.8,
        month_label_y_offset=-2.8,
        civil_month_label_y_offset=-2.0,
        season_guide_y_offset=9.0,
        ylim=(-50, 50),
        yticks=np.arange(-30, 31, 10),
        **readable_fig3_kwargs,
    )
    plot_fig3_n83_lon_lat(
        n83,
        -500,
        PLOTS_DIR / "fig3-lon-lat-zero-astrographs-prof-readable-ash360.png",
        start_lon=0.0,
        show_month_season_guides=True,
        show_rtusvabhava_label=False,
        label_actual_longitudes=False,
        guide_origin="display",
        show_fitted_line=False,
        show_nakshatra_connection=False,
        show_astrographs=True,
        show_moon_path_band=True,
        highlight_single_stars=True,
        longitude_label_x=180.0,
        longitude_label_y=-46.8,
        month_label_y_offset=-2.8,
        civil_month_label_y_offset=-2.0,
        season_guide_y_offset=9.0,
        ylim=(-50, 50),
        yticks=np.arange(-30, 31, 10),
        **readable_fig3_kwargs,
    )
    plot_fig3a_n83_ra_dec(n83, -500, PLOTS_DIR / "fig3a-rtusvabhava-500-ra-dec.png")
    plot_fig3a_n83_ra_dec(
        n83,
        -500,
        PLOTS_DIR / "fig3a-rtusvabhava-500-ra-dec-no-label.png",
        show_rtus_label=False,
    )
    plot_star_field(n83, "lon", "lat", PLOTS_DIR / "n83-lon-lat-fields.png", "N83 Star Field: Ecliptic Longitude / Latitude", "Longitude (deg)", "Latitude (deg)")
    plot_star_field(n83, "ra", "dec", PLOTS_DIR / "n83-ra-dec-fields.png", "N83 Star Field: RA / Declination", "RA (deg)", "Declination (deg)")
    plot_bound_fit(base, PLOTS_DIR / "nakshatra-bound-fit.png")
    month_df = plot_month_cycle(divisions, PLOTS_DIR / "solar-month-cycle.png")

    all_curves = [n27_curve, n83_curve, seasonal_curve, *sensitivity_curves]
    minima_rows = []
    window_rows = []
    for curve in all_curves:
        best_year, best_error, start, end, count = best_window(curve)
        minima_rows.append(
            {
                "series": curve["series"].iloc[0],
                "frame": curve["frame"].iloc[0],
                "best_year": best_year,
                "best_mean_error_deg": round(best_error, 3),
            }
        )
        window_rows.append(
            {
                "series": curve["series"].iloc[0],
                "frame": curve["frame"].iloc[0],
                "window_start_year": start,
                "window_end_year": end,
                "years_in_window": count,
                "threshold_deg": round(best_error + 1.0, 3),
            }
        )

    minima = pd.DataFrame(minima_rows).drop_duplicates()
    windows = pd.DataFrame(window_rows).drop_duplicates()
    scenario_summary = pd.concat(sensitivity_curves, ignore_index=True)
    bound_fit = (
        base.groupby("year", as_index=False)
        .agg(inside_eq=("inside_eq", "sum"), inside_rtus=("inside_rtus", "sum"), mean_eq_error_deg=("err_eq_deg", "mean"), mean_rtus_error_deg=("err_rtus_deg", "mean"))
        .round(3)
    )
    source_files = source_files_table()
    n83_preview = n83[n83["year"].isin(STAR_FIELD_EPOCHS)][["year", "nid", "naks", "gname", "lon", "lat", "ra", "dec", "mag", "err_eq_deg"]].round(3)

    divisions.to_csv(TABLES_DIR / "nakshatra-boundaries.csv", index=False)
    minima.to_csv(TABLES_DIR / "minima.csv", index=False)
    windows.to_csv(TABLES_DIR / "epoch-windows.csv", index=False)
    scenario_summary.round(3).to_csv(TABLES_DIR / "scenario-error-curves.csv", index=False)
    bound_fit.to_csv(TABLES_DIR / "bound-fit-by-year.csv", index=False)
    source_files.to_csv(TABLES_DIR / "source-files.csv", index=False)
    month_df.to_csv(TABLES_DIR / "solar-month-cycle.csv", index=False)
    n83_preview.to_csv(TABLES_DIR / "n83-star-field-preview.csv", index=False)

    summary_md = build_summary(minima, windows, source_files)
    (NARRATION_DIR / "summary.md").write_text(summary_md, encoding="utf-8")
    write_page(
        markdown_to_html(summary_md),
        {
            "minima": minima,
            "windows": windows,
            "scenarios": scenario_summary.round(3),
            "source_files": source_files,
        },
    )

    print(f"wrote {OUT_ROOT / 'index.html'}")
    print(f"plots={len(list(PLOTS_DIR.glob('*.png')))} tables={len(list(TABLES_DIR.glob('*.csv')))}")


if __name__ == "__main__":
    main()
