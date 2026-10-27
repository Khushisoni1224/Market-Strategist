// Decorative SVG artwork (no external images needed). Swap for real photos any time.
export function Blobs({ className = "" }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 800 600" preserveAspectRatio="xMidYMid slice" aria-hidden>
      <defs>
        <radialGradient id="ga"><stop offset="0" stopColor="#a78bfa" /><stop offset="1" stopColor="#a78bfa" stopOpacity="0" /></radialGradient>
        <radialGradient id="gb"><stop offset="0" stopColor="#7dd3fc" /><stop offset="1" stopColor="#7dd3fc" stopOpacity="0" /></radialGradient>
        <pattern id="dots" width="24" height="24" patternUnits="userSpaceOnUse"><circle cx="2" cy="2" r="1.5" fill="#c4b5fd" /></pattern>
      </defs>
      <rect width="800" height="600" fill="url(#dots)" opacity=".5" />
      <circle cx="160" cy="120" r="260" fill="url(#ga)" />
      <circle cx="680" cy="460" r="300" fill="url(#gb)" />
      <circle cx="620" cy="140" r="120" fill="none" stroke="#c4b5fd" strokeWidth="1.5" />
      <circle cx="620" cy="140" r="180" fill="none" stroke="#bae6fd" strokeWidth="1.5" />
    </svg>
  );
}

export function FlowArt({ className = "" }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 400 320" aria-hidden>
      <rect x="20" y="20" width="360" height="280" rx="24" fill="#fff" stroke="#ede9fe" strokeWidth="2" />
      <rect x="44" y="44" width="150" height="90" rx="14" fill="#f5f3ff" />
      {[0, 1, 2, 3, 4].map((i) => (
        <rect key={i} x={58 + i * 26} y={118 - [30, 48, 36, 62, 74][i]} width="16" height={[30, 48, 36, 62, 74][i]} rx="4" fill="#8b5cf6" opacity={0.4 + i * 0.15} />
      ))}
      <rect x="210" y="44" width="146" height="90" rx="14" fill="#f0f9ff" />
      <circle cx="283" cy="89" r="28" fill="none" stroke="#bae6fd" strokeWidth="12" />
      <circle cx="283" cy="89" r="28" fill="none" stroke="#7c3aed" strokeWidth="12" strokeDasharray="120 176" transform="rotate(-90 283 89)" />
      <path d="M44 214 C 90 170, 130 240, 180 190 S 270 160, 356 196" fill="none" stroke="#7c3aed" strokeWidth="3" strokeLinecap="round" />
      <rect x="44" y="238" width="200" height="34" rx="10" fill="#ede9fe" />
      <circle cx="62" cy="255" r="6" fill="#7c3aed" />
      <rect x="76" y="249" width="120" height="6" rx="3" fill="#a78bfa" />
      <rect x="76" y="259" width="80" height="5" rx="2.5" fill="#c4b5fd" />
    </svg>
  );
}