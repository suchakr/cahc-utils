# Demo Runbook

This file captures the live/demo sequence for the two tutorial sessions.

## General Demo Rules

- prefer one primary live demo per section
- always keep one fallback
- avoid spending time on UI fumbling
- use prepared scripts where they improve reproducibility
- if a live demo feels slow, switch to the prepared plot/image immediately

## Curated Stellarium Script Shortlist

These are the scripts from the original `stel_scripts` set that appear most usable for the current two-session tutorial plan. For this talk, the working copies now live under `/Users/sunder/projects/cahc/cahc-utils/presentations/2026-03-23-iks-astro-talk/ssc`.

### Use Strongly

- `s1-02-main-dhruva-pole-drift.ssc`
  - best fit for Dhruva / pole-shift intuition

- `thuban-circumpolarity.ssc`
  - strong support for Thuban / Abhaya Dhruva visibility discussion

- `s1-03-sun-meridian-high-low.ssc`
  - short support for the meridian high/low Sun contrast

- `s1-03-main-sun-swing.ssc`
  - the clearest lead script for visible solar swing over the year

- `s1-04-main-nakshatra-tour.ssc`
  - strongest script for a tutorial nakṣatra tour

- `a3-puri-demo.ssc`
  - strongest ready-made eclipse demo script

### Use Selectively

- `matsya-sisumara-drift.ssc`
  - relevant to Dhruva / Śiśumāra, but likely secondary to `s1-02-main-dhruva-pole-drift.ssc`

- `a2_sun_analemma.ssc`
  - useful backup for solar motion if the primary scripts do not land cleanly

- `naks-spot-check.ssc`
  - useful technical backup for nakṣatra section

- `nakshatra-db.ssc`
  - more database/inspection oriented than audience-friendly, but useful as support

- `s2-01-moon-swing.ssc`
  - preferred Moon-fundamentals demo for Session 2

- `a2_moon_analemma.ssc`
  - useful visual Moon-motion support, but may be less directly tied to the equinoctial full-moon argument

- `full_moon_vgj.ssc`
  - potentially useful for the Moon section depending on how close it stays to the chosen narrative

### Probably Too Technical for Main Tutorial Flow

- `a5_moon_pos.ssc`
- `a6_naks_pos.ssc`
- `a7_sun_naks_pos.ssc`
- `n28_lat_lon.ssc`
- `p27.ssc`
- `n89.ssc`
- `n82_prev.ssc`
- `a6_naks_pos.ssc`

These look more like extraction, inspection, or technical support scripts than live audience demos.

### Off-Scope for Current Tutorial Spine

- `mars-scrape.ssc`
- `mars-jyeshta.ssc`
- `parippaadal.ssc`
- `parippaadal2.ssc`
- `agastya-chaara.ssc`
- `vasista-arundati.ssc`
- `punarvasu_ashada_kb.ssc`
- `lvj_yugaadi.ssc`
- `3339_moon.ssc`
- `a9-moon-shranga.ssc`
- various `moon_*_events*.inc` and `lunar_*_events*.inc`

These may be valuable elsewhere, but they do not currently serve the main tutorial arc cleanly.

## Session 1

### 1. Stellarium Basics and Sky Culture

Live Mode:

- manual

Show:

- location
- date/time
- ecliptic and equator
- Alt-Az and meridian
- projections
- sky culture note

Script:

- none

Support Files:

- live use of the built-in Stellarium help / shortcuts screen
- `demo.md` may still be used as internal reference material if needed

Fallback:

- static screenshots if needed later

### 2. Dhruva / Thuban / Śiśumāra / Precession

Primary:

- `/Users/sunder/projects/cahc/cahc-utils/presentations/2026-03-23-iks-astro-talk/ssc/s1-02-main-dhruva-pole-drift.ssc`

Support:

- `/Users/sunder/projects/cahc/cahc-utils/presentations/2026-03-23-iks-astro-talk/ssc/thuban-circumpolarity.ssc`

Backup:

- `/Users/sunder/projects/cahc/cahc-utils/presentations/2026-03-23-iks-astro-talk/ssc/matsya-sisumara-drift.ssc`

Likely Setup:

- latitude about 30°N
- target talk behavior:
  - begin near the Thuban epoch, around 2840 BCE
  - show Thuban near the north celestial pole
  - step forward in time so the pole drifts away from Thuban
  - end in the modern pole-star situation

Talking Point:

- visible pole stability is historical, not timeless

Need to Tune:

- current preferred file: `s1-02-main-dhruva-pole-drift.ssc`
- legacy `two_dhruvas.ssc` is retained as backup/reference
- rehearse whether the new finite epoch sweep lands clearly enough on your box

### 3. Sun

Primary:

- `/Users/sunder/projects/cahc/cahc-utils/presentations/2026-03-23-iks-astro-talk/ssc/s1-03-main-sun-swing.ssc`

Support:

- `/Users/sunder/projects/cahc/cahc-utils/presentations/2026-03-23-iks-astro-talk/ssc/s1-03-sun-meridian-high-low.ssc`

Backup:

- `/Users/sunder/projects/cahc/cahc-utils/presentations/2026-03-23-iks-astro-talk/ssc/a2_sun_analemma.ssc`

Talking Point:

- horizon shift and meridian altitude express different aspects of solar motion

Need to Tune:

- current preferred support file: `s1-03-sun-meridian-high-low.ssc`
- legacy `sun-transit-ayana.ssc` is retained as backup/reference
- verify during rehearsal whether `s1-03-main-sun-swing.ssc` remains readable on your box

### 4. Nakṣatras

Primary:

