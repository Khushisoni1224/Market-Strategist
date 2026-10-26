import { useState, type FormEvent } from 'react';
import { Link, useLocation } from 'wouter';
import { ArrowLeft, ArrowRight, Eye, EyeOff, LockKeyhole, Sparkles } from 'lucide-react';
import { api } from '../services/api';
import { Button } from '../components/common/Elements';

export function AuthPage({ mode }: { mode: 'login' | 'register' }) {
  const [, setLocation] = useLocation();
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [visible, setVisible] = useState(false);
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);
  const isRegister = mode === 'register';
  async function submit(event: FormEvent) {
    event.preventDefault(); setError('');
    if (isRegister && name.trim().length < 2) { setError('Add your name to continue.'); return; }
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) { setError('Enter a valid email address.'); return; }
    if (password.length < 6) { setError('Use at least 6 characters for this demo password.'); return; }
    setBusy(true);
    try { const user = isRegister ? await api.register(name, email, password) : await api.login(email, password); sessionStorage.setItem('demoUser', JSON.stringify(user)); setLocation('/dashboard'); }
    catch { setError('The demo could not continue. Please try again.'); }
    finally { setBusy(false); }
  }
  return <div className="min-h-[100dvh] bg-[#F8F9FA] lg:grid lg:grid-cols-[1.02fr_.98fr]">
    <section className="relative hidden overflow-hidden bg-[#0C021C] px-12 py-10 text-white lg:flex lg:flex-col"><Link href="/" className="flex items-center gap-3 font-display font-extrabold" data-testid="link-auth-brand"><span className="grid h-10 w-10 place-items-center rounded-xl bg-[#5318EB]"><Sparkles size={19}/></span>signal / studio</Link><div className="relative z-10 my-auto max-w-lg"><div className="mb-5 text-[10px] font-bold uppercase tracking-[.18em] text-[#BBA7FF]">A clearer next step</div><h1 className="font-display text-5xl font-extrabold leading-[1.08] tracking-[-.05em]">Make your signals mean something.</h1><p className="mt-6 max-w-md text-base leading-7 text-white/60">A calmer way to see what customers respond to and decide what your business should try next.</p><div className="mt-10 flex items-center gap-2 text-sm text-white/70"><LockKeyhole size={16} className="text-[#BBA7FF]"/> You approve every move. Always.</div></div><div className="absolute -bottom-24 -right-24 h-96 w-96 rounded-full border border-white/10"/><div className="absolute -bottom-10 -right-10 h-64 w-64 rounded-full border border-white/10"/></section>
    <section className="flex min-h-[100dvh] flex-col px-5 py-6 sm:px-10 lg:px-16"><Link href="/" className="flex items-center gap-2 text-xs font-bold text-slate-500 hover:text-[#5318EB] lg:hidden" data-testid="link-back-home"><ArrowLeft size={15}/> Back to overview</Link><div className="mx-auto my-auto w-full max-w-[430px] py-10">
      <div className="mb-7 inline-flex items-center gap-1.5 rounded-full border border-[#E5DDFB] bg-white px-3 py-1.5 text-[10px] font-bold uppercase tracking-wider text-[#5318EB]"><span className="h-1.5 w-1.5 rounded-full bg-[#5318EB]"/> Demo workspace</div><h2 className="font-display text-3xl font-extrabold tracking-[-.04em]">{isRegister ? 'Set up your workspace' : 'Welcome back'}</h2><p className="mt-2 text-sm leading-6 text-slate-500">{isRegister ? 'Get a feel for how clear marketing decisions could look.' : 'Sign in to continue exploring the sample workspace.'}</p>
      <form onSubmit={submit} className="mt-8 space-y-4" noValidate>{isRegister && <label className="block text-xs font-bold text-slate-700">Your name<input value={name} onChange={(e) => setName(e.target.value)} autoComplete="name" className="mt-1.5 h-12 w-full rounded-xl border border-slate-200 bg-white px-4 text-sm outline-none transition focus:border-[#8D70E7]" placeholder="Alex Morgan" data-testid="input-name"/></label>}
        <label className="block text-xs font-bold text-slate-700">Email address<input type="email" value={email} onChange={(e) => setEmail(e.target.value)} autoComplete="email" className="mt-1.5 h-12 w-full rounded-xl border border-slate-200 bg-white px-4 text-sm outline-none transition focus:border-[#8D70E7]" placeholder="you@yourbusiness.com" data-testid="input-email"/></label>
        <label className="block text-xs font-bold text-slate-700">Demo password<div className="relative mt-1.5"><input type={visible ? 'text' : 'password'} value={password} onChange={(e) => setPassword(e.target.value)} autoComplete={isRegister ? 'new-password' : 'current-password'} className="h-12 w-full rounded-xl border border-slate-200 bg-white px-4 pr-12 text-sm outline-none transition focus:border-[#8D70E7]" placeholder="At least 6 characters" data-testid="input-password"/><button type="button" onClick={() => setVisible(!visible)} aria-label={visible ? 'Hide password' : 'Show password'} className="absolute right-3 top-3 rounded-md p-1 text-slate-400" data-testid="button-toggle-password">{visible ? <EyeOff size={17}/> : <Eye size={17}/>}</button></div></label>
        {error && <div className="rounded-xl border border-rose-200 bg-rose-50 px-3 py-2.5 text-xs font-semibold text-rose-700" role="alert" data-testid="status-auth-error">{error}</div>}
        <Button type="submit" disabled={busy} testId="button-auth-submit">{busy ? 'Preparing demo…' : isRegister ? 'Create demo workspace' : 'Continue to workspace'} <ArrowRight size={15}/></Button>
      </form>
      <div className="mt-5 rounded-xl bg-[#F0EBFF]/70 p-3.5 text-xs leading-5 text-slate-600"><strong className="text-[#3B2670]">No real account is created.</strong> This is a frontend demo. Any valid email and a password of 6+ characters will work; your inputs stay in this browser session.</div>
      <p className="mt-6 text-center text-sm text-slate-500">{isRegister ? 'Already have a demo session?' : 'New to Signal / Studio?'} <Link href={isRegister ? '/login' : '/register'} className="font-bold text-[#5318EB]" data-testid="link-switch-auth">{isRegister ? 'Log in' : 'Create a workspace'}</Link></p>
      </div><div className="pb-2 text-center text-[10px] text-slate-400">Stage 1 frontend demo · No integrations connected</div></section>
  </div>;
}
