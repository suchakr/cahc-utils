# Jyotiṣa Bodha — PRD & Implementation Notes
**Version:** Iteration 5 (chat-built)  
**Handoff target:** Claude Code (local Vite/React project)  
**Last updated:** May 2026

---

## 1. Project Purpose

A pedagogic widget that teaches Jyotiṣa (Indian astrology) as a **layered algorithmic system** — static schema → birth transformation → evaluation algorithm → temporal prediction. Designed for:
- Adult learners at IKS conferences and workshops (CAHC, Jain University)
- School teachers (Classes 8–10) introducing Indian Knowledge Systems
- Self-directed learners with a CS/analytical background

The widget is **not** a production astrology tool. It uses two hardcoded illustrative birth events. Real ephemeris integration is a future milestone.

---

## 2. Conceptual Architecture (teach this to the learner)

```
Layer 0  Sthira Kośa      Universal constants — rāśi lords, ucca/nīca, kārakas
Layer 1  Janma Snapshot   Lagna applied → bhāva numbers assigned → grahas placed
Layer 2  LOYAKS            Per-bhāva evaluation: Lord, Occupant, Yoga, Aspect, Kāraka
Layer 3  Daśā             Temporal iterator — Vimśottarī graha periods
         Viśleṣaṇa        Cross-bhāva synthesis for a life area (career, health, etc.)
```

**Key pedagogic insight:** The Lagna is a coordinate transformation. `bhāva = (rāśiId − lagnaId + 12) mod 12 + 1`. The Rāśicakra (static grid) does not move — bhāva numbers travel to meet it.

---

## 3. Navigation Rail (5 stages)

```
Sandarbha | Rāśicakra | Jātaka | LOYAKS | Viśleṣaṇa
 Global      Global     Janma   Janma    Janma
```

- **Freely navigable** — no enforced sequence
- **Visited state** shown with ✓ prefix
- **Global** stages (Sandarbha, Rāśicakra) are birth-independent
- **Janma-sāpekṣa** stages require a birth event selected + lagna applied

---

## 4. Component Tree

```
App
├── TopBar (title, Gati speed selector, theme switcher)
├── Rail (5 stage buttons)
└── MainGrid (CSS grid: chart-col | panel-col)
    ├── SIChart (SVG, 300×300, 4×4 grid)
    │   ├── 12 rāśi cells (SI_POS lookup)
    │   └── CentrePanel (2×2, inline SVG rendered conditionally)
    ├── ExplanatoryBand (below chart, animates during Jātaka bhāva 1–4)
    └── PanelCol (switches by stage)
        ├── SandarbhaPanel (tabs: rāśi | graha | bhāva | daśā | paddhati)
        ├── RāśicakraPanel (static description)
        ├── JatakaPanel (birth event cards, Apply button, animation controls)
        ├── LOYAKSPanel (5-factor animated walkthrough)
        └── VislesanaPanel (life-area animated log)
```

---

## 5. Data Architecture

### 5.1 Static Data (never changes)

```js
RASIS[12]         // id, iast, en, lordId, element, quality
GRAHAS{9}         // iast, en, ucca, uccaDeg, nīca, nīcaDeg, svakṣetra[], color
BHAVA_TYPES{12}   // array of "Kendra"|"Trikona"|"Dusthāna"|"Upacaya"|"Māraka"|"Dhana"|"Lābha"|"Dharma"
BHAVA_THEMES{12}  // iast, en, kāraka (graha id)
VIMSHOTTARI[9]    // {g: graha id, y: years}
LIFE_AREAS{4}     // career|health|wealth|marriage → {iast, en, bhāvas[], icon}
SI_POS{12}        // rāśi id → [row, col] in 4×4 grid
```

### 5.2 Birth Events (hardcoded illustrative)

```js
BIRTH_EVENTS = {
  karkata: { lagna:4, pos:{GU:4,MA:1,SU:7,SK:8,SA:10,CA:11,BU:6,RA:3,KE:9},
             bhavaTexts:{1:{header,bullets[]}, 2:…, 3:…, 4:…} },
  tula:    { lagna:7, pos:{SK:12,SU:7,CA:2,MA:10,BU:8,GU:1,SA:11,RA:6,KE:12},
             bhavaTexts:{1…4} }
}
```

`pos` maps graha id → rāśi id (where that graha is placed at birth).

### 5.3 Derived at Runtime

```js
bhavaOf(rāśiId, lagna)     // → bhāva number (1–12)
dignity(grahaId, rāśiId)   // → {label, short, col, score}
staticAnnotations(rāśiId)  // → {ucca[], nīca[], svak[]} graha ids
buildMap(event)            // → map[1..12] = {rāśiId, bhāveśa, bhāveśaBhāva, occupants[]}
buildAnalysisLog(event, map, areaKey) // → log items for Viśleṣaṇa
```

