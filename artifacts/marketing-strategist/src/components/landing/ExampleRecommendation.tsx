import { useState } from 'react';
import { CircleHelp, Sparkles } from 'lucide-react';
import { Badge } from '../common/Badge';
export function ExampleRecommendation({ compact = false }: { compact?: boolean }) {
  const [expanded,setExpanded]=useState(false);
  return <section id={compact?undefined:'example'} className={`rounded-2xl border border-[#E9E3F8] ${compact?'p-4 sm:p-5':'p-5 sm:p-7'}`} data-testid="example-recommendation">
    <div className="mb-3 flex items-center justify-between"><span className="flex items-center gap-2 text-xs font-bold"><span className="h-2 w-2 rounded-full bg-[#5318EB]"/>Suggested next step</span><Badge>HIGH SIGNAL</Badge></div>
    <p className="font-display text-[17px] font-bold leading-6 tracking-[-.02em]" data-testid="text-example-recommendation">Create a size-focused reel for a sneaker with high attention and repeated size questions.</p>
    <button onClick={()=>setExpanded(!expanded)} aria-expanded={expanded} className="mt-3 text-xs font-bold text-[#5318EB] underline decoration-[#CBBDF5] underline-offset-4" data-testid="button-expand-example">{expanded?'Hide why this surfaced':'See why this surfaced'}</button>
    {expanded&&<div className="mt-3 rounded-xl bg-[#F8F6FE] p-3 text-xs leading-5 text-slate-600" data-testid="text-example-reason">The Cloudstep Low is drawing the most attention across recent content. Customers have asked about sizing repeatedly, so a clear fit demonstration could answer a real buying question.</div>}
    {!compact&&<div className="mt-4 flex items-start gap-2.5 rounded-xl bg-[#F8F9FA] p-3 text-[11px] leading-5 text-slate-500"><CircleHelp className="mt-0.5 shrink-0 text-[#5318EB]" size={14}/>An idea—not an instruction. Review the evidence, then decide whether it fits your business.</div>}
    {!compact&&<div className="mt-5 flex items-center gap-2 text-[10px] font-bold uppercase tracking-wider text-[#6E49D9]"><Sparkles size={13}/>Reasoning stays visible</div>}
  </section>;
}
