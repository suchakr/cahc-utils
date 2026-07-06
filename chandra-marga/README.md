# chandra-marga

Astropy-based event solver + Stellarium export pipeline for the crescent-moon
(moon-shranga) series, moved out of `jyotisha/lunar-events-calculator.ipynb`
into a standalone `uv` package.

## Scope
chandra-marga's job is **dates in, strip out**:
1. Compute the event JDs (`01_compute_events.py`).
2. Crop + stitch the resulting Stellarium screenshots into a strip
   (`02_clip_and_strip.py`).

The Stellarium rendering step in between is inherently interactive/manual
(it's a GUI app) and is NOT something this package tries to own or
automate end-to-end. It's a documented handoff: chandra-marga writes a
`.inc` file that a `.ssc` script `include()`s, and a `.ssc` script writes
screenshots that chandra-marga's crop/strip step reads back in. See
"End-to-end workflow" below for the full loop.

## One-time setup
`.ssc` scripts must be run via Stellarium's *native* named-script loader
(`stelrc.py run-script <name>`, which hits the Remote Control `/scripts/run`
endpoint) for `include()` to resolve. `run-file`/`script-direct` (which POST
raw code to `/scripts/direct`) do NOT resolve `include()` -- the script has
no file identity in that path, so there's no base directory to resolve
relative includes against. `run-script` requires the `.ssc` (and any `.inc`
it includes) to live under Stellarium's own scripts directory, so symlink it
to `stel_scripts/` once:
```
ln -s /Users/sunder/projects/cahc/cahc-utils/stel_scripts \
      "$HOME/Library/Application Support/Stellarium/scripts"
```
`run-script` also pops open the Script Console window the first time it's
used in a session; that window will appear in every screenshot until
toggled off. Toggle it via the external action API (not from within the
`.ssc` -- `StelActionMgr` isn't callable from scripts in this Stellarium
build) once per Stellarium session, before running a production capture:
```
python3 ~/.agents/skills/stellarium/scripts/stelrc.py action run \
    actionShow_ScriptConsole_Window_Global
```

## End-to-end workflow
Example for the Sun-at-−9° shukla_pratipada series, year -527:
0. **Compute the base moonset/moonrise series**, if the one you need doesn't
   already exist (e.g. `lunar-set-events--0527.inc` is already committed for
   moonset, year -527; a moonrise equivalent must be generated per event
   type/window since only moonset was ever produced from the notebook):
   ```
   uv run python scripts/00_compute_base_events.py \
       --event-type set --start-time="-00527-01-01T00:00:00.000" \
       --ndays 1460 --year-tag 0527
   ```
   `--ndays` counts sampled moon events (~1.03 days apart each), not calendar
   days -- 1460 covers this project's usual ~4.15-year/51-event window
   starting 1 Jan -527. Writes `stel_scripts/lunar-<event-type>-events--<year-tag>.inc`
   with `amavasya`/`purnima`/`shukla_pratipada`/`shukla_dwitiya`/`krishna_chaturdashi` keys.
1. **Compute target JDs** (writes `stel_scripts/sun-alt-minus9-events--0527.inc`):
   ```
   uv run python scripts/01_compute_events.py \
       --source-inc lunar-set-events--0527.inc --year-tag 0527 \
       --paksha shukla --thithi 1 \
       --target-body sun --target-altitude -9.0 --event-type set
   ```
2. **Bind** the `.ssc` script to that `.inc` file. `a10-moon-shranga-sun9.ssc`
   already does this via `include("sun-alt-minus9-events--0527.inc")` --
   if you regenerate for a different year/paksha/thithi/target, update that
   filename (and the `TITHI` var used to index into the included dict) to
   match what step 1 just wrote.
3. **Run the capture** in Stellarium (produces `moon-shranga~/<mode>/<year>/<tithi>/NN.jpg`):
   ```
   python3 ~/.agents/skills/stellarium/scripts/stelrc.py run-script a10-moon-shranga-sun9.ssc
   ```
4. **Crop + strip**:
   ```
   uv run python scripts/02_clip_and_strip.py \
       /Users/sunder/projects/cahc/cahc-utils/stel_scripts/moon-shranga~/set-sun9/-527/shukla_pratipada
   ```

A second worked example -- full moon RISING in the east, Sun at -5°, same
-527 window (`a11-moon-purnima-rise-sun5.ssc`):
```
uv run python scripts/00_compute_base_events.py \
    --event-type rise --start-time="-00527-01-01T00:00:00.000" \
    --ndays 1460 --year-tag 0527
uv run python scripts/01_compute_events.py \
    --source-inc lunar-rise-events--0527.inc --year-tag 0527 \
    --paksha shukla --thithi 15 \
    --target-body sun --target-altitude -5.0 --event-type set
python3 ~/.agents/skills/stellarium/scripts/stelrc.py run-script a11-moon-purnima-rise-sun5.ssc
uv run python scripts/02_clip_and_strip.py \
    /Users/sunder/projects/cahc/cahc-utils/stel_scripts/moon-shranga~/rise-sun5/-527/purnima
```
Note `--event-type set` in step 1 here too: it selects the SUN's crossing
direction (descending through -5°, same as dusk deepening after sunset), not
the source event type -- the source (`lunar-rise-events--0527.inc`) is a
moonrise series regardless. Validated: moon illumination ~99.5-99.9% and
altitude mostly +0 to +8° (occasionally grazing the horizon) with real
az/alt variation month to month, at Sun alt exactly -5.00° (astropy-solved).

Caveat carried from this series' validation: astropy's Sun ephemeris is
extrapolated far outside its 1900-2100 AD validity range for a date this
far in the past and disagreed with live Stellarium by up to ~0.4° for -527.
The `.inc` currently committed for this series was refined against live
Stellarium (Newton-corrected, converges to sun alt = -9.0000 ± 0.0003°) --
rerunning step 1 with default settings will silently overwrite it with the
less-accurate astropy-only values (this happened once already during
development). For deep-historical dates, treat `01_compute_events.py`'s
output as a seed and spot-check/refine it against live Stellarium before
trusting it for a real capture, the same way this series was validated.

`a10-moon-shranga-sun9.ssc` also guards against a real (non-deterministic)
Stellarium race condition where `getObjectInfo()` can return a stale value
for a few seconds after `setJDay()`: it re-queries the Sun's altitude until
it actually matches the precomputed target before trusting the readback,
rather than relying on a fixed `wait()` duration (which was tried first and
proved unreliable -- three different fixed-priming attempts each converged
to a different wrong answer).

## Layout
- `src/chandra_marga/config.py` — observer locations, absolute path config,
  `event_slug(paksha, thithi)` (generic paksha/thithi -> event-key naming,
  e.g. `shukla_pratipada`, `krishna_chaturdashi`, special-cased `purnima`/
  `amavasya` for thithi 15).
- `src/chandra_marga/events.py` — moonset/moonrise/thithi calculator (ported
  from the notebook, generalized to `compute_lunar_events(..., event_type=
  'set'|'rise')`; `compute_moonset_events` is a thin backwards-compatible
  alias) plus a generic altitude-target solver
  (`compute_altitude_target_jds`) that works for EITHER the Sun or the Moon,
  EITHER a set or rise crossing, given an arbitrary target altitude.
  Generalizes both known use cases:
    - `target_body="sun", target_alt_deg=-9.0`: Sun-at-9°-below-horizon
      twilight-background series (`a10-moon-shranga-sun9.ssc`).
    - `target_body="moon", target_alt_deg=8.0`: Moon-at-8° series
      (`a9-moon-shranga.ssc`; previously only a live in-script Newton
      correction, never available as a precompute).
  Only `(sun, set)` has been empirically validated against live Stellarium
  (see `DEFAULT_SEED_OFFSET_HOURS` docstring for caveats on the other three
  combinations) -- spot-check any new combination the same way before
  trusting it for a production run.
- `src/chandra_marga/stellarium_export.py` — reads/writes `.inc` JD arrays
  (consumed via `include()` when the `.ssc` is run through `run-script`; see
  "One-time setup" above) and formats copy-pasteable JS array literals as a
  fallback for one-off scripts run via `run-file`/`script-direct`, where
  `include()` doesn't resolve.
- `src/chandra_marga/crop.py` / `strips.py` — tile-crop geometry (queries
  live Stellarium FOV, computes the pixel box for the centered-at-horizon
  framing convention) and PIL-based strip/contact-sheet assembly. These are
  already generic (they only operate on images/paths, independent of
  target-body/event-type/paksha/thithi).
- `scripts/00_compute_base_events.py` — generic CLI: compute the base
  moonset/moonrise series (amavasya/purnima/shukla_pratipada/shukla_dwitiya/
  krishna_chaturdashi) for any `--event-type {set,rise}` / `--start-time` /
  `--ndays` / `--location`, and write it as a `.inc` file (e.g.
  `lunar-set-events--0527.inc`, `lunar-rise-events--0527.inc`). This is the
  `--source-inc` consumed by `01_compute_events.py`.
- `scripts/01_compute_events.py` — generic CLI: compute altitude-target JDs
  for any `--target-body {sun,moon}` / `--target-altitude` / `--event-type
  {set,rise}` / `--paksha {shukla,krishna}` / `--thithi 1-15`, from an
  existing moonset/moonrise `.inc` file. Writes a `.inc` file named from the
  resolved tag (e.g. `sun-alt-minus9-events--0527.inc`,
  `moon-alt-8-events--0527.inc`) and prints an embeddable JS array.
- `scripts/02_clip_and_strip.py` — CLI: crop raw screenshots to tiles
  (centered-at-horizon convention) and assemble them into a strip.

Images stay owned by `stel_scripts/moon-shranga~/...`; this package only
reads/writes JD data and reads/writes into that tree via absolute paths.

Not yet generic: the `.ssc` Stellarium scripts themselves (`a9-moon-shranga.ssc`,
`a10-moon-shranga-sun9.ssc`, `a11-moon-purnima-rise-sun5.ssc`) are still
hand-written per variant. Each one's
`include("<file>.inc")` filename (and the key used to index into the
included dict) must be manually kept in sync with whatever
`01_compute_events.py` last wrote for that series -- a template/codegen
step would be needed to generate the `.ssc` itself from those parameters.

## Usage
See "End-to-end workflow" above for the full loop. Quick reference:
```
uv sync
uv run python scripts/00_compute_base_events.py --help
uv run python scripts/01_compute_events.py --help
uv run python scripts/02_clip_and_strip.py --help
```
