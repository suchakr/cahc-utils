# Chandra Marga

Slug: `chandra-marga`
Status: implemented

## Question

How should the lunar crescent strip images from the moon-shranga Stellarium workflow be collected into the Jyotisha 2026 lab so they can be browsed alongside the other explorations?

## Inputs

- source image root: `/Users/sunder/projects/cahc/cahc-utils/stel_scripts/moon-shranga~/`
- source package notes: `/Users/sunder/projects/cahc/cahc-utils/chandra-marga/README.md`
- legacy notebook context: `/Users/sunder/projects/cahc/cahc-utils/jyotisha/lunar-events-calculator.ipynb`
- curated source list: `explorations/chandra-marga-sources.tsv`
- selected strip artifacts are resolved from the TSV `source_rel` column against the source image root
- event modes:
  - Moonrise at Moon altitude `+8`
  - Eastern moonrise with western Sun altitude `-5`
  - Moonset at Moon altitude `+8`
  - Moonset view at Sun altitude `-9`

## Outputs

- runnable script: `scripts/chandra_marga.py`
- source curation file: `explorations/chandra-marga-sources.tsv`
- converted self-contained WebP gallery assets under `lab/chandra-marga/strips/`
- manifest table: `lab/chandra-marga/tables/strip-manifest.json`
- reader-facing gallery page: `lab/chandra-marga/index.html`
- lab-shell entry in `lab/index.html`

## Notes

- The old notebook is treated as context, not as the source of truth for future reusable code.
- The separate `chandra-marga` package owns the event-solving and strip-building workflow.
- This lab exploration is intentionally a browsing surface: it preserves selected rendered strip outputs without scanning every experimental variant under `moon-shranga~/`.
- `Darsha` is used as the row label for the first-visibility / Shukla 1 set in this brief.
- Reader-facing images are converted to WebP from the exact curated source rows; cropped tile frames are not surfaced.

## Open Questions

- whether the year tags should be normalized into an explicit astronomical-year/BCE labeling convention
- whether live Stellarium-refined Julian Dates should be exposed as a table beside the rendered strips
