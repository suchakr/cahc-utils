---
marp: true
theme: gaia
paginate: true
header: CAHC Tutorial · Session 2
backgroundColor: #fcfbf7
color: #1f2937
style: |
  section {
    font-family: "Aptos", "Segoe UI", sans-serif;
    font-size: 30px;
    line-height: 1.32;
    padding: 32px 60px 42px 60px;
    background: #fcfbf7;
    color: #1f2937;
  }

  header {
    width: calc(100% - 120px);
    left: 60px;
    top: 4px;
    font-size: 14px;
    font-weight: 600;
    letter-spacing: 0.05em;
    text-transform: uppercase;
    text-align: right;
    color: #6b7280;
    border-bottom: 1px solid #d6d3d1;
    padding-bottom: 6px;
  }

  footer {
    width: calc(100% - 120px);
    left: 60px;
    bottom: 4px;
    font-size: 13px;
    color: #6b7280;
  }

  section > *:first-child {
    margin-top: 14px;
  }

  h1, h2 {
    color: #0f172a;
    margin: 0 0 16px 0;
    font-weight: 700;
    letter-spacing: -0.02em;
  }

  h1 { font-size: 1.56em; }
  h2 { font-size: 1.22em; }

  h3 {
    color: #334155;
    font-size: 0.78em;
    margin: 8px 0 10px 0;
    text-transform: uppercase;
    letter-spacing: 0.04em;
  }

  p, li { font-size: 0.86em; }
  ul { margin: 0.2em 0 0.2em 1.1em; padding: 0; }
  li { margin: 0.18em 0; }

  strong { color: #7c2d12; }
  em { color: #1d4ed8; }
  a { color: #0f766e; text-decoration-thickness: 2px; }

  code {
    font-family: "SFMono-Regular", "Menlo", monospace;
    font-size: 0.82em;
    color: #7c2d12;
    background: #f8fafc;
    padding: 0.08em 0.28em;
    border-radius: 6px;
    border: 1px solid #cbd5e1;
  }

  table {
    width: 100%;
    border-collapse: collapse;
    font-size: 0.62em;
    margin-top: 0.4em;
  }

  th, td {
    border: 1px solid #d6d3d1;
    padding: 8px 10px;
    vertical-align: top;
  }

  th {
    background: #e7e5e4;
    color: #111827;
  }

  blockquote {
    font-size: 0.74em;
    line-height: 1.45;
    border-left: 5px solid #c08457;
    background: #fff7ed;
    margin: 0.5em 0;
    padding: 14px 18px;
    border-radius: 0 12px 12px 0;
  }

  .lead h1 {
    font-size: 1.75em;
    margin-top: 80px;
    margin-bottom: 0.18em;
  }

  .lead p {
    font-size: 0.78em;
    color: #475569;
    margin: 0.16em 0;
  }

  .cols {
    display: flex;
    gap: 28px;
    align-items: flex-start;
  }

  .col {
    flex: 1 1 0;
  }

  .cols.wide-right .col:first-child {
    flex: 1.2;
  }

  .cols.wide-right .col:last-child {
    flex: 0.8;
  }

  .cols.wide-left .col:first-child {
    flex: 1.1;
  }

  .cols.wide-left .col:last-child {
    flex: 0.9;
  }

  .col.img-col {
    display: flex;
    align-items: center;
    justify-content: center;
    min-height: 420px;
  }

  .col.img-col img {
    max-width: 100%;
    max-height: 560px;
    object-fit: contain;
    display: block;
    margin: 0 auto;
  }

  .callout {
    margin-top: 18px;
    padding: 10px 14px;
    background: #fef3c7;
    border-top: 2px solid #d97706;
    font-size: 0.74em;
    color: #78350f;
  }

  .full-image {
    text-align: center;
  }

  .full-image img {
    max-width: 96%;
    max-height: 560px;
    object-fit: contain;
  }

  .dial-image img {
    max-width: 86%;
    max-height: 560px;
    object-fit: contain;
  }
---

<!-- _class: lead -->

# Tools for Ancient Indian Astronomy and Cosmography

Session 2 · From Visual Demonstration to Research Workflow

Sunder Chakravarty  
CAHC, Jain University

---

# Recap and Roadmap

<div class="cols">
<div class="col">

## Session 1 covered

- Meru — cosmographic visualization
- Stellarium basics and sky culture
- Dhruva, Thuban, and precession intuition
- Sun: daily and annual motion
- Nakṣatras: stars, shapes, arc-zones
- Precession as a dating tool — VGJ sun-transit examples

</div>
<div class="col">

## Session 2

1. Moon and the equinoctial full-moon problem
2. The dial plot and Maghādi scheme
3. Eclipses — Parāśara Tantra and NASA/JLEX
4. Digital tools and CAHC resources
5. AI-assisted chores

</div>
</div>

<div class="callout">
Session 2 extends the same precession arc from the Sun to the Moon, then broadens to the research toolkit.
</div>

---

# The Moon Problem

- Session 1 used the **Sun's nakṣatra position** to date texts.
- Session 2 adds the **Moon**: _where is the full moon at the equinox?_
- The Brāhmaṇḍa Purāṇa (BP) ch. 21 gives quarter-nakṣatra precision:
  - Spring equinox full moon at **¼-Kṛttikā** (η Tau)
  - Autumn equinox full moon at **¾-Viśākhā** (α¹ Lib)

### Why this is a dating constraint

- The equinox point drifts through the nakṣatras via precession.
- These two stars were in the correct equinoctial sectors only during a specific window.
- Astropy epoch scan over −2400 to −800 locates that window.

### Stellarium demo

- `ssc/s21-moon-swing.ssc` — 30+ successive moonrises showing the monthly horizon swing

<div class="callout">
The same precession logic — now applied to the full moon rather than the seasonal sun.
</div>

---

# BP 21 — The Text

<div class="cols">
<div class="col img-col">
<img src="/Users/sunder/projects/cahc/cahc-utils/presentations/equinoctial-full-moon/bp-२१-१४२-१४९-devanaagari.jpeg" alt="BP 21 text">
</div>
<div class="col">

- Equinoctial full moons in terms of named nakṣatra sectors.
- Day and night are equal - **Equinox**
- Sun ¼Kṛttikā, Moon ¾-Viśākhā — **Vasanta Full Moon**
- Sun ¾-Viśākhā, Moon head-Kṛttikā — **Śarat Full Moon**

- The BP text is in its present form from early CE, but these astronomical statements belong to a much older observational layer.

### Stellarium demo

- `ssc/s22-bp-eqfm-best-case.ssc` — vasanta and śarat best-case views near 1700 BCE

</div>
</div>
<div class="callout">
They belong to an observational layer earlier than PT, VGJ, and Lagadha's Jyotiṣa Vedāṅga (around 1350 BCE).
</div>

---

# Equinoctial Full Moon - Analysis method

<div class="cols">
<div class="col img-col">
<img src="/Users/sunder/projects/cahc/cahc-utils/presentations/equinoctial-full-moon/bp-equinoctial-full-moon-better.png" alt="equinoctial full moon chart">
</div>
<div class="col wide-right">

- All full moons in −2400 to −800 are gathered first using Astropy, about 1300 per century.
- We then select full moons with the Sun within ±1 day of the equinox, about 13 per century.
- These Full moons are plotted as green dots in chart
  - **Vaiśākhī** - Spring Eqnx Sun ¼Kṛttikā 0°
  - **Kārttikī** - Autumn Eqnx Sun ¾Viśākhā 180°

- The nakṣatra proxy stars are then precessed
  - **Red line**: drift of η-Tau (Kṛttikā)
  - **Blue line**: drift of α¹-Lib (Viśākhā)

- The **shaded window** ~ 1980–1610 BCE - stars in their equinoctial sectors. The sharper spring equinox constraint **~1700–1600 BCE**.

- `ssc/s25-eqfm-search-visualizer.ssc` — epoch-by-epoch traversal of 2400–800 BCE candidates

</div>
</div>

---

# Maghādi scheme - MAU , BP - 1800 BCE

<div class="cols wide-left">
<div class="col img-col">
<img src="/Users/sunder/projects/cahc/cahc-utils/presentations/equinoctial-full-moon/ndial_kuru_07_-1800.png" alt="dial ~1800 BCE">
<!-- <img src="/Users/sunder/projects/cahc/cahc-utils/presentations/equinoctial-full-moon/mau-magha-scheme.png" alt="magha scheme dial"> -->
</div>
<div class="col">

### Two axes, one dial

- The **N–S axis** (MAU): winter solstice in ½-Śraviṣṭhā, summer solstice in Āśleṣā.
- The **E–W axis** (BP): spring equinox at ¼-Kṛttikā, autumn equinox at ¾-Viśākhā.

- Both axes are consistent on a single 27-sector dial — the **Maghādi scheme**.

### Key result

- Kṛttikā-¼ at spring equinox ≡ Śraviṣṭhā-½ at winter solstice.
- MAU and BP are the same scheme stated from different starting points.

- The Maghādi zodiac thus predates the Śraviṣṭhādi zodiac by ~480 years (6°40' of precession).

</div>
</div>

---

# Śraviṣṭhādi scheme - PT, VGJ ~1300 BCE

<div class="cols">
<div class="col img-col">
<img src="/Users/sunder/projects/cahc/cahc-utils/presentations/equinoctial-full-moon/ndial_kuru_12_-1300.png" alt="dial ~1300 BCE">
</div>
<div class="col">

### What has changed

- Precession has shifted the stars relative to the cardinal axis.
- By ~1300 BCE, Maghā is no longer visible at the summer-solstice sunrise — the Maghādi anchor is broken.
- The winter solstice has drifted: the beginning of the Śraviṣṭhā _sector_ now coincides with the solstice point — the **Śraviṣṭhādi scheme** takes over.
- This is the regime of PT and VGJ.

<div class="callout">
Precession rotates the outer star dial. The season boundaries stay fixed.
</div>

</div>
</div>

---

# Seasonal Nakṣatra Drift: 2400 to 1000 BCE

<div class="dial-image">
<img src="/Users/sunder/projects/cahc/cahc-utils/presentations/equinoctial-full-moon/ndial_1.gif" alt="dial animation" style="scale: 0.8;">
</div>

<div class="callout">
Animation shows precession rotating the star positions through the fixed season-domain framework, −2400 to −1000 BCE.
</div>

---

# Stellarium , Astropy - Contrast

- Stellarium GUI
  - Shows _individual_ cases convincingly.
  - Allows for targeted exploration of specific dates.
  - Scripting is possible but not as efficient as Astropy.

- Astropy supports repeatable computation
  - Measured example: next 1000 sunrise queries from a fixed Bangalore start JD
  - _Astropy/Astroplan: 10.4 s_
  - _Stellarium script: 19.3 s_
  - About _1.85×_ faster on this repeated-query task

| Method            | Best For            |
| ----------------- | ------------------- |
| Stellarium GUI    | Visualisation       |
| Stellarium script | Reproducible demo   |
| Astropy scan      | Exhaustive coverage |

<div class="callout">
AI tools speed up writing the code — not running it. Computation time is physics, not productivity.
</div>

---

# Eclipses - Parāśara Tantra

<div class="cols wide-right">
<div class="col img-col">
<img src="/Users/sunder/projects/cahc/cahc-utils/presentations/2026-03-23-iks-astro-talk/pics/pt-eclipse-table.jpg" alt="PT eclipse table">
</div>
<div class="col">

- Parāśara Tantra records eclipse sequences over lunations.

- The text encodes a periodicity claim: specific lunation counts produce eclipse pairs.
- Location anchor: Jaipur

### Verification with NASA/JLEX

- [NASA/JLEX eclipse search](http://eclipse.gsfc.nasa.gov/JLEX/JLEX-AS.html) is a free, browser-accessible tool.

- Query by location, date range, type.

### Stellarium support

- `ssc/s23-total-eclipse-india.ssc` for the visual/location demo
- `ssc/s24-pt-eclipse-jaipur.ssc` for the PT sequence support

</div>
</div>

---

# Meru — Cosmographic Visualization

<div class="cols wide-right">
<div class="col">

### What it is

- An interactive 3-D cosmographic visualization of the Meru model.
- Draws from multiple textual sources — not tied to one text.

- Built to explore and explain, not to prove.

### What it shows

- Meru as the polar axis of a concentric world model.
- Dhruva at the apex; the nakṣatra wheel rotating around it.

- Seasons and geographic zones as concentric rings.

### Access

- Live: [meru-cosmos.netlify.app](https://meru-cosmos.netlify.app/)

</div>
<div class="col">

### Notes

- Useful for connecting the textual descriptions of cardinal directions, Dhruva, and the nakṣatra wheel.

- The same precession intuition from Stellarium applies here in a cosmographic frame.

</div>
</div>
<div class="callout">
The app is a visualization aid — it makes an older descriptive cosmology navigable and discussable.
</div>

---

# Digital Tools and CAHC Resources

<div class="cols">
<div class="col">

### CAHC Search Portal

- Full-text and metadata search across CAHC-associated papers.
- Supports keyword and author search.
- _Live demo if time and connectivity allow._

### Patra Darpan

- Digitized journal index covering selected publications
- An informal, more available repository of papers in our areas
- Not complete but convenient
- [Patra Darpan](https://patra-darpan.netlify.app/)

</div>
<div class="col">

### Sanchaya

- Corpus of Sanskrit texts with text search.
- Not complete but convenient
- Example: Useful for locating nakṣatra references across texts.
- [Sanchaya](https://sanchaya.rasowshi.us/)

### Semantic Search

- Embedding-based search over CAHC paper abstracts.
- Surfaces papers by conceptual proximity, not keyword match.

<div class="callout">
These informal tools reduce the friction of source-chasing — leaving more time for careful reading.
</div>

</div>
</div>

---

# AI-Assisted Chores — What and Why

- Modern LLMs can help with **repetitive scholarly tasks** — not replace judgment.
- Two examples relevant to Jyotiṣa research:
  - **Kaṭapayādi decoding** — the numerical cipher used in astronomical mnemonics
  - **Sanskrit anvaya** — unpacking technical sūtra prose into readable order

### The guardrail

> _Always verify. The model is helpful for reducing drudgery and exploratory friction — not for final authority._

- Errors are plausible-sounding and not self-flagged.
- Works best with a domain-aware human in the loop.

---

# AI Example 1 — Kaṭapayādi

<div class="cols">
<div class="col">

### The prompt

> _Explain this verse and decode the kaṭapayādi rule it encodes:_
> नञावचश्च शून्यानि संख्याः कटपयादयः।
> मिश्रे तूपान्त्यहल् संख्या न च चिन्त्यो हलस्वरः ॥

</div>
<div class="col">

### What the model returned

- Full padaccheda and anvaya
- Mapping table: क=1 … ञ=0, ट=1 … न=0, प=1…म=5, य=1…ह=8
- Rule for conjunct consonants: only the _last_ consonant counts
- Directionality note: **अङ्कानां वामतो गतिः** — digits read right to left
- Example: भवति → भ(4), व(4), त(6) → reads as **644**

<div class="callout">
Useful as a quick reference check. The mapping table should be verified against a standard commentary.
</div>

</div>
</div>

---

# AI Example 2 — Nidānasūtra Anvaya

<div class="cols">
<div class="col">

### The prompt

> _Parse and give anvaya for Nidānasūtra 5.12 on the Āditya-Saṃvatsara._

### The text

त्रयोदशाहं त्रयोदशाहम् एकैकं नक्षत्रम् उपतिष्ठति। अहस्-तृतीयं च नवधा कृतयोः अहोरात्रयोः द्वे द्वे कले च।

</div>
<div class="col">

### What the model returned

- Padaccheda and anvaya in Sanskrit, then English
- Derivation: 13 + ⅓ + 2/9 = **122/9 days per nakṣatra**
- Total: 27 × 122/9 = **366 days** (6 × 61 = ṣaṇṇava-vargāḥ)
- Identified _navadhā_ as a 1/9-day unit predating the 60-nāḍī system

<div class="callout">
The arithmetic derivation is correct and checkable. The unit interpretation (navadhā) is a reasonable scholarly reading — treat as a hypothesis.
</div>

</div>
</div>

---

# Wrap-Up

- Stellarium makes ancient sky visible and testable.
- Precession turns visible sky change into a dating instrument.
- In both sessions, a textual sky description becomes a dating clue:
  - in Session 1 through the Sun,
  - in Session 2 through the Moon.
- Astropy extends individual visual checks into exhaustive epoch scans.
- Eclipses can be checked with NASA/JLEX and Stellarium.
- Digital tools widen the research toolkit.
- AI helps with drudgery — never with final interpretation.

<div class="callout">
These tools are most useful when they reduce repetitive effort and leave more time for careful scholarly thinking.
</div>