---

## 6. SI Grid Layout

**Fixed positions** — `SI_POS` maps rāśi id to [row, col]:

```
[Mīna 12][Meṣa 1 ][Vṛṣa 2 ][Mith 3 ]   row 0
[Kumb 11][  centre panel   ][Kark 4 ]   row 1
[Maka 10][  (2×2 spans     ][Siṃh 5 ]   row 2
[Dhan 9 ][Vṛśc 8 ][Tulā 7 ][Kany 6 ]   row 3
```

Cell size = 75px. Total SVG = 300×300. Centre panel = x:75,y:75 w:150 h:150.

---

## 7. Themes

Three themes, all tokens in `THEMES` object:

| Token | Rātri (dark) | Sandhyā (twilight) | Dina (light) |
|---|---|---|---|
| bg | Deep brown-black radial | Indigo-amber radial | Warm parchment radial |
| accent | #c4a870 (gold) | #e87840 (saffron) | #c4a870 (gold) |
| hlPulse | cyan rgba | amber rgba | blue rgba |
| text | #c8a878 | #f0c898 | #3a2810 |

Theme switching is instant (no animation needed on bg).

---

## 8. Animation System

### 8.1 Speed

Three speeds, global multiplier on all timing:

| Speed | id | mult |
|---|---|---|
| Manda | manda | 3× |
| Madhya | madhya | 1.5× |
| Tīvra | tīvra | 1× |

### 8.2 Jātaka Animation

Base stay times (at Tīvra = 1×):
- Bhāva 1–4: **6000ms** each (slow, with explanatory text)
- Bhāva 5–8: **2500ms** each
- Bhāva 9–12: **1200ms** each
- Graha reveal: 400ms pause after bhāva 12

First bhāva appears within **80ms** of Apply button press (responsiveness).

Explanatory band (below chart) appears **only for bhāva 1–4**, with:
- Header line (bold)
- 3 bullet points
- Fades in at bhāva start, stays until next bhāva

### 8.3 Animation Controls (above explanatory band)

```
⏮ Restart | ◀ Prev | ▶/⏸ Play/Pause | ▶ Next | ⏭ Jump to end
```

State managed in App via `animStepRef` (ref, not state, to avoid closure issues) and `pausedRef`.

### 8.4 LOYAKS Animation

- Per-factor delay: **2000ms × speedMult**
- Clicking a rendered factor row re-highlights its bhāva

### 8.5 Viśleṣaṇa Animation

- Per-item delay: **2500ms × speedMult**
- Log scrolls to bottom as items appear

---

## 9. Bhāva Classification Icons

Rendered as inline SVG components:

| Class | Icon | Description |
|---|---|---|
| Kendra | ⊙ Circle with central dot | stroke #5090ff, fill dot #5090ff |
| Trikona | △ Triangle | stroke #50c078 |
| Dusthāna | ● Solid red circle | fill #c05040 |

Size in chart cells: 12px. Size in badges/tables: 14–18px.  
Icons appear bottom-right of each cell after bhāva animation reveals them.

---

## 10. Sandarbha Panel Tabs

| Tab | Content |
|---|---|
| rāśi | Table: id, iast, en, svāmī (coloured), tattva, guṇa, ucca graha+degree, nīca graha+degree |
| graha | Table: iast, en, ucca rāśi+degree, nīca rāśi+degree, svakṣetra |
| bhāva | Classification cards (Kendra/Trikona/Dusthāna with icons) + full bhāva table with icons |
| daśā | Vimśottarī table + explanatory prose |
| paddhati | Algorithmic framework — 5 sections (Layer 0–3 + Viśleṣaṇa), prose with left-border styling |

---

## 11. Jātaka Panel Behaviour

- Birth event cards: always selectable, including re-selecting current event
- Once animation starts, "Reset — choose another event" button appears
- Reset clears: `eventKey`, `animStep`, `animDone`, `expText`, `expVisible`, `selected`
- Apply button: appears only when event selected AND `animStep === 0`
- Animation controls: appear when `animStep > 0 && !animDone`

---

## 12. LOYAKS Panel Behaviour

- Available only when `animDone === true`
- Default selected bhāva: 1 (Tanu/Lagna)
- Changing selected bhāva (by tapping chart) resets visible rows to 0
- Each rendered factor row is **clickable** → re-fires `onHighlight` for that factor's bhāva
- Animate button re-runs from 0 visible rows

---

