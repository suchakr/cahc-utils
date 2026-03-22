# SSC Audit

This file records the active Stellarium scripts used in the 2026-03-23 IKS astro tutorial.

## Naming Convention

Use unique per-session numbers:

- `s11-...` Session 1, item 1
- `s12-...` Session 1, item 2
- `s21-...` Session 2, item 1
- `s22-...` Session 2, item 2

Recommended active pattern:

- `s11-dhruva-pole-drift.ssc`
- `s12-sun-swing.ssc`
- `s13-sun-meridian-high-low.ssc`
- `s14-nakshatra-tour.ssc`
- `s21-moon-swing.ssc`
- `s22-bp-eqfm-best-case.ssc`
- `s23-total-eclipse-india.ssc`
- `s24-pt-eclipse-jaipur.ssc`

Rationale:
- ordered in directory listings
- easy to stop/restart during rehearsal
- easy to say aloud during live presentation

## Active Script Set

| File | Role | Session use | Status | Notes |
|---|---|---|---|---|
| `s11-dhruva-pole-drift.ssc` | Dhruva / pole-star drift | Session 1 | Active | Main Dhruva intuition script: Thuban to Polaris. |
| `s12-sun-swing.ssc` | Sunrise horizon swing | Session 1 | Active | Main Sun motion script. |
| `s13-sun-meridian-high-low.ssc` | Noon Sun high/low contrast | Session 1 | Active | Short support script after the horizon swing. |
| `s14-nakshatra-tour.ssc` | Nakṣatra visible-group and zonal tour | Session 1 | Active | Main Nakṣatra tutorial script. |
| `s21-moon-swing.ssc` | Moonrise swing fundamentals | Session 2 | Active | Establishes Moon motion before BP eqfm. |
| `s22-bp-eqfm-best-case.ssc` | BP eqfm best-case visual | Session 2 | Active | Strong positive-case BP illustration near the -1700 window. |
| `s23-total-eclipse-india.ssc` | Eclipse intuition / wow demo | Session 2 | Active | Same 16-Feb-1980 eclipse, total at Puri and partial at Mumbai. |
| `s24-pt-eclipse-jaipur.ssc` | PT eclipse-sequence support | Session 2 | Active | Jaipur-fixed sequence illustration using the Iyengar/NASA-backed runs. |

## Includes and Shared Dependencies

Current active scripts are self-contained.

- no active `s11`-`s24` script currently uses `include(...)`

## Possible Future Additions

- `s25-eqfm-search-visualizer.ssc`
  - optional, if a one-minute coarse-to-fine search visualization would help bridge the BP plots and the best-case visual

## Rehearsal Order

1. rehearse `s11-dhruva-pole-drift.ssc`
2. rehearse `s12-sun-swing.ssc`
3. rehearse `s13-sun-meridian-high-low.ssc`
4. rehearse `s14-nakshatra-tour.ssc`
5. rehearse `s21-moon-swing.ssc`
6. rehearse `s22-bp-eqfm-best-case.ssc`
7. rehearse `s23-total-eclipse-india.ssc`
8. rehearse `s24-pt-eclipse-jaipur.ssc`

## Immediate Notes

- The active presentation set is now the `s11`-`s24` series.
- House style for the active scripts:
  - keep scripts self-contained when practical
  - begin with a short title/expectation sequence
  - end in a stable, meaningful final state instead of a blank reset
- Benchmark scripts in `bm/` should come after the core demo scripts are stable enough that the deck language will not move again.
