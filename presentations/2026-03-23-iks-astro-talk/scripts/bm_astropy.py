#!/usr/bin/env python3
"""
Benchmark: next N sunrises at Bengaluru/Bangalore from a fixed starting JD.

Environment note:
- Confirmed on 2026-03-22 that this runs from the jyotisha uv environment with:
  cd /Users/sunder/projects/cahc/cahc-utils/jyotisha
  ASTROPY_IERS_AUTO_DOWNLOAD=0 uv run --with-requirements requirements.txt \
    python ../presentations/2026-03-23-iks-astro-talk/scripts/bm_astropy.py

Benchmark policy:
- Timed section computes only the sunrise JDs.
- Formatting and printing happen after timing, so output I/O does not distort the
  runtime comparison against Stellarium.
"""

from __future__ import annotations

import argparse
import time
from datetime import datetime

import astropy.units as u
from astroplan import Observer
from astropy.coordinates import EarthLocation
from astropy.time import Time
import pytz


START_JD = 2461120.2708333335  # 2026-03-21T00:00:00 Asia/Kolkata
LAT_DEG = 12.9716
LON_DEG = 77.5946
HEIGHT_M = 920
TIMEZONE = "Asia/Kolkata"


def build_observer() -> Observer:
    location = EarthLocation(
        lat=LAT_DEG * u.deg,
        lon=LON_DEG * u.deg,
        height=HEIGHT_M * u.m,
    )
    return Observer(location=location, timezone=TIMEZONE)


def compute_next_sunrises(observer: Observer, start_jd: float, count: int) -> list[float]:
    current = Time(start_jd, format="jd", scale="utc")
    results: list[float] = []

    for _ in range(count):
        sunrise = observer.sun_rise_time(current, which="next", horizon=0 * u.deg)
        results.append(float(sunrise.jd))
        # Step slightly past the event so the next query returns the next sunrise.
        current = sunrise + 1 * u.minute

    return results


def format_local_iso(jd_value: float, tz_name: str) -> str:
    tz = pytz.timezone(tz_name)
    local_dt = Time(jd_value, format="jd", scale="utc").to_datetime(timezone=tz)
    return local_dt.strftime("%Y-%m-%dT%H:%M:%S")


def main() -> None:
    parser = argparse.ArgumentParser(description="Benchmark Astroplan next-sunrise computation.")
    parser.add_argument("--count", type=int, default=100, help="Number of next sunrises to compute.")
    parser.add_argument(
        "--start-jd",
        type=float,
        default=START_JD,
        help="Starting Julian Day in UTC; default is 2026-03-21 00:00 local Bangalore.",
    )
    args = parser.parse_args()

    observer = build_observer()

    t0 = time.perf_counter()
    sunrise_jds = compute_next_sunrises(observer, args.start_jd, args.count)
    elapsed_sec = time.perf_counter() - t0

    for idx, jd_value in enumerate(sunrise_jds, start=1):
        print(
            "SUNRISE\t{idx}\t{jd:.9f}\t{local}".format(
                idx=idx,
                jd=jd_value,
                local=format_local_iso(jd_value, TIMEZONE),
            )
        )

    print(
        "SUMMARY\ttool=astropy_astroplan\tlocation=Bangalore"
        "\tstart_jd={start:.9f}\tcount={count}\telapsed_sec={elapsed:.6f}"
        "\tms_per_sunrise={msp:.3f}".format(
            start=args.start_jd,
            count=args.count,
            elapsed=elapsed_sec,
            msp=(elapsed_sec * 1000.0 / args.count) if args.count else 0.0,
        )
    )


if __name__ == "__main__":
    main()
