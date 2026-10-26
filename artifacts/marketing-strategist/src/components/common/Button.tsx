import type { ReactNode } from 'react';
export type ButtonVariant = 'primary' | 'secondary' | 'quiet' | 'danger';
export function Button({ children, onClick, variant = 'primary', type = 'button', testId, disabled, className = '' }: { children: ReactNode; onClick?: () => void; variant?: ButtonVariant; type?: 'button' | 'submit'; testId: string; disabled?: boolean; className?: string }) {
  const styles = { primary: 'bg-[#5318EB] text-white hover:bg-[#4211C5]', secondary: 'border border-slate-200 bg-white text-slate-700 hover:bg-slate-50', quiet: 'text-slate-500 hover:bg-slate-100', danger: 'border border-rose-200 bg-rose-50 text-rose-700 hover:bg-rose-100' };
  return <button type={type} onClick={onClick} disabled={disabled} data-testid={testId} className={`inline-flex min-h-10 items-center justify-center gap-2 rounded-xl px-4 text-[13px] font-bold transition disabled:cursor-not-allowed disabled:opacity-50 ${styles[variant]} ${className}`}>{children}</button>;
}
