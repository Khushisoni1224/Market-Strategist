import { useCallback } from 'react';
import { Archive, ArrowRight, Sparkles } from 'lucide-react';
import { Link } from 'wouter';
import { Workspace } from '../components/common/Workspace';
import { EmptyState, LoadError, LoadingRows, PageHeading, Panel, useDemoLoad } from '../components/common/Elements';
import { api } from '../services/api';
import { HistoryList } from '../components/history/HistoryList';

export default function History() {
  const load = useCallback(() => api.getHistory(), []);
  const { data, loading, error, refresh } = useDemoLoad(load);
  return <Workspace><PageHeading eyebrow="Your decisions" title="History" description="A simple record of the recommendations you chose to move forward with."/>
    <Panel><div className="mb-5 flex items-center justify-between"><div><h2 className="font-display text-base font-extrabold">Approved ideas</h2><p className="mt-1 text-xs text-slate-500">A private record of your choices in this demo session.</p></div><span className="grid h-10 w-10 place-items-center rounded-xl bg-[#F0EBFF] text-[#5318EB]"><Archive size={18}/></span></div>
      {loading ? <LoadingRows/> : error ? <LoadError onRetry={refresh}/> : !data?.length ? <EmptyState title="Your decision history starts here" text="When you approve a strategy idea, it will be recorded here. Approval is only a note of intent—not execution." action={<Link href="/strategy" className="inline-flex min-h-10 items-center gap-2 rounded-xl bg-[#5318EB] px-4 text-xs font-bold text-white" data-testid="link-history-strategy">Review ideas <ArrowRight size={14}/></Link>}/> : <HistoryList records={data}/>}
    </Panel>
    <div className="mt-5 rounded-2xl bg-[#0C021C] p-5 text-white"><div className="flex items-center gap-2 text-[#C8B8FF]"><Sparkles size={15}/><span className="text-[10px] font-bold uppercase tracking-[.15em]">A note on history</span></div><p className="mt-2 max-w-3xl text-sm leading-6 text-white/65">This record tracks your choices—not campaign execution or outcomes. You remain responsible for creating, publishing or sending any marketing activity.</p></div>
  </Workspace>;
}
