import { useCallback } from 'react';
import { Link } from 'wouter';
import { Activity, ArrowRight, BarChart3 } from 'lucide-react';
import { Workspace } from '../components/common/Workspace';
import { LoadError, LoadingRows, PageHeading, Panel, useDemoLoad } from '../components/common/Elements';
import { MetricsGrid } from '../components/dashboard/MetricsGrid';
import { QuickActions } from '../components/dashboard/QuickActions';
import { RecentRecommendations } from '../components/dashboard/RecentRecommendations';
import { api } from '../services/api';

export default function Dashboard() {
  const load = useCallback(() => Promise.all([api.getProducts(),api.getFeedback(),api.getRecommendations(),api.getPerformanceMetrics()]), []);
  const {data,loading,error,refresh}=useDemoLoad(load);
  const pending=data?.[2].filter((item)=>item.status==='PENDING')??[];
  return <Workspace><PageHeading eyebrow="Tuesday, March 18 · your workspace" title="Good morning, Alex." description="Here’s what your business signals are pointing to this week."/>
    <QuickActions/>
    {loading?<LoadingRows count={4}/>:error?<LoadError onRetry={refresh}/>:data&&<>
      <MetricsGrid products={data[0].length} feedback={data[1].length} views="30.1k" ideas={pending.length}/>
      <div className="mt-6 grid gap-5 xl:grid-cols-[1.2fr_.8fr]">
        <Panel><div className="flex items-start justify-between"><div><div className="text-[10px] font-bold uppercase tracking-[.15em] text-[#6E49D9]">A signal worth a look</div><h2 className="mt-2 font-display text-lg font-extrabold tracking-[-.025em]">Customers are asking about fit.</h2></div><span className="rounded-full bg-[#F0EBFF] px-2.5 py-1 text-[10px] font-bold text-[#5318EB]">HIGH SIGNAL</span></div><p className="mt-3 max-w-2xl text-sm leading-6 text-slate-500">Cloudstep Low is getting the most attention, and sizing questions are showing up across customer conversations. A fit demonstration could help answer the question before checkout.</p><div className="mt-5 flex flex-wrap gap-2"><span className="rounded-lg bg-slate-50 px-3 py-2 text-xs font-semibold text-slate-600">Product · Cloudstep Low</span><span className="rounded-lg bg-slate-50 px-3 py-2 text-xs font-semibold text-slate-600">12 fit questions</span><span className="rounded-lg bg-slate-50 px-3 py-2 text-xs font-semibold text-slate-600">Attention +28%</span></div><Link href="/strategy" className="mt-5 inline-flex items-center gap-2 text-xs font-bold text-[#5318EB]" data-testid="link-view-recommendations">Review the reasoning <ArrowRight size={14}/></Link></Panel>
        <Panel className="bg-[#0C021C] text-white"><div className="flex items-center gap-2 text-[#BFAEFF]"><Activity size={16}/><span className="text-[10px] font-bold uppercase tracking-[.15em]">Your decision, your pace</span></div><h2 className="mt-4 font-display text-xl font-extrabold tracking-[-.03em]">Nothing is automatic.</h2><p className="mt-2 text-sm leading-6 text-white/60">Every suggestion stays here until you choose to approve or dismiss it. Approval is a decision to plan—not a post or campaign sent for you.</p><Link href="/history" className="mt-5 inline-flex items-center gap-2 text-xs font-bold text-[#C8B8FF]" data-testid="link-history">See your decision history <ArrowRight size={14}/></Link></Panel>
      </div>
      <div className="mt-6 grid gap-5 xl:grid-cols-[1fr_.72fr]"><Panel><div className="mb-5 flex items-center justify-between"><div><h2 className="font-display text-base font-extrabold">Recent performance</h2><p className="mt-1 text-xs text-slate-500">A quick look across recent channels</p></div><Link href="/performance" className="text-xs font-bold text-[#5318EB]" data-testid="link-all-performance">View all</Link></div><div className="space-y-4">{data[3].slice(0,3).map((metric,index)=><div key={metric.id} className="flex items-center gap-3" data-testid={`row-dashboard-performance-${metric.id}`}><div className="grid h-9 w-9 place-items-center rounded-xl bg-[#F4F1FB] text-[#5318EB]"><BarChart3 size={16}/></div><div className="min-w-0 flex-1"><div className="flex justify-between gap-3"><span className="text-sm font-bold">{metric.platform}</span><span className="text-xs font-bold">{metric.views.toLocaleString()} views</span></div><div className="mt-2 h-1.5 rounded-full bg-slate-100"><div className="h-full rounded-full bg-[#7651E5]" style={{width:`${Math.min(96,35+index*17)}%`}}/></div><div className="mt-1.5 text-[10px] text-slate-400">{metric.engagementRate}% engagement · {metric.conversionRate}% conversion</div></div></div>)}</div></Panel><RecentRecommendations recommendations={pending}/></div>
    </>}
  </Workspace>;
}
