# Nakshatra Precession Explorer

Slug: `nakshatra-precession-explorer`
Status: implemented
Story PRD: [vyoma-sutra-prd.md](../stories/nakshatra-precession-explorer/vyoma-sutra-prd.md)

## Question

How can precessional time be shown clearly by separating the fixed sidereal nakshatra framework from the drifting seasonal framework, while joining textual nakshatra metadata with constituent-star geometry?

## Conceptual Model

- The sidereal frame is fixed:
  - stars
  - nakshatra asterism shapes
  - 27 equal nakshatra sectors on the ecliptic
  - Abhijit as an additional asterism, not one of the 27 equal sectors
- The seasonal frame drifts with epoch:
  - equinoxes
  - solstices
  - six rtus
  - equator relative to the ecliptic
  - pole position around the ecliptic pole
- Precession is therefore shown as changing alignment between the fixed sidereal frame and the drifting seasonal frame.

## Inputs

- `../datasets/n28_good_meta.csv` as the metadata spine for names, shape labels, proxies, constituent-star text, and related properties
- `../datasets/n83_full_meta_for_-1750.csv` as the main J2000 star-position source for nakshatra constituent stars
- `../nakshatra_sky_culture/vedic_25_codex/index.json` for nakshatra asterism line geometry
- `../nakshatra_sky_culture/data/stars_mag6_within_30_declination.csv` as an Abhijit coordinate supplement
- 27 equal ecliptic sectors anchored from the lunar-system link star in the sky-culture JSON
- Abhijit represented explicitly as an asterism overlay outside the equal-27 sector scheme
- epoch as a shared state variable controlled by a slider

## Outputs

- joined exploration dataset combining nakshatra metadata and asterism geometry
- epoch slider shared by all current views
- `Table` view with seasonal alignment cues and marker-in-sector annotations
- `2D Sky` view with stars, nakshatra shapes, ecliptic band, 27 sectors, Abhijit, equator, seasonal belt, equinoxes, solstices, and pole position
- `3D Sky` view as the live development baseline for the same fixed-versus-drifting model
- build-time 3D stories authored as `stories/nakshatra-precession-explorer/*.vysu` and compiled to `stories/nakshatra-precession-explorer/compiled/*.json`
- top 3D story pills sourced from `# featured: true` metadata, capped at five visible matches with search for larger story sets
- generated CSS in `lab/nakshatra-precession-explorer/assets/css/explorer.css` and an inspectable copy of the inline 3D runtime in `assets/js/three-explorer.js`
- short interpretive notes explaining the fixed-versus-drifting-frame model

## Maintenance Notes

- `scripts/nakshatra_precession_explorer.py` remains the generator for dataset, HTML, and generated 3D assets.
- `scripts/compile_stories.py nakshatra-precession-explorer` is the fast story-only path; it does not import astropy and replaces the existing lab page story payload from current story sources.
- `lab/nakshatra-precession-explorer/index.html` is generated and should not be hand-edited; CSS lives in `assets/css/explorer.css`, while the 3D module remains inline for `file://` and is also copied to `assets/js/three-explorer.js` for inspection.
- Story grammar and target vocabulary should be updated in `stories/nakshatra-precession-explorer/SKILL.md` and `vyoma-sutra-prd.md` before matching code changes.
- Use `netlify dev --dir lab` from the `jyotisha-2026` repo root for local review; `file://` viewing is secondary.

## Open Questions

- whether the equal-27 sector anchor should remain tied to the current sky-culture link-star convention or be overridden by a repo-specific convention later
- what epoch range and slider granularity should be preferred for later passes
- how far the 3D story layer should go before adding browser-side story authoring
