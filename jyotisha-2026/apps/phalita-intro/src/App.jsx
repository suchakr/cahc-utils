import { useState, useEffect, useRef, useCallback } from "react";
import { RASIS, GRAHAS } from "./data/static.js";
import { BIRTH_EVENTS } from "./data/birthEvents.js";
import { bhavaOf, buildMap } from "./utils/jyotisha.js";
import { THEMES } from "./utils/themes.js";
import { KendraIcon, TrikonaIcon, DusthanaIcon } from "./components/icons.jsx";
import { SIChart } from "./components/SIChart.jsx";
import { SandarbhaPanel } from "./components/SandarbhaPanel.jsx";
import { JatakaPanel } from "./components/JatakaPanel.jsx";
import { LOYAKSPanel } from "./components/LOYAKSPanel.jsx";
import { VislesanaPanel } from "./components/VislesanaPanel.jsx";

const RAIL = [
  { id:"sandarbha", label:"Sandarbha",  sub:"Reference",   global:true  },
  { id:"rasicakra", label:"Rāśicakra",  sub:"Static Grid", global:true  },
  { id:"jataka",    label:"Jātaka",     sub:"Birth Chart", global:false },
  { id:"loyaks",    label:"LOYAKS",     sub:"Factors",     global:false },
  { id:"vislesana", label:"Viśleṣaṇa",  sub:"Life Areas",  global:false },
];

// Base stay times in ms (Tīvra); multiplied by speed mult
const BASE_STAY = { slow:4, bhava14:6000, bhava58:2500, bhava912:1200, loyaks:2000, vislesana:2500 };

const SPEEDS = [
  { id:"manda",  label:"Manda",  mult:3 },
  { id:"madhya", label:"Madhya", mult:1.5 },
  { id:"tīvra",  label:"Tīvra",  mult:1 },
];

