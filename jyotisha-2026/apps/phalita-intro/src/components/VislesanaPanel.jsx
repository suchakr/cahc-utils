import { useState, useEffect, useRef, useCallback } from "react";
import { LIFE_AREAS } from "../data/static.js";
import { buildAnalysisLog } from "../utils/jyotisha.js";

export function VislesanaPanel({ event, map, th, onHighlight, speedMs }) {
  const [areaKey,  setAreaKey]  = useState("career");
  const [logItems, setLogItems] = useState([]);
  const [running,  setRunning]  = useState(false);
  const [done,     setDone]     = useState(false);
  const timers = useRef([]);
  const logRef = useRef(null);

  const runAnalysis = useCallback(()=>{
    timers.current.forEach(clearTimeout); timers.current=[];
    setLogItems([]); setDone(false); setRunning(true); onHighlight([]);
    const log = buildAnalysisLog(event, map, areaKey);
    log.forEach((item,i)=>{
      const t=setTimeout(()=>{
        setLogItems(prev=>[...prev,item]);
        if(item.highlight) onHighlight(item.highlight);
        if(logRef.current) logRef.current.scrollTop=logRef.current.scrollHeight;
        if(i===log.length-1){setRunning(false);setDone(true);}
      }, speedMs*i);
      timers.current.push(t);
    });
  },[event,map,areaKey,speedMs,onHighlight]);

  useEffect(()=>()=>timers.current.forEach(clearTimeout),[]);

  return (
    <div>
      <div style={{ fontSize:13, color:th.textDim, letterSpacing:2, marginBottom:8 }}>VIŚLEṢAṆA · Life-Area Analysis</div>

      <button onClick={runAnalysis} disabled={running} style={{
        width:"100%", background:running?"none":th.inputBg,
        border:`1.5px solid ${running?th.panelBorder:th.accent}`,
        color:running?th.textFaint:th.text,
        borderRadius:4, padding:"9px", cursor:running?"not-allowed":"pointer",
        fontSize:15, fontFamily:"Georgia,serif", marginBottom:10,
      }}>{running?"▶ Applying rules…":done?"↺ Re-analyse":"▶ Analyse"}</button>

      <div style={{ display:"flex", gap:8, flexWrap:"wrap", marginBottom:10 }}>
        {Object.entries(LIFE_AREAS).map(([key,a])=>(
          <button key={key}
            onClick={()=>{setAreaKey(key);setLogItems([]);setDone(false);onHighlight([]);}}
            style={{
              background:areaKey===key?th.inputBg:"none",
              border:`1.5px solid ${areaKey===key?th.accent:th.panelBorder}`,
              color:areaKey===key?th.text:th.textDim,
              borderRadius:4, padding:"6px 14px", cursor:"pointer",
              fontSize:15, fontFamily:"Georgia,serif",
            }}>{a.icon} {a.iast}</button>
        ))}
      </div>
      <div ref={logRef} className="narration-log" style={{ background:th.logBg, border:`1px solid ${th.panelBorder}`,
        borderRadius:4, padding:"14px 16px", fontFamily:"Georgia,serif" }}>
        {logItems.length===0&&(
          <div style={{ color:th.textFaint, fontSize:15, fontStyle:"italic" }}>
            Select a life area and press Analyse…
          </div>
        )}
        {logItems.map((item,i)=>{
          if(item.type==="divider") return <hr key={i} style={{ border:"none", borderTop:`1px solid ${th.panelBorder}`, margin:"14px 0" }}/>;
          if(item.type==="head") return <div key={i} style={{ fontSize:18,color:th.text,fontWeight:"bold",marginBottom:6,animation:"fadeIn 0.5s ease" }}>{item.text}</div>;
          if(item.type==="info") return (
            <div key={i} className="narration-entry" style={{ marginBottom:12, animation:"fadeIn 0.5s ease" }}>
              {item.bullets.map((b2,bi)=>(
                <div className="narration-row" key={bi} style={{ display:"flex",gap:8,marginBottom:4,alignItems:"flex-start" }}>
                  <span style={{ color:th.textDim,fontSize:15,flexShrink:0 }}>•</span>
                  <span style={{ fontSize:15,color:th.textDim,lineHeight:1.8 }}>{b2}</span>
                </div>
              ))}
            </div>
          );
          if(item.type==="bhava") return (
            <div key={i} className="narration-entry" style={{ marginTop:16,paddingTop:10,borderTop:`1px solid ${th.panelBorder}`,animation:"fadeIn 0.5s ease" }}>
              <div style={{ fontSize:16,color:th.text,fontWeight:"bold",marginBottom:3 }}>▸ {item.text}</div>
              <div style={{ fontSize:13,color:"#8888c0",fontStyle:"italic",marginBottom:6 }}>{item.sandarbha}</div>
            </div>
          );
          if(item.type==="rule") return (
            <div key={i} className="narration-entry" style={{ borderLeft:`3px solid ${item.col||th.textDim}`,paddingLeft:12,marginBottom:12,animation:"fadeIn 0.5s ease" }}>
              <div className="narration-row" style={{ display:"flex",alignItems:"center",gap:8,marginBottom:4 }}>
                <span style={{ fontSize:18,fontWeight:"bold",fontFamily:"monospace",color:th.text,minWidth:18 }}>{item.letter}</span>
                {item.score!==0&&item.score!==undefined&&(
                  <span style={{ fontSize:14,color:item.score>0?"#50c080":"#d04040",marginLeft:"auto" }}>
                    {item.score>0?`+${item.score}`:item.score}
                  </span>
                )}
              </div>
              {item.bullets.map((b2,bi)=>(
                <div className="narration-row" key={bi} style={{ display:"flex",gap:8,marginBottom:4,alignItems:"flex-start" }}>
                  <span style={{ color:item.col,fontSize:14,flexShrink:0,marginTop:2 }}>•</span>
                  <span style={{ fontSize:15,color:bi===0?item.col:th.textDim,lineHeight:1.8 }}>{b2}</span>
                </div>
              ))}
            </div>
          );
          if(item.type==="verdict") return (
            <div key={i} className="narration-entry" style={{ background:th.inputBg,border:`1px solid ${item.col}`,borderRadius:4,padding:"12px 16px",animation:"fadeIn 0.5s ease" }}>
              <div style={{ fontSize:17,color:item.col,fontWeight:"bold",marginBottom:8 }}>◉ {item.text}</div>
              {item.bullets.map((b2,bi)=>(
                <div className="narration-row" key={bi} style={{ display:"flex",gap:8,marginBottom:4,alignItems:"flex-start" }}>
                  <span style={{ color:item.col,fontSize:14,flexShrink:0,marginTop:2 }}>•</span>
                  <span style={{ fontSize:15,color:th.textDim,lineHeight:1.8 }}>{b2}</span>
                </div>
              ))}
            </div>
          );
          return null;
        })}
      </div>
    </div>
  );
}

// ═══════════════════════════════════════════════════════════════════════════════
// MAIN APP
// ═══════════════════════════════════════════════════════════════════════════════
