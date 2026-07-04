import { RASIS, GRAHAS, BHAVA_TYPES, BHAVA_THEMES, LIFE_AREAS } from "../data/static.js";

export const bhavaOf = (rId, lagna) => ((rId - lagna + 12) % 12) + 1;

export function dignity(gId, rId) {
  const g = GRAHAS[gId];
  if (!g) return { label:"—", short:"", col:"#888", score:0 };
  if (g.ucca === rId)             return { label:"Ucca",      short:"U", col:"#e8c040", score:3  };
  if (g.nīca === rId)             return { label:"Nīca",      short:"N", col:"#d04040", score:-2 };
  if (g.svakṣetra.includes(rId)) return { label:"Svakṣetra", short:"S", col:"#40b070", score:2  };
  return { label:"Sāmānya", short:"", col:"#888888", score:0 };
}

export function staticAnnotations(rāśiId) {
  const ucca = Object.entries(GRAHAS).filter(([,g])=>g.ucca===rāśiId).map(([id])=>id);
  const nīca  = Object.entries(GRAHAS).filter(([,g])=>g.nīca===rāśiId).map(([id])=>id);
  const svak  = Object.entries(GRAHAS).filter(([,g])=>g.svakṣetra.includes(rāśiId)).map(([id])=>id);
  const mtk   = Object.entries(GRAHAS).filter(([,g])=>g.mūlatrikoṇa===rāśiId).map(([id])=>id);
  return { ucca, nīca, svak, mtk };
}

export function buildMap(event) {
  const map = {};
  for (let b=1; b<=12; b++) {
    const rId = ((event.lagna-1+b-1)%12)+1;
    const rāśi = RASIS[rId-1];
    map[b] = {
      rāśiId:rId, rāśi,
      bhāveśa: rāśi.lordId,
      bhāveśaBhāva: bhavaOf(event.pos[rāśi.lordId], event.lagna),
      occupants: Object.entries(event.pos).filter(([,r])=>bhavaOf(r,event.lagna)===b).map(([g])=>g),
    };
  }
  return map;
}

export function buildAnalysisLog(event, map, areaKey) {
  const area = LIFE_AREAS[areaKey];
  const log = [];
  let totalScore = 0;
  log.push({ type:"head", text:`${area.iast} — ${area.en}` });
  log.push({ type:"info", highlight:area.bhāvas,
    bullets:[
      `Three primary bhāvas govern ${area.en}: Bhāva ${area.bhāvas.join(", ")}.`,
      `We apply the LOYAKS framework to each — Lord, Occupant, and Kāraka — then aggregate.`,
    ]
  });
  area.bhāvas.forEach((b)=>{
    const bInfo = map[b];
    const theme = BHAVA_THEMES[b];
    const bv    = GRAHAS[bInfo.bhāveśa];
    const bvDig = dignity(bInfo.bhāveśa, event.pos[bInfo.bhāveśa]);
    const bvRāśi= RASIS[event.pos[bInfo.bhāveśa]-1];
    const k     = GRAHAS[theme.kāraka];
    const kRId  = event.pos[theme.kāraka];
    const kB    = bhavaOf(kRId, event.lagna);
    const kDig  = dignity(theme.kāraka, kRId);

    log.push({ type:"bhava", text:`Bhāva ${b} · ${theme.iast} — ${theme.en}`,
      sandarbha:`Sandarbha: kāraka = ${k.iast}; prakāra = ${(BHAVA_TYPES[b]||[]).join(", ")||"Sāmānya"}`,
      highlight:[b] });

    log.push({ type:"rule", letter:"L", col:bvDig.col, score:bvDig.score, highlight:[bInfo.bhāveśaBhāva],
      bullets:[
        `Bhāveśa: ${bv.iast} placed in ${bvRāśi.iast} (Bhāva ${bInfo.bhāveśaBhāva}) — ${bvDig.label}.`,
        bvDig.label==="Ucca"?`An exalted lord is auspicious — it actively promotes the ${area.en.toLowerCase()} significations.`
        :bvDig.label==="Nīca"?`A debilitated lord is weakened — the ${area.en.toLowerCase()} area faces challenges from its own manager.`
        :bvDig.label==="Svakṣetra"?`Lord in own sign is stable and effective — reliable management of this bhāva.`
        :`Neutral placement — its efficacy depends on aspects and yogas.`,
      ]
    });
    totalScore += bvDig.score;

    if (bInfo.occupants.length) {
      bInfo.occupants.forEach(gId=>{
        const g=GRAHAS[gId]; const dig=dignity(gId,bInfo.rāśiId);
        log.push({ type:"rule", letter:"O", col:dig.col, score:dig.score, highlight:[b],
          bullets:[
            `${g.iast} occupies Bhāva ${b} directly — ${dig.label}.`,
            dig.label==="Ucca"?`Exalted here: a powerful positive presence elevating the house's significations.`
            :dig.label==="Nīca"?`Debilitated here: weakens the house from within — significations need support elsewhere.`
            :`Its natural character (benefic or malefic) determines whether presence helps or hinders.`,
          ]
        });
        totalScore += dig.score;
      });
    } else {
      log.push({ type:"rule", letter:"O", col:"#888", score:0, highlight:[b],
        bullets:[
          `Bhāva ${b} is nirgraha — no planet occupies it directly.`,
          `The bhāva reads entirely through its lord and kāraka. An empty house is not necessarily weak.`,
        ]
      });
    }

    log.push({ type:"rule", letter:"K", col:kDig.col, score:kDig.score, highlight:[kB],
      bullets:[
        `Kāraka: ${k.iast} (universal significator for ${theme.iast}) in Bhāva ${kB} — ${kDig.label}.`,
        `[Sandarbha: ${k.iast} is always the natural significator for ${area.en} — this is birth-independent.]`,
        kDig.label==="Ucca"?`Exalted kāraka: powerful universal anchor — strengthens this area regardless of bhāva configuration.`
        :kDig.label==="Nīca"?`Debilitated kāraka: persistent undercurrent of difficulty even when the bhāveśa is strong.`
        :`Neutral kāraka: standard universal support without amplification.`,
      ]
    });
    totalScore += kDig.score;
  });

  const verdict = totalScore>=6?"Strong and well-supported":totalScore>=3?"Moderately favourable":totalScore>=0?"Mixed — strengths and challenges coexist":"Challenged — needs supportive factors";
  const verdictCol = totalScore>=6?"#50c080":totalScore>=3?"#e8c040":totalScore>=0?"#c8a060":"#d04040";
  log.push({ type:"divider" });
  log.push({ type:"verdict", col:verdictCol, highlight:area.bhāvas,
    text:`${area.iast} aggregate — ${verdict}`,
    bullets:[
      `Composite score across bhāva lords, occupants, and kārakas: ${totalScore>0?"+":""}${totalScore}.`,
      `This is an L+O+K signal. Yoga (Y) and Dṛṣṭi (A) will refine the picture further.`,
    ]
  });
  return log;
}

// ═══════════════════════════════════════════════════════════════════════════════
// THEMES
// ═══════════════════════════════════════════════════════════════════════════════
