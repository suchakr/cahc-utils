import numpy as np
import json
import astropy.units as u
from astropy.time import Time, TimeDelta
from astropy.coordinates import EarthLocation, get_sun, AltAz

def generate_sunrises(year=-1350, days=366):
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
        
        # We are looking for sunrise: altitude going from negative to positive
        diffs = np.diff(np.sign(alts))
        idx_rise = np.where(diffs > 0)[0]
        
        if len(idx_rise) > 0:
            i = idx_rise[0]
            # Linear interpolation for better precision
            t_before = day_times[i]
            t_after = day_times[i+1]
            alt_before = alts[i]
            alt_after = alts[i+1]
            
            fraction = -alt_before / (alt_after - alt_before)
            jd_exact = t_before.jd + fraction * (t_after.jd - t_before.jd)
            crossings.append(jd_exact)
            
    return crossings

for epoch_year in [-1350, -1800, 2000]:
    print(f"Calculating JDs for {epoch_year}...")
    jds = generate_sunrises(epoch_year, 366)
    bcetag = "bce" if epoch_year < 0 else "ce"
    var_name = f"SUNRISES_{bcetag.upper()}_{abs(epoch_year)}"
    output = f"// Generated precisely via Astropy for Ujjain at {epoch_year}\nvar {var_name} = " + json.dumps(jds) + ";\n"
    out_path = f"/Users/sunder/projects/cahc/cahc-utils/presentations/2026-03-23-iks-astro-talk/ssc/sun-swing-{bcetag}-{abs(epoch_year)}.inc"
    with open(out_path, "w") as f:
        f.write(output)
    print(f"Generated {len(jds)} sunrise JDs to {out_path}.")