- `/Users/sunder/projects/cahc/cahc-utils/presentations/2026-03-23-iks-astro-talk/ssc/s1-04-main-nakshatra-tour.ssc`

Support:

- no live support script by default

Backup:

- no live backup script by default

Talking Point:

- from recognizable stars to research-useful zones

Technical Contrast Only:

- `/Users/sunder/projects/cahc/cahc-utils/presentations/2026-03-23-iks-astro-talk/ssc/naks-spot-check.ssc`
- `/Users/sunder/projects/cahc/cahc-utils/presentations/2026-03-23-iks-astro-talk/ssc/nakshatra-db.ssc`
- use only if you explicitly want to show:
  - what Stellarium scripting can extract
  - what Stellarium exposes out of the box for a single object
  - why Astropy becomes preferable for large scans

### 5. Precession and Sun-Transit Work

Live Mode:

- figure-led explanation, not a dedicated Stellarium script

Primary:

- Dhruva precession intuition already established by `s1-02-main-dhruva-pole-drift.ssc`

Visual Backup:

- `/Users/sunder/projects/cahc/cahc-utils/presentations/sun-transit/sun-transit-transition-abhijit.png`
- `/Users/sunder/projects/cahc/cahc-utils/presentations/sun-transit/sun-transit-rtusvabhava-charts.png`

Talking Point:

- precession turns visual sky change into a dating tool

## Session 2

### 1. Precession, Moon, Equinoctial Full Moon, and Astropy Support

Primary:

- `/Users/sunder/projects/cahc/cahc-utils/presentations/2026-03-23-iks-astro-talk/ssc/s2-01-moon-swing.ssc`
- `/Users/sunder/projects/cahc/cahc-utils/presentations/2026-03-23-iks-astro-talk/ssc/s2-01-bp-eqfm-best-case.ssc`

Other Candidates to Evaluate:

- `/Users/sunder/projects/cahc/cahc-utils/presentations/2026-03-23-iks-astro-talk/ssc/full_moon_vgj.ssc`
- `/Users/sunder/projects/cahc/cahc-utils/presentations/2026-03-23-iks-astro-talk/ssc/a2_moon_analemma.ssc`

Visual Anchors:

- `/Users/sunder/projects/cahc/cahc-utils/presentations/equinoctial-full-moon/bp-equinoctial-full-moon-better.png`
- `/Users/sunder/projects/cahc/cahc-utils/presentations/equinoctial-full-moon/mau-magha-scheme.png`
- `/Users/sunder/projects/cahc/cahc-utils/presentations/equinoctial-full-moon/bp-२१-१४२-१४९-devanaagari.jpeg`
- `/Users/sunder/projects/cahc/cahc-utils/jyotisha/images/ms-book/pg29-eqfm_paper_submit.png`
- `/Users/sunder/projects/cahc/cahc-utils/presentations/2026-03-23-iks-astro-talk/pics/eq-fm-color.png`

Optional Enhancement:

- `/Users/sunder/projects/cahc/cahc-utils/presentations/equinoctial-full-moon/ndial_1.gif`
- `/Users/sunder/projects/cahc/cahc-utils/presentations/equinoctial-full-moon/ndial_1.mp4`

Talking Point:

- first, establish the Moon's fast horizon swing against the background stars
- then show one BP best-case sky frame for vasanta and one for śarat
- precession plus textual longitude constraints turn the Moon section into a dating problem
- Stellarium shows convincing cases; Astropy supports exhaustive search
- if useful, show one compact comparison:
  - manual
  - Stellarium script
  - Astropy scan

### 2. Eclipse Section

Primary:

- `/Users/sunder/projects/cahc/cahc-utils/presentations/2026-03-23-iks-astro-talk/ssc/s2-02-total-eclipse-india.ssc`

Support / PT sequence script:

- `/Users/sunder/projects/cahc/cahc-utils/presentations/2026-03-23-iks-astro-talk/ssc/s2-03-pt-eclipse-jaipur.ssc`

Visual Anchors:

- `/Users/sunder/projects/cahc/cahc-utils/presentations/2026-03-23-iks-astro-talk/pt-eclipse-table.jpg`
- `https://archive.org/details/YgQn_parashara-tantra-with-reconstructed-text-trans-and-notes-by-r-n-iyenger-jain-uni/page/97/mode/1up`
- `http://eclipse.gsfc.nasa.gov/JLEX/JLEX-AS.html`

Talking Point:

- first show that eclipse appearance changes with location
- then use a Jaipur-sequence script to illustrate two representative PT runs
- keep the source credit brief: PT -> R. N. Iyengar -> NASA/JLEX
- use the table + JLEX to carry the exhaustive argument

### 3. Meru

Primary:

- `/Users/sunder/projects/meru/meru_cosmology.html`

Talking Point:

- interactive cosmographic visualization can clarify old descriptive models

Backup:

- screenshots from Meru if live browser interaction is risky

### 5. Digital Resources

Primary:

- `https://cahc.jainuniversity.ac.in/search/`

Mention:

- Patra Darpan
- Sanchaya
- Semantic Search

Decision Pending:

- live browser walk-through vs screenshot summary

### 6. AI-Assisted Chores

Preferred Mode:

- static slides only

Show:

- one anvaya prompt/response
- one kaṭapayādi prompt/response
- one short note on agentic prototyping

Talking Point:

- helpful for exploratory assistance, never final authority

## Immediate Tuning Tasks

1. choose the primary moon script
2. decide whether CAHC resource demo is live or screenshot-based
3. decide whether Meru precedes or follows eclipse section
4. collect one clean AI-anvaya example and one clean kaṭapayādi example
5. decide whether any `Use Selectively` script should be promoted into the main flow
