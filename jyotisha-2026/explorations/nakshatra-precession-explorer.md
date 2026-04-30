# Nakshatra Precession Explorer

Slug: `nakshatra-precession-explorer`
Status: implemented

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
- `2D Sky` view with stars, nakshatra shapes, ecliptic band, 27 sectors, Abhijit, equator, seasonal belt, equinoxes, solstices, pole position, and codex overlays for Shiṁśumāra, Matsya, and Agastya
- guided `Set Stage` and `Time Travel` modes in the 2D view, with `Time Travel` pausing at curated epoch anchors
- short interpretive notes explaining the fixed-versus-drifting-frame model

## Open Questions

- whether the equal-27 sector anchor should remain tied to the current sky-culture link-star convention or be overridden by a repo-specific convention later
- what epoch range and slider granularity should be preferred for later passes
- how much of the current 2D rendering logic should be reused directly when the Three.js sphere is revived
