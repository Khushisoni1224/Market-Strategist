import { useCallback, useState } from 'react';
import { MessageCircle, Star, Mail } from 'lucide-react';
import { Workspace } from '../components/common/Workspace';
import { EmptyState, LoadError, LoadingRows, PageHeading, Panel, useDemoLoad } from '../components/common/Elements';
import { Badge } from '../components/common/Badge';
import { FeedbackSummary } from '../components/feedback/FeedbackSummary';
import { SentimentChart } from '../components/feedback/SentimentChart';
import { api } from '../services/api';

const sourceIcon = { REVIEW:Star, COMMENT:MessageCircle, MESSAGE:Mail };
export default function Feedback() {
  const load = useCallback(() => Promise.all([api.getFeedback(), api.getFeedbackStats()]), []);
  const { data, loading, error, refresh } = useDemoLoad(load);
  const [filter, setFilter] = useState('ALL');
  const filtered = data?.[0].filter((item) => filter === 'ALL' || item.sentiment === filter) ?? [];
  const stat = data?.[1];
  return <Workspace><PageHeading eyebrow="Customer voice" title="Feedback" description="Listen for patterns in what customers praise, ask and need—without losing the individual voice."/>
    <FeedbackSummary stats={stat} loading={loading}/>
    <div className="mb-5 mt-4">{!error&&!loading&&<SentimentChart stats={stat}/>}</div>
    <Panel className="mt-5"><div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-center"><div><h2 className="font-display text-base font-extrabold">Recent customer signals</h2><p className="mt-1 text-xs text-slate-500">Illustrative demo feedback. No live inbox is connected.</p></div><div className="flex flex-wrap gap-1 rounded-xl bg-slate-100 p-1" role="group" aria-label="Filter feedback">{['ALL','POSITIVE','NEUTRAL','NEGATIVE'].map((item)=><button key={item} onClick={()=>setFilter(item)} className={`rounded-lg px-3 py-2 text-[10px] font-bold transition ${filter===item?'bg-white text-[#5318EB] shadow-sm':'text-slate-500 hover:text-slate-800'}`} data-testid={`filter-feedback-${item.toLowerCase()}`}>{item === 'ALL' ? 'All signals' : item.charAt(0)+item.slice(1).toLowerCase()}</button>)}</div></div>
      <div className="mt-5">{loading ? <LoadingRows count={4}/> : error ? <LoadError onRetry={refresh}/> : !filtered.length ? <EmptyState title="No signals in this view" text="Try another sentiment filter to see more customer feedback."/> : <div className="space-y-3">{filtered.map((item)=>{const Icon=sourceIcon[item.source];const tone=item.sentiment==='POSITIVE'?'green':item.sentiment==='NEUTRAL'?'amber':'rose';return <article key={item.id} className="rounded-2xl border border-slate-100 bg-white p-4 transition hover:border-[#E3DCF4] sm:p-5" data-testid={`card-feedback-${item.id}`}><div className="flex items-start gap-3"><div className="grid h-9 w-9 shrink-0 place-items-center rounded-xl bg-[#F5F2FB] text-[#6550A6]"><Icon size={16}/></div><div className="min-w-0 flex-1"><div className="flex flex-wrap items-center gap-2"><span className="text-xs font-bold">{item.source.toLowerCase()}</span><Badge tone={tone} testId={`status-sentiment-${item.id}`}>{item.sentiment}</Badge><time className="ml-auto text-[10px] text-slate-400">{new Date(`${item.date}T12:00:00`).toLocaleDateString('en-US',{month:'short',day:'numeric'})}</time></div><p className="mt-2 text-sm leading-6 text-slate-600">{item.content}</p><div className="mt-3 flex items-center gap-1.5 text-[10px] font-semibold uppercase tracking-wider text-slate-400">{item.id==='fb-02'||item.id==='fb-05'?'Fit & sizing':'Product experience'}<span className="h-1 w-1 rounded-full bg-slate-300"/>Northline Goods demo</div></div></div></article>})}</div>}</div></Panel>
    <div className="mt-5 rounded-2xl border border-[#E5DDFB] bg-[#F5F1FF] p-4 text-xs leading-5 text-slate-600"><strong className="text-[#3B2670]">What this tells us:</strong> sizing questions recur across more than one source. That pattern can inform a product page update or a piece of helpful content—your choice.</div>
  </Workspace>;
}
