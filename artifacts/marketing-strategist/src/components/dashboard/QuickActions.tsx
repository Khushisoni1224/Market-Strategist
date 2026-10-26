import { useRef, useState } from 'react';
import { Link } from 'wouter';
import { CloudUpload, MessageSquareText, Sparkles } from 'lucide-react';
import { Button } from '../common/Button';
export function QuickActions() {
  const inputRef=useRef<HTMLInputElement>(null);
  const [message,setMessage]=useState('');
  return <div className="mb-5 flex flex-wrap items-center gap-2 rounded-2xl border border-slate-200 bg-white p-3.5" aria-label="Quick actions"><span className="mr-2 text-xs font-bold text-slate-500">Quick actions</span><Button variant="secondary" testId="button-dashboard-upload" onClick={()=>inputRef.current?.click()}><CloudUpload size={15}/>Upload data</Button><input ref={inputRef} type="file" accept=".csv,.pdf,.xlsx,.png,.jpg" className="sr-only" aria-label="Choose a demo business data file" data-testid="input-dashboard-upload" onChange={(event)=>{const file=event.target.files?.[0];setMessage(file?`${file.name} selected for this demo. No file was uploaded.`:'');}}/><Link href="/feedback" className="inline-flex min-h-10 items-center gap-2 rounded-xl px-4 text-[13px] font-bold text-slate-600 hover:bg-slate-50" data-testid="link-quick-feedback"><MessageSquareText size={15}/>Review feedback</Link><Link href="/strategy" className="inline-flex min-h-10 items-center gap-2 rounded-xl px-4 text-[13px] font-bold text-[#5318EB] hover:bg-[#F6F2FF]" data-testid="link-quick-strategy"><Sparkles size={15}/>Review ideas</Link>{message&&<span role="status" className="basis-full px-2 text-xs font-semibold text-[#5318EB]" data-testid="status-upload">{message}</span>}</div>;
}
