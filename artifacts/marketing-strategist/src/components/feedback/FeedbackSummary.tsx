import { ArrowDownRight, ArrowUpRight, MessageSquareText, Minus } from 'lucide-react';
import { Panel } from '../common/Elements';
export type FeedbackStats={total:number;positive:number;neutral:number;negative:number};
export function FeedbackSummary({ stats,loading=false }: { stats?:FeedbackStats; loading?:boolean }) {
  const cards=[{label:'Total signals',value:stats?.total,icon:MessageSquareText,color:'text-[#5318EB] bg-[#F0EBFF]'},{label:'Positive',value:stats?.positive,icon:ArrowUpRight,color:'text-emerald-700 bg-emerald-50'},{label:'Questions / neutral',value:stats?.neutral,icon:Minus,color:'text-amber-700 bg-amber-50'},{label:'Needs attention',value:stats?.negative,icon:ArrowDownRight,color:'text-rose-700 bg-rose-50'}];
  return <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">{cards.map(({label,value,icon:Icon,color})=><Panel key={label} className="flex items-center gap-3 !p-4"><span className={`grid h-10 w-10 place-items-center rounded-xl ${color}`}><Icon size={18}/></span><div><div className="font-display text-xl font-extrabold">{loading?'—':value??0}</div><div className="text-[11px] text-slate-500">{label}</div></div></Panel>)}</div>;
}
