import numpy as np
import json
import astropy.units as u
from astropy.time import Time, TimeDelta
from astropy.coordinates import EarthLocation, get_sun, AltAz

def generate_meridians(year=-1350, days=366):
    ujjain = EarthLocation(lat=23.1765*u.deg, lon=75.7885*u.deg, height=490*u.m)
    
    # Start around the beginning of the given year
    start_time = Time(float(year), format='jyear', scale='utc')
    
    crossings = []
    
    for d in range(days):
        t0 = start_time + TimeDelta(d, format='jd')
        # We sample 24 hours in 5-minute increments
        delta_hours = np.linspace(0, 24, 24*12)
        day_times = t0 + TimeDelta(delta_hours/24., format='jd')
        
        sun = get_sun(day_times)
        altaz = sun.transform_to(AltAz(obstime=day_times, location=ujjain, pressure=0))
        alts = altaz.alt.degree
        
        # Local maximum: altitude derivative goes from positive to negative
        diffs_alts = np.diff(alts)
        cross_idx = np.where(np.diff(np.sign(diffs_alts)) < 0)[0]
        
        if len(cross_idx) > 0:
            i = cross_idx[0]
            peak_idx = i + 1
            if 0 < peak_idx < len(alts) - 1:
                t1, t2 = day_times[peak_idx-1].jd, day_times[peak_idx].jd
                a1, a2, a3 = alts[peak_idx-1], alts[peak_idx], alts[peak_idx+1]
                # Parabolic peak interpolation
                denom = (a1 - 2*a2 + a3)
                if denom != 0:
                    offset = 0.5 * (a1 - a3) / denom
                    jd_exact = t2 + offset * (t2 - t1)
                else:
                    jd_exact = t2
                crossings.append(jd_exact)
            else:
                crossings.append(day_times[peak_idx].jd)
            
    return crossings

for epoch_year in [-1350, -1800, 2000]:
    print(f"Calculating Meridian JDs for {epoch_year}...")
    jds = generate_meridians(epoch_year, 366)
    bcetag = "bce" if epoch_year < 0 else "ce"
    var_name = f"MERIDIANS_{bcetag.upper()}_{abs(epoch_year)}"
    output = f"// Generated precisely via Astropy for Ujjain at {epoch_year}\nvar {var_name} = " + json.dumps(jds) + ";\n"
    out_path = f"/Users/sunder/projects/cahc/cahc-utils/presentations/2026-03-23-iks-astro-talk/ssc/sun-meridian-{bcetag}-{abs(epoch_year)}.inc"
    with open(out_path, "w") as f:
        f.write(output)
    print(f"Generated {len(jds)} meridian JDs to {out_path}.")
