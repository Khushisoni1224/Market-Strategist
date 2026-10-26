import { BarChart3 } from 'lucide-react';
import type { PerformanceMetric } from '../../types';
const colors=['#5318EB','#9074E9','#C5B7F2','#4A9C7B'];
export function TrendChart({ metrics }: { metrics:PerformanceMetric[] }) {
  const max=Math.max(...metrics.map((item)=>item.views),1);
  return <section className="surface rounded-2xl p-5 sm:p-6"><div className="flex items-start justify-between"><div><h2 className="font-display text-base font-extrabold">Views by recent activity</h2><p className="mt-1 text-xs text-slate-500">A directional look across sample channel data</p></div><BarChart3 size={18} className="text-[#5318EB]"/></div><div className="mt-8 flex h-[224px] items-end gap-3 border-b border-l border-slate-100 px-2 pb-2 sm:gap-5 sm:px-5">{metrics.map((item,index)=>{const height=Math.max(12,Math.round(item.views/max*100));return <div key={item.id} className="flex h-full flex-1 flex-col items-center justify-end gap-2" data-testid={`bar-performance-${item.id}`}><span className="text-[9px] font-bold text-slate-500 sm:text-[10px]">{(item.views/1000).toFixed(1)}k</span><div className="w-full max-w-16 rounded-t-lg transition-[height] duration-500" style={{height:`${height}%`,background:colors[index%colors.length]}}/><span className="text-[9px] text-slate-400">{item.platform}</span></div>})}</div></section>;
}
