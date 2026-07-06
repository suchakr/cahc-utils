#!/usr/bin/env python3
"""Compute the base moonset/moonrise event series (amavasya, purnima,
shukla_pratipada, shukla_dwitiya, krishna_chaturdashi) for a date range and
write it as a `.inc` file, e.g. `lunar-set-events--0527.inc` /
`lunar-rise-events--0527.inc`.

This is step 0 of the pipeline: `01_compute_events.py` consumes one of these
files as its `--source-inc` to solve for a target-body altitude crossing
(e.g. Sun at -9 deg) near each source event.

Previously this base series was only ever produced ad hoc from
jyotisha/lunar-events-calculator.ipynb (event_type='set' only, exact
start_time/ndays not preserved anywhere). This script makes it a reproducible,
generic CLI over event_type/start_time/ndays/location.

Usage:
    uv run python scripts/00_compute_base_events.py --help
    uv run python scripts/00_compute_base_events.py \\
        --event-type rise --start-time "-00527-01-01T00:00:00.000" \\
        --ndays 1460 --year-tag 0527
"""

from __future__ import annotations

import argparse

from chandra_marga import config, events, stellarium_export
from chandra_marga.events import LunarCalendarAnalyzer

# Matches jyotisha/lunar-events-calculator.ipynb's
# LunarEventsCalculator.export_for_stellarium default event set.
EVENT_CATEGORIES = [
    ("amavasya", "krishna", 15),
    ("purnima", "shukla", 15),
    ("shukla_pratipada", "shukla", 1),
    ("shukla_dwitiya", "shukla", 2),
    ("krishna_chaturdashi", "krishna", 14),
]


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--event-type", choices=["set", "rise"], default="set",
                         help="Which moon crossing anchors each sampled event")
    parser.add_argument("--start-time", required=True,
                         help="astropy.time.Time-parseable string, e.g. '-00527-01-01T00:00:00.000' or '2025-01-01'")
    parser.add_argument("--ndays", type=int, required=True,
                         help="Number of sequential moon events to sample (~1.03 days apart each, NOT calendar days)")
    parser.add_argument("--location", default="kurukshetra")
    parser.add_argument("--year-tag", required=True, help="Tag used in the output filename, e.g. '0527'")
    parser.add_argument("--out-inc", default=None, help="Output .inc filename override")
    args = parser.parse_args()

    location = config.get_location(args.location)
    print(f"Computing '{args.event_type}' events from {args.start_time} for {args.ndays} events "
          f"at {args.location}...")
    analysis = events.compute_lunar_events(
        args.start_time, ndays=args.ndays, event_type=args.event_type, location=location
    )

    jd_dict = {}
    for name, paksha, thithi in EVENT_CATEGORIES:
        if name in ("amavasya", "purnima"):
            events_df = analysis[name]
        else:
            events_df = LunarCalendarAnalyzer.get_specific_events(analysis, paksha, thithi)
        jds = sorted(events_df["JD"].tolist())
        jd_dict[name] = jds
        print(f"  {name:22s} n={len(jds)}"
              + (f"  first={jds[0]:.6f}  last={jds[-1]:.6f}" if jds else ""))

    out_inc = args.out_inc or f"lunar-{args.event_type}-events--{args.year_tag}.inc"
    var_name = f"MOON_{args.event_type.upper()}_JDS"
    inc_path = stellarium_export.write_inc_file(jd_dict, var_name, out_inc)
    print(f"\nWrote {inc_path}")


if __name__ == "__main__":
    main()
