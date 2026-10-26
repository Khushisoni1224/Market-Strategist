import { Link } from 'wouter';
import { ArrowRight, Sparkles } from 'lucide-react';
import type { StrategyRecommendation } from '../../types';
import { EmptyState, Panel } from '../common/Elements';
export function RecentRecommendations({ recommendations }: { recommendations:StrategyRecommendation[] }) {
  return <Panel><div className="mb-4 flex items-center justify-between"><div><h2 className="font-display text-base font-extrabold">Next decisions</h2><p className="mt-1 text-xs text-slate-500">{recommendations.length} ideas waiting for your review</p></div><Sparkles size={17} className="text-[#5318EB]"/></div>{recommendations.length?<div className="space-y-3">{recommendations.slice(0,2).map((item)=><Link key={item.id} href="/strategy" className="block rounded-xl border border-slate-100 p-3.5 transition hover:border-[#D9CFF8]" data-testid={`card-dashboard-rec-${item.id}`}><span className="text-[10px] font-bold uppercase tracking-wider text-[#6E49D9]">{item.priority} PRIORITY</span><p className="mt-1.5 text-sm font-bold leading-5">{item.title}</p><span className="mt-2 inline-flex items-center gap-1 text-[11px] font-bold text-[#5318EB]">Review <ArrowRight size={12}/></span></Link>)}</div>:<EmptyState title="You’re up to date" text="No pending recommendations to review."/>}</Panel>;
}
