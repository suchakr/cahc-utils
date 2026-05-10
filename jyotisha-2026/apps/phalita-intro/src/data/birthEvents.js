export const BIRTH_EVENTS = {
  karkata: {
    id:"karkata", label:"The Scholar", date:"16 November 1905",
    lagna:4, lagnaName:"Karkaṭa",
    pos:{ GU:4, MA:1, SU:7, SK:8, SA:10, CA:11, BU:6, RA:3, KE:9 },
    description:"A learned man of letters, born at dawn in a river-valley town.",
    notes:"Guru ucca in Bhāva 1; Maṅgala svakṣetra in Bhāva 10; Sūrya nīca in Bhāva 4; Budha ucca in Bhāva 3",
    bhavaTexts: {
      1: {
        header:"Bhāva 1 — The Lagna itself",
        bullets:[
          "Bhāva 1 is always the lagna rāśi — the Ascendant. For this Jātaka, Karkaṭa (Cancer) rises at birth.",
          "Candra becomes the lagneśa, the governing lord of the entire chart — its placement will colour every reading.",
          "Guru (Jupiter) is exalted (ucca) in Karkaṭa and occupies this very first house — an exceptionally auspicious opening.",
        ]
      },
      2: {
        header:"Bhāva 2 — Dhana · Wealth and Speech",
        bullets:[
          "Moving one rāśi clockwise from Karkaṭa: Siṃha (Leo) becomes Bhāva 2.",
          "Sūrya, lord of Siṃha, becomes the functional Dhana-bhāveśa — the manager of wealth for this native.",
          "We will find Sūrya placed in Tulā (Bhāva 4), its sign of debilitation — a detail that matters greatly.",
        ]
      },
      3: {
        header:"Bhāva 3 — Sahaja · Siblings and Courage",
        bullets:[
          "Formula in action: (rāśiId − lagnaId + 12) mod 12 + 1 = (6 − 4 + 12) mod 12 + 1 = 3.",
          "Kanyā (Virgo) becomes Bhāva 3. Its lord Budha is the Sahaja-bhāveśa.",
          "Budha is exalted (ucca) in Kanyā itself — the lord of courage sits in maximum strength in its own house.",
        ]
      },
      4: {
        header:"Bhāva 4 — Sukha · Home and Mother",
        bullets:[
          "Tulā (Libra) becomes Bhāva 4, the house of home, mother, and inner happiness.",
          "Śukra, lord of Tulā, becomes the Sukha-bhāveśa.",
          "Critically: Sūrya (lord of Bhāva 2) is placed here in Tulā — its sign of debilitation (nīca). A nīca graha in Bhāva 4 troubles domestic peace.",
        ]
      },
      5: {
        header:"Bhāva 5 — Putra · Children and Intellect",
        bullets:[
          "Vṛścika (Scorpio) becomes Bhāva 5 — a Trikona, house of merit and past-life credit.",
          "Maṅgala, lord of Vṛścika, becomes the Putra-bhāveśa. Maṅgala is in svakṣetra (Meṣa, Bhāva 10).",
          "A strong 5th-lord in the 10th creates a productive link between intellect and career.",
        ]
      },
      6: {
        header:"Bhāva 6 — Śatru · Enemies and Disease",
        bullets:[
          "Dhanus (Sagittarius) becomes Bhāva 6 — a Dusthāna, house of obstacles and effort.",
          "Guru, lord of Dhanus, becomes the Śatru-bhāveśa. Guru is ucca in Bhāva 1 — auspicious.",
          "An exalted 6th-lord is a classical indicator of victory over enemies and recovery from illness.",
        ]
      },
      7: {
        header:"Bhāva 7 — Kalatra · Spouse and Partnerships",
        bullets:[
          "Makara (Capricorn) becomes Bhāva 7 — a Kendra, the house of marriage and alliances.",
          "Śani, lord of Makara, becomes the Kalatra-bhāveśa. Śani is in svakṣetra here — stable and reliable.",
          "Śani in svakṣetra in Bhāva 10 (the Karma house) gives this native's partnerships a disciplined, work-oriented character.",
        ]
      },
      8: {
        header:"Bhāva 8 — Māraṇa · Longevity and Secrets",
        bullets:[
          "Kumbha (Aquarius) becomes Bhāva 8 — a Dusthāna governing longevity, hidden knowledge, and transformation.",
          "Śani also lords Kumbha, making it the Māraṇa-bhāveśa as well — a double lordship.",
          "Candra is placed in Kumbha (Bhāva 8) — the lagneśa in a Dusthāna introduces emotional complexity.",
        ]
      },
      9: {
        header:"Bhāva 9 — Dharma · Fortune and Guru",
        bullets:[
          "Mīna (Pisces) becomes Bhāva 9 — a Trikona, the house of fortune, dharma, and the teacher.",
          "Guru, lord of Mīna, becomes the Dharma-bhāveśa. A strong Guru as 9th lord augments spiritual fortune.",
          "With Guru also ucca in Bhāva 1, this native carries a double Guru signature — knowledge and wisdom are central.",
        ]
      },
      10: {
        header:"Bhāva 10 — Karma · Career and Authority",
        bullets:[
          "Meṣa (Aries) becomes Bhāva 10 — a Kendra, the most prominent house of action and public life.",
          "Maṅgala, lord of Meṣa, becomes the Karma-bhāveśa — and is placed in Meṣa itself (svakṣetra).",
          "A svakṣetra lord in the 10th is a powerful career indicator — initiative, energy, and authority in the public sphere.",
        ]
      },
      11: {
        header:"Bhāva 11 — Lābha · Gains and Desires",
        bullets:[
          "Vṛṣabha (Taurus) becomes Bhāva 11 — the house of gains, elder siblings, and fulfillment of desires.",
          "Śukra, lord of Vṛṣabha, becomes the Lābha-bhāveśa. Śukra is placed in Vṛścika (Bhāva 5).",
          "A 11th lord in the 5th connects gains to intellectual effort and creative merit — learning bears fruit.",
        ]
      },
      12: {
        header:"Bhāva 12 — Vyaya · Loss and Liberation",
        bullets:[
          "Mithuna (Gemini) becomes Bhāva 12 — a Dusthāna governing expenditure, foreign lands, and mokṣa.",
          "Budha, lord of Mithuna, becomes the Vyaya-bhāveśa. Budha is ucca in Kanyā (Bhāva 3).",
          "Rāhu occupies Bhāva 12 — a classic placement associated with foreign connections and spiritual seeking.",
        ]
      },
    }, // closes karkata bhavaTexts
  }, // closes karkata
  tula: {
    id:"tula", label:"The Musician", date:"7 April 1920",
    lagna:7, lagnaName:"Tulā",
    pos:{ SK:12, SU:7, CA:2, MA:10, BU:8, GU:1, SA:11, RA:6, KE:12 },
    description:"A gifted performer, born at dusk in a coastal city.",
    notes:"Śukra ucca (Lagneśa) in Bhāva 6; Sūrya nīca in Bhāva 1; Maṅgala ucca in Bhāva 4; Śani svakṣetra in Bhāva 5",
    bhavaTexts: {
      1: {
        header:"Bhāva 1 — The Lagna itself",
        bullets:[
          "Tulā (Libra) rises — Śukra becomes the lagneśa, the chart's governing lord.",
          "Sūrya, debilitated (nīca) in Tulā, occupies the very first house — a defining tension in the native's self-expression.",
          "A debilitated sun in one's own lagna creates an internal complexity: vitality and identity carry a subtle strain.",
        ]
      },
      2: {
        header:"Bhāva 2 — Dhana · Wealth and Speech",
        bullets:[
          "Vṛścika (Scorpio) becomes Bhāva 2. Its lord Maṅgala becomes the Dhana-bhāveśa.",
          "Maṅgala is placed in Makara — its sign of exaltation (ucca). A strong functional wealth-lord is a significant asset.",
          "Candra also sits in Vṛṣabha, which is Bhāva 8 from Tulā lagna — the emotional world is complex and deep.",
        ]
      },
      3: {
        header:"Bhāva 3 — Sahaja · Siblings and Courage",
        bullets:[
          "Dhanus (Sagittarius) becomes Bhāva 3. Guru becomes the Sahaja-bhāveśa.",
          "Guru is placed in Meṣa (Bhāva 7 from Tulā), a Kendra — angular house lending philosophical depth.",
          "For this musician, courage and initiative carry a expansive, dharmic quality — initiative rooted in wisdom.",
        ]
      },
      4: {
        header:"Bhāva 4 — Sukha · Home and Mother",
        bullets:[
          "Makara (Capricorn) becomes Bhāva 4. Its lord Śani becomes the Sukha-bhāveśa.",
          "Maṅgala — lord of Bhāva 2 — is placed in Makara, its exaltation sign (ucca). An exalted planet in the 4th brings material stability.",
          "For this native, the home is a place of real strength and comfort — a grounding anchor amid the chart's complexities.",
        ]
      },
      5: {
        header:"Bhāva 5 — Putra · Children and Intellect",
        bullets:[
          "Kumbha (Aquarius) becomes Bhāva 5 — a Trikona, house of past merit and creative intelligence.",
          "Śani, lord of Kumbha, becomes the Putra-bhāveśa. Śani is in svakṣetra in Bhāva 5 itself.",
          "A svakṣetra planet in a Trikona is highly auspicious — discipline and structure elevate the native's intellect.",
        ]
      },
      6: {
        header:"Bhāva 6 — Śatru · Enemies and Disease",
        bullets:[
          "Mīna (Pisces) becomes Bhāva 6 — a Dusthāna of obstacles and daily struggle.",
          "Guru, lord of Mīna, becomes the Śatru-bhāveśa. Guru is placed in Meṣa (Bhāva 7).",
          "Rāhu also occupies Bhāva 6 — intensifying the area of competition and requiring conscious effort to overcome.",
        ]
      },
      7: {
        header:"Bhāva 7 — Kalatra · Spouse and Partnerships",
        bullets:[
          "Meṣa (Aries) becomes Bhāva 7 — a Kendra, the house of partnerships and marriage.",
          "Maṅgala, lord of Meṣa, becomes the Kalatra-bhāveśa — but Maṅgala is also the Dhana-bhāveśa (Bhāva 2 lord).",
          "Guru is placed in Meṣa — an expansive, philosophical influence on the native's partnerships and collaborations.",
        ]
      },
      8: {
        header:"Bhāva 8 — Māraṇa · Longevity and Secrets",
        bullets:[
          "Vṛṣabha (Taurus) becomes Bhāva 8 — Dusthāna of longevity, hidden matters, and sudden change.",
          "Śukra, lord of Vṛṣabha, becomes the Māraṇa-bhāveśa — and Śukra is the lagneśa, placed in Mīna (ucca, Bhāva 6).",
          "An exalted lagneśa as 8th lord creates a nuanced paradox: spiritual depth alongside the dusthāna's transformative pressures.",
        ]
      },
      9: {
        header:"Bhāva 9 — Dharma · Fortune and Guru",
        bullets:[
          "Mithuna (Gemini) becomes Bhāva 9 — a Trikona, house of fortune, higher wisdom, and the father.",
          "Budha, lord of Mithuna, becomes the Dharma-bhāveśa. Budha is placed in Vṛścika (Bhāva 8).",
          "A 9th lord in the 8th brings fortune through research, hidden knowledge, and esoteric disciplines — fitting for a musical temperament.",
        ]
      },
      10: {
        header:"Bhāva 10 — Karma · Career and Authority",
        bullets:[
          "Karkaṭa (Cancer) becomes Bhāva 10 — a Kendra, the apex of the chart representing career and public standing.",
          "Candra, lord of Karkaṭa, becomes the Karma-bhāveśa. Candra is placed in Vṛṣabha (Bhāva 8).",
          "A 10th lord in the 8th can indicate a career with hidden or behind-the-scenes dimensions — the performing artist works in a liminal space.",
        ]
      },
      11: {
        header:"Bhāva 11 — Lābha · Gains and Desires",
        bullets:[
          "Siṃha (Leo) becomes Bhāva 11 — the house of gains, networks, and fulfillment of ambitions.",
          "Sūrya, lord of Siṃha, becomes the Lābha-bhāveśa. Sūrya is nīca in Tulā (Bhāva 1).",
          "A debilitated 11th lord in the lagna means gains come with personal cost — the native pays with effort and identity.",
        ]
      },
      12: {
        header:"Bhāva 12 — Vyaya · Loss and Liberation",
        bullets:[
          "Kanyā (Virgo) becomes Bhāva 12 — Dusthāna of expenditure, distant lands, and spiritual liberation.",
          "Budha, lord of Kanyā, also lords Bhāva 9 — the same planet governs both fortune and loss.",
          "Ketu occupies Bhāva 12 alongside Śukra (ucca) — a striking conjunction: the lagneśa exalted in the house of liberation.",
        ]
      },
    }, // closes bhavaTexts
  }, // closes tula
}; // closes BIRTH_EVENTS

// ═══════════════════════════════════════════════════════════════════════════════
// HELPERS
// ═══════════════════════════════════════════════════════════════════════════════
