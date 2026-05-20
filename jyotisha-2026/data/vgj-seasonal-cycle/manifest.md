# VGJ Seasonal Nakshatra Cycle Seed Manifest

Copy date: 2026-05-16

These files are vendored one time from the read-only upstream `../datasets/nakshatras/`
tree so this exploration can regenerate from `jyotisha-2026` alone. The generator
does not import legacy VGJ code.

| File | Original path | Role | Purpose |
| --- | --- | --- | --- |
| `n27_lon_divisions.csv` | `../datasets/nakshatras/n27_lon_divisions.csv` | canonical seed | Equal and shifted nakshatra boundary longitudes used for bound-fit scoring. |
| `n83_lat_lon_ra_dec_bce2500_ce1000.tsv` | `../datasets/nakshatras/n83_lat_lon_ra_dec_bce2500_ce1000.tsv` | canonical seed | 83-star family positions at coarse epochs for field plots and coarse error curves. |
| `n83_mag.tsv` | `../datasets/nakshatras/n83_mag.tsv` | validation-only | Magnitudes at -1500 used for plot sizing where names match. |
| `n27_base_Feb24_bce2500_to_ce0500.tsv` | `../datasets/nakshatras/n27_base_Feb24_bce2500_to_ce0500.tsv` | canonical seed | Main 27-proxy epoch series. |
| `n27_delta_Feb20_bce2500_to_ce0500.tsv` | `../datasets/nakshatras/n27_delta_Feb20_bce2500_to_ce0500.tsv` | canonical patch seed | Aṣāḍhā replacement rows used in the base scenario. Other rows remain available for validation. |
| `n27_delta_shr_dha_bce2500_to_ce0500.tsv` | `../datasets/nakshatras/n27_delta_shr_dha_bce2500_to_ce0500.tsv` | canonical scenario seed | Śraviṣṭhā/Dhaniṣṭhā sensitivity replacements. |
| `n27_delta_abhyankar_bce2500_to_ce0500.tsv` | `../datasets/nakshatras/n27_delta_abhyankar_bce2500_to_ce0500.tsv` | canonical scenario seed | Abhyankar-style representative substitutions. |
