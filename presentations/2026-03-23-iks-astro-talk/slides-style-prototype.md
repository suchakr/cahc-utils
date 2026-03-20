---
marp: true
theme: gaia
paginate: true
header: CAHC Tutorial Prototype
backgroundColor: #fcfbf7
color: #1f2937
style: |
  section {
    font-family: "Aptos", "Segoe UI", sans-serif;
    font-size: 28px;
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

  h1 { font-size: 1.52em; }
  h2 { font-size: 1.2em; }

  h3 {
    color: #334155;
    font-size: 0.78em;
    margin: 8px 0 10px 0;
    text-transform: uppercase;
    letter-spacing: 0.04em;
  }

  p, li { font-size: 0.82em; }
  ul { margin: 0.2em 0 0.2em 1.1em; padding: 0; }
  li { margin: 0.18em 0; }

  strong { color: #7c2d12; }
  em { color: #1d4ed8; }

  a {
    color: #0f766e;
    text-decoration-thickness: 2px;
  }

  code {
    font-family: "SFMono-Regular", "Menlo", monospace;
    font-size: 0.78em;
    background: #f1f5f9;
    padding: 0.08em 0.28em;
    border-radius: 6px;
  }

  pre {
    font-family: "SFMono-Regular", "Menlo", monospace;
    font-size: 0.64em;
    line-height: 1.3;
    background: #f8fafc;
    border: 1px solid #cbd5e1;
    border-radius: 12px;
    padding: 14px 16px;
    margin: 0.5em 0;
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
    font-size: 1.78em;
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

  .col.img-col {
    display: flex;
    align-items: center;
    justify-content: center;
    min-height: 430px;
  }

  .col.img-col img {
    max-width: 100%;
    max-height: 500px;
    object-fit: contain;
    display: block;
    margin: 0 auto;
  }

  .callout {
    margin-top: 18px;
    padding: 10px 14px;
    background: #fef3c7;
    border-top: 2px solid #d97706;
    font-size: 0.7em;
    color: #78350f;
  }

  .full-image {
    text-align: center;
  }

  .full-image img {
    max-width: 92%;
    max-height: 520px;
    object-fit: contain;
  }
---

<!-- _class: lead -->

# Tools for Ancient Indian Astronomy and Cosmography

Marp prototype for slide geometry, typography, header/footer, and layout classes.

Sunder Chakravarty · CAHC

---

# Dhruva and Precession

<div class="cols">
<div class="col">

### Purpose

- show a visually memorable precession example
- keep the text light and the image large
- use this for Dhruva, Sun, and Moon demos

### Use when

- one image carries most of the slide
- the spoken explanation matters more than dense text

</div>
<div class="col img-col">
<img src="/Users/sunder/projects/cahc/cahc-utils/presentations/sun-transit/sun-transit-precession.png" alt="precession figure">
</div>
</div>

<div class="callout">
Optional callout band for one key sentence, a caution, or a “what to notice” prompt.
</div>

---

# Seasonal Marker Dating

<div class="cols">
<div class="col img-col">
<img src="/Users/sunder/projects/cahc/cahc-utils/presentations/sun-transit/sun-transit-adityacara-charts.png" alt="adityacara chart">
</div>
<div class="col">

### Analytical Ladder

- text gives a seasonal nakṣatra constraint
- compute the solar alignment error at a candidate epoch
- repeat across epochs
- find minima and transition regions

### Use when

- the chart needs space
- the method can be stated compactly
- this is a paper-core explanation slide

</div>
</div>

---

# Full-width Text Slide

### Good for

- opening questions
- section dividers with substance
- methods that need a clean verbal explanation

### Example body

- We use precession only as an aide to interpret textual astronomical constraints.
- The tool does not create the research question.
- It reduces repetitive checking and makes large epoch scans practical.

> This is also a good layout for a short Devanāgarī verse plus translation.

---

# Full-width Image Slide

<div class="full-image">
<img src="/Users/sunder/projects/cahc/cahc-utils/jyotisha/images/ms-book/pg29-eqfm_paper_submit.png" alt="equinoctial full moon chart">
</div>

<div class="callout">
Best for paper figures, charts that need visual breathing room, or a pause slide before discussion.
</div>

---

# Comparison Slide

<div class="cols">
<div class="col">

### Stellarium

- excellent for seeing
- good for selected epochs
- slower for large scans

```text
visual inspection
scripted replay
object properties
```

</div>
<div class="col">

### Astropy

- excellent for batch computation
- good for large epoch scans
- less intuitive visually unless paired with plots

```text
epoch scan
error curves
candidate windows
```

</div>
</div>

---

# Verse, Table, and Link Styles

> कृत्तिकानां यदा सूर्यः प्रथमांशगतो भवेत् ।  
> विशाखानां तदा ज्ञेयश्चतुर्थांश निशाकरः ॥

| Element     | Intended style              |
| ----------- | --------------------------- |
| verse block | warm background, left rule  |
| table       | fixed compact size          |
| code        | muted, readable, not flashy |
| links       | visible but restrained      |

Reference: [BP paper PDF](https://cahcblr.github.io/assets/cached_papers/rni/01_58_4.pdf)
