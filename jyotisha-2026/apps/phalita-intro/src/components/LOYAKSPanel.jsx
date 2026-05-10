import { useState, useEffect, useRef, useCallback } from "react";
import { RASIS, GRAHAS, BHAVA_TYPES, BHAVA_THEMES } from "../data/static.js";
import { bhavaOf, dignity } from "../utils/jyotisha.js";
import { KendraIcon, TrikonaIcon, DusthanaIcon } from "./icons.jsx";

export function LOYAKSPanel({ event, map, selected, th, onHighlight, speedMs }) {
  const [visibleRows, setVisibleRows] = useState(0);
  const [running, setRunning]         = useState(false);
  const timers = useRef([]);

  const b=selected||1; const bInfo=map[b]; const theme=BHAVA_THEMES[b];
  const types=BHAVA_TYPES[b]||[];
  const bv=GRAHAS[bInfo.bhāveśa]; const bvDig=dignity(bInfo.bhāveśa,event.pos[bInfo.bhāveśa]);
  const k=GRAHAS[theme.kāraka];   const kDig=dignity(theme.kāraka,event.pos[theme.kāraka]);

  const rows = [
    { key:"L", full:"Bhāveśa — Functional Lord", gCol:bv.color, noteCol:bvDig.col,
      highlight:[bInfo.bhāveśaBhāva],
      bullets:[
        `${bv.iast} lords ${RASIS[bInfo.rāśiId-1].iast} and therefore governs Bhāva ${b}.`,
        `It is currently placed in Bhāva ${bInfo.bhāveśaBhāva} (${RASIS[event.pos[bInfo.bhāveśa]-1].iast}) — ${bvDig.label}.`,
        bvDig.label==="Ucca"?"An exalted lord strongly promotes this bhāva's significations.":bvDig.label==="Nīca"?"A debilitated lord struggles to protect its house.":bvDig.label==="Svakṣetra"?"Lord in own sign — comfortable, stable management.":"Neutral placement — context from other factors needed.",
      ]
    },
    { key:"O", full:"Sthita Graha — Occupants", gCol:th.text, noteCol:th.text,
      highlight:[b],
      bullets: bInfo.occupants.length
        ? [ `${bInfo.occupants.map(g=>GRAHAS[g].iast).join(", ")} ${bInfo.occupants.length===1?"occupies":"occupy"} Bhāva ${b} directly.`,
            `Dignity: ${bInfo.occupants.map(g=>dignity(g,bInfo.rāśiId).label).join(", ")}.`,
            "A planet's presence colours the house by its natural character — benefics nurture, malefics complicate but also activate.",
          ]
        : [ `Bhāva ${b} is nirgraha — no planet occupies it.`,
            "The house reads through its lord and kāraka alone.",
            "An empty house is not weak; its lord's placement carries the full expression.",
          ]
    },
    { key:"Y", full:"Yoga — Combinatorial Patterns", gCol:"#80b890", noteCol:"#80b890",
      highlight:[b],
      bullets:[
        b===10&&event.lagna===4?"Rāja-yoga candidate: Guru (Kendra lord, ucca) relates to the Trikona axis.":"Full yoga-scan requires all 12 bhāvas — partial reading here.",
        "Yogas arise when lords of Kendra and Trikona bhāvas are conjunct, mutually aspecting, or exchange signs.",
        "See Viśleṣaṇa for the life-area synthesis which draws on yoga signals.",
      ]
    },
    { key:"A", full:"Dṛṣṭi — Aspectual Gaze", gCol:"#8888c0", noteCol:"#8888c0",
      highlight:[b],
      bullets:[
        "Every planet aspects the 7th house from its position (opposition gaze).",
        "Special aspects — Maṅgala: 4th & 8th; Guru: 5th & 9th; Śani: 3rd & 10th from their positions.",
        "Full dṛṣṭi computation from graha positions is planned for the next iteration.",
      ]
    },
    { key:"K", full:"Kāraka — Natural Significator", gCol:k.color, noteCol:kDig.col,
      highlight:[bhavaOf(event.pos[theme.kāraka],event.lagna)],
      bullets:[
        `${k.iast} is the universal kāraka for ${theme.iast} — a Sandarbha constant, birth-independent.`,
        `Here, ${k.iast} is placed in Bhāva ${bhavaOf(event.pos[theme.kāraka],event.lagna)} — ${kDig.label}.`,
        kDig.label==="Ucca"?"Exalted kāraka: powerful universal support for this life area.":kDig.label==="Nīca"?"Debilitated kāraka: persistent background weakness for this area.":"Neutral kāraka — standard universal support.",
      ]
    },
  ];

  const runAnimation = useCallback(()=>{
    timers.current.forEach(clearTimeout); timers.current=[];
    setVisibleRows(0); setRunning(true); onHighlight([]);
    rows.forEach((_,i)=>{
      const t=setTimeout(()=>{
        setVisibleRows(i+1);
        onHighlight(rows[i].highlight||[]);
        if(i===rows.length-1) setRunning(false);
      }, speedMs*(i+1));
      timers.current.push(t);
    });
  },[b,speedMs]);

  useEffect(()=>{ setVisibleRows(0); setRunning(false); onHighlight([]); timers.current.forEach(clearTimeout); },[b]);
  useEffect(()=>()=>timers.current.forEach(clearTimeout),[]);

  return (
    <div>
      <div style={{ fontSize:13, color:th.textDim, letterSpacing:2, marginBottom:6 }}>LOYAKS · BHĀVA {b} — {theme.iast}</div>

      <button onClick={runAnimation} disabled={running} style={{
        width:"100%", background:running?"none":th.inputBg,
        border:`1px solid ${running?th.panelBorder:th.accent}`,
        color:running?th.textFaint:th.text,
        borderRadius:4, padding:"8px", cursor:running?"not-allowed":"pointer",
        fontSize:15, fontFamily:"Georgia,serif", marginBottom:12,
      }}>{running?"▶ Analysing…":"▶ Animate LOYAKS factors"}</button>

      <div style={{ fontSize:14, color:th.textDim, fontStyle:"italic", marginBottom:8 }}>{theme.en}</div>
      <div style={{ display:"flex", gap:8, flexWrap:"wrap", marginBottom:12 }}>
        {types.map(t=>(
          <span key={t} style={{ display:"inline-flex", alignItems:"center", gap:5, fontSize:14,
            padding:"3px 10px", borderRadius:3,
            background:t==="Kendra"?"rgba(55,110,210,0.12)":t==="Trikona"?"rgba(55,170,90,0.12)":"rgba(190,55,35,0.12)",
            border:`1px solid ${t==="Kendra"?"#5090ff44":t==="Trikona"?"#50c07844":"#c0504044"}`,
            color:t==="Kendra"?"#7ab0ff":t==="Trikona"?"#70d090":"#e07060",
          }}>
            {t==="Kendra"&&<KendraIcon size={14}/>}
            {t==="Trikona"&&<TrikonaIcon size={14}/>}
            {t==="Dusthāna"&&<DusthanaIcon size={14}/>}
            {t}
          </span>
        ))}
      </div>
      {rows.slice(0,visibleRows).map((r,i)=>(
        <div key={r.key} onClick={()=>onHighlight(r.highlight||[])}
          style={{ borderLeft:`3px solid ${r.gCol}`, marginBottom:14, paddingLeft:12,
            animation:"fadeIn 0.5s ease", cursor:"pointer" }}
          className="narration-entry"
          title="Click to highlight bhāva">
          <div className="narration-row" style={{ display:"flex", alignItems:"center", gap:10, marginBottom:6 }}>
            <span style={{ fontSize:20, color:th.text, fontWeight:"bold", fontFamily:"monospace", minWidth:20 }}>{r.key}</span>
            <span style={{ fontSize:14, color:th.textDim }}>{r.full}</span>
          </div>
          {r.bullets.map((b2,bi)=>(
            <div className="narration-row" key={bi} style={{ display:"flex", gap:8, marginBottom:4, alignItems:"flex-start" }}>
              <span style={{ color:r.gCol, fontSize:14, marginTop:2, flexShrink:0 }}>•</span>
              <span style={{ fontSize:15, color:bi===0?r.gCol:th.textDim, lineHeight:1.8 }}>{b2}</span>
            </div>
          ))}
        </div>
      ))}
      {visibleRows===0&&(
        <div style={{ fontSize:15, color:th.textFaint, fontStyle:"italic" }}>
          Press animate to walk through the five LOYAKS factors for Bhāva {b}.
        </div>
      )}
    </div>
  );
}

// ═══════════════════════════════════════════════════════════════════════════════
// VISLESANA PANEL
// ═══════════════════════════════════════════════════════════════════════════════
