# Sanskrit Verb Generation - Interactive Animation

Short summary

- A self-contained interactive HTML animation that demonstrates Paninian verb derivation (धातु -> तिङन्त). Great for classroom demos and quick exploration of verb formation rules.

Quick start

1. Open `dhaatu-animation.html` in a browser (no server required).
2. Choose a धातु and a लकार to begin the step-by-step derivation.
3. Use the Sutra Reference tab to see which सूत्र apply at each step.

## पाणिनीयधातुपाठस्य सम्प्रयोगबोधनम्

This repository contains an interactive web application that demonstrates the step-by-step generation of Sanskrit verbs (तिङ्न्त forms) using Paninian grammar principles.

## 🎬 [Try the Animation](./dhaatu-animation.html)

## Features

- **Interactive Animation**: Step-by-step visualization of Sanskrit verb generation
- **Complete Grammar Coverage**: All 10 gaṇas with proper vikaraṇa pratyayas
- **Comprehensive Lakara Support**: 8 lakaras with proper classification
- **3x3 Conjugation Grid**: Display all 9 purush-vacana combinations
- **Sutra References**: Integrated reference table with 21 key sutras
- **Mobile Responsive**: Optimized for all device sizes
- **Educational**: Perfect for students of Sanskrit grammar

## Application Overview

The animation demonstrates the derivation process from dhātu to final tiṅanta form through 6 grammatical steps:

1. **Dhātu Selection** - Choose from 11 representative dhātus
2. **Lakāra Selection** - Pick tense/mood (laṭ, luṭ, loṭ, etc.)
3. **Gaṇa & Vikaraṇa** - Automatic gaṇa identification and vikaraṇa assignment
4. **Pada Determination** - Parasmaipada/Ātmanepada classification
5. **Iṭ-ness Resolution** - सेट्/अनिट् determination with sutra references
6. **Final Derivation** - Complete 3x3 grid of all purush-vacana forms

## Process Flow

```text
उपदेश-धातुः → अनुबन्ध-लोपः → लौकिक-धातुः → विकरण-प्रत्ययः → तिङ्-प्रत्ययः → तिङन्तम्
```

## Grammatical Framework

### Gaṇa System

| गणः | विकरण | धातु-उदाहरणम् | प्रत्ययः |
|-----|--------|-------------|---------|
| भ्वादिः | शप् (अ) | भू | कर्तरि शप् (३.१.६८) |
| अदादिः | शप्-लुक् | अद् | अदिप्रभृतिभ्यः शपः (२.४.७२) |
| जुहोत्यादिः | शप्-श्लुः | हु | जुहोत्यादिभ्यः श्लुः (२.४.७५) |
| दिवादिः | श्यन् (य) | दिव् | दिवादिभ्यः श्यन् (३.१.६९) |
| स्वादिः | श्नु (नु) | सु | स्वादिभ्यः श्नुः (३.१.७३) |
| तुदादिः | श (अ) | तुद् | तुदादिभ्यः शः (३.१.७७) |
| रुधादिः | श्नम् (न) | रुध् | रुधादिभ्यः श्नम् (३.१.७८) |
| तनादिः | उ | तन् | तनादिकृञ्भ्य उः (३.१.७९) |
| क्र्यादिः | श्ना (ना) | क्री | क्र्यादिभ्यः श्ना (३.१.८१) |
| चुरादिः | णिच् (इ) | चुर् | चूर्णचुरादिभ्यो णिच् (३.१.२५) |

### Lakāra Classification

**सार्वधातुक-लकाराः** (Present System):

- **लट्** (वर्तमान): भवति, भवन्ति
- **लङ्** (भूतकाल): अभवत्, अभवन्
- **लोट्** (आज्ञार्थ): भवतु, भवन्तु
- **विधिलिङ्** (विध्यर्थ): भवेत्, भवेयुः

**आर्धधातुक-लकाराः** (Future/Perfect System):

- **लुट्** (भविष्यत्): भविता, भविष्यन्ति
- **लृट्** (भविष्यत्): भविष्यति, भविष्यन्ति
- **लुङ्** (भूतकाल): अभूत्, अभूवन्
- **लृङ्** (कृदन्त): अभविष्यत्, अभविष्यन्

## Technical Implementation

### Architecture

```text
┌─────────────────────────┐
│    dhaatu-animation.html │
├─────────────────────────┤
│ • HTML Structure        │
│ • CSS Animations        │
│ • JavaScript Logic      │
│ • Embedded Data         │
└─────────────────────────┘
```

### Key Components

1. **Data Structure**: Complete dhātu derivation information
2. **Animation Engine**: Step-by-step visualization
3. **Grid System**: 3x3 purush-vacana display
4. **Sutra References**: Integrated grammar rules
5. **Responsive Design**: Mobile-optimized interface

## Key Concepts

### पदसंज्ञाः (Grammatical Terms)

- **तिङन्तम्** = धातुः + विकरणप्रत्ययः + तिङ्प्रत्ययः
- **सार्वधातुकप्रत्ययाः** – शप्, श्यन्, श्ना (Present system)
- **आर्धधातुकप्रत्ययाः** – लुट्-तास्, स्य, सिच् (Future/Perfect system)

### इत्संज्ञाः (Anubandha Markers)

- अनुनासिकस्वरः = इत् (Nasal vowels are deleted)
- हलन्त्यम् = इत् (Final consonants are deleted)  
- आदिर्जिटुडवः = इत् (Initial ji, ṭu, ḍu are deleted)

### पदनिर्णयः (Pada Determination)

- **अनुदात्त-डितः** = आत्मनेपदम् (Anudātta or ḍit → Ātmanepada)
- **उदात्तेतः** = परस्मैपदम् (Udātta → Parasmaipada)
- **सस्वरितेतः** = उभयपदम् (Svarita → Ubhayapada)

### सेट्-अनिट्-वेट् Classification

- **सेट्**: उदात्त धातुs (Most dhātus take iḍ-āgama)
- **अनिट्**: अनुदात्त धातुs (Prohibition of iḍ-āgama)
- **वेट्**: ऊदित् धातुs (Optional iḍ-āgama)

## Educational Value

This application serves as:

- **Learning Tool**: Visual demonstration of complex grammar rules
- **Reference**: Quick lookup for dhātu properties and derivations
- **Practice Aid**: Interactive exploration of verb generation
- **Teaching Resource**: Step-by-step breakdown for instructors

## Files in Repository

- **dhaatu-animation.html** - Main interactive application
- **README.md** - This documentation
- **_redirects** - Netlify routing configuration
- **gemini/** - Alternative implementations and experiments

## Usage

1. Open `dhaatu-animation.html` in any modern web browser
2. Select a dhātu from the dropdown (11 options available)
3. Choose a lakāra (8 options with proper classification)
4. Click "प्रारम्भः" to start the animation
5. Watch the step-by-step derivation process
6. View the final 3x3 conjugation grid
7. Use the Sutra Reference tab for grammar details

## Browser Compatibility

- Chrome/Edge: Full support
- Firefox: Full support  
- Safari: Full support
- Mobile browsers: Responsive design optimized

## Development

The application is built as a single self-contained HTML file with:

- **No external dependencies**
- **Embedded CSS and JavaScript**
- **Complete grammar data**
- **Progressive enhancement**

---

*For questions about Sanskrit grammar or technical implementation, please refer to the integrated sutra references or create an issue in the repository.*
