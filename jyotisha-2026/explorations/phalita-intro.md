# Phalita Intro

Slug: `phalita-intro`
Status: interactive app integrated

## Question

How can a pedagogic widget introduce phalita Jyotiṣa as a layered algorithmic system: static schema, birth transformation, bhāva evaluation, and life-area synthesis?

## Inputs

- Hardcoded illustrative birth events in `apps/phalita-intro/src/data/birthEvents.js`
- Static Jyotiṣa schema in `apps/phalita-intro/src/data/static.js`
- Product and teaching notes in `apps/phalita-intro/phalita-intro.prd.md`
- No upstream ephemeris dataset yet

## Outputs

- Vite React source app under `apps/phalita-intro/`
- Static publish artifact under `lab/phalita-intro/`
- Lab shell entry in `lab/index.html`
- Shell deep link: `/#phalita-intro`
- Focused direct URL: `/phalita-intro/index.html`

## Current Implementation

- Source follows the Section 17 split from the PRD:
  - `src/App.jsx`
  - `src/data/static.js`
  - `src/data/birthEvents.js`
  - `src/utils/jyotisha.js`
  - `src/utils/themes.js`
  - `src/components/SIChart.jsx`
  - `src/components/SandarbhaPanel.jsx`
  - `src/components/JatakaPanel.jsx`
  - `src/components/LOYAKSPanel.jsx`
  - `src/components/VislesanaPanel.jsx`
  - `src/components/icons.jsx`
- Build command from `apps/phalita-intro/`: `npm run build`
- Build output target: `lab/phalita-intro/`
- The app uses a South Indian fixed-rāśi SVG chart, a five-stage rail, three themes, and speed controls.
- Jātaka completion is centralized through `completeJataka()`, so natural B12 completion, B12 Next, and Jump to end produce the same completed state.
- Jātaka completion shows a `Proceed to LOYAKS →` CTA.
- LOYAKS and Viśleṣaṇa auto-finish a partial Jātaka before entering, and also expose `Finish Jātaka` when needed.
- Static narrator copy and narration logs use compact spacing classes for mobile.
- The chart column is sticky and the right/bottom panel scrolls independently so the grid remains visible while logs scroll.

## Manual Test Notes

- In Netlify dev, open `/#phalita-intro` for the lab shell view.
- Open `/phalita-intro/index.html` for focused mobile testing.
- Check Jātaka Apply through B12, Jump to end, Proceed to LOYAKS, LOYAKS animation, and Viśleṣaṇa analysis.

## Open Questions

- Whether the next iteration should add real ephemeris integration or keep the examples hardcoded for teaching clarity.
- Whether dṛṣṭi overlays and daśā timelines should remain within this app or become reusable lab components.
- Whether mobile panel height should remain fixed at `46vh` or become dynamically computed from the chart/rail height.
