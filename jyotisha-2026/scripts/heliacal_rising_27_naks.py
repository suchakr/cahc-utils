from __future__ import annotations

import csv
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

from jyotisha_2026.paths import LAB_ROOT, upstream_dataset_path


iers.conf.auto_download = False
iers.conf.auto_max_age = None
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=RuntimeWarning)

LATITUDE_DEG = 30.0
LONGITUDE_DEG = 0.0
SUN_ALT_THRESHOLD_DEG = -10.0
EPOCHS = [-1500, -1000, -500]
SLUG = "heliacal-rising-27-naks"


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
    plt.xlabel("Nakshatra", fontsize=20)
    plt.ylabel(ylabel, fontsize=20)
    plt.xticks(rotation=65, ha="right", fontsize=15)
    plt.yticks(fontsize=17)
    plt.grid(True, alpha=0.25)
    plt.legend(title="Epoch", fontsize=16, title_fontsize=16)
    plt.tight_layout()
    plt.savefig(output_path, dpi=180)
    plt.close()


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

    frame = compute_results()
    frame.to_csv(tables_dir / "heliacal-rising-27-naks.csv", index=False)

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

    summary_md = build_summary(frame)
    (narration_dir / "summary.md").write_text(summary_md, encoding="utf-8")
    summary_html = summary_markdown_to_html(summary_md)
    table_html = preview_table_html(frame)
    write_page(summary_html, table_html)


if __name__ == "__main__":
    main()
