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

## Timing policy

For both benchmark scripts:

- the timed section computes sunrise JDs only
- output formatting and printing happen after timing
- this keeps output I/O from polluting the runtime comparison
