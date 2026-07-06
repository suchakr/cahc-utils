"""Lunar event (moonset/thithi) calculation, ported from
jyotisha/lunar-events-calculator.ipynb's LunarDataCalculator +
LunarCalendarAnalyzer, plus a new Sun-altitude-target solver for the
Sun-at-\u22129\u00b0 crescent series.

This module is the source of truth going forward; the notebook becomes a
thin interactive shell that imports it.
"""

from __future__ import annotations

import os
from functools import lru_cache

import astropy.units as u
import numpy as np
import pandas as pd
from astroplan import Observer
from astropy.coordinates import AltAz, GeocentricTrueEcliptic, EarthLocation, get_body
from astropy.time import Time
from joblib import Memory
from scipy.signal import argrelextrema

from chandra_marga import config


class LunarDataCalculator:
    """Core calculator for lunar astronomical data with elegant caching.

    Faithful port of the notebook's class of the same name; only the cache
    directory now defaults to an absolute path (chandra-marga/cache_lunar~)
    instead of a cwd-relative one.
    """

    def __init__(self, location: EarthLocation | None = None, cache_dir=None):
        self.location = location if location is not None else config.get_location("kurukshetra")
        self.observer = Observer(location=self.location, timezone="Asia/Kolkata")

        cache_path = str(cache_dir or config.CACHE_DIR)
        os.makedirs(cache_path, exist_ok=True)
        self.memory = Memory(location=cache_path, verbose=0)

        self._calculate_moon_data_disk = self.memory.cache(self._calculate_moon_data_raw)

    def _calculate_moon_data_raw(self, start_time_jd, ndays, event_type="set"):
        start_time = Time(start_time_jd, format="jd")
        data = []

        current_time = start_time
        for day in range(ndays):
            try:
                if event_type == "set":
                    moon_event = self.observer.moon_set_time(current_time + 0.5 * u.day, which="next")
                else:
                    moon_event = self.observer.moon_rise_time(current_time + 0.5 * u.day, which="next")

                phase = self.observer.moon_illumination(moon_event)
                moon = get_body("moon", moon_event, self.location)
                sun = get_body("sun", moon_event, self.location)

                moon_altaz = moon.transform_to(AltAz(obstime=moon_event, location=self.location))
                moon_ecliptic = moon.transform_to(GeocentricTrueEcliptic(equinox=moon_event))

                try:
                    local_time = (moon_event + 5.5 * u.hour).iso
                except (ValueError, OverflowError):
                    local_time = moon_event.iso

                data.append({
                    "JD": moon_event.jd,
                    "UTC": moon_event.iso,
                    "LocalTime": local_time,
                    "Phase": phase * 100,
                    "Altitude": moon_altaz.alt.deg,
                    "Azimuth": moon_altaz.az.deg,
                    "Longitude": moon_ecliptic.lon.deg,
                    "Declination": moon.dec.deg,
                    "Distance_km": moon.distance.km,
                    "Elongation": moon.separation(sun).deg,
                })

                current_time = moon_event

            except Exception as e:
                print(f"Warning: Error calculating day {day}: {e}")
                current_time += 1 * u.day
                continue

        return pd.DataFrame(data)

    @lru_cache(maxsize=128)
    def get_moon_data(self, start_time_jd, ndays=60, event_type="set"):
        return self._calculate_moon_data_disk(start_time_jd, ndays, event_type)

    def clear_cache(self):
        self.get_moon_data.cache_clear()
        self.memory.clear()