## 13. Highlight System

`highlighted` state in App: `null | number[] | number`

Chart cells check `isHL(b)` — if highlighted, they get:
- `hlPulse` background fill (theme-specific rgba)
- Thicker border (2.5px vs 1px)
- Animated inner ring (`hlPulse` keyframe, alternating opacity)

Both LOYAKS and Viśleṣaṇa call `onHighlight(bhāvaArray)` as items animate in.

---

## 14. Responsive Layout

- Desktop (≥600px): `grid-template-columns: 310px 1fr`
- Mobile (<600px): single column via `@media(max-width:600px){ .main-grid{ grid-template-columns:1fr } }`
- Chart col gets `max-width:320px; margin:0 auto` on mobile
- Panel col flows below chart on mobile

---

## 15. Outstanding Items (Next Iteration)

### High priority
- [ ] **Dṛṣṭi (aspect) overlay** — draw lines on SVG chart for Maṅgala/Guru/Śani special aspects from their cell positions
- [ ] **Mobile: explanatory band** — on narrow viewports, ensure explanatory band doesn't overflow; consider collapsible
- [ ] **LOYAKS Y factor** — implement basic Rāja-yoga detection (Kendra lord + Trikona lord relationship) for both charts
- [ ] **Daśā panel** — add Vimśottarī timeline bar (horizontal, hover to highlight bhāva) as a sixth stage or within Viśleṣaṇa

### Medium priority
- [ ] **Real ephemeris** — integrate Swiss Ephemeris WASM for arbitrary birth date → lagna + graha positions
- [ ] **Additional birth events** — add 2–3 more illustrative events (teacher, poet, athlete archetypes)
- [ ] **Arudha Lagna** — second coordinate transformation for "perceived" vs "actual" self
- [ ] **Sandarbha degree precision** — ucca/nīca exact degrees are currently approximate; verify against classical sources

### Low priority / Future
- [ ] **Nakṣatra layer** — 27 nakṣatras overlaid on Rāśicakra
- [ ] **Yoga library** — 10–15 classical yogas as a pattern-matching panel
- [ ] **Print/export** — generate a PDF Jātaka from the widget
- [ ] **Multilingual** — Tamil/Kannada rāśi names alongside IAST

---

## 16. Local Setup (Claude Code)

```bash
# One-time setup
npm create vite@latest jyotisha-bodha -- --template react
cd jyotisha-bodha
npm install

# Copy widget
cp /path/to/jyotisha-widget.jsx src/App.jsx

# Dev server
npm run dev
# → http://localhost:5173
```

No additional dependencies needed. The widget uses only React hooks and inline SVG.

---

## 17. File Structure (target)

```
jyotisha-bodha/
  src/
    App.jsx              ← the widget (currently monolithic, split later)
    data/
      static.js          ← RASIS, GRAHAS, BHAVA_TYPES, etc.
      birthEvents.js     ← BIRTH_EVENTS with bhavaTexts
    components/
      SIChart.jsx
      SandarbhaPanel.jsx
      JatakaPanel.jsx
      LOYAKSPanel.jsx
      VislesanaPanel.jsx
      icons.jsx          ← KendraIcon, TrikonaIcon, DusthanaIcon
    utils/
      jyotisha.js        ← bhavaOf, dignity, buildMap, buildAnalysisLog
      themes.js          ← THEMES object
  JYOTISHA_PRD.md        ← this file
  README.md
```

Splitting into this structure is **first task for Claude Code** — no functional changes, pure refactor.

---

## 18. Conversation History Summary

This widget was built over ~12 iterations in Claude chat (claude.ai). Key design decisions made:

1. **South Indian chart convention** chosen over North Indian — fixed rāśi positions make the coordinate transformation pedagogically visible
2. **Rāśicakra** (not "Jātaka") for the static grid — Jātaka implies birth-dependence
3. **IAST/Indic terminology throughout** — prepares learners for śāstra texts
4. **Constructed illustrative events** (The Scholar, The Musician) — avoids chart-accuracy disputes; real names can be added later
5. **SVG not CSS grid** for the chart — pixel-exact placement, no auto-placement ambiguity
6. **Explanatory prose in Sandarbha paddhati tab** — connects the algorithmic framing to the visual widget
7. **Sandhyā theme** added for mobile readability in ambient light conditions
8. **All animation text bulleted** (Option B: header + 3 bullets) — scannable under time pressure
9. **Speed in Sanskrit** (Manda/Madhya/Tīvra) — consistent with Indic vocabulary register

---

*Document prepared for handoff to Claude Code. Start with the refactor task (Section 17), then implement outstanding items in priority order.*
