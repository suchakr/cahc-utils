import { BIRTH_EVENTS } from "../data/birthEvents.js";
import { BHAVA_TYPES } from "../data/static.js";
import { KendraIcon, TrikonaIcon, DusthanaIcon } from "./icons.jsx";

export function JatakaPanel({ selectedEvent, onSelectEvent, onApply, onReset, animStep, animDone, animPaused, th, jatakaLog, logRef, onHighlight, onPause, onPrev, onNext, onFF, onRew, onProceed }) {
  const isAnimating = animStep>0 && !animDone;
  const hasLog = jatakaLog.length>0;

  // Accent colour per bhāva type for left border
  function entryAccent(b) {
    const t = BHAVA_TYPES[b]||[];
    if (t.includes("Kendra")&&t.includes("Trikona")) return "#d8b030";
    if (t.includes("Kendra"))   return "#5090ff";
    if (t.includes("Trikona"))  return "#50c078";
    if (t.includes("Dusthāna")) return "#c05040";
    return "#888";
  }

  return (
    <div>
      <div style={{ fontSize:13, color:th.textDim, letterSpacing:2, marginBottom:10 }}>JĀTAKA · Birth Chart</div>
      <div className="static-narrator" style={{ fontSize:15, color:th.textFaint, marginBottom:14, lineHeight:1.8,
        borderLeft:`2px solid ${th.panelBorder}`, paddingLeft:10 }}>
        A Jātaka is a Rāśicakra made personal. The Lagna seeds a coordinate transformation — every rāśi receives a bhāva number, and the native's grahas are placed on the grid.
      </div>

      {/* Birth event cards — only before animation starts */}
      {!hasLog && (
        <>
          <div style={{ fontSize:15, color:th.textDim, marginBottom:10 }}>Select a birth event:</div>
          <div style={{ display:"flex", flexDirection:"column", gap:10, marginBottom:14 }}>
            {Object.values(BIRTH_EVENTS).map(ev=>(
              <div key={ev.id} onClick={()=>onSelectEvent(ev.id)} style={{
                border:`1.5px solid ${selectedEvent?.id===ev.id?th.accent:th.panelBorder}`,
                background:selectedEvent?.id===ev.id?th.inputBg:"none",
                borderRadius:6, padding:"12px 14px", cursor:"pointer", transition:"all 0.2s",
              }}>
                <div style={{ display:"flex", justifyContent:"space-between", alignItems:"baseline" }}>
                  <span style={{ fontSize:16, color:th.text, fontWeight:"bold", fontFamily:"Georgia,serif" }}>{ev.label}</span>
                  <span style={{ fontSize:14, color:th.textDim }}>{ev.date}</span>
                </div>
                <div style={{ fontSize:14, color:th.textDim, marginTop:4, fontStyle:"italic" }}>{ev.description}</div>
                <div style={{ fontSize:14, color:"#e8c040", marginTop:6 }}>Lagna: {ev.lagnaName}</div>
              </div>
            ))}
          </div>
          {selectedEvent && (
            <button onClick={onApply} style={{
              width:"100%", background:"rgba(232,192,64,0.12)",
              border:`1.5px solid #e8c040`, color:"#e8c040",
              borderRadius:4, padding:"10px", cursor:"pointer",
              fontSize:16, fontFamily:"Georgia,serif", marginBottom:12,
            }}>▶ Apply Lagna → Animate Jātaka</button>
          )}
        </>
      )}

      {/* Reset */}
      {hasLog && (
        <button onClick={onReset} style={{
          background:"none", border:`1px solid ${th.panelBorder}`,
          color:th.textDim, borderRadius:4, padding:"6px 14px",
          cursor:"pointer", fontSize:14, fontFamily:"Georgia,serif", marginBottom:12,
        }}>↺ Reset — choose another event</button>
      )}

      {/* Playback controls */}
      {isAnimating && (
        <div style={{ marginBottom:12 }}>
          <div style={{ fontSize:14, color:th.textDim, marginBottom:8, textAlign:"center",
            fontStyle:"italic", animation:"pulse 1.5s infinite" }}>
            Assigning bhāva {animStep} of 12…
          </div>
          <div style={{ display:"flex", justifyContent:"center", gap:8 }}>
            {[
              { label:"⏮", title:"Restart",       fn:onRew   },
              { label:"◀", title:"Previous bhāva", fn:onPrev  },
              { label:animPaused?"▶":"⏸", title:animPaused?"Resume":"Pause", fn:onPause },
              { label:"▶", title:"Next bhāva",     fn:onNext  },
              { label:"⏭", title:"Jump to end",    fn:onFF    },
            ].map(({label,title,fn})=>(
              <button key={title} onClick={fn} title={title} style={{
                background:th.inputBg, border:`1px solid ${th.panelBorder}`,
                color:th.text, borderRadius:4, padding:"6px 12px",
                cursor:"pointer", fontSize:17, minWidth:38,
              }}>{label}</button>
            ))}
          </div>
        </div>
      )}

      {/* After completion — replay/FF controls */}
      {animDone && hasLog && (
        <div style={{ display:"flex", gap:8, marginBottom:12, flexWrap:"wrap" }}>
          <button onClick={onRew} style={{
            background:th.inputBg, border:`1px solid ${th.panelBorder}`,
            color:th.textDim, borderRadius:4, padding:"5px 12px",
            cursor:"pointer", fontSize:14,
          }}>⏮ Replay</button>
          <button onClick={onFF} style={{
            background:th.inputBg, border:`1px solid ${th.panelBorder}`,
            color:th.textDim, borderRadius:4, padding:"5px 12px",
            cursor:"pointer", fontSize:14,
          }}>⏭ Jump to end</button>
          <div style={{ fontSize:14, color:"#50c080", alignSelf:"center" }}>
            ✓ Jātaka complete
          </div>
          <button onClick={onProceed} style={{
            marginLeft:"auto", background:th.inputBg, border:`1px solid ${th.panelBorder}`,
            color:th.text, borderRadius:4, padding:"6px 14px",
            cursor:"pointer", fontSize:15, fontFamily:"Georgia,serif",
          }}>Proceed to LOYAKS →</button>
        </div>
      )}

      {/* Rolling log — same LOYAKS style */}
      {hasLog && (
        <div
          ref={logRef}
          style={{
            background:th.logBg, border:`1px solid ${th.panelBorder}`,
            borderRadius:6, padding:"12px 14px",
            // A during animation: fixed height + scroll; B after: expand
            maxHeight: animDone ? "none" : 360,
            overflowY: animDone ? "visible" : "auto",
            transition:"max-height 0.5s ease",
          }}
          className="narration-log">
          {jatakaLog.map((entry, idx)=>{
            const isActive = animStep===entry.b && !animDone;
            const accent   = entryAccent(entry.b);
            const types    = BHAVA_TYPES[entry.b]||[];
            return (
              <div
                key={idx}
                onClick={()=>onHighlight([entry.b])}
                style={{
                  borderLeft:`3px solid ${accent}`,
                  paddingLeft:12, marginBottom:16,
                  background: isActive ? `${accent}12` : "none",
                  borderRadius: isActive ? "0 4px 4px 0" : 0,
                  cursor:"pointer",
                  animation:"fadeIn 0.4s ease",
                  transition:"background 0.3s",
                }}
                className="narration-entry"
                title="Click to highlight this bhāva in chart"
              >
                {/* Header row */}
                <div className="narration-row" style={{ display:"flex", alignItems:"center", gap:8, marginBottom:6 }}>
                  <span style={{ fontSize:14, color:accent, fontWeight:"bold",
                    fontFamily:"monospace", minWidth:22 }}>B{entry.b}</span>
                  <span style={{ fontSize:15, color:th.text, fontWeight:"bold",
                    fontFamily:"Georgia,serif" }}>{entry.header}</span>
                  {/* Type icons inline */}
                  <span style={{ marginLeft:"auto", display:"inline-flex", gap:4, alignItems:"center" }}>
                    {types.includes("Kendra")   && <KendraIcon   size={12}/>}
                    {types.includes("Trikona")  && <TrikonaIcon  size={12}/>}
                    {types.includes("Dusthāna") && <DusthanaIcon size={12}/>}
                  </span>
                </div>
                {/* Bullets */}
                {entry.bullets.map((bullet, bi)=>(
                  <div className="narration-row" key={bi} style={{ display:"flex", gap:8, marginBottom:5, alignItems:"flex-start" }}>
                    <span style={{ color:accent, fontSize:15, flexShrink:0, marginTop:1 }}>•</span>
                    <span style={{ fontSize:15, color:bi===0?th.text:th.textDim, lineHeight:1.8 }}>
                      {bullet}
                    </span>
                  </div>
                ))}
              </div>
            );
          })}

          {/* Animated cursor during playback */}
          {isAnimating && (
            <div style={{ fontSize:14, color:th.textFaint, fontStyle:"italic",
              animation:"pulse 1s infinite", paddingLeft:12 }}>▌</div>
          )}
        </div>
      )}
    </div>
  );
}

// ═══════════════════════════════════════════════════════════════════════════════
// LOYAKS PANEL
// ═══════════════════════════════════════════════════════════════════════════════