class LunarCalendarAnalyzer:
    """Astronomically accurate lunar calendar analyzer using phase extrema.

    Faithful port of the notebook's class of the same name (unchanged logic).
    """

    def __init__(self, data_calculator: LunarDataCalculator):
        self.calculator = data_calculator

    def analyze_lunar_events(self, moon_data_df: pd.DataFrame):
        if len(moon_data_df) < 10:
            raise ValueError("Need at least 10 data points for reliable phase analysis")

        phase_array = moon_data_df["Phase"].values

        local_minima_idx = argrelextrema(phase_array, np.less, order=2)[0]
        local_maxima_idx = argrelextrema(phase_array, np.greater, order=2)[0]

        moon_data_with_thithis = self._calculate_thithis(moon_data_df, local_minima_idx, local_maxima_idx)

        amavasya_events = moon_data_with_thithis.iloc[local_minima_idx].copy()
        purnima_events = moon_data_with_thithis.iloc[local_maxima_idx].copy()

        return {
            "full_data": moon_data_with_thithis,
            "amavasya": amavasya_events,
            "purnima": purnima_events,
            "phase_extrema": {
                "minima_indices": local_minima_idx,
                "maxima_indices": local_maxima_idx,
            },
        }

    def _calculate_thithis(self, df, minima_idx, maxima_idx):
        result_df = df.copy()
        result_df["Thithi"] = 1
        result_df["Paksha"] = ""
        result_df["Parva"] = ""

        all_extrema = []
        for idx in minima_idx:
            all_extrema.append((idx, "Amavasya"))
        for idx in maxima_idx:
            all_extrema.append((idx, "Purnima"))

        all_extrema.sort(key=lambda x: x[0])

        if len(all_extrema) == 0:
            result_df["Paksha"] = "Unknown"
            result_df["Parva"] = "-"
            return result_df

        if all_extrema[0][0] > 0:
            first_extrema_idx, first_extrema_type = all_extrema[0]
            paksha = "Krishna" if first_extrema_type == "Amavasya" else "Shukla"
            for idx in range(first_extrema_idx):
                distance_from_extrema = first_extrema_idx - idx
                thithi = max(1, min(14, 15 - distance_from_extrema))
                result_df.iloc[idx, result_df.columns.get_loc("Thithi")] = thithi
                result_df.iloc[idx, result_df.columns.get_loc("Paksha")] = paksha
                result_df.iloc[idx, result_df.columns.get_loc("Parva")] = "-"

        for i, (extrema_idx, extrema_type) in enumerate(all_extrema):
            result_df.iloc[extrema_idx, result_df.columns.get_loc("Thithi")] = 15
            result_df.iloc[extrema_idx, result_df.columns.get_loc("Parva")] = extrema_type

            if i < len(all_extrema) - 1:
                next_extrema_idx = all_extrema[i + 1][0]
                next_extrema_type = all_extrema[i + 1][1]

                if extrema_type == "Amavasya" and next_extrema_type == "Purnima":
                    paksha = "Shukla"
                elif extrema_type == "Purnima" and next_extrema_type == "Amavasya":
                    paksha = "Krishna"
                else:
                    paksha = "Unknown"

                range_indices = list(range(extrema_idx + 1, next_extrema_idx))

                for j, idx in enumerate(range_indices):
                    if idx < len(result_df):
                        if len(range_indices) > 0:
                            thithi = min(14, max(1, round((j + 1) * 14 / len(range_indices))))
                        else:
                            thithi = 1

                        result_df.iloc[idx, result_df.columns.get_loc("Thithi")] = thithi
                        result_df.iloc[idx, result_df.columns.get_loc("Paksha")] = paksha
                        result_df.iloc[idx, result_df.columns.get_loc("Parva")] = "-"

                result_df.iloc[extrema_idx, result_df.columns.get_loc("Paksha")] = paksha

        if len(all_extrema) > 0 and all_extrema[-1][0] < len(result_df) - 1:
            last_extrema_idx, last_extrema_type = all_extrema[-1]
            paksha = "Shukla" if last_extrema_type == "Amavasya" else "Krishna"
            for idx in range(last_extrema_idx + 1, len(result_df)):
                distance_from_extrema = idx - last_extrema_idx
                thithi = min(14, max(1, distance_from_extrema))
                result_df.iloc[idx, result_df.columns.get_loc("Thithi")] = thithi
                result_df.iloc[idx, result_df.columns.get_loc("Paksha")] = paksha
                result_df.iloc[idx, result_df.columns.get_loc("Parva")] = "-"

        return result_df

    @classmethod
    def get_specific_events(cls, lunar_analysis, paksha, thithi):
        full_data = lunar_analysis["full_data"]
        event_filter = (full_data["Paksha"].str.lower() == paksha.lower()) & (full_data["Thithi"] == thithi)
        return full_data[event_filter].copy()


def compute_lunar_events(
    start_time,
    ndays=60,
    event_type: str = "set",
    location: EarthLocation | None = None,
):
    """Compute the moonset/moonrise series + thithi classification for a date range.

    `event_type` selects which body-crossing anchors each iteration's event:
    'set' (moonset, the notebook's original/only mode) or 'rise' (moonrise --
    needed e.g. for a full moon actually rising, visible in the east, as
    opposed to the existing moonset-based series where a full moon is setting
    near dawn).

    Returns the `lunar_analysis` dict (full_data/amavasya/purnima/phase_extrema),
    same shape as the notebook's `calculate_events(..., event_type=...)`. Thithi
    classification is derived purely from phase extrema, so it's identical
    logic regardless of event_type -- only which moment of each lunar day is
    sampled (set vs rise) differs.
    """
    if event_type not in ("set", "rise"):
        raise ValueError(f"event_type must be 'set' or 'rise' (got {event_type!r})")

    if not isinstance(start_time, Time):
        if isinstance(start_time, str) and start_time.startswith("-"):
            start_time = Time(start_time, format="fits", scale="utc")
        else:
            start_time = Time(start_time)

    calculator = LunarDataCalculator(location)
    analyzer = LunarCalendarAnalyzer(calculator)

    moon_data = calculator.get_moon_data(start_time.jd, ndays, event_type)
    if moon_data.empty:
        raise ValueError("No moon data calculated")

    return analyzer.analyze_lunar_events(moon_data)


def compute_moonset_events(start_time, ndays=60, location: EarthLocation | None = None):
    """Backwards-compatible alias for `compute_lunar_events(..., event_type='set')`."""
    return compute_lunar_events(start_time, ndays=ndays, event_type="set", location=location)


def shukla_pratipada_jds(lunar_analysis) -> list[float]:
    """Extract sorted shukla_pratipada moonset JDs from a lunar_analysis dict."""
    events = LunarCalendarAnalyzer.get_specific_events(lunar_analysis, "shukla", 1)
    return sorted(events["JD"].tolist())


