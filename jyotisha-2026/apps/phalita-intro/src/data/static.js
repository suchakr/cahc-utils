export const RASIS = [
  { id:1,  iast:"Meṣa",    en:"Aries",       lordId:"MA", element:"Agni",   quality:"Cara"    },
  { id:2,  iast:"Vṛṣabha", en:"Taurus",      lordId:"SK", element:"Pṛthvī", quality:"Sthira"  },
  { id:3,  iast:"Mithuna", en:"Gemini",      lordId:"BU", element:"Vāyu",   quality:"Dvandva" },
  { id:4,  iast:"Karkaṭa", en:"Cancer",      lordId:"CA", element:"Jala",   quality:"Cara"    },
  { id:5,  iast:"Siṃha",   en:"Leo",         lordId:"SU", element:"Agni",   quality:"Sthira"  },
  { id:6,  iast:"Kanyā",   en:"Virgo",       lordId:"BU", element:"Pṛthvī", quality:"Dvandva" },
  { id:7,  iast:"Tulā",    en:"Libra",       lordId:"SK", element:"Vāyu",   quality:"Cara"    },
  { id:8,  iast:"Vṛścika", en:"Scorpio",     lordId:"MA", element:"Jala",   quality:"Sthira"  },
  { id:9,  iast:"Dhanus",  en:"Sagittarius", lordId:"GU", element:"Agni",   quality:"Dvandva" },
  { id:10, iast:"Makara",  en:"Capricorn",   lordId:"SA", element:"Pṛthvī", quality:"Cara"    },
  { id:11, iast:"Kumbha",  en:"Aquarius",    lordId:"SA", element:"Vāyu",   quality:"Sthira"  },
  { id:12, iast:"Mīna",    en:"Pisces",      lordId:"GU", element:"Jala",   quality:"Dvandva" },
];

export const GRAHAS = {
  SU: { iast:"Sūrya",   sa:"सूर्य",  en:"Sun",     ucca:1,  uccaDeg:"10°", nīca:7,  nīcaDeg:"10°", mūlatrikoṇa:5,  svakṣetra:[5],     color:"#e8a020" },
  CA: { iast:"Candra",  sa:"चन्द्र", en:"Moon",    ucca:2,  uccaDeg:"3°",  nīca:8,  nīcaDeg:"3°",  mūlatrikoṇa:2,  svakṣetra:[4],     color:"#90b8d8" },
  MA: { iast:"Maṅgala", sa:"मङ्गल", en:"Mars",    ucca:10, uccaDeg:"28°", nīca:4,  nīcaDeg:"28°", mūlatrikoṇa:1,  svakṣetra:[1,8],   color:"#d04030" },
  BU: { iast:"Budha",   sa:"बुध",   en:"Mercury", ucca:6,  uccaDeg:"15°", nīca:12, nīcaDeg:"15°", mūlatrikoṇa:6,  svakṣetra:[3,6],   color:"#40a060" },
  GU: { iast:"Guru",    sa:"गुरु",   en:"Jupiter", ucca:4,  uccaDeg:"5°",  nīca:10, nīcaDeg:"5°",  mūlatrikoṇa:9,  svakṣetra:[9,12],  color:"#d8b030" },
  SK: { iast:"Śukra",   sa:"शुक्र",  en:"Venus",   ucca:12, uccaDeg:"27°", nīca:6,  nīcaDeg:"27°", mūlatrikoṇa:7,  svakṣetra:[2,7],   color:"#d070b0" },
  SA: { iast:"Śani",    sa:"शनि",   en:"Saturn",  ucca:7,  uccaDeg:"20°", nīca:1,  nīcaDeg:"20°", mūlatrikoṇa:11, svakṣetra:[10,11], color:"#7878a8" },
  RA: { iast:"Rāhu",    sa:"राहु",   en:"Rahu",    ucca:3,  uccaDeg:"—",   nīca:9,  nīcaDeg:"—",   mūlatrikoṇa:6,  svakṣetra:[],      color:"#586068" },
  KE: { iast:"Ketu",    sa:"केतु",   en:"Ketu",    ucca:9,  uccaDeg:"—",   nīca:3,  nīcaDeg:"—",   mūlatrikoṇa:12, svakṣetra:[],      color:"#786858" },
};

