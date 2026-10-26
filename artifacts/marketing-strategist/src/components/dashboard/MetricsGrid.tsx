import { Link } from 'wouter';
import { ArrowRight, BarChart3, Boxes, MessageSquareText, Sparkles } from 'lucide-react';
const metrics = [
  { key:'products',label:'Products tracked',sub:'Across your catalog',icon:Boxes,href:'/products',accent:'bg-[#F0EBFF] text-[#5318EB]' },
  { key:'signals',label:'Customer signals',sub:'Recent comments & reviews',icon:MessageSquareText,href:'/feedback',accent:'bg-[#EAF5F1] text-[#287D60]' },
  { key:'views',label:'Views this week',sub:'Across 3 channels',icon:BarChart3,href:'/performance',accent:'bg-[#FFF3E5] text-[#BF7623]' },
  { key:'ideas',label:'Ideas to review',sub:'Nothing moves without you',icon:Sparkles,href:'/strategy',accent:'bg-[#F2EDFF] text-[#5318EB]' },
];
export function MetricsGrid({ products, feedback, views, ideas }: { products:number; feedback:number; views:string; ideas:number }) {
  const values: Record<string,string> = { products:String(products).padStart(2,'0'),signals:String(feedback).padStart(2,'0'),views,ideas:String(ideas).padStart(2,'0') };
  return <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">{metrics.map(({key,label,sub,icon:Icon,href,accent})=><Link key={key} href={href} className="surface group rounded-2xl p-5 transition hover:-translate-y-0.5 hover:shadow-md" data-testid={`card-metric-${key}`}><div className="flex items-start justify-between"><span className="text-xs font-semibold text-slate-500">{label}</span><span className={`grid h-9 w-9 place-items-center rounded-xl ${accent}`}><Icon size={17}/></span></div><div className="mt-4 flex items-end justify-between"><div><div className="font-display text-3xl font-extrabold tracking-[-.04em]">{values[key]}</div><div className="mt-1 text-[11px] text-slate-400">{sub}</div></div><ArrowRight size={15} className="mb-1 text-slate-300 transition group-hover:translate-x-1 group-hover:text-[#5318EB]"/></div></Link>)}</div>;
}
