# Notebook summaries

## CAHC Explorations - nakṣatra , seasonal astronomy, others .. (cahc_explore.ipynb)
<a class="anchor" id="top_"></a>

This notebook contains exploratory code, data and visualizations for investigating traditional Indian sky-culture concepts (nakṣatras, aditya-cāra/seasonal motion, maasa/rtu patterns and lunar motion) for different historical epochs and geographic locations. It collects nakṣatra metadata, computes/plots nakṣatra and seasonal boundaries for chosen epochs, traces the Moon's path through nakṣatras over time, and inspects circumpolarity (sisuāra) behavior.

This document summarizes what the notebook does, how to run it, and what to look for when interpreting its results.

### High-level goals (what the notebook helps you do)
- Load and examine nakṣatra metadata (names, ecliptic ranges, reference stars).
- Visualize nakṣatra positions overlayed with seasons (rtu / aditya-cāra) for a given epoch and location.
- Simulate and plot lunar motion among nakṣatras over date ranges.
- Analyze circumpolarity (stars/nakṣatras that are circumpolar / near-circumpolar) at selected latitudes and epochs.
- Produce publication-ready plots and simple animations that illustrate seasonal/nakṣatra changes over long timescales (precession / epoch shifts).

### Intended audience
- Historians of astronomy, students of Vedāṅga Jyotiṣa / Lagadha traditions.
- Researchers who want to compare textual descriptions of nakṣatra/rtu relationships with astronomical reconstructions.
- Practitioners who want visual/contextual tools for teaching sky-culture.

