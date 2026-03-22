---
marp: true
theme: gaia
paginate: true
header: CAHC Tutorial
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
    max-height: 580px;
    object-fit: contain;
  }
---

<!-- _class: lead -->

# Tools for Ancient Indian Astronomy and Cosmography

Stellarium as a tutorial instrument for seeing, checking, and explaining ancient astronomical ideas.

Sunder Chakravarty  
CAHC, Jain University

---

# Sessions

<div class="cols">
<div class="col">

## Session 1

- Meru — cosmographic visualization
- Stellarium basics and sky culture
- Dhruva, Sun, and Nakṣatra demonstrations
- Precession as a visual and textual dating aid

</div>
<div class="col">

## Session 2

- BP chapter 21 and equinoctial full moon
- Astropy-supported scanning
- Eclipses and digital research aids

</div>
</div>

<div class="callout">
Session 1 emphasizes visual and observational foundations. Session 2 extends the same arc with Moon-focused and computational examples.
</div>

---

# Session 1 Roadmap

1. Meru Cosmology
2. Stellarium basics, coordinates, and sky culture
3. Dhruva, Thuban, and Śiśumāra
4. Sun: daily and annual motion
5. Nakṣatras: stars, shapes, and zones
6. Precession and textual dating

# Why Stellarium?

- It makes **astronomical ideas visible** quickly.
- It lets us change location, epoch, and viewing frame.
- It helps _connect text_ to **sky appearance**.
- Prepared scripts improve repeatability and reduce demo friction.

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

# Stellarium Basics

<div class="cols wide-right">
<div class="col">

### Topics

- **Location:** The visible sky changes with latitude and longitude.
- **Date and time:** Epoch and local time are essential to historical sky reconstruction.
- **Ecliptic and equator:** These overlays make solar and seasonal motion easier to read.
- **Alt-Az and meridian:** These help separate horizon phenomena from meridian phenomena.
- **Projections:** Different projections make different features easier to see.
- **Sky culture:** Naming systems and sky groupings matter when texts are interpreted visually.

</div>
<div class="col">

### Why this matters

- These controls make the Stellarium screen readable and comparable across epochs and locations.
- Once the viewing frame is understood, the astronomical demonstrations become easier to follow.
- Stellarium can then function as a repeatable observational aid.

</div>
</div>

<div class="callout">
These controls establish the visual vocabulary for the rest of the session.
</div>

---

# Dhruva, Thuban, and Śiśumāra

<div class="cols">
<div class="col">

### Main idea:

- The identity of the **pole star** is historical, not timeless.

### Main script - `ssc/s11-dhruva-pole-drift.ssc`

- Location: about 30°N
- 2830 BCE, **Abhaya Dhruva** (Thuban) of Śiśumāra close to the north celestial pole
- Step forward in time and watch the pole drift away from Thuban
- End in the modern sky, with the pole near **Polaris**

</div>
<div class="col img-col">
<img src="/Users/sunder/projects/cahc/cahc-utils/presentations/sun-transit/sun-transit-precession.png" alt="precession">
</div>
</div>

---

# Sun: Daily and Annual Motion

<div class="cols wide-right">
<div class="col">

### Topics

- **Daily path:** The Sun rises, culminates, and sets in a regular daily pattern.
- **Sunrise shift on the horizon:** The rising point moves north and south through the year, the sun's **annual swing** best seen with `ssc/s12-sun-swing.ssc`.
- **High and low Sun:** The Sun also changes in noon/meridian height, appearing higher in summer and lower in winter, best seen with `ssc/s13-sun-meridian-high-low.ssc`.
- **Dakṣiṇāyana and Uttarāyaṇa:** The turning points of the annual swing can be explained with `ssc/s13-sun-meridian-high-low.ssc`.

</div>
<div class="col">

### What to Notice

- The horizon view makes annual movement immediately visible - _Dakṣiṇāyana and Uttarāyaṇa, annual swing_
- The meridian view explains high and low Sun more clearly - _High and low Sun_
</div>
</div>

<div class="callout">
This is clearer in live motion than in a static figure.
</div>

---

# Nakṣatras: Visible Stars, Arc Spans

<div class="cols img-col">
<div class="col img-col">
<img src="/Users/sunder/projects/cahc/cahc-utils/presentations/sun-transit/sun-transit-nakshatra-table.png" alt="nakshatra table">
</div>

<div class="col">

### Topics

- **27 nakṣatras** : 83 stars on the ecliptic
- **28th nakṣatra** : Abhijit : 3 stars
- Are either **visible stars with shapes** or **arc spans**
- **Equal spans** of 13°20' each - for Sun tracking
- **Variable spans** - for Moon tracking in some traditions

<div class="callout">
Nakṣatras are <b>not lunar mansions</b>
</div>

### Stellarium Script

- `ssc/s14-nakshatra-tour.ssc` - tour of the 27 nakṣatras.

</div>
</div>

