import * as React from 'react';
import type { ReactNode } from 'react';
import { AlertCircle, ArrowRight, RefreshCw } from 'lucide-react';
import { Button } from './Button';
import { Card } from './Card';
import { LoadingSkeleton } from './LoadingSkeleton';

export { Button } from './Button';
export function PageHeading({ eyebrow, title, description, action }: { eyebrow?: string; title: string; description?: string; action?: ReactNode }) {
  return <div className="mb-7 flex flex-col justify-between gap-4 sm:mb-9 sm:flex-row sm:items-end"><div>{eyebrow && <div className="mb-2 text-[10px] font-bold uppercase tracking-[.16em] text-[#6E49D9]">{eyebrow}</div>}<h1 className="font-display text-[28px] font-extrabold leading-tight tracking-[-.04em] text-[#17112B] sm:text-[34px]">{title}</h1>{description && <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-500">{description}</p>}</div>{action}</div>;
}
export function Panel({ children, className = '' }: { children: ReactNode; className?: string }) { return <Card className={className}>{children}</Card>; }
export function LoadingRows({ count = 3 }: { count?: number }) { return <LoadingSkeleton rows={count}/>; }
export function LoadError({ onRetry }: { onRetry: () => void }) { return <div className="rounded-2xl border border-rose-100 bg-rose-50/70 p-6 text-center"><AlertCircle className="mx-auto text-rose-500" size={23}/><p className="mt-2 font-semibold text-slate-800">Couldn’t load this demo data</p><p className="mt-1 text-sm text-slate-500">Please retry. Your workspace is still in demo mode.</p><Button onClick={onRetry} variant="secondary" testId="button-retry" ><RefreshCw size={14}/>Try again</Button></div>; }
export function EmptyState({ title, text, action }: { title: string; text: string; action?: ReactNode }) { return <div className="rounded-2xl border border-dashed border-slate-200 bg-white/60 px-6 py-12 text-center"><div className="mx-auto grid h-11 w-11 place-items-center rounded-2xl bg-[#F0EBFF] text-[#5318EB]"><ArrowRight size={19}/></div><h3 className="mt-4 font-display font-bold">{title}</h3><p className="mx-auto mt-1 max-w-sm text-sm leading-6 text-slate-500">{text}</p>{action && <div className="mt-5">{action}</div>}</div>; }
export function useDemoLoad<T>(load: () => Promise<T>) {
  const [state, setState] = React.useState<{ data?: T; loading: boolean; error: boolean }>({ loading: true, error: false });
  const refresh = React.useCallback(() => { setState((old) => ({ ...old, loading: true, error: false })); load().then((data) => setState({ data, loading: false, error: false })).catch(() => setState({ loading: false, error: true })); }, [load]);
  React.useEffect(() => { refresh(); }, [refresh]);
  return { ...state, refresh };
}
