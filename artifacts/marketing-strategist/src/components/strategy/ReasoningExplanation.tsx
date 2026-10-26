import { Sparkles } from 'lucide-react';
export function ReasoningExplanation({ text, testId }: { text:string; testId:string }) {
  return <div className="mt-5 rounded-xl bg-[#F7F5FB] p-4" data-testid={testId}><div className="mb-1.5 flex items-center gap-2 text-[10px] font-bold uppercase tracking-wider text-[#6E49D9]"><Sparkles size={13}/>Why this surfaced</div><p className="text-sm leading-6 text-slate-600">{text}</p></div>;
}
