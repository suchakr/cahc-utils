/**
 * Nakshatra constellation data parser and validator
 * Combines constellationship.fab and n83 CSV data
 */

// Constellation data from constellationship.fab
const CONSTELLATION_DATA = `
N01  3 9884 9153   9153 8903  8903 9884
N02  2 12719 13061   13061 13209
N03   7 17499 17608 17608 17847 17847 17851 17851 17702 17702 17573 17573 17531 17531 17499
N04  5 21421 20894   20894 20205   20205 20455   20455 20889   20889 21421
N05  3 25336 26207   26207 27989   27989 25336
N06  1 31681 31681
N07  1 37826 36850
N08  1 42911 42911
N09 7 42402 42799    43109 42313    42313 42402   43813 47431   43109 43234    43234 42799    43234 43813
N10  5 50583 50335   50335 48455   48455 47908    49669 49583    49583 50583
N11  1 54879 54872
N12  1 57632 57565
N13   5 61359 60965   61359 59803   61359 59316    61359 59199    61359 60425
N14  1 65474 65474
N15  1 69673 69673
N16  1 72622 72622
N17  5 80112 78933   80112 78821    80112 78401   80112 78265  80112 78933
N18  1 80763 80763
N19  3 86228  87073    87073 86670    86670 85927
N20  4 88635 90185    90185 89931    89931 90496    90496 88635
N21  4 92041 93506   93506 93864   93864 92855   92855 92041
N22  3 97649 97278     97278 98036    98036 97649
N23  5 101421 102281   102281 102532   102532 101958   101958 101769   101769 101421
N24  3 110395 111710    111710 112961     112961 110395
N25  1 113881 113963
N26  1 677 1067
N27  1 9487 9487
N28  3 91971 91262  91262 91919   91919 91971
`;

