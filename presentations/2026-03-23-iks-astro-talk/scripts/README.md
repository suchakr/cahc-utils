# Scripts Notes

## Benchmark scripts

These two files form a like-for-like sunrise benchmark:

- `/Users/sunder/projects/cahc/cahc-utils/presentations/2026-03-23-iks-astro-talk/scripts/bm_astropy.py`
- `/Users/sunder/projects/cahc/cahc-utils/presentations/2026-03-23-iks-astro-talk/scripts/bm_stell.ssc`

Shared benchmark problem:

- location: `Bangalore, India`
- start JD: `2461120.2708333335`
- meaning of start JD: `2026-03-21T00:00:00` local time in `Asia/Kolkata`
- task: compute the next `N` sunrises

## Astropy / Astroplan environment

The Python benchmark is meant to run from the existing `jyotisha` uv-managed environment:

```bash
cd /Users/sunder/projects/cahc/cahc-utils/jyotisha
ASTROPY_IERS_AUTO_DOWNLOAD=0 uv run --with-requirements requirements.txt \
  python ../presentations/2026-03-23-iks-astro-talk/scripts/bm_astropy.py
```

This was re-verified during the benchmark setup:

- `requirements.txt` includes `astropy==6.0.1`
- `requirements.txt` includes `astroplan==0.10.1`
- `uv run --with-requirements requirements.txt python ...` works from the
  `jyotisha` directory

Why keep this note here:

- we had already resolved the environment once and then lost that context
- this README keeps the benchmark run path next to the benchmark files

## User Query Script: Pole Stars Over Time

This script handles the first student-driven follow-up topic:

- method note:
  `/Users/sunder/projects/cahc/cahc-utils/presentations/2026-03-23-iks-astro-talk/docs/user-01-pole-stars-over-time.md`
- Python/Astropy scan:
  `/Users/sunder/projects/cahc/cahc-utils/presentations/2026-03-23-iks-astro-talk/scripts/user_01_pole_stars_over_time.py`
- generated Stellarium script target:
  `/Users/sunder/projects/cahc/cahc-utils/presentations/2026-03-23-iks-astro-talk/ssc/user-01-pole-stars-over-time.ssc`

Run it from the existing `jyotisha` uv-managed environment:

```bash
cd /Users/sunder/projects/cahc/cahc-utils/jyotisha
ASTROPY_IERS_AUTO_DOWNLOAD=0 uv run --with-requirements requirements.txt \
  python ../presentations/2026-03-23-iks-astro-talk/scripts/user_01_pole_stars_over_time.py
```

The script:

- fetches Hipparcos once from Vizier if `data/hip_main_vizier.tsv` is missing
- caches a normalized local TSV for repeatable runs
- scans candidate stars with Astropy across the chosen epoch range
- emits a self-contained Stellarium script with one best-fit row per HIP

## Timing policy

For both benchmark scripts:

- the timed section computes sunrise JDs only
- output formatting and printing happen after timing
- this keeps output I/O from polluting the runtime comparison
