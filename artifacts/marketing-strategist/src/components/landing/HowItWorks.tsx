import { ArrowRight } from 'lucide-react';
const process = [
  ['Enter','Bring in the product, customer, performance and market context you already have.'],
  ['Analyze','Connect recurring patterns across signals, not just isolated numbers.'],
  ['Prioritize','Surface the most relevant opportunity for your business right now.'],
  ['Recommend','Turn that opportunity into a concrete idea you can review.'],
  ['Explain','Show the evidence and reasoning behind the suggestion, in plain language.'],
];
export function HowItWorks() {
  return <section id="how-it-works" className="mx-auto max-w-[1280px] px-5 py-20 sm:px-10 sm:py-28"><div className="max-w-xl"><div className="mb-3 text-[10px] font-bold uppercase tracking-[.16em] text-[#6E49D9]">A simpler decision loop</div><h2 className="font-display text-3xl font-extrabold tracking-[-.045em] sm:text-5xl">From scattered signals to a next step you understand.</h2><p className="mt-4 text-sm leading-6 text-slate-500">A practical five-step loop. The recommendation is a starting point, and the decision stays with you.</p></div><div className="mt-12 grid gap-3 md:grid-cols-5">{process.map(([title,text],i)=><article key={title} className="relative rounded-2xl border border-slate-200 bg-white p-5 shadow-[0_5px_18px_rgba(23,17,43,.025)]" data-testid={`process-step-${title.toLowerCase()}`}><div className="font-display text-xs font-extrabold text-[#5318EB]">0{i+1}</div><h3 className="mt-5 font-display text-[15px] font-extrabold">{title}</h3><p className="mt-2 text-xs leading-5 text-slate-500">{text}</p>{i<4&&<ArrowRight className="absolute -right-3 top-6 z-10 hidden rounded-full bg-white p-1 text-slate-300 md:block" size={22}/>}</article>)}</div></section>;
}
