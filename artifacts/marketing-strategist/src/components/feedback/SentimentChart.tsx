import { Badge } from '../common/Badge';
import type { FeedbackStats } from './FeedbackSummary';
export function SentimentChart({ stats }: { stats?:FeedbackStats }) {
  const total=stats?.total??0;
  const items=[{label:'Positive',value:stats?.positive??0,tone:'green' as const,color:'bg-emerald-500'},{label:'Neutral',value:stats?.neutral??0,tone:'amber' as const,color:'bg-amber-400'},{label:'Negative',value:stats?.negative??0,tone:'rose' as const,color:'bg-rose-400'}];
  return <section className="rounded-xl border border-slate-100 bg-[#FCFBFE] p-4" data-testid="chart-feedback-sentiment"><div className="mb-3 flex items-center justify-between"><h3 className="text-xs font-bold">Sentiment snapshot</h3><span className="text-[10px] text-slate-400">{total} sample signals</span></div><div className="flex h-2 overflow-hidden rounded-full bg-slate-100">{items.map((item)=><div key={item.label} className={`${item.color} transition-all`} style={{width:`${total?item.value/total*100:0}%`}} aria-label={`${item.label}: ${item.value}`}/>)}</div><div className="mt-3 flex flex-wrap gap-3">{items.map((item)=><span key={item.label} className="flex items-center gap-1.5 text-[10px] font-semibold text-slate-600"><Badge tone={item.tone} className="!px-2 !py-0.5">{item.value}</Badge>{item.label}</span>)}</div></section>;
}
