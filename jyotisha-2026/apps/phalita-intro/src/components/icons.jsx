export function KendraIcon({ size=12 }) {
  return (
    <svg width={size} height={size} viewBox="0 0 12 12" style={{ display:"inline-block", verticalAlign:"middle" }}>
      <circle cx={6} cy={6} r={5} fill="none" stroke="#5090ff" strokeWidth={1.5}/>
      <circle cx={6} cy={6} r={2} fill="#5090ff"/>
    </svg>
  );
}

export function TrikonaIcon({ size=12 }) {
  return (
    <svg width={size} height={size} viewBox="0 0 12 12" style={{ display:"inline-block", verticalAlign:"middle" }}>
      <polygon points="6,1 11,11 1,11" fill="none" stroke="#50c078" strokeWidth={1.5} strokeLinejoin="round"/>
    </svg>
  );
}

export function DusthanaIcon({ size=12 }) {
  return (
    <svg width={size} height={size} viewBox="0 0 12 12" style={{ display:"inline-block", verticalAlign:"middle" }}>
      <circle cx={6} cy={6} r={5} fill="#c05040"/>
    </svg>
  );
}

export function BhavaTypeIcons({ types, size=12 }) {
  return (
    <span style={{ display:"inline-flex", gap:3, alignItems:"center" }}>
      {types.includes("Kendra")   && <KendraIcon   size={size}/>}
      {types.includes("Trikona")  && <TrikonaIcon  size={size}/>}
      {types.includes("Dusthāna") && <DusthanaIcon size={size}/>}
    </span>
  );
}

// ═══════════════════════════════════════════════════════════════════════════════
// SVG CHART
// ═══════════════════════════════════════════════════════════════════════════════
