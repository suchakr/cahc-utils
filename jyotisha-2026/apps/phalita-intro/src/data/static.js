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
  SU: { iast:"Sūrya",   en:"Sun",     ucca:1,  uccaDeg:"10°", nīca:7,  nīcaDeg:"10°", svakṣetra:[5],     color:"#e8a020" },
  CA: { iast:"Candra",  en:"Moon",    ucca:2,  uccaDeg:"3°",  nīca:8,  nīcaDeg:"3°",  svakṣetra:[4],     color:"#90b8d8" },
  MA: { iast:"Maṅgala", en:"Mars",    ucca:10, uccaDeg:"28°", nīca:4,  nīcaDeg:"28°", svakṣetra:[1,8],   color:"#d04030" },
  BU: { iast:"Budha",   en:"Mercury", ucca:6,  uccaDeg:"15°", nīca:12, nīcaDeg:"15°", svakṣetra:[3,6],   color:"#40a060" },
  GU: { iast:"Guru",    en:"Jupiter", ucca:4,  uccaDeg:"5°",  nīca:10, nīcaDeg:"5°",  svakṣetra:[9,12],  color:"#d8b030" },
  SK: { iast:"Śukra",   en:"Venus",   ucca:12, uccaDeg:"27°", nīca:6,  nīcaDeg:"27°", svakṣetra:[2,7],   color:"#d070b0" },
  SA: { iast:"Śani",    en:"Saturn",  ucca:7,  uccaDeg:"20°", nīca:1,  nīcaDeg:"20°", svakṣetra:[10,11], color:"#7878a8" },
  RA: { iast:"Rāhu",    en:"Rahu",    ucca:3,  uccaDeg:"—",   nīca:9,  nīcaDeg:"—",   svakṣetra:[],      color:"#586068" },
  KE: { iast:"Ketu",    en:"Ketu",    ucca:9,  uccaDeg:"—",   nīca:3,  nīcaDeg:"—",   svakṣetra:[],      color:"#786858" },
};

export const BHAVA_TYPES = {
  1:["Kendra","Trikona"], 2:["Māraka","Dhana"],   3:["Upacaya"],
  4:["Kendra"],           5:["Trikona"],           6:["Dusthāna","Upacaya"],
  7:["Kendra","Māraka"],  8:["Dusthāna"],          9:["Trikona","Dharma"],
  10:["Kendra","Upacaya"],11:["Upacaya","Lābha"],  12:["Dusthāna","Vyaya"],
};

export const BHAVA_THEMES = {
  1: { iast:"Tanu",    en:"Self, Body, Personality",       kāraka:"SU" },
  2: { iast:"Dhana",   en:"Wealth, Speech, Family",        kāraka:"GU" },
  3: { iast:"Sahaja",  en:"Siblings, Courage, Effort",     kāraka:"MA" },
  4: { iast:"Sukha",   en:"Home, Mother, Happiness",       kāraka:"CA" },
  5: { iast:"Putra",   en:"Children, Intellect, Merit",    kāraka:"GU" },
  6: { iast:"Śatru",   en:"Enemies, Disease, Obstacles",   kāraka:"MA" },
  7: { iast:"Kalatra", en:"Spouse, Partnerships",          kāraka:"SK" },
  8: { iast:"Māraṇa",  en:"Longevity, Secrets, Change",    kāraka:"SA" },
  9: { iast:"Dharma",  en:"Fortune, Guru, Higher Wisdom",  kāraka:"GU" },
  10:{ iast:"Karma",   en:"Career, Authority, Action",     kāraka:"SU" },
  11:{ iast:"Lābha",   en:"Gains, Desires, Elder Sibling", kāraka:"GU" },
  12:{ iast:"Vyaya",   en:"Loss, Liberation, Expenditure", kāraka:"SA" },
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