// Star coordinate data (will be loaded from CSV)
const STAR_DATA = {
  // N01-Ash - Aśvini
  8903: { lon: 33.97, lat: 8.49, nid: 'N01-Ash', tag: 'rep', naks: 'अश्विनी', enaks: 'Aśvini' },
  9884: { lon: 37.66, lat: 9.97, nid: 'N01-Ash', tag: 'other', naks: 'अश्विनी', enaks: 'Aśvini' },
  9153: { lon: 33.18, lat: 7.16, nid: 'N01-Ash', tag: 'other', naks: 'अश्विनी', enaks: 'Aśvini' },
  8832: { lon: 33.18, lat: 7.16, nid: 'N01-Ash', tag: 'other', naks: 'अश्विनी', enaks: 'Aśvini' },
  
  // N02-Bha - Bharaṇī
  13209: { lon: 48.20, lat: 10.45, nid: 'N02-Bha', tag: 'rep', naks: 'भरणी', enaks: 'Bharaṇī' },
  13061: { lon: 48.37, lat: 12.48, nid: 'N02-Bha', tag: 'other', naks: 'भरणी', enaks: 'Bharaṇī' },
  12719: { lon: 46.93, lat: 11.31, nid: 'N02-Bha', tag: 'other', naks: 'भरणी', enaks: 'Bharaṇī' },
  
  // N03-Kri - Kṛttikā
  17702: { lon: 59.99, lat: 4.05, nid: 'N03-Kri', tag: 'rep', naks: 'क्रित्तिका', enaks: 'Kṛttikā' },
  17499: { lon: 59.41, lat: 4.19, nid: 'N03-Kri', tag: 'other', naks: 'क्रित्तिका', enaks: 'Kṛttikā' },
  17531: { lon: 59.57, lat: 4.52, nid: 'N03-Kri', tag: 'other', naks: 'क्रित्तिका', enaks: 'Kṛttikā' },
  17573: { lon: 59.68, lat: 4.39, nid: 'N03-Kri', tag: 'other', naks: 'क्रित्तिका', enaks: 'Kṛttikā' },
  17608: { lon: 59.70, lat: 3.96, nid: 'N03-Kri', tag: 'other', naks: 'क्रित्तिका', enaks: 'Kṛttikā' },
  17847: { lon: 60.36, lat: 3.92, nid: 'N03-Kri', tag: 'other', naks: 'क्रित्तिका', enaks: 'Kṛttikā' },
  17851: { lon: 60.36, lat: 3.92, nid: 'N03-Kri', tag: 'other', naks: 'क्रित्तिका', enaks: 'Kṛttikā' },
  
  // N04-Roh - Rohiṇī
  21421: { lon: 69.79, lat: -5.47, nid: 'N04-Roh', tag: 'rep', naks: 'रोहिणी', enaks: 'Rohiṇī' },
  20205: { lon: 65.81, lat: -5.73, nid: 'N04-Roh', tag: 'other', naks: 'रोहिणी', enaks: 'Rohiṇī' },
  20455: { lon: 66.87, lat: -3.97, nid: 'N04-Roh', tag: 'other', naks: 'रोहिणी', enaks: 'Rohiṇī' },
  20889: { lon: 68.47, lat: -2.57, nid: 'N04-Roh', tag: 'other', naks: 'रोहिणी', enaks: 'Rohiṇī' },
  20894: { lon: 67.96, lat: -5.84, nid: 'N04-Roh', tag: 'other', naks: 'रोहिणी', enaks: 'Rohiṇī' },
  
  // N05-Mrg - Mṛgaśira
  26207: { lon: 83.71, lat: -13.37, nid: 'N05-Mrg', tag: 'rep', naks: 'मृगशीर्ष', enaks: 'Mṛgaśira' },
  25336: { lon: 80.95, lat: -16.82, nid: 'N05-Mrg', tag: 'other', naks: 'मृगशीर्ष', enaks: 'Mṛgaśira' },
  27989: { lon: 88.76, lat: -16.03, nid: 'N05-Mrg', tag: 'other', naks: 'मृगशीर्ष', enaks: 'Mṛgaśira' },
  
  // N06-Ard - Ārdrā
  31681: { lon: 99.11, lat: -6.74, nid: 'N06-Ard', tag: 'rep', naks: 'आर्द्रा', enaks: 'Ārdrā' },
  
  // N07-Pun - Punarvasu
  37826: { lon: 113.22, lat: 6.68, nid: 'N07-Pun', tag: 'rep', naks: 'पुनर्वसू', enaks: 'Punarvasu' },
  36850: { lon: 110.24, lat: 10.10, nid: 'N07-Pun', tag: 'other', naks: 'पुनर्वसू', enaks: 'Punarvasu' },
  
  // N08-Pus - Puṣya
  42911: { lon: 128.72, lat: 0.08, nid: 'N08-Pus', tag: 'rep', naks: 'पुष्य', enaks: 'Puṣya' },
  
  // N09-Asl - Āśleṣā
  43813: { lon: 134.58, lat: -10.97, nid: 'N09-Asl', tag: 'rep', naks: 'आश्लेषा', enaks: 'Āśleṣā' },
  42313: { lon: 130.31, lat: -12.39, nid: 'N09-Asl', tag: 'other', naks: 'आश्लेषा', enaks: 'Āśleṣā' },
  43109: { lon: 132.35, lat: -11.10, nid: 'N09-Asl', tag: 'other', naks: 'आश्लेषा', enaks: 'Āśleṣā' },
  42799: { lon: 132.31, lat: -14.25, nid: 'N09-Asl', tag: 'other', naks: 'आश्लेषा', enaks: 'Āśleṣā' },
  43234: { lon: 132.91, lat: -11.55, nid: 'N09-Asl', tag: 'other', naks: 'आश्लेषा', enaks: 'Āśleṣā' },
  42402: { lon: 131.21, lat: -14.60, nid: 'N09-Asl', tag: 'other', naks: 'आश्लेषा', enaks: 'Āśleṣā' },
  47431: { lon: 135.0, lat: -12.0, nid: 'N09-Asl', tag: 'other', naks: 'आश्लेषा', enaks: 'Āśleṣā' }, // Approximate
  
  // N10-Mag - Maghā
  50335: { lon: 147.57, lat: 11.86, nid: 'N10-Mag', tag: 'rep', naks: 'मघा', enaks: 'Maghā' },
  49669: { lon: 149.83, lat: 0.46, nid: 'N10-Mag', tag: 'other', naks: 'मघा', enaks: 'Maghā' },
  50583: { lon: 149.61, lat: 8.81, nid: 'N10-Mag', tag: 'other', naks: 'मघा', enaks: 'Maghā' },
  47908: { lon: 140.71, lat: 9.71, nid: 'N10-Mag', tag: 'other', naks: 'मघा', enaks: 'Maghā' },
  49583: { lon: 147.91, lat: 4.87, nid: 'N10-Mag', tag: 'other', naks: 'मघा', enaks: 'Maghā' },
  48455: { lon: 141.43, lat: 12.35, nid: 'N10-Mag', tag: 'other', naks: 'मघा', enaks: 'Maghā' },
  
  // N11-PPal - Pūrva Phalgunī
  54872: { lon: 161.32, lat: 14.33, nid: 'N11-PPal', tag: 'rep', naks: 'पूर्वफल्गुनी', enaks: 'Pūrva Phalgunī' },
  54879: { lon: 163.42, lat: 9.67, nid: 'N11-PPal', tag: 'other', naks: 'पूर्वफल्गुनी', enaks: 'Pūrva Phalgunī' },
  
  // N12-UPal - Uttara Phalgunī
  57632: { lon: 171.62, lat: 12.27, nid: 'N12-UPal', tag: 'rep', naks: 'उत्तरफल्गुनी', enaks: 'Uttara Phalgunī' },
  57565: { lon: 168.97, lat: 17.31, nid: 'N12-UPal', tag: 'other', naks: 'उत्तरफल्गुनी', enaks: 'Uttara Phalgunī' },
  
  // N13-Has - Hasta
  60965: { lon: 193.45, lat: -12.20, nid: 'N13-Has', tag: 'rep', naks: 'हस्त', enaks: 'Hasta' },
  59199: { lon: 192.24, lat: -21.75, nid: 'N13-Has', tag: 'other', naks: 'हस्त', enaks: 'Hasta' },
  61359: { lon: 197.36, lat: -18.04, nid: 'N13-Has', tag: 'other', naks: 'हस्त', enaks: 'Hasta' },
  59803: { lon: 190.72, lat: -14.50, nid: 'N13-Has', tag: 'other', naks: 'हस्त', enaks: 'Hasta' },
  59316: { lon: 191.66, lat: -19.67, nid: 'N13-Has', tag: 'other', naks: 'हस्त', enaks: 'Hasta' },
  60425: { lon: 195.0, lat: -15.0, nid: 'N13-Has', tag: 'other', naks: 'हस्त', enaks: 'Hasta' }, // Approximate
  
  // N14-Chi - Citrā
  65474: { lon: 203.84, lat: -2.05, nid: 'N14-Chi', tag: 'rep', naks: 'चित्रा', enaks: 'Citrā' },
  
  // N15-Swa - Svātī
  69673: { lon: 204.23, lat: 30.73, nid: 'N15-Swa', tag: 'rep', naks: 'स्वाती', enaks: 'Svātī' },
  
  // N16-Vis - Viśākhā
  72622: { lon: 225.08, lat: 0.33, nid: 'N16-Vis', tag: 'rep', naks: 'विशाखे', enaks: 'Viśākhā' },
  
  // N17-Anu - Anūrādhā
  78401: { lon: 242.56, lat: -1.99, nid: 'N17-Anu', tag: 'rep', naks: 'अनूराधा', enaks: 'Anūrādhā' },
  78820: { lon: 243.18, lat: 1.01, nid: 'N17-Anu', tag: 'other', naks: 'अनूराधा', enaks: 'Anūrādhā' },
  78821: { lon: 243.18, lat: 1.01, nid: 'N17-Anu', tag: 'other', naks: 'अनूराधा', enaks: 'Anūrādhā' },
  78265: { lon: 242.93, lat: -5.48, nid: 'N17-Anu', tag: 'other', naks: 'अनूराधा', enaks: 'Anūrādhā' },
  78933: { lon: 243.66, lat: 0.22, nid: 'N17-Anu', tag: 'other', naks: 'अनूराधा', enaks: 'Anūrādhā' },
  80112: { lon: 247.79, lat: -4.04, nid: 'N17-Anu', tag: 'other', naks: 'अनूराधा', enaks: 'Anūrādhā' },
  
  // N18-Jye - Jyeṣṭhā
  80763: { lon: 249.75, lat: -4.57, nid: 'N18-Jye', tag: 'rep', naks: 'ज्येष्ठा', enaks: 'Jyeṣṭhā' },
  82396: { lon: 255.33, lat: -11.74, nid: 'N18-Jye', tag: 'other', naks: 'ज्येष्ठा', enaks: 'Jyeṣṭhā' },
  
  // N19-Mul - Mūla
  86670: { lon: 266.46, lat: -15.64, nid: 'N19-Mul', tag: 'rep', naks: 'मूल', enaks: 'Mūla' },
  82729: { lon: 257.23, lat: -19.64, nid: 'N19-Mul', tag: 'other', naks: 'मूल', enaks: 'Mūla' },
  86228: { lon: 265.59, lat: -19.64, nid: 'N19-Mul', tag: 'other', naks: 'मूल', enaks: 'Mūla' },
  87073: { lon: 267.51, lat: -16.71, nid: 'N19-Mul', tag: 'other', naks: 'मूल', enaks: 'Mūla' },
  85927: { lon: 264.58, lat: -13.79, nid: 'N19-Mul', tag: 'other', naks: 'मूल', enaks: 'Mūla' },
  85696: { lon: 264.00, lat: -14.01, nid: 'N19-Mul', tag: 'other', naks: 'मूल', enaks: 'Mūla' },
  
  // N20-PAsh - Pūrva Aṣāḍhā
  90496: { lon: 276.31, lat: -2.14, nid: 'N20-PAsh', tag: 'rep', naks: 'पूर्वाषाढा', enaks: 'Pūrva Aṣāḍhā' },
  88635: { lon: 271.25, lat: -6.99, nid: 'N20-PAsh', tag: 'other', naks: 'पूर्वाषाढा', enaks: 'Pūrva Aṣāḍhā' },
  89931: { lon: 274.57, lat: -6.47, nid: 'N20-PAsh', tag: 'other', naks: 'पूर्वाषाढा', enaks: 'Pūrva Aṣāḍhā' },
  90185: { lon: 275.07, lat: -11.05, nid: 'N20-PAsh', tag: 'other', naks: 'पूर्वाषाढा', enaks: 'Pūrva Aṣāḍhā' },
  
  // N21-UAsh - Uttara Aṣāḍhā
  93864: { lon: 284.82, lat: -5.09, nid: 'N21-UAsh', tag: 'rep', naks: 'उत्तराषाढा', enaks: 'Uttara Aṣāḍhā' },
  93506: { lon: 283.63, lat: -7.18, nid: 'N21-UAsh', tag: 'other', naks: 'उत्तराषाढा', enaks: 'Uttara Aṣāḍhā' },
  92855: { lon: 282.38, lat: -3.45, nid: 'N21-UAsh', tag: 'other', naks: 'उत्तराषाढा', enaks: 'Uttara Aṣāḍhā' },
  92041: { lon: 280.17, lat: -3.95, nid: 'N21-UAsh', tag: 'other', naks: 'उत्तराषाढा', enaks: 'Uttara Aṣāḍhā' },
  
  // N22-Shr - Śravaṇa
  97649: { lon: 301.77, lat: 29.30, nid: 'N22-Shr', tag: 'rep', naks: 'श्रवण', enaks: 'Śravaṇa' },
  97278: { lon: 300.93, lat: 31.24, nid: 'N22-Shr', tag: 'other', naks: 'श्रवण', enaks: 'Śravaṇa' },
  98036: { lon: 302.41, lat: 26.66, nid: 'N22-Shr', tag: 'other', naks: 'श्रवण', enaks: 'Śravaṇa' },
  
  // N23-Dha - Dhaniṣṭhā
  101769: { lon: 316.33, lat: 31.92, nid: 'N23-Dha', tag: 'rep', naks: 'धनिष्ठा', enaks: 'Dhaniṣṭhā' },
  101958: { lon: 317.37, lat: 33.02, nid: 'N23-Dha', tag: 'other', naks: 'धनिष्ठा', enaks: 'Dhaniṣṭhā' },
  102532: { lon: 319.36, lat: 32.70, nid: 'N23-Dha', tag: 'other', naks: 'धनिष्ठा', enaks: 'Dhaniṣṭhā' },
  102281: { lon: 318.11, lat: 31.95, nid: 'N23-Dha', tag: 'other', naks: 'धनिष्ठा', enaks: 'Dhaniṣṭhā' },
  101421: { lon: 316.0, lat: 32.0, nid: 'N23-Dha', tag: 'other', naks: 'धनिष्ठा', enaks: 'Dhaniṣṭhā' }, // Approximate
  
  // N24-Sha - Śatabhiṣak
  112961: { lon: 341.57, lat: -0.39, nid: 'N24-Sha', tag: 'rep', naks: 'शतभिषक्', enaks: 'Śatabhiṣak' },
  110395: { lon: 338.0, lat: 0.0, nid: 'N24-Sha', tag: 'other', naks: 'शतभिषक्', enaks: 'Śatabhiṣak' }, // Approximate
  111710: { lon: 340.0, lat: 0.0, nid: 'N24-Sha', tag: 'other', naks: 'शतभिषक्', enaks: 'Śatabhiṣak' }, // Approximate
  
  // N25-PBha - Pūrva Proṣṭapada
  113963: { lon: 353.48, lat: 19.41, nid: 'N25-PBha', tag: 'rep', naks: 'पूर्वाभाद्रपदा', enaks: 'Pūrva Proṣṭapada' },
  113881: { lon: 359.37, lat: 31.14, nid: 'N25-PBha', tag: 'other', naks: 'पूर्वाभाद्रपदा', enaks: 'Pūrva Proṣṭapada' },
  
  // N26-UBha - Uttara Proṣṭapada
  677: { lon: 14.31, lat: 25.68, nid: 'N26-UBha', tag: 'rep', naks: 'उत्तराभाद्रपदा', enaks: 'Uttara Proṣṭapada' },
  1067: { lon: 9.15, lat: 12.60, nid: 'N26-UBha', tag: 'other', naks: 'उत्तराभाद्रपदा', enaks: 'Uttara Proṣṭapada' },
  
  // N27-Rev - Revatī
  9487: { lon: 17.5, lat: 1.0, nid: 'N27-Rev', tag: 'rep', naks: 'रेवती', enaks: 'Revatī' },
  4906: { lon: 17.52, lat: 1.09, nid: 'N27-Rev', tag: 'rep', naks: 'रेवती', enaks: 'Revatī' },
  
  // N28-Abh - Abhijit
  91262: { lon: 290.0, lat: 60.0, nid: 'N28-Abh', tag: 'rep', naks: 'अभिजित', enaks: 'Abhijit' },
  91971: { lon: 292.0, lat: 61.0, nid: 'N28-Abh', tag: 'other', naks: 'अभिजित', enaks: 'Abhijit' },
  91919: { lon: 291.0, lat: 59.0, nid: 'N28-Abh', tag: 'other', naks: 'अभिजित', enaks: 'Abhijit' }
};

