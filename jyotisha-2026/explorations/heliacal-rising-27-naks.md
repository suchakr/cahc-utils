# 27 Nakshatra Heliacal Rising and Setting Across Three BCE Epochs

Slug: `heliacal-rising-27-naks`
Status: implemented

## Question

For an ordered 27-nakshatra sequence, how do heliacal-rising and heliacal-setting azimuth and declination compare across the epochs -1500, -1000, and -500?

## Inputs

- reusable nakshatra metadata, likely seeded from `n28_good_meta.csv` and related upstream files
- ordered base from `../datasets/nakshatras/n27_full_meta.csv`
- proxy cross-check from `../datasets/n28_good_meta.csv`
- chosen representative star or proxy for each of 27 nakshatras
- site latitude: `30°N`
- longitude fixed at `0°` for the first pass because the requested plots depend on latitude and declination rather than site longitude
- heliacal criteria:
  - rising: first morning when the proxy star is above the horizon while the Sun is at `-10°` altitude
  - setting: last evening when the proxy star is above the horizon while the Sun is at `-10°` altitude
- epoch list: `-1500`, `-1000`, `-500`
- label style: full transliterated names

## Outputs

- plot: ordered nakshatras on x, rising azimuth on y, one series per epoch
- plot: ordered nakshatras on x, rising azimuth on y, one series per epoch, with contiguous `veethi` bands annotated and subtly color-filled
- plot: ordered nakshatras on x, setting azimuth on y, one series per epoch
- plot: ordered nakshatras on x, setting azimuth on y, one series per epoch, with contiguous `veethi` bands annotated and subtly color-filled
- plot: ordered nakshatras on x, rising declination on y, one series per epoch
- plot: ordered nakshatras on x, rising declination on y, one series per epoch, with contiguous `veethi` bands annotated and subtly color-filled
- plot: ordered nakshatras on x, setting declination on y, one series per epoch
- plot: ordered nakshatras on x, setting declination on y, one series per epoch, with contiguous `veethi` bands annotated and subtly color-filled
- A-variant plot: rising azimuth for epoch `-500` only, with each nakshatra rendered as a VGJ-style constituent-star cluster centered on its computed point, without trend or fitted lines
- A-variant plot: setting azimuth for epoch `-500` only, with the same cluster convention and the source plot's axis range
- A-variant plot: rising declination for epoch `-500` only, with the same cluster convention and the source plot's axis range
- A-variant plot: setting declination for epoch `-500` only, with the same cluster convention and the source plot's axis range
- B-variant plot: rising and setting azimuth for epoch `-500`, with reduced star-dot diameter, Stellarium skyculture stick figures, no inline cluster labels, and bottom labels formatted as `<nakshatra:count>`
- B-variant plot: rising and setting declination for epoch `-500`, with the same bounded star-span scaling for dots and stick figures
- B-variant line art uses the Stellarium skyculture topology where enough plotted HIP endpoints are present; otherwise it falls back to a best-fit ordered line and connects remaining isolated stars to their nearest plotted neighbor
- B-variant orientation guides mark rising east at `90°`, setting west at `270°`, and the declination equator at `0°`, with compact north/south side cues on the y-axis
- C-variant plot: B-style rising and setting azimuth with a smooth Bharani-zero ecliptic ±5° latitude band projected into horizon azimuth at `30°N`
- C-variant plot: B-style rising and setting declination with a smooth Bharani-zero ecliptic declination curve and ±5° ecliptic-latitude band
- D-variant plot: measured rising and setting azimuth, positioning individual stars by their `-500` ecliptic longitude and declination-derived horizon azimuth against the same Bharani-zero ecliptic band
- D-variant plot: measured rising and setting declination, positioning individual stars by their `-500` ecliptic longitude and true declination so distance from the ecliptic band is directly readable
- export table for all computed values
- short written narration highlighting visible shifts and outliers
- side-by-side presentation of rise/set plain plots, followed by side-by-side rise/set veethi-annotated plots

## Open Questions

- whether later passes should use a site-specific longitude tied to a particular historical region
- whether a stricter visibility threshold should be used beyond `star altitude > 0°`
- whether the veethi color palette should be standardized across future explorations
