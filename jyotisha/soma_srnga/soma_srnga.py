import numpy as np
from astropy.coordinates import EarthLocation, get_body, get_sun, AltAz
from astropy.time import Time
import astropy.units as u
from astroplan import Observer
import argparse
from datetime import date
import pytz

def calculate_crescent_orientation(location: EarthLocation, date_time: Time):
    """
    Calculates the orientation of the lunar crescent at the next moonset.
    """
    observer = Observer(location=location)
    moonset_time = observer.moon_set_time(date_time, which="next", horizon=-0.5 * u.deg)

    if moonset_time is None:
        return None

    observer_frame = AltAz(obstime=moonset_time, location=location)
    sun_icrs = get_sun(moonset_time)
    moon_icrs = get_body("moon", moonset_time, location)
    moon_altaz = moon_icrs.transform_to(observer_frame)

    parallactic_angle = observer.parallactic_angle(moonset_time, moon_icrs)
    position_angle_sun = moon_icrs.position_angle(sun_icrs)

    cusp_orientation = (parallactic_angle - position_angle_sun + 90*u.deg)
    cusp_orientation = cusp_orientation.wrap_at(180 * u.deg)

    elongation = sun_icrs.separation(moon_icrs)
    phase_angle = np.arctan2(sun_icrs.distance * np.sin(elongation),
                           moon_icrs.distance - sun_icrs.distance * np.cos(elongation))
    illumination = (1 + np.cos(phase_angle)) / 2 * 100

    return {
        "moonset_time_obj": moonset_time,
        "moonset_time_jd": moonset_time.jd,
        "moon_az_at_set": moon_altaz.az.deg,
        "cusp_orientation_deg": cusp_orientation.deg,
        "illumination": illumination.value
    }

def get_cusp_tilt_glyph(angle_deg):
    """Converts a cusp tilt angle to a representative Unicode glyph based on a 15-degree lookup table."""
    lean_glyphs_15deg = {
        0:   "─", 15:  "╱", 30:  "⟋", 45:  "╲", 60:  "⟍", 75:  "╲",
        90:  "│", 105: "╱", 120: "⟋", 135: "╱", 150: "⟍", 165: "╲",
        180: "─", 195: "╱", 210: "⟋", 225: "╱", 240: "⟍", 255: "╲",
        270: "│", 285: "╱", 300: "⟋", 315: "╱", 330: "⟍", 345: "╲",
    }
    # Convert angle from [-180, 180] to [0, 360] range
    angle_360 = (angle_deg + 360) % 360
    # Find the nearest 15-degree key in the dictionary
    nearest_key = int(round(angle_360 / 15.0) * 15) % 360
    return lean_glyphs_15deg.get(nearest_key, "~")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Calculate lunar crescent orientation for N consecutive days from a start date.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        '--start_date',
        default=date.today().isoformat(),
        help="""Start date in YYYY-MM-DD format.
For BCE dates, use a zero-padded 4+ digit negative year, e.g., -01237-01-02 for 1238 BCE.
Defaults to today's date."""
    )
    parser.add_argument(
        '-n', '--num_days',
        type=int,
        default=15,
        help="Number of consecutive days to calculate.\nDefaults to 15."
    )
    args = parser.parse_args()

    locations = {
        "Bangalore": (EarthLocation(lat=12.97*u.deg, lon=77.59*u.deg, height=920*u.m), "Asia/Kolkata"),
        "Kurukshetra": (EarthLocation(lat=29.97*u.deg, lon=76.85*u.deg, height=260*u.m), "Asia/Kolkata")
    }

    print(f"Running calculations for {args.num_days} days, starting from {args.start_date}")

    start_time = Time(args.start_date)

    for name, (loc, tz_name) in locations.items():
        print(f"\n--- Crescent Data for {name} (Timezone: {tz_name}) ---")
        header = f"{'Moonset Time (Local)':<28} | {'JD':>14} | {'Azimuth (deg)':>15} | {'Cusp Tilt (deg)':>18} | {'Illumination (%)':>20}"
        print(header)
        print("-" * len(header))

        for i in range(args.num_days):
            current_date = start_time + i * u.day
            results = calculate_crescent_orientation(loc, current_date)

            if results:
                tz = pytz.timezone(tz_name)
                moonset_time_local = results['moonset_time_obj'].to_datetime(timezone=tz)
                time_str = moonset_time_local.strftime('%Y-%m-%d %H:%M:%S %Z')

                jd_str = f"{results['moonset_time_jd']:.2f}"
                az_str = f"{results['moon_az_at_set']:.2f}"
                tilt_str = f"{results['cusp_orientation_deg']:.2f}"
                illum_str = f"{results['illumination']:.2f}"

                print(f"{time_str:<28} | {jd_str:>14} | {az_str:>15} | {tilt_str:>18} | {illum_str:>20}")
            else:
                date_str = current_date.to_datetime(timezone=pytz.utc).strftime('%Y-%m-%d')
                print(f"No moonset found for start date {date_str}")

        print("-" * len(header))