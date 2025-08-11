# Dataset Reorganization Log

## Overview
Reorganized CAHC Utils datasets from flat structure to organized hierarchy.

## New Structure
```
datasets/
├── raw/                    # Original, unprocessed data
│   ├── catalogs/          # Star catalogs, reference data
│   └── references/        # Lookup tables, metadata
├── intermediate/           # Processing outputs
│   ├── moon_phases/       # Moon rise/set events
│   ├── planet_positions/  # Planetary position data
│   ├── kuru_calculations/ # Kuru-specific computations
│   ├── nakshatras/        # Nakshatra calculations
│   ├── full_moons/        # Full moon data
│   ├── eclipses/          # Eclipse data
│   └── calculations/      # Large computation files (.pickle)
├── archive/               # Old versions and backups
│   ├── backups/          # Files with ~ suffix
│   └── old_versions/     # Dated snapshots
├── final/                 # Clean, analysis-ready datasets
└── metadata/              # Documentation
```

## File Migrations
- `amara-kosha-list.csv` → `raw/catalogs/amara-kosha-list.csv`
- `5MKLEcatalog.txt` → `raw/catalogs/5MKLEcatalog.txt`
- `amara-kosha-months.csv` → `raw/catalogs/amara-kosha-months.csv`
- `n90_full_meta_for_-1600.csv` → `raw/references/n90_full_meta_for_-1600.csv`
- `n90_full_meta_for_2023.csv` → `raw/references/n90_full_meta_for_2023.csv`
- `n28_full_meta.csv` → `raw/references/n28_full_meta.csv`
- `n90_full_meta_for_-1400.csv` → `raw/references/n90_full_meta_for_-1400.csv`
- `n83_full_meta_for_-1600.csv` → `raw/references/n83_full_meta_for_-1600.csv`
- `tara-circumpolarity.tsv` → `raw/references/tara-circumpolarity.tsv`
- `n83_full_meta_for_-1700.csv` → `raw/references/n83_full_meta_for_-1700.csv`
- `n90_full_meta_for_-1700.csv` → `raw/references/n90_full_meta_for_-1700.csv`
- `n28_good_meta.csv` → `raw/references/n28_good_meta.csv`
- `n83_full_meta_mar_16_2023_snapshot~.csv` → `raw/references/n83_full_meta_mar_16_2023_snapshot~.csv`
- `ss-units-ratios.csv` → `raw/references/ss-units-ratios.csv`
- `n27_limited_meta.csv` → `raw/references/n27_limited_meta.csv`
- `n90_full_meta_for_-2000.csv` → `raw/references/n90_full_meta_for_-2000.csv`
- `vj-units-fractions.csv` → `raw/references/vj-units-fractions.csv`
- `n83_full_meta_for_2023.csv` → `raw/references/n83_full_meta_for_2023.csv`
- `n27_full_meta.csv` → `raw/references/n27_full_meta.csv`
- `n90_full_meta_for_-1650.csv` → `raw/references/n90_full_meta_for_-1650.csv`
- `n83_full_meta_for_-1650.csv` → `raw/references/n83_full_meta_for_-1650.csv`
- `ss-units-fractions.csv` → `raw/references/ss-units-fractions.csv`
- `vj-units-ratios.csv` → `raw/references/vj-units-ratios.csv`
- `n90_full_meta_for_-1800.csv` → `raw/references/n90_full_meta_for_-1800.csv`
- `n83_full_meta_for_-1750.csv` → `raw/references/n83_full_meta_for_-1750.csv`
- `n90_full_meta_for_-1550.csv` → `raw/references/n90_full_meta_for_-1550.csv`
- `n90_full_meta_for_-1750.csv` → `raw/references/n90_full_meta_for_-1750.csv`
- `n83_full_meta_for_-1550.csv` → `raw/references/n83_full_meta_for_-1550.csv`
- `n90_full_meta.csv` → `raw/references/n90_full_meta.csv`
- `n83_full_meta.csv` → `raw/references/n83_full_meta.csv`
- `n83_full_meta_for_-1800.csv` → `raw/references/n83_full_meta_for_-1800.csv`
- `_moon_rise_events_0_36600_27~.csv` → `intermediate/moon_phases/_moon_rise_events_0_36600_27~.csv`
- `moon_set_events.csv~` → `intermediate/moon_phases/moon_set_events.csv~`
- `sun_moon_pos_-1000-01-01_for_100_years_in_0.056_jd_steps.csv` → `intermediate/moon_phases/sun_moon_pos_-1000-01-01_for_100_years_in_0.056_jd_steps.csv`
- `_moon_rise_events_0_3660_28~.csv` → `intermediate/moon_phases/_moon_rise_events_0_3660_28~.csv`
- `moon-phases-js-array.ssc` → `intermediate/moon_phases/moon-phases-js-array.ssc`
- `moon_set_events_2025_35_1.0~.csv` → `intermediate/moon_phases/moon_set_events_2025_35_1.0~.csv`
- `_moon_set_events_-499_12000_29.5~.csv` → `intermediate/moon_phases/_moon_set_events_-499_12000_29.5~.csv`
- `_moon_set_events_-499_1200_29.5~.csv` → `intermediate/moon_phases/_moon_set_events_-499_1200_29.5~.csv`
- `moon-phases-scrape-raw.txt` → `intermediate/moon_phases/moon-phases-scrape-raw.txt`
- `_moon_set_events_-499_800_29.5~.csv` → `intermediate/moon_phases/_moon_set_events_-499_800_29.5~.csv`
- `moon_rise_events_-499_40_1~.csv` → `intermediate/moon_phases/moon_rise_events_-499_40_1~.csv`
- `_moon_rise_events_-499_7320_1~.csv` → `intermediate/moon_phases/_moon_rise_events_-499_7320_1~.csv`
- `sun_moon_pos_-1000-01-01_for_100_years_in_0.167_jd_steps.csv` → `intermediate/moon_phases/sun_moon_pos_-1000-01-01_for_100_years_in_0.167_jd_steps.csv`
- `_moon_rise_events_-499_40_1~.csv` → `intermediate/moon_phases/_moon_rise_events_-499_40_1~.csv`
- `moon_rise_events_-499_1098_1.0~.csv` → `intermediate/moon_phases/moon_rise_events_-499_1098_1.0~.csv`
- `moon_set_events_-1300_1098_1.0~.csv` → `intermediate/moon_phases/moon_set_events_-1300_1098_1.0~.csv`
- `_moon_set_events_2025_35_1.0~.csv` → `intermediate/moon_phases/_moon_set_events_2025_35_1.0~.csv`
- `moon-phases-scrape-cooked.csv` → `intermediate/moon_phases/moon-phases-scrape-cooked.csv`
- `anamalous_moon_-2000_1830_10~.pickle` → `intermediate/moon_phases/anamalous_moon_-2000_1830_10~.pickle`
- `moon_rise_events_2025_35_1.0~.csv` → `intermediate/moon_phases/moon_rise_events_2025_35_1.0~.csv`
- `_moon_set_events_-499_120_29.5~.csv` → `intermediate/moon_phases/_moon_set_events_-499_120_29.5~.csv`
- `_moon_rise_events_-499_120_29.5~.csv` → `intermediate/moon_phases/_moon_rise_events_-499_120_29.5~.csv`
- `moon_dwell_scp_span_left.csv` → `intermediate/moon_phases/moon_dwell_scp_span_left.csv`
- `moon_set_events_2025_1098_1.0~.csv` → `intermediate/moon_phases/moon_set_events_2025_1098_1.0~.csv`
- `moon_set_events_-499_12000_29.5~.csv` → `intermediate/moon_phases/moon_set_events_-499_12000_29.5~.csv`
- `moon_set_events_2025_5_1.0~.csv` → `intermediate/moon_phases/moon_set_events_2025_5_1.0~.csv`
- `_moon_set_events_-499_1200_1~.csv` → `intermediate/moon_phases/_moon_set_events_-499_1200_1~.csv`
- `_moon_set_events_2025_5_1.0~.csv` → `intermediate/moon_phases/_moon_set_events_2025_5_1.0~.csv`
- `_moon_set_events_-1300_1098_1.0~.csv` → `intermediate/moon_phases/_moon_set_events_-1300_1098_1.0~.csv`
- `_moon_rise_events_-499_1098_1.0~.csv` → `intermediate/moon_phases/_moon_rise_events_-499_1098_1.0~.csv`
- `moon_set_events_-499_800_29.5~.csv` → `intermediate/moon_phases/moon_set_events_-499_800_29.5~.csv`
- `_moon_rise_events_2025_35_1.0~.csv` → `intermediate/moon_phases/_moon_rise_events_2025_35_1.0~.csv`
- `moon_rise_events_-499_120_29.5~.csv` → `intermediate/moon_phases/moon_rise_events_-499_120_29.5~.csv`
- `moon_rise_events_-499_3660_29.5~.csv` → `intermediate/moon_phases/moon_rise_events_-499_3660_29.5~.csv`
- `full_moon_bce1500.tsv` → `intermediate/moon_phases/full_moon_bce1500.tsv`
- `nasa-moon-phases-jd.tsv` → `intermediate/moon_phases/nasa-moon-phases-jd.tsv`
- `_moon_rise_events_0_3660_26~.csv` → `intermediate/moon_phases/_moon_rise_events_0_3660_26~.csv`
- `moon-planet-pos-bce2000-to-bce0100.csv` → `intermediate/moon_phases/moon-planet-pos-bce2000-to-bce0100.csv`
- `_moon_rise_events_-499_40_2~.csv` → `intermediate/moon_phases/_moon_rise_events_-499_40_2~.csv`
- `moon_dwell_proxy_0445_left.csv` → `intermediate/moon_phases/moon_dwell_proxy_0445_left.csv`
- `moon_dwell_proxy_1479_left.csv` → `intermediate/moon_phases/moon_dwell_proxy_1479_left.csv`
- `moon_set_events_-499_1200_1~.csv` → `intermediate/moon_phases/moon_set_events_-499_1200_1~.csv`
- `moon_rise_events_-499_40_2~.csv` → `intermediate/moon_phases/moon_rise_events_-499_40_2~.csv`
- `_moon_rise_events_0_3660_27.5~.csv` → `intermediate/moon_phases/_moon_rise_events_0_3660_27.5~.csv`
- `_moon_rise_events_-499_3660_29.5~.csv` → `intermediate/moon_phases/_moon_rise_events_-499_3660_29.5~.csv`
- `moon_rise_events_-499_7320_1~.csv` → `intermediate/moon_phases/moon_rise_events_-499_7320_1~.csv`
- `_moon_set_events_2025_1098_1.0~.csv` → `intermediate/moon_phases/_moon_set_events_2025_1098_1.0~.csv`
- `full_new_moon_2500_1500_bce.csv` → `intermediate/moon_phases/full_new_moon_2500_1500_bce.csv`
- `full-moon-planet-pos-bce2000-to-bce0100.csv` → `intermediate/moon_phases/full-moon-planet-pos-bce2000-to-bce0100.csv`
- `_moon_rise_events_0_3660_27~.csv` → `intermediate/moon_phases/_moon_rise_events_0_3660_27~.csv`
- `moon_set_events_-499_1200_29.5~.csv` → `intermediate/moon_phases/moon_set_events_-499_1200_29.5~.csv`
- `moon_set_events_-499_120_29.5~.csv` → `intermediate/moon_phases/moon_set_events_-499_120_29.5~.csv`
- `fm_kv_planetpos_4.tsv` → `intermediate/planet_positions/fm_kv_planetpos_4.tsv`
- `kuru_sunrises_-1200.csv` → `intermediate/kuru_calculations/kuru_sunrises_-1200.csv`
- `kuru_naksset_-1700.csv` → `intermediate/kuru_calculations/kuru_naksset_-1700.csv`
- `kuru_sunrises_-2250.csv` → `intermediate/kuru_calculations/kuru_sunrises_-2250.csv`
- `kuru_naksrise_-1700.csv` → `intermediate/kuru_calculations/kuru_naksrise_-1700.csv`
- `kb_381bce-1008years~.pkl` → `intermediate/kuru_calculations/kb_381bce-1008years~.pkl`
- `kuru_sunrises_-2050.csv` → `intermediate/kuru_calculations/kuru_sunrises_-2050.csv`
- `kuru_naksrise_-1500.csv` → `intermediate/kuru_calculations/kuru_naksrise_-1500.csv`
- `kb_2500bce-3years~.pkl` → `intermediate/kuru_calculations/kb_2500bce-3years~.pkl`
- `kuru_sunrises_-1000.csv` → `intermediate/kuru_calculations/kuru_sunrises_-1000.csv`
- `kuru_naksrise_daynum--1300~.csv` → `intermediate/kuru_calculations/kuru_naksrise_daynum--1300~.csv`
- `kuru_sunsets.csv` → `intermediate/kuru_calculations/kuru_sunsets.csv`
- `kuru_naksrise_daynum--2350~.csv` → `intermediate/kuru_calculations/kuru_naksrise_daynum--2350~.csv`
- `kuru_sunrises_-1400.csv` → `intermediate/kuru_calculations/kuru_sunrises_-1400.csv`
- `kuru_naksrise_-1100.csv` → `intermediate/kuru_calculations/kuru_naksrise_-1100.csv`
- `kuru_naksrise_daynum--1100~.csv` → `intermediate/kuru_calculations/kuru_naksrise_daynum--1100~.csv`
- `kuru_sunrises_-950.csv` → `intermediate/kuru_calculations/kuru_sunrises_-950.csv`
- `kuru_sunrises_-1950.csv` → `intermediate/kuru_calculations/kuru_sunrises_-1950.csv`
- `kuru_naksrise_-1300.csv` → `intermediate/kuru_calculations/kuru_naksrise_-1300.csv`
- `kuru_sunrises_-1600.csv` → `intermediate/kuru_calculations/kuru_sunrises_-1600.csv`
- `kuru_naksrise_daynum--1675~.csv` → `intermediate/kuru_calculations/kuru_naksrise_daynum--1675~.csv`
- `kuru_naksrise_daynum--1900~.csv` → `intermediate/kuru_calculations/kuru_naksrise_daynum--1900~.csv`
- `kuru_naksrise_-1400.csv` → `intermediate/kuru_calculations/kuru_naksrise_-1400.csv`
- `kuru_naksrise_daynum--1500~.csv` → `intermediate/kuru_calculations/kuru_naksrise_daynum--1500~.csv`
- `kb_2500bce-20years~.pkl` → `intermediate/kuru_calculations/kb_2500bce-20years~.pkl`
- `kuru_sunrises_-2150.csv` → `intermediate/kuru_calculations/kuru_sunrises_-2150.csv`
- `kuru_sunrises_-1100.csv` → `intermediate/kuru_calculations/kuru_sunrises_-1100.csv`
- `kuru_naksrise_daynum--2300~.csv` → `intermediate/kuru_calculations/kuru_naksrise_daynum--2300~.csv`
- `kb_2500bce-1008years.tsv` → `intermediate/kuru_calculations/kb_2500bce-1008years.tsv`
- `kuru_sunrises_-1300.csv` → `intermediate/kuru_calculations/kuru_sunrises_-1300.csv`
- `kuru_naksrise_-1600.csv` → `intermediate/kuru_calculations/kuru_naksrise_-1600.csv`
- `kuru_sunrises_-2350.csv` → `intermediate/kuru_calculations/kuru_sunrises_-2350.csv`
- `kb_2500bce-2years~.pkl` → `intermediate/kuru_calculations/kb_2500bce-2years~.pkl`
- `kuru_naksrise_-1200.csv` → `intermediate/kuru_calculations/kuru_naksrise_-1200.csv`
- `kuru_sunrises_-1675.csv` → `intermediate/kuru_calculations/kuru_sunrises_-1675.csv`
- `kb_pakshas_cooked_20230202.tsv` → `intermediate/kuru_calculations/kb_pakshas_cooked_20230202.tsv`
- `kb_tuned_fm.tsv` → `intermediate/kuru_calculations/kb_tuned_fm.tsv`
- `kuru_sunrises_-1700.csv` → `intermediate/kuru_calculations/kuru_sunrises_-1700.csv`
- `kuru_naksrise_daynum--1700~.csv` → `intermediate/kuru_calculations/kuru_naksrise_daynum--1700~.csv`
- `kuru_sunrises_-1500.csv` → `intermediate/kuru_calculations/kuru_sunrises_-1500.csv`
- `kuru_sunrises_plot_cache~.csv` → `intermediate/kuru_calculations/kuru_sunrises_plot_cache~.csv`
- `kuru_sunrises_-1850.csv` → `intermediate/kuru_calculations/kuru_sunrises_-1850.csv`
- `kuru_naksrise_daynum--2100~.csv` → `intermediate/kuru_calculations/kuru_naksrise_daynum--2100~.csv`
- `kuru_naksrise_-1000.csv` → `intermediate/kuru_calculations/kuru_naksrise_-1000.csv`
- `kuru_naksrise_-2100.csv` → `intermediate/kuru_calculations/kuru_naksrise_-2100.csv`
- `kuru_naksrise_daynum--1200~.csv` → `intermediate/kuru_calculations/kuru_naksrise_daynum--1200~.csv`
- `kuru_sunrises_-1450.csv` → `intermediate/kuru_calculations/kuru_sunrises_-1450.csv`
- `kuru_sunrises_-2400.csv` → `intermediate/kuru_calculations/kuru_sunrises_-2400.csv`
- `kuru_naksrise_daynum--2400~.csv` → `intermediate/kuru_calculations/kuru_naksrise_daynum--2400~.csv`
- `kuru_sunrises.csv` → `intermediate/kuru_calculations/kuru_sunrises.csv`
- `kuru_sunrises_-1900.csv` → `intermediate/kuru_calculations/kuru_sunrises_-1900.csv`
- `kuru_naksrise_-2300.csv` → `intermediate/kuru_calculations/kuru_naksrise_-2300.csv`
- `kuru_sunrises_-1650.csv` → `intermediate/kuru_calculations/kuru_sunrises_-1650.csv`
- `kuru_sunrises_-1250.csv` → `intermediate/kuru_calculations/kuru_sunrises_-1250.csv`
- `kb_1441bce-1008years~.pkl` → `intermediate/kuru_calculations/kb_1441bce-1008years~.pkl`
- `kuru_sunrises_-2200.csv` → `intermediate/kuru_calculations/kuru_sunrises_-2200.csv`
- `kuru_naksrise_daynum--1000~.csv` → `intermediate/kuru_calculations/kuru_naksrise_daynum--1000~.csv`
- `kuru_sunrises_-2000.csv` → `intermediate/kuru_calculations/kuru_sunrises_-2000.csv`
- `kuru_naksrise_-1800.csv` → `intermediate/kuru_calculations/kuru_naksrise_-1800.csv`
- `kuru_naksset_-1800.csv` → `intermediate/kuru_calculations/kuru_naksset_-1800.csv`
- `kuru_sunrises_-1050.csv` → `intermediate/kuru_calculations/kuru_sunrises_-1050.csv`
- `kuru_sunrises_-1750.csv` → `intermediate/kuru_calculations/kuru_sunrises_-1750.csv`
- `kuru_naksrise_-2200.csv` → `intermediate/kuru_calculations/kuru_naksrise_-2200.csv`
- `kuru_naksrise_daynum--2200~.csv` → `intermediate/kuru_calculations/kuru_naksrise_daynum--2200~.csv`
- `kuru_sunrises_-1550.csv` → `intermediate/kuru_calculations/kuru_sunrises_-1550.csv`
- `kuru_naksrise_-2000.csv` → `intermediate/kuru_calculations/kuru_naksrise_-2000.csv`
- `kuru_naksrise_daynum--1800~.csv` → `intermediate/kuru_calculations/kuru_naksrise_daynum--1800~.csv`
- `kuru_sunrises_-1800.csv` → `intermediate/kuru_calculations/kuru_sunrises_-1800.csv`
- `kb_2500bce-1008years~.pkl` → `intermediate/kuru_calculations/kb_2500bce-1008years~.pkl`
- `kuru_naksrise_daynum--1400~.csv` → `intermediate/kuru_calculations/kuru_naksrise_daynum--1400~.csv`
- `kuru_naksrise_daynum--1050~.csv` → `intermediate/kuru_calculations/kuru_naksrise_daynum--1050~.csv`
- `kb_1441bce-1008years.tsv` → `intermediate/kuru_calculations/kb_1441bce-1008years.tsv`
- `kb_pakshas_cooked_2023-02-02.tsv` → `intermediate/kuru_calculations/kb_pakshas_cooked_2023-02-02.tsv`
- `kuru_naksrise_heliacals--1050~.csv` → `intermediate/kuru_calculations/kuru_naksrise_heliacals--1050~.csv`
- `kuru_sunrises_-2100.csv` → `intermediate/kuru_calculations/kuru_sunrises_-2100.csv`
- `kuru_naksrise_daynum--2000~.csv` → `intermediate/kuru_calculations/kuru_naksrise_daynum--2000~.csv`
- `kuru_naksrise_-2400.csv` → `intermediate/kuru_calculations/kuru_naksrise_-2400.csv`
- `kuru_sunrises_-1150.csv` → `intermediate/kuru_calculations/kuru_sunrises_-1150.csv`
- `kuru_naksrise_daynum--1600~.csv` → `intermediate/kuru_calculations/kuru_naksrise_daynum--1600~.csv`
- `kuru_naksrise_-1900.csv` → `intermediate/kuru_calculations/kuru_naksrise_-1900.csv`
- `kb_381bce-1008years.tsv` → `intermediate/kuru_calculations/kb_381bce-1008years.tsv`
- `kuru_sunrises_-1350.csv` → `intermediate/kuru_calculations/kuru_sunrises_-1350.csv`
- `kuru_sunrises_-2300.csv` → `intermediate/kuru_calculations/kuru_sunrises_-2300.csv`
- `n90_heliacal_rising_times_for_-1600.csv` → `intermediate/nakshatras/n90_heliacal_rising_times_for_-1600.csv`
- `n83_heliacal_rising_times_for_-1600.csv` → `intermediate/nakshatras/n83_heliacal_rising_times_for_-1600.csv`
- `naks-davita-table~` → `intermediate/nakshatras/naks-davita-table~`
- `n90_heliacal_rising_times_for_-1400.csv` → `intermediate/nakshatras/n90_heliacal_rising_times_for_-1400.csv`
- `naks-marga-veethi.tsv` → `intermediate/nakshatras/naks-marga-veethi.tsv`
- `n27_delta_shr_dha_bce2500_to_ce0500.tsv` → `intermediate/nakshatras/n27_delta_shr_dha_bce2500_to_ce0500.tsv`
- `n27_delta_abhyankar_bce2500_to_ce0500.tsv` → `intermediate/nakshatras/n27_delta_abhyankar_bce2500_to_ce0500.tsv`
- `sun-naks` → `intermediate/nakshatras/sun-naks`
- `n83_heliacal_rising_times_for_a_year.csv` → `intermediate/nakshatras/n83_heliacal_rising_times_for_a_year.csv`
- `n28_devata.psv` → `intermediate/nakshatras/n28_devata.psv`
- `n90_heliacal_rising_times_for_-1700.csv` → `intermediate/nakshatras/n90_heliacal_rising_times_for_-1700.csv`
- `n83_hr_daynums.tsv` → `intermediate/nakshatras/n83_hr_daynums.tsv`
- `n83_heliacal_rising_times_for_-1700.csv` → `intermediate/nakshatras/n83_heliacal_rising_times_for_-1700.csv`
- `naks-az-alt-about-0-alt.tsv` → `intermediate/nakshatras/naks-az-alt-about-0-alt.tsv`
- `n83_base_Feb24_bce2500_to_ce0500.tsv` → `intermediate/nakshatras/n83_base_Feb24_bce2500_to_ce0500.tsv`
- `n90_hr_daynums.tsv` → `intermediate/nakshatras/n90_hr_daynums.tsv`
- `best_fit_gruha_naks_-2400_-1000_2.0 d~.pickle` → `intermediate/nakshatras/best_fit_gruha_naks_-2400_-1000_2.0 d~.pickle`
- `n90_heliacal_rising_times_for_-2000.csv` → `intermediate/nakshatras/n90_heliacal_rising_times_for_-2000.csv`
- `n83_heliacal_rising_times_for_2023.csv` → `intermediate/nakshatras/n83_heliacal_rising_times_for_2023.csv`
- `naks_eq_bounds_report.csv` → `intermediate/nakshatras/naks_eq_bounds_report.csv`
- `n83_mag.tsv` → `intermediate/nakshatras/n83_mag.tsv`
- `n90_heliacal_rising_times_for_-1650.csv` → `intermediate/nakshatras/n90_heliacal_rising_times_for_-1650.csv`
- `n27_delta_Feb20_bce2500_to_ce0500.tsv` → `intermediate/nakshatras/n27_delta_Feb20_bce2500_to_ce0500.tsv`
- `naks-visible-rising-az.tsv` → `intermediate/nakshatras/naks-visible-rising-az.tsv`
- `n83_heliacal_rising_times_for_-1650.csv` → `intermediate/nakshatras/n83_heliacal_rising_times_for_-1650.csv`
- `n83_lat_lon_ra_dec_bce2500_ce1000.tsv` → `intermediate/nakshatras/n83_lat_lon_ra_dec_bce2500_ce1000.tsv`
- `n90_heliacal_rising_times_for_2023.csv` → `intermediate/nakshatras/n90_heliacal_rising_times_for_2023.csv`
- `n90_heliacal_rising_times_for_-1350.csv` → `intermediate/nakshatras/n90_heliacal_rising_times_for_-1350.csv`
- `n27_base_Feb24_bce2500_to_ce0500.tsv` → `intermediate/nakshatras/n27_base_Feb24_bce2500_to_ce0500.tsv`
- `n90_heliacal_rising_times_for_-1800.csv` → `intermediate/nakshatras/n90_heliacal_rising_times_for_-1800.csv`
- `n83_heliacal_rising_times_for_-1550.csv` → `intermediate/nakshatras/n83_heliacal_rising_times_for_-1550.csv`
- `n27_lon_divisions.csv` → `intermediate/nakshatras/n27_lon_divisions.csv`
- `n83_heliacal_rising_times_for_-1800.csv` → `intermediate/nakshatras/n83_heliacal_rising_times_for_-1800.csv`
- `n90_heliacal_rising_times_for_-1550.csv` → `intermediate/nakshatras/n90_heliacal_rising_times_for_-1550.csv`
- `n90_heliacal_rising_times_for_-1750.csv` → `intermediate/nakshatras/n90_heliacal_rising_times_for_-1750.csv`
- `n83_heliacal_rising_times_for_-1750.csv` → `intermediate/nakshatras/n83_heliacal_rising_times_for_-1750.csv`
- `astropy-fm-bce-2000.tsv` → `intermediate/full_moons/astropy-fm-bce-2000.tsv`
- `fm_kv_eqfm_paper_submit_1.tsv` → `intermediate/full_moons/fm_kv_eqfm_paper_submit_1.tsv`
- `fm_kv_astropy_1.tsv` → `intermediate/full_moons/fm_kv_astropy_1.tsv`
- `fm_kv_astropy_3.tsv` → `intermediate/full_moons/fm_kv_astropy_3.tsv`
- `fm_kv_astropy_2.tsv` → `intermediate/full_moons/fm_kv_astropy_2.tsv`
- `astropy-fm-bce-2500.tsv` → `intermediate/full_moons/astropy-fm-bce-2500.tsv`
- `fm_pakshas_cooked.tsv` → `intermediate/full_moons/fm_pakshas_cooked.tsv`
- `astropy-fm-bce-2500-old~.tsv` → `intermediate/full_moons/astropy-fm-bce-2500-old~.tsv`
- `fm_kv_astropy_4.tsv` → `intermediate/full_moons/fm_kv_astropy_4.tsv`
- `astropy-nm-bce-safe-copy~.tsv` → `intermediate/full_moons/astropy-nm-bce-safe-copy~.tsv`
- `fm_kv_better_1.tsv` → `intermediate/full_moons/fm_kv_better_1.tsv`
- `fm_kv_better_3.tsv` → `intermediate/full_moons/fm_kv_better_3.tsv`
- `fm_kv_better_2.tsv` → `intermediate/full_moons/fm_kv_better_2.tsv`
- `astropy-fm-bce~~.tsv` → `intermediate/full_moons/astropy-fm-bce~~.tsv`
- `fm_kv_better_4.tsv` → `intermediate/full_moons/fm_kv_better_4.tsv`
- `astropy-nm-bce-2500.tsv` → `intermediate/full_moons/astropy-nm-bce-2500.tsv`
- `astropy-fm-bce-safe-copy~.tsv` → `intermediate/full_moons/astropy-fm-bce-safe-copy~.tsv`
- `jaipur-solar-eclipses-cooked.csv` → `intermediate/eclipses/jaipur-solar-eclipses-cooked.csv`
- `jaipur-lunar-eclipses-cooked.csv` → `intermediate/eclipses/jaipur-lunar-eclipses-cooked.csv`
- `jaipur-solar-lunar-eclipses.csv` → `intermediate/eclipses/jaipur-solar-lunar-eclipses.csv`
- `jaipur-lunar-eclipses.csv` → `intermediate/eclipses/jaipur-lunar-eclipses.csv`
- `jaipur-solar-eclipses.csv` → `intermediate/eclipses/jaipur-solar-eclipses.csv`
- `kbx_2500bce-5years~.pkl` → `intermediate/calculations/kbx_2500bce-5years~.pkl`
- `mar_5~.pkl` → `intermediate/calculations/mar_5~.pkl`
- `kbx_2500bce-11years~.pkl` → `intermediate/calculations/kbx_2500bce-11years~.pkl`
- `Untitled-2~` → `archive/backups/Untitled-2~`
- `_SavatiSampatam_rise_events_-1299_5490_1~.csv` → `temp/_SavatiSampatam_rise_events_-1299_5490_1~.csv`
- `_ThiruppavaiFM_rise_events_0_366000_27~.csv` → `temp/_ThiruppavaiFM_rise_events_0_366000_27~.csv`
- `_MargazhiThingal_set_events_800_73200_29.52~.csv` → `temp/_MargazhiThingal_set_events_800_73200_29.52~.csv`
- `_MargazhiThingal_rise_events_0_3660_27~.csv` → `temp/_MargazhiThingal_rise_events_0_3660_27~.csv`
- `_SavatiSampatam_rise_events_-1299_3660_1~.csv` → `temp/_SavatiSampatam_rise_events_-1299_3660_1~.csv`
- `_MargazhiThingal_set_events_800_500_1~.csv` → `temp/_MargazhiThingal_set_events_800_500_1~.csv`
- `_MargazhiThingal_rise_events_800_5000_27~.csv` → `temp/_MargazhiThingal_rise_events_800_5000_27~.csv`
- `_MargazhiThingal_set_events_800_2000_29.54~.csv` → `temp/_MargazhiThingal_set_events_800_2000_29.54~.csv`
- `_MargazhiThingal_set_events_800_5000_29.54~.csv` → `temp/_MargazhiThingal_set_events_800_5000_29.54~.csv`
- `_MargazhiThingal_set_events_800_2000_28.5~.csv` → `temp/_MargazhiThingal_set_events_800_2000_28.5~.csv`
- `_MargazhiThingal_rise_events_800_7320_27~.csv` → `temp/_MargazhiThingal_rise_events_800_7320_27~.csv`
- `_MargazhiThingal_set_events_800_20000_29.52~.csv` → `temp/_MargazhiThingal_set_events_800_20000_29.52~.csv`
- `Untitled-1` → `temp/Untitled-1`
- `_SvatiSampatam_rise_events_-1299_5490_1~.csv` → `temp/_SvatiSampatam_rise_events_-1299_5490_1~.csv`
- `_MargazhiThingal_rise_events_0_36600_27~.csv` → `temp/_MargazhiThingal_rise_events_0_36600_27~.csv`
- `_MargazhiThingal_rise_events_800_500_27~.csv` → `temp/_MargazhiThingal_rise_events_800_500_27~.csv`
- `_MargazhiThingal_set_events_800_2000_27~.csv` → `temp/_MargazhiThingal_set_events_800_2000_27~.csv`
- `_MargazhiThingal_set_events_800_5000_27~.csv` → `temp/_MargazhiThingal_set_events_800_5000_27~.csv`
- `_MargazhiThingal_set_events_700_73200_27~.csv` → `temp/_MargazhiThingal_set_events_700_73200_27~.csv`
- `_MargazhiThingal_rise_events_700_73200_27~.csv` → `temp/_MargazhiThingal_rise_events_700_73200_27~.csv`
- `_SvatiSampatam2_rise_events_-1284_3660_1~.csv` → `temp/_SvatiSampatam2_rise_events_-1284_3660_1~.csv`
- `_MargazhiThingal_set_events_800_7320_29.52~.csv` → `temp/_MargazhiThingal_set_events_800_7320_29.52~.csv`
- `_MargazhiThingal_set_events_800_10000_28.5~.csv` → `temp/_MargazhiThingal_set_events_800_10000_28.5~.csv`
- `_MargazhiThingal_rise_events_800_73200_27~.csv` → `temp/_MargazhiThingal_rise_events_800_73200_27~.csv`


## Notebooks Updated
Updated file paths in 14 notebooks to reflect new structure.

## Next Steps
1. Clean notebook outputs to reduce file sizes
2. Archive old notebook versions
3. Create data dictionary documentation
4. Set up automated cleanup scripts
