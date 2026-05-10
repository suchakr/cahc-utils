import { useCallback } from "react";
import { RASIS, GRAHAS, BHAVA_TYPES, BHAVA_THEMES, SI_POS } from "../data/static.js";
import { bhavaOf, dignity, staticAnnotations } from "../utils/jyotisha.js";

export function SIChart({ event, map, selected, onSelect, highlighted, chartMode, animStep, th, showGrahas }) {
  const S=300, C=75;
  const isHL = useCallback((b)=>Array.isArray(highlighted)?highlighted.includes(b):highlighted===b,[highlighted]);

  function cellFill(b) {
    const t=BHAVA_TYPES[b]||[];
    if (isHL(b)) return "transparent"; // animated overlay handles fill
    if (b===selected&&chartMode==="jataka") return th.name==="dina"?"rgba(200,160,40,0.18)":"rgba(232,192,64,0.16)";
    if (t.includes("Kendra")&&t.includes("Trikona")) return th.name==="dina"?"rgba(200,175,55,0.13)":"rgba(200,175,55,0.08)";
    if (t.includes("Kendra"))   return th.name==="dina"?"rgba(55,110,210,0.11)":"rgba(55,110,210,0.07)";
    if (t.includes("Trikona"))  return th.name==="dina"?"rgba(55,170,90,0.11)":"rgba(55,170,90,0.07)";
    if (t.includes("Dusthāna")) return th.name==="dina"?"rgba(190,55,35,0.09)":"rgba(190,55,35,0.06)";
    return th.cellBg;
  }

  function cellStroke(b) {
    if (isHL(b)) return "transparent"; // animated overlay handles stroke
    if (b===selected&&chartMode==="jataka") return "#e8c04099";
    return th.cellBorder;
  }

  return (
    <svg viewBox={`0 0 ${S} ${S}`} style={{ display:"block", width:"100%", maxWidth:S, height:"auto" }}>
      <rect x={0} y={0} width={S} height={S} fill={th.cellBg}/>

      {Object.entries(SI_POS).map(([rIdStr,[row,col]])=>{
        const rId=parseInt(rIdStr);
        const b=event?bhavaOf(rId,event.lagna):rId;
        const bInfo=map?map[b]:null;
        const x=col*C, y=row*C;
        const ann=staticAnnotations(rId);
        const rāśi=RASIS[rId-1];
        const lord=GRAHAS[rāśi.lordId];
        const bhāvaRevealed=chartMode==="jataka"&&(animStep>=b);
        const grahasRevealed=showGrahas&&chartMode==="jataka";
        const lagnaRevealed=chartMode==="jataka"&&animStep>=1;
        const isLagna=event&&rId===event.lagna;
        const isHighlighted=isHL(b);

        return (
          <g key={rId}
            onClick={()=>chartMode==="jataka"&&animStep>=13&&onSelect&&onSelect(b)}
            style={{ cursor:chartMode==="jataka"&&animStep>=13?"pointer":"default" }}>

            <rect x={x+0.5} y={y+0.5} width={C-1} height={C-1}
              fill={cellFill(chartMode==="jataka"?b:rId)}
              stroke={cellStroke(chartMode==="jataka"?b:rId)}
              strokeWidth={isHighlighted?2.5:1} rx={1}/>

            {/* Dramatic highlight — animated fill + double ring + corner glows */}
            {isHighlighted && (
              <g>
                {/* Animated fill overlay */}
                <rect x={x+0.5} y={y+0.5} width={C-1} height={C-1}
                  fill={th.name==="sandhyā"?"#f09040":"#40d0ff"}
                  rx={1} style={{ animation:"hlFill 1s ease-in-out infinite" }}/>
                {/* Outer ring */}
                <rect x={x+1} y={y+1} width={C-2} height={C-2}
                  fill="none"
                  stroke={th.name==="sandhyā"?"#f09040":"#40d0ff"}
                  strokeWidth={3} rx={2}
                  style={{ animation:"hlRing 1s ease-in-out infinite" }}/>
                {/* Inner ring */}
                <rect x={x+5} y={y+5} width={C-10} height={C-10}
                  fill="none"
                  stroke={th.name==="sandhyā"?"rgba(240,144,64,0.5)":"rgba(64,208,255,0.5)"}
                  strokeWidth={1.5} rx={2}
                  style={{ animation:"hlRing 1s ease-in-out infinite 0.15s" }}/>
                {/* Corner accent dots */}
                {[[x+4,y+4],[x+C-4,y+4],[x+4,y+C-4],[x+C-4,y+C-4]].map(([cx2,cy2],di)=>(
                  <circle key={di} cx={cx2} cy={cy2} r={3}
                    fill={th.name==="sandhyā"?"#f09040":"#40d0ff"}
                    style={{ animation:`hlPulse 1s ease-in-out infinite ${di*0.1}s` }}/>
                ))}
              </g>
            )}

            {/* Lagna marker */}
            {isLagna&&lagnaRevealed&&(
              <>
                <polygon points={`${x+1},${y+1} ${x+22},${y+1} ${x+1},${y+22}`}
                  fill="#e8c04038" stroke="#e8c04077" strokeWidth={0.8}/>
                <text x={x+4} y={y+13} fontSize={11} fill="#e8c040"
                  fontFamily="Georgia,serif" fontWeight="bold">La</text>
              </>
            )}

            {/* Rāśi number */}
            <text x={x+C-4} y={y+13} textAnchor="end"
              fontSize={11} fill={th.textFaint} fontFamily="Georgia,serif">{rId}</text>

            {/* Rāśi name */}
            <text x={x+5} y={y+16} fontSize={13}
              fill={isLagna&&lagnaRevealed?"#e8c040":th.text}
              fontFamily="Georgia,serif" fontWeight={isLagna&&lagnaRevealed?"bold":"normal"}>
              {rāśi.iast}
            </text>

            {/* Lord */}
            <text x={x+5} y={y+29} fontSize={11} fill={lord.color} fontFamily="Georgia,serif">
              {lord.iast.slice(0,4)}
            </text>

            {/* Static annotations */}
            {ann.ucca.map((gId,i)=>(
              <text key={`u${gId}`} x={x+5} y={y+42+i*11}
                fontSize={10.5} fill="#e8c040" fontFamily="Georgia,serif">
                ↑{GRAHAS[gId].iast.slice(0,3)}
              </text>
            ))}
            {ann.nīca.map((gId,i)=>(
              <text key={`n${gId}`} x={x+5} y={y+42+ann.ucca.length*11+i*11}
                fontSize={10.5} fill="#d04040" fontFamily="Georgia,serif">
                ↓{GRAHAS[gId].iast.slice(0,3)}
              </text>
            ))}
            {ann.svak.map((gId,i)=>(
              <text key={`s${gId}`} x={x+C/2+2} y={y+42+i*11}
                fontSize={10.5} fill="#40b070" fontFamily="Georgia,serif">
                ◆{GRAHAS[gId].iast.slice(0,3)}
              </text>
            ))}

            {/* Bhāva number + icons */}
            {bhāvaRevealed&&(()=>{
              const t=BHAVA_TYPES[b]||[];
              return (
                <>
                  <text x={x+4} y={y+C-6} fontSize={11}
                    fill={th.textDim} fontFamily="Georgia,serif" fontStyle="italic">B{b}</text>
                  {/* Kendra icon: ⊙ */}
                  {t.includes("Kendra")&&(
                    <g transform={`translate(${x+C-30},${y+C-16})`}>
                      <circle cx={6} cy={6} r={6} fill="none" stroke="#5090ff" strokeWidth={1.5}/>
                      <circle cx={6} cy={6} r={2.5} fill="#5090ff"/>
                    </g>
                  )}
                  {/* Trikona icon: △ */}
                  {t.includes("Trikona")&&(
                    <g transform={`translate(${x+C-(t.includes("Kendra")?46:30)},${y+C-17})`}>
                      <polygon points="6,1 12,12 0,12" fill="none" stroke="#50c078" strokeWidth={1.5} strokeLinejoin="round"/>
                    </g>
                  )}
                  {/* Dusthāna icon: ● red */}
                  {t.includes("Dusthāna")&&(
                    <circle
                      cx={x+C-(t.includes("Kendra")?46:30)-(t.includes("Trikona")?16:0)-8}
                      cy={y+C-10} r={5} fill="#c05040"/>
                  )}
                </>
              );
            })()}

            {/* Graha tokens */}
            {grahasRevealed&&bInfo&&bInfo.occupants.map((gId,i)=>{
              const g=GRAHAS[gId]; const dig=dignity(gId,rId);
              const gy=y+C-18-i*14;
              return (
                <g key={gId}>
                  <rect x={x+C/2} y={gy-11} width={C/2-5} height={13}
                    rx={2} fill={`${g.color}1e`} stroke={`${g.color}55`} strokeWidth={0.8}/>
                  <text x={x+C/2+4} y={gy} fontSize={11} fill={g.color}
                    fontFamily="Georgia,serif" fontWeight="bold">
                    {g.iast.slice(0,3)}
                  </text>
                  {dig.short&&(
                    <text x={x+C-5} y={gy-2} fontSize={9} fill={dig.col}
                      fontFamily="Georgia,serif">{dig.short}</text>
                  )}
                </g>
              );
            })}
          </g>
        );
      })}

      {/* Centre panel */}
      {(()=>{
        const cx=C, cy=C, w=C*2, h=C*2;
        if (chartMode==="rasicakra") {
          return (
            <g>
              <rect x={cx} y={cy} width={w} height={h} fill={th.centerBg} stroke={th.cellBorder} strokeWidth={1}/>
              <text x={cx+w/2} y={cy+20} textAnchor="middle" fontSize={12} fill={th.textDim} fontFamily="Georgia,serif" letterSpacing={1.5}>RĀŚICAKRA</text>
              <text x={cx+w/2} y={cy+34} textAnchor="middle" fontSize={10.5} fill={th.textFaint} fontFamily="Georgia,serif">Universal · Birth-independent</text>
              <line x1={cx+16} y1={cy+44} x2={cx+w-16} y2={cy+44} stroke={th.cellBorder}/>
              <text x={cx+16} y={cy+62} fontSize={12} fill={th.text} fontFamily="Georgia,serif">↑ Ucca</text>
              <text x={cx+16} y={cy+78} fontSize={12} fill={th.text} fontFamily="Georgia,serif">↓ Nīca</text>
              <text x={cx+16} y={cy+94} fontSize={12} fill={th.text} fontFamily="Georgia,serif">◆ Svakṣetra</text>
              <line x1={cx+16} y1={cy+104} x2={cx+w-16} y2={cy+104} stroke={th.cellBorder}/>
              <text x={cx+w/2} y={cy+120} textAnchor="middle" fontSize={10.5} fill={th.textFaint} fontFamily="Georgia,serif" fontStyle="italic">Proceed to Jātaka →</text>
            </g>
          );
        }
        if (animStep>0&&animStep<13) {
          const lagId=event?.lagna||4;
          const curRId=((lagId-1+animStep-1)%12)+1;
          return (
            <g>
              <rect x={cx} y={cy} width={w} height={h} fill={th.centerBg} stroke="#e8c04044" strokeWidth={1}/>
              <text x={cx+w/2} y={cy+22} textAnchor="middle" fontSize={11} fill="#e8c04099" fontFamily="Georgia,serif" letterSpacing={1.5}>APPLYING LAGNA</text>
              <text x={cx+w/2} y={cy+56} textAnchor="middle" fontSize={36} fill="#e8c040" fontFamily="Georgia,serif" fontWeight="bold">{animStep}</text>
              <text x={cx+w/2} y={cy+75} textAnchor="middle" fontSize={11} fill={th.textDim} fontFamily="Georgia,serif">Bhāva {animStep} → {RASIS[curRId-1].iast}</text>
              <text x={cx+w/2} y={cy+92} textAnchor="middle" fontSize={10} fill={th.textFaint} fontFamily="Georgia,serif">({curRId}−{lagId}+12) mod 12+1={animStep}</text>
            </g>
          );
        }
        if (animStep===0) {
          return (
            <g>
              <rect x={cx} y={cy} width={w} height={h} fill={th.centerBg} stroke={th.cellBorder} strokeWidth={1}/>
              <text x={cx+w/2} y={cy+40} textAnchor="middle" fontSize={13} fill={th.textDim} fontFamily="Georgia,serif">Select a birth event</text>
              <text x={cx+w/2} y={cy+58} textAnchor="middle" fontSize={11} fill={th.textFaint} fontFamily="Georgia,serif">then press Apply Lagna</text>
            </g>
          );
        }
        const b=selected||1; const bInfo=map?map[b]:null; const theme=BHAVA_THEMES[b]; const types=BHAVA_TYPES[b]||[];
        if (!bInfo) return null;
        const bv=GRAHAS[bInfo.bhāveśa]; const bvDig=dignity(bInfo.bhāveśa,event.pos[bInfo.bhāveśa]); const k=GRAHAS[theme.kāraka];
        return (
          <g>
            <rect x={cx} y={cy} width={w} height={h} fill={th.centerBg} stroke="#e8c04033" strokeWidth={1}/>
            <text x={cx+w/2} y={cy+17} textAnchor="middle" fontSize={11} fill={th.textDim} fontFamily="Georgia,serif" letterSpacing={2}>BHĀVA {b}</text>
            <text x={cx+w/2} y={cy+34} textAnchor="middle" fontSize={18} fill={th.text} fontFamily="Georgia,serif" fontWeight="bold">{theme.iast}</text>
            <text x={cx+w/2} y={cy+50} textAnchor="middle" fontSize={11} fill={th.textDim} fontFamily="Georgia,serif">{theme.en.split(",")[0]}</text>
            <line x1={cx+14} y1={cy+58} x2={cx+w-14} y2={cy+58} stroke={th.cellBorder}/>
            <text x={cx+12} y={cy+72} fontSize={10.5} fill={th.textFaint} fontFamily="Georgia,serif">L · Bhāveśa</text>
            <text x={cx+w-12} y={cy+72} textAnchor="end" fontSize={12} fill={bv.color} fontFamily="Georgia,serif" fontWeight="bold">{bv.iast}</text>
            <text x={cx+w-12} y={cy+84} textAnchor="end" fontSize={10.5} fill={bvDig.col} fontFamily="Georgia,serif">B{bInfo.bhāveśaBhāva} · {bvDig.label}</text>
            <text x={cx+12} y={cy+99} fontSize={10.5} fill={th.textFaint} fontFamily="Georgia,serif">O · Sthita</text>
            <text x={cx+w-12} y={cy+99} textAnchor="end" fontSize={11.5} fill={th.text} fontFamily="Georgia,serif">{bInfo.occupants.length?bInfo.occupants.map(g=>GRAHAS[g].iast.slice(0,4)).join(", "):"Nirgraha"}</text>
            <text x={cx+12} y={cy+116} fontSize={10.5} fill={th.textFaint} fontFamily="Georgia,serif">K · Kāraka</text>
            <text x={cx+w-12} y={cy+116} textAnchor="end" fontSize={12} fill={k.color} fontFamily="Georgia,serif" fontWeight="bold">{k.iast}</text>
            <text x={cx+12} y={cy+132} fontSize={10.5} fill={th.textFaint} fontFamily="Georgia,serif">Prakāra</text>
            <text x={cx+w-12} y={cy+132} textAnchor="end" fontSize={10.5} fill="#8888b8" fontFamily="Georgia,serif">{types.join(" · ")||"Sāmānya"}</text>
            <line x1={cx+14} y1={cy+h-22} x2={cx+w-14} y2={cy+h-22} stroke={th.cellBorder}/>
            <text x={cx+w/2} y={cy+h-9} textAnchor="middle" fontSize={10} fill={th.textFaint} fontFamily="Georgia,serif" fontStyle="italic">tap any bhāva</text>
          </g>
        );
      })()}

      {[1,2,3].map(i=>(
        <g key={i}>
          <line x1={i*C} y1={0} x2={i*C} y2={S} stroke={th.cellBorder} strokeWidth={0.5}/>
          <line x1={0} y1={i*C} x2={S} y2={i*C} stroke={th.cellBorder} strokeWidth={0.5}/>
        </g>
      ))}
      <rect x={0.5} y={0.5} width={S-1} height={S-1} fill="none" stroke={th.panelBorder} strokeWidth={1.2}/>
    </svg>
  );
}

// ═══════════════════════════════════════════════════════════════════════════════
// SANDARBHA
// ═══════════════════════════════════════════════════════════════════════════════