### TOC
- [Moon Longitude and Longitude Diff by sidereal cycle](#m_l_ld)
- [Moon Longitude by sidereal cycle](#m_l)
  - [Interpolate the time series mdf](#mdf_interpolate)
- [Nakshatras Meta Data](#naks_meta_data)
- [Moon Dwell Time by Nakshatra](#moon_dwell_time_by_nakshatra)
- [Explore longitude diff at Full Moon between Moon and other Gruhas](#ld_m_g)
- [Explore Relation of Full Moon to Maasa Names](#fm_mn)
- [Mars and Moon Parvas](#mm_prv)
- [Eclipses](#eclipses)
  - [Lunar Eclipse - Six in a row](#lunar-eclipse-at-jaipur)
  - [Eclipse Triples](#eclipse-triples-analysis)
- [Sundial](#sun-dial)
- [Sisumara Circumpolarity](#sisumara-circumpolarity)
- [Kausitiki Brahmana Punarvasu](#kb-puanrvasu)
- [Brahmanda Purana KV](#brahmanda-purana-kv)
  - [PlanetPos based KV plots](#planetpos-based-kv-plots)
  - [Astropy based KV plots](#astropy-based-kv-plots)
  - [Equinoctial Full Moons](#equinoctial-full-moons-for-iks)
  - [Seasonal Nakṣatras of BP/MAU , VGJ and LVJ](#seasonal-naks-of-bp)
- [FM/NM Sequence Explorations](#fm-nm-sequence-explorations)
  - [FM Sequences](#fm-sequences)
  - [NM Sequences](#nm-sequences)
- [Nakshatras Heliacal Rising analysis](#nakshatras-heliacal-rising-analysis)
- [Sunrise azimuths for a year](#sunrise-azimuths-for-a-year)
- [वायुपुराणम् १.५३](#vayu-puranam)
  - [Least Errror Fit for Sun+Gruhas with Naks](#least-error-fit)
  - [Jupiter and Saturn Only](#jupiter-and-saturn-only)
- [Jyeṣṭhā and Rohiṇi](#jyeshtha-rohini)
- [Eclipse by Century](#eclipse-by-century)
- Plots for Mahāsalilam book
  - [Moon illumination](#moon-illumination)
  - [Graha Magnitudes](#graha-magnitudes)
- [Chandra maarga of VGJ](#chandra-maarga-of-vgj)
- [Moon Rise Set Events](#moon-rise-set-events)
- [Nālāyira Divya Prabandham](#nalayira-divya-prabandham)
- [Mārgazhi Thiṇgaḻ](#margazhi-thingal)
- [Sāvātisampātaṁ](#savatisampatam)

[top](#top_)

## Consecutive Full Moon Analysis Notebook (consecutive_fms.ipynb)

This notebook analyzes full moon data, focusing on historical lunar events and their periodicity. It processes a dataset of full moons, extracts relevant features, and performs various analyses to identify patterns and anomalies in the lunar cycle.

### Objectives
- Analyze full moon data over a historical period (BCE dates)
- Extract features such as date, year, season, century, and lunar positions
- Perform analyses to identify:
  - Grouping of full moons by century
  - Equinoctial full moons
  - Full moons near specific nakshatras (Kṛttikā and Viśākhā)
  - Patterns in sequences of full moons using the "smud" metric

### What is "smud"?
- Smud stands for "sequential moon uniform days."
- "Smud" is derived from the last digit of the difference in Julian dates between consecutive full moons, then combined in blocks of six.
- The notebook searches for repeated digits in these blocks (e.g., six consecutive full moons with the same last digit in their JD difference).
- The analysis aims to find rare or interesting periodicities in the lunar cycle, possibly for calendrical or astronomical significance.

## Lunar Standstills and Eclipse Analysis (Jaipur, BCE 1400–1500) (lunar_standstills.ipynb)

This notebook analyzes lunar standstills and eclipse patterns over a century in ancient Jaipur, focusing on astronomical cycles and eclipse clustering. It combines historical lunar rise/set data and eclipse records to:

- Parse and normalize lunar event data (rise, azimuth, phase, paksha, etc.) for BCE dates using Astropy.
- Join lunar phase and eclipse datasets to identify eclipse types and their timing.
- Visualize full moon, new moon, and eclipse events, highlighting their azimuth and phase distributions.
- Detect and display eclipse tetrads—clusters of four or more lunar eclipses occurring within short intervals.
- Provide sample tables and plots for eclipse events and tetrads, supporting research into ancient astronomical cycles.

The notebook is designed for historical astronomy research, with robust handling of BCE dates and clear visualizations of lunar phenomena.

## Gruha Chaara — Planet Motion Explorer  (gruha_chaara.ipynb)

This notebook is an astronomical research tool that explores planetary motion and visualizes prograde/retrograde behavior for five classical planets: Mercury, Venus, Mars, Jupiter, and Saturn.

### Scope and purpose
- Covered planets: Mercury, Venus, Mars, Jupiter, Saturn.
- Visual analyses: identify intervals of prograde and retrograde motion, plot apparent motion timelines, and compute summary statistics (durations, frequency, transition dates).
- Intended audience: researchers using astronomical observations and descriptions from ancient Indic texts; outputs are numerical and visual (not astrological interpretations).

### Quick run notes
1. Ensure required datasets are available under `../datasets/` or generate positions with the provided utilities in `jyotisha`.
2. Large date ranges may be slow — use a smaller sample for exploration or pre-compute ephemerides where possible.
3. Cells marked LONG are optional for quick runs.

### Notes
- This is exploratory code; consider extracting stable functions into `jyotisha/` modules for reproducible research.

## वेदाङ्गजयोतिषम् — लगधः: Time units and conversions (lagadha_units.ipynb)

This notebook extracts and computes traditional time units described in the Vedāṅga Jyotiṣa (Lagadha) and related texts.
It encodes slokas as algebraic relations among classical units (पलम्, आढकः, नाडिका, मुहुर्तम्, कला, द्युः, etc.),
solves the linear system to derive conversion factors, and outputs the results as both fractional ratios and decimal floats.

## Lunar Events Calculator (lunar-events-calculator.ipynb)

An astronomically accurate tool for calculating key lunar events, designed for both modern and historical research. This calculator determines:

- Thithi (lunar day) based on precise phase extrema
- Paksha (fortnight) transitions: Krishna (Purnima→Amavasya), Shukla (Amavasya→Purnima)
- Parva (major lunar events) identification using local minima/maxima
- Support for BCE dates and ancient calendar studies
- Visualization-ready outputs for integration with Stellarium

## Transit of sun through the seasonal nakṣatra cycle in the Vṛddha-Gārgīya Jyotiṣa  (vgj_ac_rs.ipynb)

The notebook plots the transit of the sun through the seasonal nakṣatra cycle as described in the Vṛddha-Gārgīya Jyotiṣa. 

Some of these plots are included in the Indian Journal of History of Science 56.3 (2021) - [Transit of sun through the seasonal nakṣatra cycle in the  Vṛddha-Gārgīya Jyotiṣa](https://insa.nic.in//writereaddata/UpLoadedFiles/IJHS/1.pdf).

