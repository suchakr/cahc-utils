# 2026-03-23/24/25 IKS Astronomy Tutorial Sessions

## Purpose

This folder is for preparing two linked tutorial-style sessions on the use of modern tools in CAHC astronomical and cosmographic research.

The working assumption is that Prof. Iyengar's academic sessions provide the textual, historical, and conceptual foundation. These sessions should complement that by showing how modern tools help us:

- see ancient astronomical ideas
- test them against the sky
- illustrate them clearly
- reduce repetitive scholarly chores

Suggested spoken framing:

- `In this session, I show how we use modern tools to inspect, test, and illustrate ancient astronomical ideas.`

More formal framing:

- `This tutorial shows how modern tools help us see, test, and illustrate ideas from ancient Indian astronomy and cosmology.`

## Format

- two sessions
- each session about 90 minutes
- scheduled in post-lunch slots beginning around 3:00 pm
- lecture-demo format, not a hands-on lab

Audience assumptions:

- mixed scholars and interested learners
- not expected to be fluent in Stellarium
- may be asked to install Stellarium beforehand and explore offline later
- should not be expected to perform live interactive tasks during the session

## Core Design Principles

- Stellarium is the visible teaching instrument
- Astropy is the analytical support layer, shown mostly through plots and results
- Meru is a core section, but not necessarily the final section
- digital tools and AI may be included, but only as modest scholarly aides
- tools should be presented as assistants, not as drivers of interpretation

Closing principle to preserve:

- `These tools are most useful when they reduce repetitive effort and leave more time for careful scholarly thinking.`

## Structure

The talk should be treated as two linked tutorial sessions rather than one long 4-hour talk.

### Session 1

Focus:

- Stellarium tutorial and visible sky concepts
- how to see what the texts are talking about

Working sequence:

1. Stellarium basics and sky culture
2. Dhruva, Śiśumāra, Thuban, and precession intuition
3. Sun: daily and annual motion, horizon and meridian phenomena
4. Nakṣatras: stars, shapes, zones, and tour
5. Precession and seasonal markers in the sun-transit work

### Session 2

Focus:

- how visual intuition becomes research workflow
- how other tools support analysis, checking, search, and visualization

Working sequence:

1. Moon and the equinoctial full-moon problem
2. Astropy as analytical support
3. Eclipses: Parāśara Tantra and NASA/JLEX
4. Meru as interactive cosmographic visualization
5. Digital tools and resources in CAHC workflow
6. AI-assisted chores: anvaya, kaṭapayādi, and rapid prototyping
7. Wrap-up

## Approved Scope

### Include Strongly

- Stellarium basics
- sky culture as brief orientation
- Dhruva / Thuban / Śiśumāra / precession
- Sun demonstrations
- Nakṣatra demonstrations
- sun-transit paper examples
- equinoctial full-moon paper examples
- eclipse example linked to Parāśara Tantra and NASA/JLEX
- Meru as cosmographic visualization
- CAHC digital resources
- cautious AI-aide examples

### Include Carefully

- Astropy
  - not as a coding class
  - mainly through plots, results, and one or two comparison slides

- AI tools
  - one modest example for Sanskrit anvaya support
  - one modest example for kaṭapayādi assistance
  - one modest example of agentic prototyping if helpful
  - always framed as requiring verification

### Avoid

- making the talk about personal tooling enthusiasm
- broad claims that AI is transforming scholarship
- long live-coding segments
- too many raw scripts
- Meru presented as a proof engine

## Key Source Materials

### Papers

- `/Users/sunder/projects/cahcblr.github.io/assets/cached_papers/rni/1.pdf`
- `/Users/sunder/projects/cahcblr.github.io/assets/cached_papers/rni/01_58_4.pdf`

### Presentation Assets

- `/Users/sunder/projects/cahc/cahc-utils/presentations/sun-transit`
- `/Users/sunder/projects/cahc/cahc-utils/presentations/equinoctial-full-moon`
- `/Users/sunder/projects/cahc/cahc-utils/presentations/2024-03-17-mythic`

### Stellarium Scripts

- `/Users/sunder/projects/cahc/cahc-utils/stel_scripts`

### Meru

- `/Users/sunder/projects/meru`

### Eclipse Support

- local table image: `/Users/sunder/projects/cahc/cahc-utils/presentations/2026-03-23-iks-astro-talk/pt-eclipse-table.jpg`
- NASA JLEX: `http://eclipse.gsfc.nasa.gov/JLEX/JLEX-AS.html`
- Parāśara Tantra archive pages 97-99:
  - `https://archive.org/details/YgQn_parashara-tantra-with-reconstructed-text-trans-and-notes-by-r-n-iyenger-jain-uni/page/97/mode/1up`

### Digital Research Tools

- CAHC search portal: `https://cahc.jainuniversity.ac.in/search/`
- linked resources to mention:
  - Patra Darpan
  - Sanchaya
  - Semantic Search

## Working Files in This Folder

- `agent.md`
  - stable brief and decision log

- `slides-plan.md`
  - active session outline with asset anchors

- `demo-runbook.md`
  - live demo order, settings, scripts, and backups

## Workflow Rules

- keep the outline anchored to actual assets
- for each section, identify:
  - primary visual asset
  - primary script if any
  - backup asset or fallback
  - external references if needed
- prefer tuning existing scripts over writing many new ones
- use one primary script per major demo section
- keep backup options ready for any fragile live demo

## Iteration Policy

This project is expected to iterate.

Preferred iteration pattern:

1. refine structure
2. attach concrete assets
3. tighten demo flow
4. tune wording and timing

Detailed presentation tuning is expected later and should happen in `slides-plan.md` and `demo-runbook.md`.
