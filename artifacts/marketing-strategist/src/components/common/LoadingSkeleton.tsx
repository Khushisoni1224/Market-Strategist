export function LoadingSkeleton({ rows = 3, compact = false }: { rows?: number; compact?: boolean }) {
  return <div className="space-y-3" aria-label="Loading"><span className="sr-only">Loading demo data</span>{Array.from({ length: rows }, (_, i) => <div key={i} className={`animate-pulse rounded-xl border border-slate-100 bg-white ${compact ? 'p-3' : 'p-4'}`}><div className="h-3 w-1/3 rounded bg-slate-100"/><div className="mt-3 h-3 w-4/5 rounded bg-slate-100"/>{!compact && <div className="mt-2 h-3 w-2/5 rounded bg-slate-100"/>}</div>)}</div>;
}
