# SSC Audit

This file audits the local Stellarium scripts used for the 2026-03-23 IKS astro tutorial.

## Naming Convention

Use explicit session, section, and role markers:

- `s1-01-...` Session 1, section 1
- `s2-01-...` Session 2, section 1
- role markers: `main`, `support`, `backup`, `tech`

Recommended pattern:

- `s1-02-main-dhruva-pole-drift.ssc`
- `s1-02-support-thuban-circumpolarity.ssc`
- `s1-03-main-sun-swing.ssc`
- `s1-03-sun-meridian-high-low.ssc`
- `s1-04-main-nakshatra-tour.ssc`
- `s2-01-main-eqfm-window.ssc`
- `s2-02-main-eclipse-demo.ssc`

Rationale:
- ordered in directory listings
- easy to stop/restart during rehearsal
- makes the talk role clear without opening the file

## Includes and Shared Dependencies

Current include dependency seen in the localized working set:

- `nakshatras.inc`

This file must remain in the same working `ssc/` folder for any dependent scripts.

## Audit Table

| Current file | Current role | Fit | Action | Proposed disciplined name | Notes |
|---|---|---|---|---|---|
| `two_dhruvas.ssc` | Session 1 legacy Dhruva demo | Weak as current main file | Retain as backup/reference | `s1-02-main-dhruva-pole-drift.ssc` | Legacy script is a static three-step comparison (`2022 CE`, `1019 CE`, `-2019 BCE`). A talk-specific finite sweep has now been created as the preferred main copy. |
| `thuban-circumpolarity.ssc` | Session 1 support | Weak for live demo | Keep as support or convert to data/appendix mode | `s1-02-support-thuban-circumpolarity.ssc` | Produces tabular output by latitude/epoch. More useful for verification than projection. |
| `matsya-sisumara-drift.ssc` | Session 1 backup | Weak | Demote or replace later | `s1-02-backup-sisumara-drift.ssc` | Currently thin on visible audience payoff. Good conceptually, but likely not worth live time unless improved. |
| `sun-swing.ssc` | Session 1 legacy Sun demo | Moderate | Retain as backup/reference | `s1-03-main-sun-swing.ssc` | A talk-specific main copy now exists with clearer labels and faster pacing. Rehearsal should confirm readability on your box. |
| `sun-transit-ayana.ssc` | Session 1 legacy Sun support demo | Moderate | Retain as backup/reference | `s1-03-sun-meridian-high-low.ssc` | A trimmed talk-specific support copy now exists for the meridian high/low contrast. |
| `a2_sun_analemma.ssc` | Session 1 backup Sun demo | Moderate | Keep as backup | `s1-03-backup-sun-analemma.ssc` | Good backup when the main scripts do not land cleanly. Too busy to lead the section. |
| `a4-tour-of-nakshatras.ssc` | Session 1 legacy Nakṣatra demo | Moderate | Retain as backup/reference | `s1-04-main-nakshatra-tour.ssc` | A talk-specific copy now exists with cleaner intro/outro and shorter waits. |
| `sun-transit-precession.ssc` | Session 1 legacy precession bridge | Weak for current talk flow | Cut from active path; retain only historically if needed later | none | The dedicated bridge script was dropped because the Dhruva demo plus the paper/core figures carry the precession-to-dating transition more clearly. |
| `naks-spot-check.ssc` | Technical contrast only | Weak for live use | Keep only as tech support | `s1-04-tech-nakshatra-spot-check.ssc` | Better for script-structure/runtime contrast than audience projection. |
| `nakshatra-db.ssc` | Technical contrast only | Moderate as appendix | Keep only as tech support | `s1-04-tech-nakshatra-db.ssc` | Useful to show what Stellarium exposes for a single object. Not main-stage material. |
| `moon_swing.ssc` | Session 2 Moon candidate | Weak | Likely replace with a more explicit eqfm script | `s2-01-candidate-moon-swing.ssc` | Too generic by itself for the BP equinoctial full-moon story. |
| `full_moon_vgj.ssc` | Session 2 Moon candidate | Weak | Likely replace or repurpose | `s2-01-candidate-full-moon-sample.ssc` | More like a sampling/extraction script than a clear tutorial demo. |
| `a2_moon_analemma.ssc` | Session 2 Moon backup | Moderate | Keep as backup only | `s2-01-backup-moon-analemma.ssc` | May help visualize Moon motion, but is not tightly tied to the eqfm argument. |
| `a3-puri-demo.ssc` | Session 2 eclipse demo | Partial | Tune or fork to match talk framing | `s2-02-main-eclipse-demo.ssc` | Visually useful, but current script is anchored to Puri while the slide framing discusses PT and Jaipur/NASA JLEX. Needs alignment. |

## Likely New Scripts Needed

### Session 1

- preferred Session 1 copies now exist for Dhruva, Sun, and Nakṣatra
- additional new Session 1 scripts are not currently required unless rehearsal exposes gaps

### Session 2

The current Moon scripts do not yet look like a clean fit for the deck. Likely new scripts:

- `s2-01-main-eqfm-window.ssc`
  - show selected BP-supporting epochs only
  - present Sun/Moon/nakṣatra geometry clearly
  - avoid raw extraction feel

- `s2-01-support-maghadi-dial.ssc`
  - optional, only if a Stellarium-side dial demonstration proves worthwhile

- `s2-02-main-eclipse-demo.ssc`
  - either tune `a3-puri-demo.ssc` or fork it into a talk-specific version matching the slide narrative

## Recommended Tuning Order

1. rehearse `s1-02-main-dhruva-pole-drift.ssc`
2. rehearse `s1-03-sun-meridian-high-low.ssc`
3. rehearse `s1-03-main-sun-swing.ssc`
4. rehearse `s1-04-main-nakshatra-tour.ssc`
5. no dedicated Session 1 precession bridge script at present
6. `a3-puri-demo.ssc`
7. Session 2 Moon script decision: tune existing vs create new

## Immediate Notes

- The preferred Session 1 copies have now been created under the disciplined naming scheme.
- Keep the older files in place as backups until the preferred copies are smell-tested in Stellarium 25.1.
- House style for the preferred `s1-*` copies:
  - remove `nakshatras.inc` dependency when the script only needs a small helper subset
  - begin with a short title/expectation sequence
  - end in a stable, meaningful final state instead of a blank reset
- Benchmark scripts in `bm/` should come after the core demo scripts are stable enough that the deck language will not move again.
