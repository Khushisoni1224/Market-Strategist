import type { ReactNode } from 'react';
export function Badge({ children, tone = 'violet', className = '', testId }: { children: ReactNode; tone?: 'violet' | 'green' | 'amber' | 'rose' | 'slate'; className?: string; testId?: string }) {
  const tones = { violet:'bg-[#F0EBFF] text-[#5318EB]', green:'bg-emerald-50 text-emerald-700', amber:'bg-amber-50 text-amber-700', rose:'bg-rose-50 text-rose-700', slate:'bg-slate-100 text-slate-600' };
  return <span data-testid={testId} className={`inline-flex items-center rounded-full px-2.5 py-1 text-[10px] font-bold ${tones[tone]} ${className}`}>{children}</span>;
}
