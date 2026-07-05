# Chandra Marga

Slug: `chandra-marga`
Status: implemented

## Question

How should the lunar crescent strip images from the moon-shranga Stellarium workflow be collected into the Jyotisha 2026 lab so they can be browsed alongside the other explorations?

## Inputs

- source image root: `/Users/sunder/projects/cahc/cahc-utils/stel_scripts/moon-shranga~/`
- source package notes: `/Users/sunder/projects/cahc/cahc-utils/chandra-marga/README.md`
- legacy notebook context: `/Users/sunder/projects/cahc/cahc-utils/jyotisha/lunar-events-calculator.ipynb`
- selected strip artifacts:
  - `clip04-strip*.jpg`
  - `*darsha*.jpg` / `*darsha*.jpeg`
  - `strip-set-sun-below-9*.jpg`
- event modes:
  - Moonrise at Moon altitude `+8`
  - Moonset at Moon altitude `+8`
  - Moonset view at Sun altitude `-9`

## Outputs

- runnable script: `scripts/chandra_marga.py`
- converted self-contained WebP gallery assets under `lab/chandra-marga/strips/`
- manifest table: `lab/chandra-marga/tables/strip-manifest.json`
- reader-facing gallery page: `lab/chandra-marga/index.html`
- lab-shell entry in `lab/index.html`

## Notes

- The old notebook is treated as context, not as the source of truth for future reusable code.
- The separate `chandra-marga` package owns the event-solving and strip-building workflow.
- This lab exploration is intentionally a browsing surface: it preserves the rendered strip outputs without exposing local source paths in the deployed page.
- For `S1` in `-527`, the curated strip uses the Sun-altitude `-9` moonset view; the other selected moonset strips use Moon altitude `+8`.

## Open Questions

- whether later passes should include the larger source collection or keep this curated strip set
- whether the year tags should be normalized into an explicit astronomical-year/BCE labeling convention
- whether live Stellarium-refined Julian Dates should be exposed as a table beside the rendered strips
