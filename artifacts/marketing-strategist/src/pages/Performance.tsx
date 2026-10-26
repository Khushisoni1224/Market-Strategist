import { useCallback } from 'react';
import { ArrowUpRight, Eye, MousePointerClick, TrendingUp } from 'lucide-react';
import { Workspace } from '../components/common/Workspace';
import { LoadError, LoadingRows, PageHeading, Panel, useDemoLoad } from '../components/common/Elements';
import { TrendChart } from '../components/performance/TrendChart';
import { PlatformBreakdown } from '../components/performance/PlatformBreakdown';
import { api } from '../services/api';
export default function Performance() {
  const load=useCallback(()=>api.getPerformanceMetrics(),[]);const {data,loading,error,refresh}=useDemoLoad(load);
  const totalViews=data?.reduce((sum,item)=>sum+item.views,0)??0;const avgEngagement=data?.length?data.reduce((sum,item)=>sum+item.engagementRate,0)/data.length:0;const avgConversion=data?.length?data.reduce((sum,item)=>sum+item.conversionRate,0)/data.length:0;
  return <Workspace><PageHeading eyebrow="Your marketing readout" title="Performance" description="See which channels are earning attention and where customers are taking the next step." action={<span className="rounded-xl border border-slate-200 bg-white px-3.5 py-2.5 text-xs font-semibold text-slate-500">Recent activity · Demo sample</span>}/>
    {loading?<LoadingRows count={4}/>:error?<LoadError onRetry={refresh}/>:data&&<>
      <div className="grid gap-3 sm:grid-cols-3">{[{label:'Views in sample',value:totalViews.toLocaleString(),icon:Eye,trend:'+18.4%'},{label:'Avg. engagement',value:`${avgEngagement.toFixed(1)}%`,icon:TrendingUp,trend:'Across channels'},{label:'Avg. conversion',value:`${avgConversion.toFixed(1)}%`,icon:MousePointerClick,trend:'From tracked signals'}].map(({label,value,icon:Icon,trend})=><Panel key={label} className="!p-5"><div className="flex items-center justify-between"><span className="text-xs font-semibold text-slate-500">{label}</span><span className="grid h-9 w-9 place-items-center rounded-xl bg-[#F0EBFF] text-[#5318EB]"><Icon size={17}/></span></div><div className="mt-4 flex items-end justify-between"><span className="font-display text-3xl font-extrabold tracking-[-.04em]">{value}</span><span className="mb-1 flex items-center gap-1 text-[10px] font-bold text-emerald-700"><ArrowUpRight size={12}/>{trend}</span></div></Panel>)}</div>
      <div className="mt-5 grid gap-5 xl:grid-cols-[1.25fr_.75fr]"><TrendChart metrics={data}/><PlatformBreakdown metrics={data}/></div>
      <div className="mt-5 rounded-2xl border border-slate-200 bg-white p-4 text-xs leading-5 text-slate-500">Performance values are illustrative, locally stored sample data for this Stage 1 interface. They do not reflect a connected social or commerce account.</div>
    </>}</Workspace>;
}
