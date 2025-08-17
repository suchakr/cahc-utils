# Notebook summaries (first markdown cell)

## .ipynb_checkpoints/c2-checkpoint.ipynb

<a class="anchor" id="top_"></a>


# Some CAHC Explorations
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

## .ipynb_checkpoints/cahc_explore-checkpoint.ipynb

<a class="anchor" id="top_"></a>


# Some CAHC Explorations
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

## cahc_explore.ipynb

<a class="anchor" id="top_"></a>

# cahc_explore.ipynb — CAHC Explorations (nakṣatra & seasonal astronomy)

This notebook contains exploratory code, data and visualizations for investigating traditional Indian sky-culture concepts (nakṣatras, aditya-cāra/seasonal motion, maasa/rtu patterns and lunar motion) for different historical epochs and geographic locations. It collects nakṣatra metadata, computes/plots nakṣatra and seasonal boundaries for chosen epochs, traces the Moon's path through nakṣatras over time, and inspects circumpolarity (sisuāra) behavior.

This document summarizes what the notebook does, how to run it, and what to look for when interpreting its results.

## High-level goals (what the notebook helps you do)
- Load and examine nakṣatra metadata (names, ecliptic ranges, reference stars).
- Visualize nakṣatra positions overlayed with seasons (rtu / aditya-cāra) for a given epoch and location.
- Simulate and plot lunar motion among nakṣatras over date ranges.
- Analyze circumpolarity (stars/nakṣatras that are circumpolar / near-circumpolar) at selected latitudes and epochs.
- Produce publication-ready plots and simple animations that illustrate seasonal/nakṣatra changes over long timescales (precession / epoch shifts).

## Intended audience
- Historians of astronomy, students of Vedāṅga Jyotiṣa / Lagadha traditions.
- Researchers who want to compare textual descriptions of nakṣatra/rtu relationships with astronomical reconstructions.
- Practitioners who want visual/contextual tools for teaching sky-culture.

## TOC
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

## consecutive_fms.ipynb

## Consecutive Full Moon Analysis Notebook

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

## darsha_poornamasa/lunar_standstills.ipynb

## Purpose — quick overview

This notebook analyses lunar standstills and eclipse clustering for Jaipur (BCE 1400–1500).
It expects input CSVs (moon rise/set and eclipse lists) under `../datasets` and produces summary CSVs and plots under `darsha_poornamasa/`.

Use this notebook to: parse and normalise BCE moon event data, join eclipse records, visualise azimuth/phase distributions, and detect eclipse tetrads.

## gruha_chaara.ipynb

## Explore the duration between succesive Planet - Nakshatra interaction

## lagadha_units.ipynb

# वेदाङ्गजयोतिषम् - Time units by लगध

## lunar-events-calculator.ipynb

# Lunar Events Calculator

An astronomically accurate tool for calculating key lunar events, designed for both modern and historical research. This calculator determines:

- Thithi (lunar day) based on precise phase extrema
- Paksha (fortnight) transitions: Krishna (Purnima→Amavasya), Shukla (Amavasya→Purnima)
- Parva (major lunar events) identification using local minima/maxima
- Support for BCE dates and ancient calendar studies
- Visualization-ready outputs for integration with Stellarium

---

**Engineering Improvements:**

- Separation of concerns: calculation, caching, filtering, visualization
- Hybrid caching: joblib disk cache + lru_cache memory cache
- Modular, maintainable code structure
- Robust error handling and graceful BCE date support
- Clean interface and extensible design

## vgj_ac_rs.ipynb

# Transit of sun through the seasonal nakṣatra cycle in the Vṛddha-Gārgīya Jyotiṣa 
## [Indian Journal of History of Science, 56.3(2021)](https://insa.nic.in//writereaddata/UpLoadedFiles/IJHS/1.pdf)
### Supplementary Material

