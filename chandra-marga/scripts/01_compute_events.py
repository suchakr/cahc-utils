#!/usr/bin/env python3
"""Compute altitude-target JDs (e.g. Sun-at-9deg-below-horizon, or
Moon-at-8deg) for a given paksha/thithi, from an existing moonset/moonrise
.inc file.

Generic over:
  --target-body   sun | moon      (which body's altitude to solve for)
  --target-altitude   float, deg  (e.g. -9.0 for sun, 8.0 for moon)
  --event-type    set | rise      (which source event to key off of)
  --paksha        shukla | krishna
  --thithi        1-15

We deliberately reuse an existing moonset/moonrise JD array (rather than
re-deriving it from scratch each time) since it's already the validated
ground truth consumed by the a9/a10 .ssc scripts. `chandra_marga.events.
compute_moonset_events` remains available for regenerating that series
itself from scratch if needed.

Usage:
    uv run python scripts/01_compute_events.py --help
    uv run python scripts/01_compute_events.py \\
        --source-inc lunar-set-events--0527.inc --year-tag 0527 \\
        --paksha shukla --thithi 1 \\
        --target-body sun --target-altitude -9.0 --event-type set
"""

from __future__ import annotations

import argparse
import re

from astropy.time import Time

from chandra_marga import config, events, stellarium_export


def infer_year_tag(source_inc: str) -> str | None:
    """Best-effort extraction of a '--NNNN' / '-NNNN' year tag from a source
    filename like 'lunar-set-events--0527.inc' -> '0527'."""
    m = re.search(r"-(\d{3,5})\.inc$", source_inc)
    return m.group(1) if m else None


def alt_tag(target_body: str, target_alt_deg: float) -> str:
    sign = "minus" if target_alt_deg < 0 else ""
    magnitude = f"{abs(target_alt_deg):g}"
    return f"{target_body}-alt-{sign}{magnitude}"


def default_pilot_indices(n: int) -> list[int]:
    if n <= 6:
        return list(range(n))
    step = n // 6
    return sorted(set([0, *(i * step for i in range(1, 6)), n - 1]))


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--source-inc", default="lunar-set-events--0527.inc",
                         help="Existing moonset/moonrise .inc file (in stel_scripts/) to read source JDs from")
    parser.add_argument("--year-tag", default=None,
                         help="Tag used in output filenames (default: inferred from --source-inc, e.g. '0527')")
    parser.add_argument("--paksha", choices=["shukla", "krishna"], default="shukla")
    parser.add_argument("--thithi", type=int, default=1, help="1-15")
    parser.add_argument("--event-type", choices=["set", "rise"], default="set",
                         help="Which source event type this is, AND which crossing type to solve for the target body")
    parser.add_argument("--target-body", choices=["sun", "moon"], default="sun")
    parser.add_argument("--target-altitude", type=float, default=-9.0, help="Target altitude in degrees")
    parser.add_argument("--seed-offset-hours", type=float, default=None,
                         help="Override the default seed offset (see events.DEFAULT_SEED_OFFSET_HOURS)")
    parser.add_argument("--location", default="kurukshetra")
    parser.add_argument("--out-inc", default=None, help="Output .inc filename override")
    parser.add_argument("--out-var", default=None, help="Output .inc variable name override")
    parser.add_argument("--pilot-indices", default=None,
                         help="Comma-separated indices to print a validation table for (default: auto-spread)")
    args = parser.parse_args()

    tithi_key = config.event_slug(args.paksha, args.thithi)
    year_tag = args.year_tag or infer_year_tag(args.source_inc) or "0000"

    source_dict = stellarium_export.load_inc_dict(args.source_inc)
    if tithi_key not in source_dict:
        raise SystemExit(
            f"'{tithi_key}' not found in {args.source_inc}. Available keys: {sorted(source_dict.keys())}"
        )
    source_jds = sorted(source_dict[tithi_key])
    print(f"Loaded {len(source_jds)} '{tithi_key}' {args.event_type} JDs from {args.source_inc}")

    location = config.get_location(args.location)
    target_jds = events.compute_altitude_target_jds(
        source_jds,
        location=location,
        target_body=args.target_body,
        event_type=args.event_type,
        target_alt_deg=args.target_altitude,
        seed_offset_hours=args.seed_offset_hours,
    )

    pilot = (
        [int(i) for i in args.pilot_indices.split(",")]
        if args.pilot_indices
        else default_pilot_indices(len(source_jds))
    )
    print(f"\nPilot validation (indices {pilot}):")
    print(f"{'idx':>4}  {'source JD':>18}  {'target JD':>18}  {'UTC':>20}  {'delta(hrs)':>10}")
    for i in pilot:
        source_jd = source_jds[i]
        target_jd = target_jds[i]
        t = Time(target_jd, format="jd")
        delta_hrs = (target_jd - source_jd) * 24.0
        print(f"{i:>4}  {source_jd:>18.6f}  {target_jd:>18.6f}  {t.iso:>20}  {delta_hrs:>+10.2f}")

    tag = alt_tag(args.target_body, args.target_altitude)
    out_inc = args.out_inc or f"{tag}-events--{year_tag}.inc"
    out_var = args.out_var or f"{tag.upper().replace('-', '_')}_JDS"

    inc_path = stellarium_export.write_inc_file({tithi_key: target_jds}, out_var, out_inc)
    print(f"\nWrote {inc_path}")

    print(f"\nEmbeddable JS array for '{tithi_key}' (paste into a .ssc script's JDS = [...]):\n")
    print(stellarium_export.format_js_array(target_jds, var_name="JDS"))


if __name__ == "__main__":
    main()
