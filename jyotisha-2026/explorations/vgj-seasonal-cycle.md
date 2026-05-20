# VGJ Seasonal Nakshatra Cycle

Slug: `vgj-seasonal-cycle`
Status: stage-1

## Question

How closely do the Vṛddhagārgīya Jyotiṣa Ādityacāra and Ṛtusvabhāva
nakshatra-season alignments fit reconstructed stellar longitudes across BCE
epochs, and how sensitive is that fit to representative-star identification?

## Inputs

- Vendored local seed data under `data/vgj-seasonal-cycle/`.
- Equal and shifted nakshatra longitude divisions from `n27_lon_divisions.csv`.
- 27-proxy epoch series from `n27_base_Feb24_bce2500_to_ce0500.tsv`, patched
  for the Aṣāḍhā pair from `n27_delta_Feb20_bce2500_to_ce0500.tsv`.
- Sensitivity replacements from `n27_delta_shr_dha_bce2500_to_ce0500.tsv`.
- Abhyankar-style replacements from `n27_delta_abhyankar_bce2500_to_ce0500.tsv`.
- 83-star coarse epoch positions from `n83_lat_lon_ra_dec_bce2500_ce1000.tsv`.
- Magnitude hints from `n83_mag.tsv` for star-field sizing.

## Outputs

- Epoch error curves for 27 proxies, 83 stars, and nine seasonal boundary representatives.
- Identification-sensitivity curves for base, Śraviṣṭhā/Dhaniṣṭhā sensitivity,
  and Abhyankar-style substitutions.
- A seed-derived solar month-cycle schematic over the nakshatra boundary frame.
- N83 longitude/latitude and RA/Dec star fields for -1500, -1000, and -500.
- Bound-fit counts and strongest-fit epoch windows.
- Inline preview tables and short narration in `lab/vgj-seasonal-cycle/`.

## Reproduction Policy

The Stage 1 implementation does not import code from the legacy `cahc-utils/jyotisha`
tree. The copied seed files are the runtime source of truth. Upstream and legacy
materials may be used as qualitative reference, but the generated lab page must be
reproducible from this repository alone.

## Drift Policy

Astropy regeneration is allowed only when a seed value is unclear or absent. Any
material differences from seed-derived conclusions should be called out in the
narration and tables. Stage 1 uses vendored seed data only, so no regenerated
Astropy drift is expected.

## Open Questions

- Whether the twelve-month solar transit chart should eventually use regenerated
  solar longitudes rather than the current seed-derived schematic.
- Whether a later pass should include full-moon overlays, Mars vakra paths, and
  Venus visibility diagrams.