# ---------------------------------------------------------------------------
# Generic altitude-target solver: given a series of source events (typically
# moonset/moonrise JDs), find when EITHER the Sun OR the Moon crosses an
# arbitrary target altitude near each source event. Generalizes the two
# known use cases:
#   - target_body="sun",  target_alt_deg=-9.0: Sun-at-9deg-below-horizon
#     twilight-background series (a10-moon-shranga-sun9.ssc).
#   - target_body="moon", target_alt_deg=8.0:  Moon-at-8deg series
#     (a9-moon-shranga.ssc; previously only a live 2-iteration Newton
#     correction inside the .ssc script, never available as a precompute).
# ---------------------------------------------------------------------------

# Default seed offset (hours, signed; applied as source_jd + offset) for
# each (target_body, event_type) combination, chosen so the seed reliably
# lands on the correct side of target_alt_deg before searching for the
# *next* crossing:
#   - sun targets: seed hours before/after the source event, since the Sun's
#     twilight-altitude crossing can be well separated in time from the
#     Moon's own set/rise. -6h/+6h is validated (this session) for (sun,set).
#   - moon targets: solving for the SAME body near its OWN 0deg crossing,
#     so only a small margin is needed -- but it must be big enough that,
#     at ~15deg/hour (typical altitude rate near the horizon), the Moon is
#     still clearly on the far side of target_alt_deg from the source event.
# NOTE: only (sun, set) has been empirically validated against live
# Stellarium (see chandra-marga session notes). (moon, set) is a reasoned
# estimate; (sun, rise) and (moon, rise) are untested mirror-image guesses.
# Spot-check any new combination against Stellarium before trusting it for
# a production run, the same way (sun, set) was validated.
DEFAULT_SEED_OFFSET_HOURS = {
    ("sun", "set"): -6.0,
    ("sun", "rise"): 6.0,
    ("moon", "set"): -1.5,
    ("moon", "rise"): 0.2,
}

_TIME_FN_NAMES = {
    ("sun", "set"): "sun_set_time",
    ("sun", "rise"): "sun_rise_time",
    ("moon", "set"): "moon_set_time",
    ("moon", "rise"): "moon_rise_time",
}


def _resolve_time_fn(observer: Observer, target_body: str, event_type: str):
    key = (target_body, event_type)
    if key not in _TIME_FN_NAMES:
        raise ValueError(
            f"target_body must be 'sun' or 'moon' and event_type must be 'set' or 'rise' "
            f"(got target_body={target_body!r}, event_type={event_type!r})"
        )
    return getattr(observer, _TIME_FN_NAMES[key])


def body_altitude_at(observer: Observer, t: Time, target_body: str = "sun") -> float:
    """Altitude (deg) of `target_body` at time t, for validation against a solved JD."""
    return observer.altaz(t, target=get_body(target_body, t, observer.location)).alt.deg


def solve_altitude_target_time(
    observer: Observer,
    seed_time: Time,
    target_body: str = "sun",
    event_type: str = "set",
    target_alt_deg: float = -9.0,
) -> Time:
    """Find the next time after `seed_time` when `target_body` crosses `target_alt_deg`.

    Uses astroplan's own horizon-aware rise/set solvers (`Observer.sun_set_time`,
    `sun_rise_time`, `moon_set_time`, `moon_rise_time`), all of which accept an
    arbitrary `horizon=` -- no bespoke per-body solver needed.
    """
    time_fn = _resolve_time_fn(observer, target_body, event_type)
    return time_fn(seed_time, which="next", horizon=target_alt_deg * u.deg)


def compute_altitude_target_jds(
    source_jds: list[float],
    location: EarthLocation | None = None,
    target_body: str = "sun",
    event_type: str = "set",
    target_alt_deg: float = -9.0,
    seed_offset_hours: float | None = None,
) -> list[float]:
    """For each source event JD (typically a moonset/moonrise), find the JD
    at which `target_body`'s altitude crosses `target_alt_deg`.

    `seed_offset_hours` (signed hours, added to each source JD) defaults per
    (target_body, event_type) via DEFAULT_SEED_OFFSET_HOURS -- override if
    the default margin doesn't safely bracket your target (see caveats above
    DEFAULT_SEED_OFFSET_HOURS).
    """
    if location is None:
        location = config.get_location("kurukshetra")
    observer = Observer(location=location, timezone="Asia/Kolkata")

    if seed_offset_hours is None:
        key = (target_body, event_type)
        if key not in DEFAULT_SEED_OFFSET_HOURS:
            raise ValueError(f"No default seed_offset_hours for {key}; pass seed_offset_hours explicitly.")
        seed_offset_hours = DEFAULT_SEED_OFFSET_HOURS[key]

    result = []
    for jd in source_jds:
        source_time = Time(jd, format="jd")
        seed_time = source_time + seed_offset_hours * u.hour
        target_time = solve_altitude_target_time(
            observer, seed_time, target_body=target_body, event_type=event_type, target_alt_deg=target_alt_deg
        )
        result.append(float(target_time.jd))
    return result