export const GRAHA_SIGNIFICATIONS = {
  SU: {
    transit:"1 month",
    nature:"Mild Krūra",
    guṇa:"Sāttvika",
    role:"Royal",
    people:["Father"],
    qualities:["ego", "dignity", "charm", "brilliance", "dominance"],
    strength:"Strong in most signs",
    friends:["Candra", "Maṅgala", "Guru"],
    enemies:["Śani", "Śukra", "Rāhu"],
    neutral:["Budha", "Ketu"],
  },
  CA: {
    transit:"2 days",
    nature:"Saumya",
    guṇa:"Sāttvika",
    role:"Royal",
    people:["Mother"],
    qualities:["compassion", "food", "water", "emotions"],
    strength:"Strongest around Pūrṇimā; weakest around Amāvasyā.",
    friends:["Sūrya", "Budha"],
    enemies:[],
    neutral:["The rest"],
  },
  MA: {
    transit:"45 days",
    nature:"Krūra",
    guṇa:"Tāmasika/Rājasika",
    role:"Army Chief",
    people:["Younger siblings"],
    qualities:["courage", "aggression", "parākrama"],
    strength:"Strong in most signs",
    friends:["Sūrya", "Candra", "Guru"],
    enemies:["Budha"],
    neutral:["Śukra", "Śani", "Rāhu", "Ketu"],
  },
  BU: {
    transit:"~1 month",
    nature:"Saumya",
    guṇa:"Rājasika",
    role:"Prince",
    people:["Maternal relatives", "friends"],
    qualities:["learning", "ability", "mathematics", "speech", "śāstra", "medicine"],
    strength:"Mimics company: with krūras he acts krūra; with saumyas he acts saumya.",
    friends:["Sūrya", "Śukra"],
    enemies:["Candra", "Ketu"],
    neutral:["Maṅgala", "Guru", "Śani", "Rāhu"],
  },
  GU: {
    transit:"12 months",
    nature:"Saumya",
    guṇa:"Sāttvika",
    role:"Rāja Guru",
    people:["teachers", "children", "husband"],
    qualities:["wisdom", "religion", "wealth", "peace", "expansion"],
    strength:"Strong in most signs",
    friends:["Sūrya", "Candra", "Maṅgala"],
    enemies:["Budha", "Śukra", "Rāhu"],
    neutral:["Śani", "Ketu"],
  },
  SK: {
    transit:"~1 month",
    nature:"Saumya",
    guṇa:"Rājasika",
    role:"Arts/Dance",
    people:["spouse", "teachers"],
    qualities:["pleasures", "luxuries", "vehicles"],
    strength:"Strong in most signs",
    friends:["Budha", "Śani"],
    enemies:["Sūrya", "Candra"],
    neutral:["Maṅgala", "Guru", "Ketu"],
  },
  SA: {
    transit:"30 months",
    nature:"Krūra",
    guṇa:"Tāmasika",
    role:"Servant",
    people:["elder siblings"],
    qualities:["grief", "tradition", "delays", "ailments", "hard work", "longevity", "karmakāraka"],
    strength:"Strong in most signs",
    friends:["Budha", "Śukra", "Rāhu"],
    enemies:["Sūrya", "Candra", "Maṅgala"],
    neutral:["Guru", "Ketu"],
  },
  RA: {
    transit:"18 months",
    nature:"Krūra",
    guṇa:"Tāmasika",
    role:"Thief",
    people:[],
    qualities:["cunning", "accidents", "greed", "foreign", "poisons", "electronics", "non-traditional", "out-of-box"],
    strength:"Chāyā graha; gives results of sign lord.",
    friends:["Śukra", "Śani"],
    enemies:["Sūrya", "Candra", "Maṅgala"],
    neutral:["Budha", "Guru", "Ketu"],
  },
  KE: {
    transit:"18 months",
    nature:"Krūra",
    guṇa:"Sāttvika",
    role:"Mystic",
    people:[],
    qualities:["occult", "blind belief", "detachment", "mathematics", "computers"],
    strength:"Chāyā graha; gives results of sign lord.",
    friends:["Sūrya", "Maṅgala"],
    enemies:["Śukra", "Śani"],
    neutral:["Budha", "Guru", "Candra", "Rāhu"],
  },
};

export const BHAVA_TYPES = {
  1:["Kendra","Trikona"], 2:["Māraka","Dhana"],   3:["Upacaya"],
  4:["Kendra"],           5:["Trikona"],           6:["Dusthāna","Upacaya"],
  7:["Kendra","Māraka"],  8:["Dusthāna"],          9:["Trikona","Dharma"],
  10:["Kendra","Upacaya"],11:["Upacaya","Lābha"],  12:["Dusthāna","Vyaya"],
};

