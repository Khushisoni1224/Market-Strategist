import { Link, useLocation } from 'wouter';
import { Activity, Archive, BarChart3, Boxes, ChevronRight, Compass, Home, MessageSquareText, Sparkles, X } from 'lucide-react';

const items = [
  { href:'/dashboard', label:'Overview', icon:Home },
  { href:'/products', label:'Products', icon:Boxes },
  { href:'/feedback', label:'Customer signals', icon:MessageSquareText },
  { href:'/performance', label:'Performance', icon:BarChart3 },
  { href:'/strategy', label:'Strategy', icon:Sparkles },
  { href:'/history', label:'Decision history', icon:Archive },
];
export function Sidebar({ open, onClose }: { open: boolean; onClose: () => void }) {
  const [location] = useLocation();
  const links = (mobile = false) => items.map(({ href, label, icon:Icon }) => <Link key={href} href={href} onClick={mobile ? onClose : undefined} data-testid={`${mobile?'mobile-':''}nav-${label.toLowerCase().replaceAll(' ','-')}`} className={`group flex items-center gap-3 rounded-xl px-3 py-2.5 text-[13px] font-semibold transition-colors ${location===href?'bg-[#F0EBFF] text-[#5318EB]':'text-slate-600 hover:bg-slate-50 hover:text-[#17112B]'}`}><Icon size={17} strokeWidth={1.8}/>{label}{location===href&&<ChevronRight className="ml-auto" size={14}/>}</Link>);
  const sidebarBody = <><Link href="/" className="mb-9 flex items-center gap-3 px-2" data-testid="link-brand"><span className="grid h-9 w-9 place-items-center rounded-xl bg-[#0C021C] text-white"><Activity size={18}/></span><span><span className="block font-display text-[15px] font-extrabold tracking-tight">signal / studio</span><span className="text-[10px] font-semibold uppercase tracking-[.16em] text-slate-400">marketing strategist</span></span></Link><div className="mb-3 px-3 text-[10px] font-bold uppercase tracking-[.15em] text-slate-400">Workspace</div><nav className="space-y-1" aria-label="Main navigation">{links()}</nav><div className="mt-auto rounded-2xl bg-[#0C021C] p-4 text-white"><div className="mb-3 flex items-center gap-2 text-[#C2AEFF]"><Compass size={16}/><span className="text-[11px] font-bold uppercase tracking-wider">Your control</span></div><p className="text-sm font-semibold leading-5">Ideas are yours to decide.</p><p className="mt-1.5 text-xs leading-5 text-white/60">Nothing is published or sent without your approval.</p><Link href="/strategy" className="mt-3 flex items-center gap-2 text-xs font-semibold text-white hover:text-[#C2AEFF]" data-testid="link-review-strategy">Review strategy <ChevronRight size={14}/></Link></div><div className="mt-4 flex items-center gap-3 border-t border-slate-100 pt-4"><div className="grid h-9 w-9 place-items-center rounded-full bg-[#EEE8FF] text-xs font-bold text-[#5318EB]">NG</div><div><div className="text-xs font-bold">Northline Goods</div><div className="text-[11px] text-slate-400">Demo business</div></div></div></>;
  return <>
    <aside className="fixed inset-y-0 left-0 z-30 hidden w-[248px] flex-col border-r border-slate-200/80 bg-white px-5 py-6 lg:flex">{sidebarBody}</aside>
    {open&&<button aria-label="Close navigation overlay" className="fixed inset-0 z-40 bg-[#0C021C]/30 lg:hidden" onClick={onClose} data-testid="button-close-drawer"/>}
    <aside aria-label="Mobile navigation" className={`fixed inset-y-0 left-0 z-50 flex w-[280px] flex-col bg-white px-5 py-6 shadow-xl transition-transform lg:hidden ${open?'translate-x-0':'-translate-x-full'}`}>
      <div className="mb-8 flex items-center justify-between"><Link href="/" onClick={onClose} className="flex items-center gap-2 font-display font-extrabold"><span className="grid h-9 w-9 place-items-center rounded-xl bg-[#0C021C] text-white"><Activity size={18}/></span>signal / studio</Link><button onClick={onClose} className="rounded-lg p-2 text-slate-500" aria-label="Close menu" data-testid="button-close-menu"><X size={18}/></button></div>
      <div className="mb-3 px-3 text-[10px] font-bold uppercase tracking-[.15em] text-slate-400">Workspace</div><nav className="space-y-1" aria-label="Mobile main navigation">{links(true)}</nav>
      <div className="mt-auto rounded-2xl bg-[#0C021C] p-4 text-white"><div className="text-[11px] font-bold uppercase tracking-wider text-[#C2AEFF]">Your control</div><p className="mt-2 text-sm font-semibold">Ideas are yours to decide.</p><p className="mt-1 text-xs leading-5 text-white/60">Nothing is published or sent without your approval.</p></div>
    </aside>
  </>;
}