---

# Nakṣatra Shapes and Proxy Stars

<div class="cols">
<div class="col img-col">
<img src="/Users/sunder/projects/cahc/cahc-utils/presentations/sun-transit/sun-transit-astrographs.png" alt="astrographs">
</div>
<div class="col">

### Notes

- **Rohiṇī** has a shape of _vedic triangular cart_
- **Āślesā** as a _snake_
- **Maghā** as an _enclosure_
- Some nakṣatras are easier to identify than others
- Our work shows 27 proxy stars yield results close to using 83 actual stars

</div>
</div>

---

# Precession as a Dating Tool

- Precession slowly shifts the relation between seasonal points and nakṣatras.
- This makes certain astronomical statements in texts date-sensitive.

### Chronological arc

- **Brāhmaṇḍa Purāṇa Chapter 21** _(about 1800 BCE)_
- **Vṛddhagārgīya Jyotiṣa / Ādityacāra** _(about 1350 BCE)_
- **Vṛddhagārgīya Jyotiṣa / Ṛtusvabhāva** _(about 500 BCE)_

### The Analytical Method

- **Extract** - text states the sun's nakṣatra at each season boundary
- **Compute** - for each candidate epoch, find the sun's nakṣatra at each textual season boundary
- **Measure** - error = mismatch between computed nakṣatra and textual target
- **Minimise** - epoch with smallest accumulated error is the best-fit date

<div class="callout">
Automation reduces repetitive checking and makes comparison across epochs practical.
</div>

---

# The Earliest Anchor in This Arc

<div class="cols wide-right">
<div class="col img-col">
<img src="/Users/sunder/projects/cahc/cahc-utils/jyotisha/images/ms-book/pg29-eqfm_paper_submit.png" alt="eqfm chart">
</div>
<div class="col">

### BP Chapter 21

- Specifies equinoctial full moons at quarter-nakṣatra precision.
- This is the earliest case in the chronological precession story here.
- It belongs to an earlier chronological layer than the VGJ examples.
- Its fuller Moon-focused treatment follows in Session 2.
- The **two slanting lines** show the precession-induced drift of the kṛttikā and viśākhā over time.

</div>
</div>

---

# Ādityacāra - Vṛddhagārgīya Jyotiṣa 11

<div class="cols">

<div class="col">
<img src="/Users/sunder/projects/cahc/cahc-utils/presentations/sun-transit/sun-transit-adityacara-charts.png" alt="adityacara charts">
</div>

<div class="col wide">

- The verse encodes 9 nakṣatra boundaries for 6 seasons; śiśira-ṛtu start anchors the sun at 270°
- Each nakṣatra's expected longitude span is 13°20' in the equal-division model
- Error = mean non-containment of the sun across the 3 boundary nakṣatra sets
- Top figure: error minimum at **1350 BCE** → best-fit epoch
- Dot figure: same result — maximum nakṣatra containment

</div>

---

# Ṛtusvabhāva - Vṛddhagārgīya Jyotiṣa 59

<div class="cols wide-right">

<div class="col">
<img src="/Users/sunder/projects/cahc/cahc-utils/presentations/sun-transit/sun-transit-rtusvabhava-charts.png" alt="rtusvabhava charts">
</div>

<div class="col">

- The verse maps seasons to
  - nakṣatra,
  - vedic solar months,
  - laukika months
- The _top figure_ shows this mapping.
- e.g. **vasanta** is
  - _(revati,madhu,caitra)_,
  - _(bharaṇi,mādhava,vaiśākha)_
- We take
  - **mid-vasanta as sun at 0°**
  - and find best fit epoch by minimizing error
- The **red curve** in the _lower figure_ shows the best fit epoch ~ **500 BCE**

</div>

</div>

---

# Transition from unequal to equal regime

<div class="cols wide-right">
<div class="col img-col">
<img src="/Users/sunder/projects/cahc/cahc-utils/presentations/sun-transit/sun-transit-transition-abhijit.png" alt="transition abhijit">
</div>
<div class="col">

- **Abhijit** (Aquila zone) elided
  - to equalize seasons at 4½ nakṣatras each
  - off ecliptic by ~10°
  - **Śravaṇa** inherited its Aquila slot
- Precession shifted winter solstice
  - from **Śraviṣṭhā** (β Aqr zone)
  - to newly named **Dhaniṣṭhā** (α/β Del)
- Older scheme
  - valid 1700–1350 BCE
  - breaks down after → reform pressure
- Reformed 27-equal system best fits **~1250 BCE**

</div>
</div>

---

# End of Session 1

- Stellarium helps us see and rehearse the sky logic.
- Precession turns visible sky change into a dating aid.
- Seasonal and lunar textual constraints can then be tested more systematically.

### Session 2 will continue with

- BP chapter 21 in fuller detail
- Moon-focused examples
- Astropy-supported scanning
- Eclipses, Meru, and digital research aids