export const BHAVA_THEMES = {
  1: { iast:"Tanu",    en:"Self, Body, Personality",       kāraka:"SU", significations:["physical body", "complexion", "appearance", "head", "intelligence", "strength", "energy", "fame", "success", "nature of birth", "caste"] },
  2: { iast:"Dhana",   en:"Wealth, Speech, Family",        kāraka:"GU", significations:["wealth", "assets", "family", "speech", "eyes", "mouth", "face", "voice", "food"] },
  3: { iast:"Sahaja",  en:"Siblings, Courage, Effort",     kāraka:"MA", significations:["younger co-borns", "confidants", "courage", "mental strength", "communication", "creativity", "throat", "ears", "arms", "travels"] },
  4: { iast:"Sukha",   en:"Home, Mother, Happiness",       kāraka:"CA", significations:["mother", "vehicles", "house", "lands", "immovable property", "motherland", "childhood", "education", "relatives", "happiness", "comforts", "peace", "state of mind", "heart"] },
  5: { iast:"Putra",   en:"Children, Intellect, Merit",    kāraka:"GU", significations:["children", "pūrvapuṇya", "intelligence", "knowledge", "scholarship", "devotion", "mantras", "stomach", "digestion", "authority", "fame", "love", "judgment", "speculation"] },
  6: { iast:"Śatru",   en:"Enemies, Disease, Obstacles",   kāraka:"MA", significations:["enemies", "service", "servants", "relatives", "mental tension", "injuries", "health", "diseases", "agriculture", "accidents", "mental affliction", "maternal uncle", "hips"] },
  7: { iast:"Kalatra", en:"Spouse, Partnerships",          kāraka:"SK", significations:["marriage", "marital life", "life partner", "sex", "passion", "long journeys", "partners", "business", "death", "body below the navel"] },
  8: { iast:"Māraṇa",  en:"Longevity, Secrets, Change",    kāraka:"SA", significations:["longevity", "debts", "disease", "ill-fame", "inheritance", "loss of friends", "occult studies", "evils", "gifts", "unearned wealth", "windfall", "disgrace", "secrets", "genitals"] },
  9: { iast:"Dharma",  en:"Fortune, Guru, Higher Wisdom",  kāraka:"GU", significations:["father", "teacher", "boss", "fortune", "religiousness", "spirituality", "God", "higher studies", "foreign fortune", "foreign trips", "dīkṣā", "past life", "grandchildren", "principles", "dharma", "intuition", "compassion", "leadership", "charity", "thighs"] },
  10:{ iast:"Karma",   en:"Career, Authority, Action",     kāraka:"SU", significations:["growth", "profession", "career", "karma", "conduct in society", "fame", "honors", "awards", "self-respect", "dignity", "knees"] },
  11:{ iast:"Lābha",   en:"Gains, Desires, Elder Sibling", kāraka:"GU", significations:["elder co-borns", "income", "gains", "realization of hopes", "friends", "ankles"] },
  12:{ iast:"Vyaya",   en:"Loss, Liberation, Expenditure", kāraka:"SA", significations:["losses", "expenditure", "punishment", "imprisonment", "hospitalization", "pleasures in bed", "misfortune", "bad habits", "sleep", "meditation", "donation", "secret enemies", "heaven", "birthplace", "mokṣa"] },
};

export const VIMSHOTTARI = [
  {g:"KE",y:7},{g:"SK",y:20},{g:"SU",y:6},{g:"CA",y:10},{g:"MA",y:7},
  {g:"RA",y:18},{g:"GU",y:16},{g:"SA",y:19},{g:"BU",y:17},
];

export const LIFE_AREAS = {
  career:  { iast:"Karma",  en:"Career",  bhāvas:[10,6,2], icon:"⚖" },
  health:  { iast:"Ārogya", en:"Health",  bhāvas:[1,6,8],  icon:"✦" },
  wealth:  { iast:"Dhana",  en:"Wealth",  bhāvas:[2,11,5], icon:"◈" },
  marriage:{ iast:"Vivāha", en:"Marriage",bhāvas:[7,2,8],  icon:"◎" },
};

export const SI_POS = {
  12:[0,0], 1:[0,1], 2:[0,2],  3:[0,3],
  11:[1,0],                     4:[1,3],
  10:[2,0],                     5:[2,3],
   9:[3,0], 8:[3,1], 7:[3,2],  6:[3,3],
};

// ═══════════════════════════════════════════════════════════════════════════════
// BIRTH EVENTS
// ═══════════════════════════════════════════════════════════════════════════════
