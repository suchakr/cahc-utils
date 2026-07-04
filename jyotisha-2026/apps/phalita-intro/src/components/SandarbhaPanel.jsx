import { useState } from "react";
import { RASIS, GRAHAS, GRAHA_SIGNIFICATIONS, BHAVA_TYPES, BHAVA_THEMES, VIMSHOTTARI } from "../data/static.js";
import { KendraIcon, TrikonaIcon, DusthanaIcon, BhavaTypeIcons } from "./icons.jsx";

export function SandarbhaPanel({ th }) {
  const [sec, setSec] = useState("rāśi");
  const tabs = ["rāśi","graha","bhāva","daśā","paddhati"];
  const thS = { textAlign:"left", padding:"7px 8px", color:th.textDim, fontWeight:"normal",
    fontSize:14, borderBottom:`1px solid ${th.panelBorder}` };
  const tdS = (extra={}) => ({ padding:"7px 8px", fontSize:15, borderBottom:`1px solid ${th.tabBorder}`, ...extra });

  return (
    <div className="sandarbha-panel">
      <div className="sandarbha-heading" style={{ fontSize:13, color:th.textDim, letterSpacing:2, marginBottom:8 }}>SANDARBHA KOŚA · Universal Reference</div>
      <div className="static-narrator" style={{ fontSize:14, color:th.textFaint, marginBottom:10, fontStyle:"italic",
        borderLeft:`2px solid ${th.panelBorder}`, paddingLeft:8 }}>
        Sthira (fixed) constants — birth-independent. Every chart shares this substrate.
      </div>
      <div className="sandarbha-tabs" style={{ display:"flex", borderBottom:`1px solid ${th.tabBorder}`, marginBottom:16, flexWrap:"wrap" }}>
        {tabs.map(t=>(
          <button className="sandarbha-tab" key={t} onClick={()=>setSec(t)} style={{
            background:"none", border:"none",
            borderBottom:sec===t?`2px solid ${th.accent}`:"2px solid transparent",
            color:sec===t?th.text:th.textDim,
            padding:"6px 12px", cursor:"pointer", fontSize:15, marginBottom:-1,
            fontFamily:"Georgia,serif",
          }}>{t}</button>
        ))}
      </div>

      {sec==="rāśi"&&(
        <div style={{ overflowX:"auto" }}>
          <table style={{ width:"100%", borderCollapse:"collapse", fontFamily:"Georgia,serif" }}>
            <thead><tr>
              {["#","Rāśi","En","Svāmī","Tattva","Guṇa","Ucca","Nīca","MTK"].map(h=><th key={h} style={thS}>{h}</th>)}
            </tr></thead>
            <tbody>{RASIS.map(r=>{
              const lord=GRAHAS[r.lordId];
              const uccaE=Object.entries(GRAHAS).find(([,g])=>g.ucca===r.id);
              const nīcaE=Object.entries(GRAHAS).find(([,g])=>g.nīca===r.id);
              const mtk=Object.entries(GRAHAS).filter(([,g])=>g.mūlatrikoṇa===r.id);
              return (<tr key={r.id}>
                <td style={tdS({color:th.textFaint})}>{r.id}</td>
                <td style={tdS({color:th.text,fontWeight:"bold"})}>{r.iast}</td>
                <td style={tdS({color:th.textDim})}>{r.en}</td>
                <td style={tdS({color:lord.color,fontWeight:"bold"})}>{lord.iast}</td>
                <td style={tdS({color:th.textDim})}>{r.element}</td>
                <td style={tdS({color:th.textFaint})}>{r.quality}</td>
                <td style={tdS({color:"#e8c040"})}>{uccaE?`${GRAHAS[uccaE[0]].iast} ${GRAHAS[uccaE[0]].uccaDeg}`:"—"}</td>
                <td style={tdS({color:"#d04040"})}>{nīcaE?`${GRAHAS[nīcaE[0]].iast} ${GRAHAS[nīcaE[0]].nīcaDeg}`:"—"}</td>
                <td style={tdS({color:"#50c078"})}>{mtk.length?mtk.map(([id])=>`${GRAHAS[id].iast} (${GRAHAS[id].sa})`).join(", "):"—"}</td>
              </tr>);
            })}</tbody>
          </table>
        </div>
      )}

      {sec==="graha"&&(
        <div style={{ overflowX:"auto" }}>
          <div className="sandarbha-note" style={{ fontSize:15, color:th.textFaint, marginBottom:12, lineHeight:1.7 }}>
            Natural graha properties qualify interpretation text. They do not change the current dignity score.
          </div>
          <table style={{ width:"100%", borderCollapse:"collapse", fontFamily:"Georgia,serif" }}>
            <thead><tr>
              {["Graha","En","Dignity","Transit","Nature","Guṇa","Role","People","Qualities","Friends","Enemies","Neutral"].map(h=><th key={h} style={thS}>{h}</th>)}
            </tr></thead>
            <tbody>{Object.entries(GRAHAS).map(([id,g])=>{
              const sig=GRAHA_SIGNIFICATIONS[id];
              return (
                <tr key={id}>
                  <td style={tdS({color:g.color,fontWeight:"bold"})}>{g.iast}<br/><span style={{ color:th.textFaint, fontWeight:"normal" }}>{g.sa}</span></td>
                  <td style={tdS({color:th.textDim})}>{g.en}</td>
                  <td style={tdS({color:th.textDim, minWidth:145})}>
                    <span style={{ color:"#e8c040" }}>↑ {RASIS[g.ucca-1]?.iast} {g.uccaDeg}</span><br/>
                    <span style={{ color:"#d04040" }}>↓ {RASIS[g.nīca-1]?.iast} {g.nīcaDeg}</span><br/>
                    <span style={{ color:"#40b070" }}>◆ {g.svakṣetra.map(r=>RASIS[r-1].iast).join(", ")||"—"}</span><br/>
                    <span style={{ color:"#50c078" }}>△ {RASIS[g.mūlatrikoṇa-1]?.iast}</span>
                  </td>
                  <td style={tdS({color:th.textDim})}>{sig.transit}</td>
                  <td style={tdS({color:th.text})}>{sig.nature}</td>
                  <td style={tdS({color:th.textDim})}>{sig.guṇa}</td>
                  <td style={tdS({color:th.text})}>{sig.role}</td>
                  <td style={tdS({color:th.textDim})}>{sig.people.join(", ")||"—"}</td>
                  <td style={tdS({color:th.textDim, minWidth:160})}>{sig.qualities.join(", ")}</td>
                  <td style={tdS({color:"#50c080"})}>{sig.friends.join(", ")}</td>
                  <td style={tdS({color:"#d07060"})}>{sig.enemies.join(", ")||"—"}</td>
                  <td style={tdS({color:th.textFaint})}>{sig.neutral.join(", ")}</td>
                </tr>
              );
            })}</tbody>
          </table>
        </div>
      )}

      {sec==="bhāva"&&(
        <div style={{ overflowX:"auto" }}>
          <div className="sandarbha-note" style={{ fontSize:15, color:th.textFaint, marginBottom:12, lineHeight:1.7 }}>
            The three fundamental classifications determine a bhāva's functional character. A bhāva can belong to more than one class.
          </div>
          <div className="sandarbha-card-grid" style={{ display:"flex", gap:16, marginBottom:16, flexWrap:"wrap" }}>
            {[
              { Icon:KendraIcon, label:"Kendra", desc:"Angular houses (1,4,7,10) — the pillars of the chart. Strong planets here have maximum impact.", houses:"1, 4, 7, 10" },
              { Icon:TrikonaIcon, label:"Trikona", desc:"Trine houses (1,5,9) — houses of fortune, dharma, and merit. Considered the most auspicious.", houses:"1, 5, 9" },
              { Icon:DusthanaIcon, label:"Dusthāna", desc:"Difficult houses (6,8,12) — houses of challenge, transformation, and dissolution.", houses:"6, 8, 12" },
            ].map(({Icon,label,desc,houses})=>(
              <div className="sandarbha-card" key={label} style={{ flex:1, minWidth:160, border:`1px solid ${th.panelBorder}`,
                borderRadius:6, padding:"12px", background:th.inputBg }}>
                <div className="sandarbha-card-title" style={{ display:"flex", alignItems:"center", gap:8, marginBottom:6 }}>
                  <Icon size={18}/>
                  <span style={{ fontSize:16, color:th.text, fontWeight:"bold" }}>{label}</span>
                </div>
                <div style={{ fontSize:14, color:th.textDim, lineHeight:1.7, marginBottom:6 }}>{desc}</div>
                <div style={{ fontSize:13, color:th.textFaint }}>Houses: {houses}</div>
              </div>
            ))}
          </div>
          <table style={{ width:"100%", borderCollapse:"collapse", fontFamily:"Georgia,serif" }}>
            <thead><tr>
              {["B","Nāma","Viṣaya","Kāraka","Prakāra","Significations"].map(h=><th key={h} style={thS}>{h}</th>)}
            </tr></thead>
            <tbody>{Object.entries(BHAVA_THEMES).map(([n,t])=>(
              <tr key={n}>
                <td style={tdS({color:th.textFaint})}>{n}</td>
                <td style={tdS({color:th.text,fontWeight:"bold"})}>{t.iast}</td>
                <td style={tdS({color:th.textDim,fontSize:14})}>{t.en}</td>
                <td style={tdS({color:GRAHAS[t.kāraka].color,fontWeight:"bold"})}>{GRAHAS[t.kāraka].iast}</td>
                <td style={tdS()}>
                  <BhavaTypeIcons types={BHAVA_TYPES[n]||[]} size={14}/>
                  <span style={{ fontSize:13, color:th.textFaint, marginLeft:6 }}>
                    {(BHAVA_TYPES[n]||[]).join(", ")||"—"}
                  </span>
                </td>
                <td style={tdS({color:th.textDim,fontSize:14,minWidth:240})}>{t.significations.join(", ")}</td>
              </tr>
            ))}</tbody>
          </table>
        </div>
      )}

      {sec==="daśā"&&(
        <div>
          <div className="sandarbha-note" style={{ fontSize:15, color:th.textFaint, marginBottom:14, lineHeight:1.8 }}>
            Vimśottarī assigns each of the 9 grahas a period of governance totalling 120 varṣas. Entry point is determined by the nakṣatra of Candra at birth.
          </div>
          <table style={{ width:"100%", borderCollapse:"collapse", fontFamily:"Georgia,serif" }}>
            <thead><tr>{["#","Graha","En","Duration"].map(h=><th key={h} style={thS}>{h}</th>)}</tr></thead>
            <tbody>{VIMSHOTTARI.map((d,i)=>(
              <tr key={d.g}>
                <td style={tdS({color:th.textFaint})}>{i+1}</td>
                <td style={tdS({color:GRAHAS[d.g].color,fontWeight:"bold"})}>{GRAHAS[d.g].iast}</td>
                <td style={tdS({color:th.textDim})}>{GRAHAS[d.g].en}</td>
                <td style={tdS({color:th.text})}>{d.y} varṣa</td>
              </tr>
            ))}</tbody>
          </table>
        </div>
      )}

      {sec==="paddhati"&&(
        <div className="sandarbha-paddhati" style={{ fontSize:15, color:th.textDim, lineHeight:1.9 }}>
          <div style={{ fontSize:17, color:th.text, fontWeight:"bold", marginBottom:12 }}>Paddhati — The Algorithmic Framework</div>
          {[
            { layer:"Layer 0 · Sthira Kośa", title:"The Universal Schema",
              body:"The foundation is a set of pure static relationships — rāśi lords, ucca/nīca/svakṣetra/mūlatrikoṇa positions, natural graha significations, kārakas, and bhāva themes. These are compile-time constants: no birth event can alter them. They form the relational database from which every chart is computed." },
            { layer:"Layer 1 · Janma Snapshot", title:"The Birth Transformation",
              body:"The single input is the Lagna — the ascending rāśi at the moment of birth. This acts as a coordinate origin, triggering a modular-arithmetic transformation: bhāva = (rāśiId − lagnaId + 12) mod 12 + 1. Every rāśi receives a bhāva number. Graha positions from the ephemeris are then projected onto this numbered grid. The result is the Jātaka." },
            { layer:"Layer 2 · LOYAKS", title:"The Evaluation Algorithm",
              body:"To assess any bhāva, five factors are examined in sequence: Lord (L) — the bhāveśa and its placement; Occupant (O) — grahas physically in the house; Yoga (Y) — special combinatorial patterns; Aspect (A — Dṛṣṭi) — planetary gazes from a distance; Kāraka (K) — the natural significator. Each factor is scored; the aggregate signal characterises the bhāva's strength for a given life area." },
            { layer:"Layer 3 · Daśā", title:"The Temporal Iterator",
              body:"Vimśottarī partitions the native's lifetime into planetary periods. The active daśā graha — determined by Candra's nakṣatra at birth — acts as a gate: it foregrounds the bhāvas it lords, occupies, or aspects. Prediction is the intersection of a bhāva's static potential (LOYAKS) and its temporal activation (Daśā)." },
            { layer:"Viśleṣaṇa", title:"Life-Area Synthesis",
              body:"A life area (career, health, marriage, wealth) is governed by multiple bhāvas. Viśleṣaṇa applies LOYAKS across all relevant bhāvas and aggregates the signals. The Kāraka factor in each bhāva is a bridge back to the Sandarbha — it is a birth-independent anchor that qualifies every chart-specific finding." },
          ].map(({layer,title,body})=>(
            <div className="sandarbha-paddhati-item" key={layer} style={{ marginBottom:18, borderLeft:`3px solid ${th.accent}`, paddingLeft:12 }}>
              <div style={{ fontSize:13, color:th.textFaint, letterSpacing:1, marginBottom:2 }}>{layer}</div>
              <div style={{ fontSize:16, color:th.text, fontWeight:"bold", marginBottom:6 }}>{title}</div>
              <div style={{ fontSize:15, color:th.textDim, lineHeight:1.8 }}>{body}</div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

// ═══════════════════════════════════════════════════════════════════════════════
// JATAKA PANEL  (animation controller lives in App, panel just renders)
// ═══════════════════════════════════════════════════════════════════════════════