/**
 * Parse constellation data from .fab format
 * @returns {Array} Array of nakshatra objects with segments
 */
export function parseConstellationData() {
  const lines = CONSTELLATION_DATA.trim().split('\n').filter(line => 
    line.trim() && !line.startsWith('#')
  );
  
  const nakshatras = [];
  const warnings = [];
  
  for (const line of lines) {
    const parts = line.trim().split(/\s+/);
    const nid = parts[0]; // e.g., "N01"
    const segmentCount = parseInt(parts[1]);
    const hipIds = parts.slice(2).map(id => parseInt(id));
    
    // Parse segments (pairs of HIP IDs)
    const segments = [];
    for (let i = 0; i < hipIds.length; i += 2) {
      if (i + 1 < hipIds.length) {
        const fromHip = hipIds[i];
        const toHip = hipIds[i + 1];
        
        // Validate HIP IDs exist in STAR_DATA
        if (!STAR_DATA[fromHip]) {
          warnings.push(`⚠️  Missing HIP ${fromHip} in ${nid}`);
        }
        if (!STAR_DATA[toHip]) {
          warnings.push(`⚠️  Missing HIP ${toHip} in ${nid}`);
        }
        
        if (STAR_DATA[fromHip] && STAR_DATA[toHip]) {
          segments.push({
            from: {
              hip: fromHip,
              lon: STAR_DATA[fromHip].lon,
              lat: STAR_DATA[fromHip].lat
            },
            to: {
              hip: toHip,
              lon: STAR_DATA[toHip].lon,
              lat: STAR_DATA[toHip].lat
            }
          });
        }
      }
    }
    
    // Find representative star
    const repHip = hipIds.find(hip => STAR_DATA[hip]?.tag === 'rep') || hipIds[0];
    const repStar = STAR_DATA[repHip];
    
    if (repStar && segments.length > 0) {
      // Get first two characters of Devanagari name
      const fullName = repStar.naks;
      const firstTwoChars = fullName.substring(0, 2);
      
      nakshatras.push({
        id: repStar.nid,
        nnid: parseInt(nid.substring(1)), // Extract number from N01
        name: {
          devanagari: fullName,
          firstTwoChars: firstTwoChars,
          iast: repStar.enaks,
          notation: repStar.nid
        },
        repStar: {
          hip: repHip,
          lon: repStar.lon,
          lat: repStar.lat
        },
        segments: segments
      });
    }
  }
  
  return { nakshatras, warnings };
}

/**
 * Get nakshatra data with validation
 * @returns {Object} {nakshatras: Array, warnings: Array}
 */
export function getNakshatraData() {
  return parseConstellationData();
}
