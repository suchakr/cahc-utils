# Migration Notes

- Source folder: `vedic_sky_culture`
- Target folder: `vedic_25_codex`
- Reference schema: Stellarium 25 `indian` sky culture installed under `/Applications/Stellarium.app/Contents/Resources/skycultures/indian`
- Preserved active legacy constellation records from `constellationship.fab` as Stellarium 25 `constellations`
- Preserved active legacy `C01`-`C04` asterism records from `asterism_lines.fab` as Stellarium 25 `asterisms`
- Mirrored the active nakshatra constellation records `N01`-`N28` into `asterisms` to match Stellarium 25's `indian` package model
- Copied only the two legacy illustration assets referenced by `constellationsart.fab`
- `C01`, `C02`, and `C04` remain unlabeled because the legacy folder does not provide active labels for them
- `i3.json` is emitted as a compact mirror of `index.json` for compatibility with the installed Stellarium 25 package layout
- `zodiac` and `lunar_system` were not invented in this pass because the legacy source does not contain active Stellarium 25-ready definitions for them