export default function App() {
  const [stage,       setStage]       = useState("sandarbha");
  const [theme,       setTheme]       = useState("dina");
  const [speed,       setSpeed]       = useState("madhya");
  const [visited,     setVisited]     = useState(new Set(["sandarbha"]));
  const [eventKey,    setEventKey]    = useState(null);
  const [animStep,    setAnimStep]    = useState(0);
  const [animDone,    setAnimDone]    = useState(false);
  const [animPaused,  setAnimPaused]  = useState(false);
  const [selected,    setSelected]    = useState(1);
  const [highlighted, setHighlighted] = useState(null);
  const [jatakaLog,   setJatakaLog]   = useState([]); // rolling log entries

  const animStepRef  = useRef(0);
  const animTimer    = useRef(null);
  const pausedRef    = useRef(false);
  const th = THEMES[theme];
  const speedMult = SPEEDS.find(s=>s.id===speed)?.mult||1.5;
  const event = eventKey ? BIRTH_EVENTS[eventKey] : null;
  const map   = event ? buildMap(event) : null;

  const logRef = useRef(null);

  // Build a log entry for bhāva b
  const makeLogEntry = useCallback((b, ev) => {
    const bt = ev?.bhavaTexts[b];
    if (!bt) return null;
    const rId = ((ev.lagna-1+b-1)%12)+1;
    return { b, rId, header:bt.header, bullets:bt.bullets };
  },[]);

  const buildFullJatakaLog = useCallback((ev) => {
    if (!ev) return [];
    return Array.from({length:12},(_,i)=>makeLogEntry(i+1,ev)).filter(Boolean);
  },[makeLogEntry]);

  // Append one entry to the rolling log
  const appendLog = useCallback((b, ev)=>{
    const entry = makeLogEntry(b, ev);
    if (!entry) return;
    setJatakaLog(prev=>[...prev, entry]);
    setHighlighted([b]);
    setTimeout(()=>{
      if (logRef.current) logRef.current.scrollTop = logRef.current.scrollHeight;
    }, 50);
  },[makeLogEntry]);

  const completeJataka = useCallback((ev) => {
    if (animTimer.current) clearTimeout(animTimer.current);
    pausedRef.current=false;
    setAnimPaused(false);
    if (ev) {
      setJatakaLog(buildFullJatakaLog(ev));
    }
    animStepRef.current=13;
    setHighlighted(null);
    setAnimStep(13);
    setAnimDone(true);
  },[buildFullJatakaLog]);

  const goTo = useCallback((id) => {
    if ((id==="loyaks" || id==="vislesana") && event && !animDone) {
      completeJataka(event);
    }
    setStage(id);
    setVisited(v=>new Set([...v,id]));
    setHighlighted(null);
  },[animDone,completeJataka,event]);

  // Core advance function
  const advanceTo = useCallback((b, ev)=>{
    if (b>12) {
      setTimeout(()=>completeJataka(ev),400*speedMult);
      return;
    }
    animStepRef.current=b;
    setAnimStep(b);
    appendLog(b, ev);
    if (!pausedRef.current) {
      const base = b<=4 ? BASE_STAY.bhava14 : b<=8 ? BASE_STAY.bhava58 : BASE_STAY.bhava912;
      animTimer.current=setTimeout(()=>{
        if (!pausedRef.current) advanceTo(b+1, ev);
      }, base*speedMult);
    }
  },[speedMult,appendLog,completeJataka]);

  const applyLagna = useCallback(()=>{
    if (!event) return;
    if (animTimer.current) clearTimeout(animTimer.current);
    pausedRef.current=false;
    setAnimPaused(false);
    setAnimStep(0); setAnimDone(false); setSelected(1);
    setJatakaLog([]);
    setHighlighted(null);
    setTimeout(()=>advanceTo(1, event), 80);
  },[event,advanceTo]);

  const handlePause = useCallback(()=>{
    if (animPaused) {
      pausedRef.current=false; setAnimPaused(false);
      advanceTo(animStepRef.current+1, event);
    } else {
      pausedRef.current=true; setAnimPaused(true);
      if (animTimer.current) clearTimeout(animTimer.current);
    }
  },[animPaused,advanceTo,event]);

  const handlePrev = useCallback(()=>{
    pausedRef.current=true; setAnimPaused(true);
    if (animTimer.current) clearTimeout(animTimer.current);
    const target=Math.max(1,animStepRef.current-1);
    animStepRef.current=target;
    setAnimStep(target);
    // Trim log back to target entries
    setJatakaLog(prev=>prev.slice(0,target));
    if (event) appendLog(target, event);
  },[appendLog,event]);

  const handleNext = useCallback(()=>{
    pausedRef.current=true; setAnimPaused(true);
    if (animTimer.current) clearTimeout(animTimer.current);
    if (animStepRef.current>=12) {
      completeJataka(event);
      return;
    }
    const target=Math.min(12,animStepRef.current+1);
    animStepRef.current=target;
    setAnimStep(target);
    if (event) appendLog(target, event);
  },[appendLog,completeJataka,event]);

  const handleFF = useCallback(()=>{
    completeJataka(event);
  },[completeJataka,event]);

  const handleRew = useCallback(()=>{
    if (animTimer.current) clearTimeout(animTimer.current);
    pausedRef.current=false; setAnimPaused(false);
    setJatakaLog([]); setAnimStep(0); setAnimDone(false); setHighlighted(null);
    setTimeout(()=>advanceTo(1, event),80);
  },[advanceTo,event]);

  const handleReset = useCallback(()=>{
    if (animTimer.current) clearTimeout(animTimer.current);
    pausedRef.current=false;
    setEventKey(null); setAnimStep(0); setAnimDone(false);
    setAnimPaused(false); setJatakaLog([]); setHighlighted(null); setSelected(1);
  },[]);

  useEffect(()=>()=>{ if(animTimer.current) clearTimeout(animTimer.current); },[]);

  useEffect(()=>{
    if (animDone && event && jatakaLog.length===0) {
      setJatakaLog(buildFullJatakaLog(event));
    }
  },[animDone,buildFullJatakaLog,event,jatakaLog.length]);

  const handleHighlight = useCallback((bList)=>{
    setHighlighted(bList&&bList.length?bList:null);
  },[]);

  const showChart = ["rasicakra","jataka","loyaks","vislesana"].includes(stage);
  const chartMode = stage==="rasicakra"?"rasicakra":"jataka";
  const showGrahas = animDone && stage!=="rasicakra";
  const loyaksSpeedMs = 2000*speedMult;
  const vislesanaSpeedMs = 2500*speedMult;

  return (
    <div style={{ minHeight:"100vh", background:th.bg, color:th.text,
      fontFamily:"Georgia,serif", transition:"background 0.4s" }}>
      <style>{`
        *{box-sizing:border-box;}
        ::-webkit-scrollbar{width:4px;height:4px;}
        ::-webkit-scrollbar-thumb{background:#c4a87044;border-radius:2px;}
        @keyframes fadeIn{from{opacity:0;transform:translateY(6px)}to{opacity:1;transform:translateY(0)}}
        @keyframes pulse{0%,100%{opacity:.6}50%{opacity:1}}
        @keyframes hlPulse{0%{opacity:0.5}50%{opacity:1}100%{opacity:0.5}}
        @keyframes hlRing{0%{stroke-width:1.5;opacity:0.6}50%{stroke-width:4;opacity:1}100%{stroke-width:1.5;opacity:0.6}}
        @keyframes hlFill{0%{opacity:0.18}50%{opacity:0.55}100%{opacity:0.18}}
        .topbar{display:flex;justify-content:space-between;align-items:center;padding:7px 0 5px;gap:6px;flex-wrap:wrap;}
        .rail{display:flex;border-radius:8px;overflow:hidden;margin-bottom:12px;}
        .rail-btn{flex:1;border:none;padding:6px 3px;cursor:pointer;transition:all 0.2s;border-bottom-width:2px;border-bottom-style:solid;}
        .rail-label{font-size:13px;font-family:Georgia,serif;}
        .rail-sub{font-size:10px;margin-top:1px;}
        .main-grid{display:grid;gap:14px;align-items:start;}
        .chart-col{position:sticky;top:8px;align-self:start;}
        .panel-col{border-radius:8px;padding:14px;max-height:calc(100vh - 126px);overflow-y:auto;}
        .static-narrator{margin-bottom:10px!important;padding-left:8px!important;line-height:1.55!important;}
        .narration-log{padding:10px 12px!important;}
        .narration-entry{padding-left:9px!important;margin-bottom:11px!important;}
        .narration-row{gap:6px!important;margin-bottom:3px!important;}
        @media(max-width:600px){
          .topbar{padding:5px 0 3px;}
          .t-title{font-size:18px!important;letter-spacing:1px!important;}
          .t-sub{display:none;}
          .rail{overflow-x:auto;-webkit-overflow-scrolling:touch;border-radius:8px;flex-shrink:0;}
          .rail-btn{flex:0 0 auto;min-width:64px;padding:6px 2px;}
          .rail-label{font-size:12px;}
          .rail-sub{display:none;}
          .main-grid{grid-template-columns:1fr!important;}
          .chart-col{max-width:100%;position:sticky;top:0;z-index:2;}
          .panel-col{padding:10px;max-height:46vh;overflow-y:auto;}
          .static-narrator{margin-bottom:7px!important;padding-left:6px!important;line-height:1.4!important;}
          .narration-log{padding:7px 8px!important;}
          .narration-entry{padding-left:7px!important;margin-bottom:8px!important;}
          .narration-row{gap:5px!important;margin-bottom:2px!important;}
          .ctrl-btn{padding:2px 6px!important;font-size:12px!important;}
          .theme-btn{padding:2px 7px!important;font-size:13px!important;}
          .outer-pad{padding-left:5px!important;padding-right:5px!important;}
        }
      `}</style>

      {/* Mandala */}
      <svg style={{ position:"fixed",top:"50%",left:"50%",transform:"translate(-50%,-50%)",
        opacity:theme==="dina"?.04:.025,pointerEvents:"none",zIndex:0 }} width={500} height={500}>
        {[50,90,130,170,210,250].map((r,i)=>(
          <circle key={r} cx={250} cy={250} r={r} fill="none"
            stroke={theme==="dina"?"#8a6020":theme==="sandhyā"?"#e07840":"#f0d060"}
            strokeWidth={0.5} strokeDasharray={`${r*.25} ${r*.08}`}
            transform={`rotate(${i*8} 250 250)`}/>
        ))}
      </svg>

      <div style={{ position:"relative",zIndex:1,maxWidth:920,margin:"0 auto",padding:"0 10px 24px" }}>

        {/* TOP BAR — compressed */}
        <div className="topbar">
          <div>
            <div className="t-title" style={{ fontSize:21,fontWeight:"normal",letterSpacing:2,color:th.text }}>
              Jyotiṣa Bodha
            </div>
            <div className="t-sub" style={{ fontSize:11,color:th.textFaint,letterSpacing:3,marginTop:1 }}>
              ALGORITHMIC FRAMEWORK · PEDAGOGIC YANTRA
            </div>
          </div>
          <div style={{ display:"flex",gap:4,alignItems:"center",flexWrap:"wrap" }}>
            {/* Theme icons */}
            {[{id:"rātri",icon:"☽"},{id:"sandhyā",icon:"◑"},{id:"dina",icon:"☀"}].map(t=>(
              <button key={t.id} className="theme-btn" onClick={()=>setTheme(t.id)} title={t.id} style={{
                background:theme===t.id?th.inputBg:"none",
                border:`1px solid ${theme===t.id?th.accent:th.panelBorder}`,
                color:theme===t.id?th.text:th.textDim,
                borderRadius:20,padding:"2px 9px",cursor:"pointer",fontSize:14,
              }}>{t.icon}</button>
            ))}
            <span style={{ color:th.textFaint,fontSize:13,padding:"0 2px" }}>|</span>
            {/* Speed — chevrons with IAST tooltip */}
            {[
              {id:"manda", icon:"▸",   title:"Manda — slow"},
              {id:"madhya",icon:"▸▸",  title:"Madhya — normal"},
              {id:"tīvra", icon:"▸▸▸", title:"Tīvra — fast"},
            ].map(s=>(
              <button key={s.id} className="ctrl-btn" onClick={()=>setSpeed(s.id)} title={s.title} style={{
                background:speed===s.id?th.inputBg:"none",
                border:`1px solid ${speed===s.id?th.accent:th.panelBorder}`,
                color:speed===s.id?th.text:th.textDim,
                borderRadius:3,padding:"2px 8px",cursor:"pointer",fontSize:13,letterSpacing:1,
              }}>{s.icon}</button>
            ))}
          </div>
        </div>

        {/* RAIL — 5 buttons desktop, 2×3 grid mobile */}
        <div className="rail" style={{ background:th.railBg,border:`1px solid ${th.railBorder}` }}>
          {RAIL.map((r,i)=>{
            const isCur=stage===r.id; const isVis=visited.has(r.id);
            return (
              <button key={r.id} className="rail-btn" onClick={()=>goTo(r.id)} style={{
                background:isCur?th.inputBg:"none",
                borderRight:i<RAIL.length-1?`1px solid ${th.railBorder}`:"none",
                borderBottomColor:isCur?th.accent:"transparent",
              }}>
                <div className="rail-label" style={{
                  color:isCur?th.accent:isVis?th.text:th.textFaint,
                  fontWeight:isCur?"bold":"normal",
                }}>{isVis&&!isCur?"✓ ":""}{r.label}</div>
                <div className="rail-sub" style={{ color:th.textFaint }}>
                  {r.global?"Global":"Janma"}
                </div>
              </button>
            );
          })}
        </div>

        {/* MAIN GRID */}
        <div className="main-grid" style={{
          gridTemplateColumns:showChart?"minmax(0,305px) minmax(0,1fr)":"1fr",
        }}>

          {/* CHART COLUMN */}
          {showChart&&(
            <div className="chart-col">
              <div style={{ display:"flex",gap:6,marginBottom:5,fontSize:12,color:th.textFaint,flexWrap:"wrap" }}>
                <span>↑ Ucca</span><span>↓ Nīca</span><span>◆ Svak</span>
                {animDone&&<>
                  <span style={{ display:"inline-flex",alignItems:"center",gap:2 }}><KendraIcon size={11}/> Ke</span>
                  <span style={{ display:"inline-flex",alignItems:"center",gap:2 }}><TrikonaIcon size={11}/> Tri</span>
                  <span style={{ display:"inline-flex",alignItems:"center",gap:2 }}><DusthanaIcon size={11}/> Du</span>
                </>}
              </div>

              <SIChart event={event} map={map} selected={selected}
                onSelect={setSelected} highlighted={highlighted}
                chartMode={chartMode} animStep={animStep} th={th} showGrahas={showGrahas}/>

              {animDone&&event&&(
                <div style={{ marginTop:7,display:"flex",gap:10,fontSize:13,color:th.textDim,flexWrap:"wrap" }}>
                  <span>Lagna: <span style={{ color:"#e8c040" }}>{event.lagnaName}</span></span>
                  <span>Lagneśa: <span style={{ color:GRAHAS[RASIS[event.lagna-1].lordId].color }}>
                    {GRAHAS[RASIS[event.lagna-1].lordId].iast}
                  </span></span>
                  {map&&<span>B{bhavaOf(event.pos[RASIS[event.lagna-1].lordId],event.lagna)}</span>}
                </div>
              )}
            </div>
          )}

          {/* PANEL COLUMN */}
          <div className="panel-col" style={{ background:th.panelBg,border:`1px solid ${th.panelBorder}` }}>
            {stage==="sandarbha"&&<SandarbhaPanel th={th}/>}

            {stage==="rasicakra"&&(
              <div>
                <div style={{ fontSize:13,color:th.textDim,letterSpacing:2,marginBottom:10 }}>RĀŚICAKRA · The Universal Grid</div>
                <div className="static-narrator" style={{ fontSize:15,color:th.textFaint,marginBottom:16,lineHeight:1.8,
                  borderLeft:`2px solid ${th.panelBorder}`,paddingLeft:10 }}>
                  The Rāśicakra is the birth-independent template. All twelve rāśis hold fixed positions — Meṣa always second from left on the top row, proceeding clockwise. What you see in each cell is from the Sandarbha: svāmī, ucca, nīca, svakṣetra. No birth event alters these.
                </div>
                {[["↑ Ucca","Exaltation — the rāśi where a graha reaches maximum strength."],
                  ["↓ Nīca","Debilitation — always the 7th rāśi from the ucca. The graha is at its weakest."],
                  ["◆ Svakṣetra","Own sign — comfortable and effective, though not as potent as ucca."],
                  ["Svāmī","The natural lord of each rāśi — shown in colour. A birth-independent relationship."],
                ].map(([t,d])=>(
                  <div key={t} style={{ marginBottom:12,borderLeft:`2px solid ${th.panelBorder}`,paddingLeft:10 }}>
                    <div style={{ fontSize:16,color:th.text,marginBottom:3 }}>{t}</div>
                    <div style={{ fontSize:15,color:th.textDim,lineHeight:1.7 }}>{d}</div>
                  </div>
                ))}
                <button onClick={()=>goTo("jataka")} style={{
                  marginTop:10,background:th.inputBg,border:`1px solid ${th.panelBorder}`,
                  color:th.text,borderRadius:4,padding:"8px 18px",cursor:"pointer",fontSize:15,
                }}>Proceed to Jātaka →</button>
              </div>
            )}

            {stage==="jataka"&&(
              <JatakaPanel
                selectedEvent={event}
                onSelectEvent={k=>{setEventKey(k);setAnimStep(0);setAnimDone(false);setJatakaLog([]);setHighlighted(null);}}
                onApply={applyLagna}
                onReset={handleReset}
                animStep={animStep} animDone={animDone} animPaused={animPaused}
                th={th} jatakaLog={jatakaLog} logRef={logRef}
                onHighlight={handleHighlight}
                onPause={handlePause} onPrev={handlePrev}
                onNext={handleNext} onFF={handleFF} onRew={handleRew}
                onProceed={()=>goTo("loyaks")}
              />
            )}

            {stage==="loyaks"&&!animDone&&(
              <div style={{ fontSize:15,color:th.textFaint,fontStyle:"italic" }}>
                Complete the Jātaka first — select a birth event and apply the lagna.
                {event&&(
                  <button onClick={()=>completeJataka(event)} style={{
                    display:"block", marginTop:10, background:th.inputBg,
                    border:`1px solid ${th.panelBorder}`, color:th.text,
                    borderRadius:4, padding:"7px 14px", cursor:"pointer",
                    fontSize:15, fontFamily:"Georgia,serif",
                  }}>Finish Jātaka</button>
                )}
              </div>
            )}
            {stage==="loyaks"&&animDone&&map&&event&&(
              <LOYAKSPanel event={event} map={map} selected={selected}
                th={th} onHighlight={handleHighlight} speedMs={loyaksSpeedMs}/>
            )}

            {stage==="vislesana"&&!animDone&&(
              <div style={{ fontSize:15,color:th.textFaint,fontStyle:"italic" }}>
                Complete the Jātaka first — select a birth event and apply the lagna.
                {event&&(
                  <button onClick={()=>completeJataka(event)} style={{
                    display:"block", marginTop:10, background:th.inputBg,
                    border:`1px solid ${th.panelBorder}`, color:th.text,
                    borderRadius:4, padding:"7px 14px", cursor:"pointer",
                    fontSize:15, fontFamily:"Georgia,serif",
                  }}>Finish Jātaka</button>
                )}
              </div>
            )}
            {stage==="vislesana"&&animDone&&map&&event&&(
              <VislesanaPanel event={event} map={map} th={th}
                onHighlight={handleHighlight} speedMs={vislesanaSpeedMs}/>
            )}
          </div>
        </div>

        <div style={{ marginTop:24,fontSize:12,color:th.textFaint,opacity:.35,textAlign:"center",letterSpacing:2 }}>
          JANMA PATRĪ · DARŚANA YANTRA · PEDAGOGIC USE ONLY
        </div>
      </div>
    </div>
  );
}
