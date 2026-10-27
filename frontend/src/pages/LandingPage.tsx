import { useState } from "react";
import { Link } from "react-router-dom";
import { AnimatePresence, motion } from "framer-motion";
import { ArrowRight, BarChart3, Building2, CheckCircle2, ChevronLeft, ChevronRight, Package, Repeat, Sparkles, TrendingUp, UserPlus, type LucideIcon } from "lucide-react";
import { Area, AreaChart, ResponsiveContainer } from "recharts";
import { actions, sentiment, traffic } from "../data/demo-data";
import { Blobs, FlowArt } from "../components/Art";

interface Step { title: string; desc: string; items: string[]; icon: LucideIcon }
const flow: Step[] = [
  { title: "Sign Up / Create Account", icon: UserPlus, desc: "Register with your email and password to create your account.", items: ["Email address", "Password", "Confirm password"] },
  { title: "Complete Business Profile (Onboarding)", icon: Building2, desc: "Add basic information about your business to create your portfolio.", items: ["Brand / Entity name", "Business domain / industry", "Business description", "Business model", "Sales channels", "(Optional) Target audience, website, location, marketing goals"] },
  { title: "Add Products", icon: Package, desc: "Upload and manage your product catalog.", items: ["Product name", "Category", "Description (optional)", "Price", "Inventory count (optional)"] },
  { title: "View Insights & Analytics", icon: BarChart3, desc: "See your customer feedback, performance metrics and key business insights.", items: ["Customer sentiment", "Recurring themes", "Sales / traffic trends", "Product performance"] },
  { title: "Get AI Recommendations", icon: Sparkles, desc: "The system analyzes your data and provides ranked, explainable marketing recommendations.", items: ["Top recommended actions", "Supporting reasons / evidence", "Priority ranking"] },
  { title: "Review & Take Action", icon: CheckCircle2, desc: "Edit, accept or reject recommendations based on your business needs.", items: ["View details", "Edit / customize", "Accept or reject", "Implement the action"] },
  { title: "Track Results & Improve", icon: TrendingUp, desc: "Monitor the impact of your actions and get better recommendations over time.", items: ["Track performance", "View outcomes", "Build history", "Get improved suggestions"] },
];
const headline = "Your Business Has the Data. Now Turn It Into Strategy.".split(" ");
const pill = (on: boolean) => `rounded-full px-5 py-2 text-sm font-medium transition ${on ? "bg-violet-600 text-white shadow" : "bg-white text-slate-600 hover:bg-violet-50"}`;

export default function LandingPage() {
  const [idx, setIdx] = useState(0);
  const [all, setAll] = useState(false);

  return (
    <div className="overflow-x-hidden">
      <nav className="mx-auto flex max-w-6xl items-center justify-between px-5 py-5">
        <span className="flex items-center gap-2 font-semibold"><img src="/logo.png" alt="" className="h-8 w-8" />Market-Strategist</span>
        <div className="flex gap-3 text-sm">
          <a href="#flow" className="hidden px-3 py-2 text-slate-600 hover:text-slate-900 sm:block">How it works</a>
          <Link to="/login" className="px-3 py-2 text-slate-600 hover:text-slate-900">Log in</Link>
          <Link to="/signup" className="rounded-full bg-violet-600 px-4 py-2 text-white hover:bg-violet-700">Get started</Link>
        </div>
      </nav>

      <header className="relative bg-gradient-to-b from-violet-50 via-sky-50/60 to-white">
        <Blobs className="absolute inset-0 h-full w-full opacity-50" />
        <div className="relative mx-auto grid max-w-6xl gap-12 px-5 pb-24 pt-12 md:grid-cols-2 md:items-center">
          <div>
            <h1 className="text-4xl font-bold leading-tight md:text-5xl">
              {headline.map((w, i) => (
                <motion.span key={i} className="mr-2 inline-block" initial={{ opacity: 0, y: 24 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.06, duration: 0.5 }}>{w}</motion.span>
              ))}
            </h1>
            <p className="mt-5 text-lg text-slate-600">Market-Strategist helps small businesses understand customer feedback, uncover product opportunities, and identify which marketing actions to prioritize next.</p>
            <div className="mt-8 flex flex-wrap gap-3">
              <Link to="/signup"><motion.span whileHover={{ scale: 1.04 }} whileTap={{ scale: 0.97 }} className="inline-flex items-center gap-2 rounded-full bg-violet-600 px-6 py-3 font-medium text-white shadow-lg shadow-violet-200">Get Started Free <ArrowRight size={16} /></motion.span></Link>
              <a href="#flow" className="rounded-full border border-slate-200 bg-white px-6 py-3 font-medium hover:border-violet-300">Explore How It Works</a>
            </div>
          </div>
          <motion.div initial={{ opacity: 0, y: 40 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4, duration: 0.7 }} className="rounded-2xl border border-slate-100 bg-white p-5 shadow-xl shadow-violet-100">
            <p className="mb-3 text-xs text-slate-400">Illustrative demo data, not live business data</p>
            <div className="h-32"><ResponsiveContainer width="100%" height="100%"><AreaChart data={traffic}><Area dataKey="v" stroke="#7c3aed" fill="#ede9fe" strokeWidth={2} /></AreaChart></ResponsiveContainer></div>
            <div className="mt-4 space-y-2">{sentiment.map((s, i) => (
              <div key={s.label} className="flex items-center gap-3 text-xs"><span className="w-16">{s.label}</span>
                <div className="h-2 flex-1 rounded bg-slate-100"><motion.div className={`h-2 rounded ${s.color}`} initial={{ width: 0 }} animate={{ width: `${s.pct}%` }} transition={{ delay: 0.8 + i * 0.15, duration: 0.8 }} /></div>{s.pct}%</div>))}</div>
            <motion.div animate={{ y: [0, -4, 0] }} transition={{ duration: 3, repeat: Infinity }} className="mt-4 rounded-xl bg-violet-50 p-3 text-sm"><b>#1</b> {actions[0].t}<div className="text-xs text-slate-500">{actions[0].why}</div></motion.div>
          </motion.div>
        </div>
      </header>

      <section id="features" className="mx-auto max-w-6xl px-5 py-20">
        <h2 className="text-center text-3xl font-bold">Your project flow at a glance</h2>
        <p className="mx-auto mt-3 max-w-xl text-center text-slate-600">Seven steps from signup to smarter marketing. Hover a card to explore it.</p>
        <div className="mt-12 grid gap-5 sm:grid-cols-2 lg:grid-cols-4">
          {flow.map((f, i) => (
            <motion.div key={f.title} initial={{ opacity: 0, y: 40 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true, amount: 0.15 }} transition={{ duration: 0.5, delay: (i % 4) * 0.08 }}>
            <div className="group h-full cursor-default rounded-2xl border border-slate-100 bg-white p-5 shadow-sm transition duration-300 hover:-translate-y-2 hover:border-violet-300 hover:shadow-xl hover:shadow-violet-100">
              <div className="flex items-center justify-between">
                <span className="grid h-11 w-11 place-items-center rounded-xl bg-violet-50 text-violet-600 transition group-hover:bg-violet-600 group-hover:text-white"><f.icon size={20} /></span>
                <span className="text-xs font-semibold text-slate-300 transition group-hover:text-violet-500">STEP {String(i + 1).padStart(2, "0")}</span>
              </div>
              <h3 className="mt-4 font-semibold leading-snug">{f.title}</h3>
              <p className="mt-1 text-xs text-slate-500">{f.desc}</p>
              <p className="mt-4 text-3xl font-bold text-violet-600">{f.items.length}<span className="ml-1 text-xs font-normal text-slate-400">key inputs</span></p>
              <ul className="mt-2 space-y-1 text-xs text-slate-500">{f.items.map((it) => <li key={it} className="transition group-hover:text-slate-700">• {it}</li>)}</ul>
            </div>
            </motion.div>
          ))}
        </div>
      </section>

      <section id="flow" className="bg-gradient-to-b from-violet-50 to-sky-50 py-20">
        <div className="mx-auto max-w-5xl px-5">
          <h2 className="text-center text-3xl font-bold">See the complete flow</h2>
          <div className="my-6 flex justify-center gap-2"><button className={pill(!all)} onClick={() => setAll(false)}>One by one</button><button className={pill(all)} onClick={() => setAll(true)}>Complete flow</button></div>
          <AnimatePresence mode="wait">
            {!all ? (
              <motion.div key="slides" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
                <div className="overflow-hidden rounded-3xl bg-white shadow-xl shadow-violet-100">
                  <motion.div className="flex" animate={{ x: `-${idx * 100}%` }} transition={{ type: "spring", stiffness: 110, damping: 20 }}>
                    {flow.map((f, i) => (
                      <div key={f.title} className="grid w-full shrink-0 gap-6 p-8 md:grid-cols-2">
                        <div><span className="grid h-14 w-14 place-items-center rounded-2xl bg-violet-600 text-white"><f.icon size={26} /></span>
                          <p className="mt-4 text-xs font-semibold text-violet-500">STEP {i + 1} OF {flow.length}</p>
                          <h3 className="mt-1 text-2xl font-bold">{f.title}</h3><p className="mt-2 text-slate-600">{f.desc}</p></div>
                        <ul className="space-y-2 self-center">{f.items.map((it) => <li key={it} className="rounded-xl bg-violet-50 px-4 py-2 text-sm">{it}</li>)}</ul>
                      </div>))}
                  </motion.div>
                </div>
                <div className="mt-5 flex items-center justify-center gap-4">
                  <button aria-label="Previous step" disabled={idx === 0} onClick={() => setIdx(idx - 1)} className="rounded-full bg-white p-2 shadow disabled:opacity-40"><ChevronLeft /></button>
                  <div className="flex gap-2">{flow.map((f, i) => <button key={f.title} aria-label={`Go to step ${i + 1}`} onClick={() => setIdx(i)} className={`h-2.5 rounded-full transition-all ${i === idx ? "w-8 bg-violet-600" : "w-2.5 bg-violet-200"}`} />)}</div>
                  <button aria-label="Next step" disabled={idx === flow.length - 1} onClick={() => setIdx(idx + 1)} className="rounded-full bg-white p-2 shadow disabled:opacity-40"><ChevronRight /></button>
                </div>
              </motion.div>
            ) : (
              <motion.div key="all" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
                <div className="flex snap-x items-stretch gap-3 overflow-x-auto pb-4">
                  {flow.map((f, i) => (
                    <div key={f.title} className="flex shrink-0 snap-start items-center gap-3">
                      <div className="w-60 self-stretch rounded-2xl bg-white p-4 shadow"><f.icon className="text-violet-600" size={20} /><p className="mt-2 text-xs text-slate-400">STEP {i + 1}</p><h3 className="text-sm font-semibold">{f.title}</h3>
                        <ul className="mt-2 space-y-1 text-xs text-slate-500">{f.items.map((it) => <li key={it}>• {it}</li>)}</ul></div>
                      {i < flow.length - 1 && <ArrowRight className="text-violet-400" />}
                    </div>))}
                </div>
                <p className="mt-2 flex items-center justify-center gap-2 text-sm text-slate-500"><Repeat size={14} />Continuous learning: results feed back into better recommendations</p>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </section>

      <section className="mx-auto grid max-w-6xl items-center gap-10 px-5 py-20 md:grid-cols-2">
        <FlowArt className="w-full drop-shadow-xl" />
        <div><h2 className="text-3xl font-bold">Built for small business owners</h2>
          <p className="mt-3 text-slate-600">No analyst needed. Add your business and products, and Market-Strategist turns your feedback and performance signals into clear, ranked actions, each with the reasoning behind it.</p>
          <Link to="/signup" className="mt-6 inline-flex items-center gap-2 rounded-full bg-violet-600 px-6 py-3 font-medium text-white">Create Your Account <ArrowRight size={16} /></Link></div>
      </section>

      <section className="bg-gradient-to-b from-white to-violet-50 py-16 text-center">
        <h2 className="text-3xl font-bold">Ready to turn your data into strategy?</h2>
        <div className="mt-6 flex justify-center gap-3"><Link to="/signup" className="rounded-full bg-violet-600 px-6 py-3 font-medium text-white">Create Your Account</Link><Link to="/login" className="rounded-full border border-slate-200 bg-white px-6 py-3 font-medium">Log In</Link></div>
      </section>

      <footer className="bg-slate-900 text-slate-300">
        <div className="mx-auto grid max-w-6xl gap-8 px-5 py-12 md:grid-cols-4">
          <div className="md:col-span-2"><span className="flex items-center gap-2 font-semibold text-white"><img src="/logo.png" alt="" className="h-7 w-7 rounded bg-white p-0.5" />Market-Strategist</span>
            <p className="mt-3 max-w-sm text-sm">An AI-powered e-commerce marketing strategist for small businesses. A college project.</p></div>
          <div><p className="mb-2 text-sm font-semibold text-white">Product</p><ul className="space-y-1 text-sm"><li><a className="hover:text-white" href="#features">Project flow</a></li><li><a className="hover:text-white" href="#flow">Complete flow</a></li></ul></div>
          <div><p className="mb-2 text-sm font-semibold text-white">Account</p><ul className="space-y-1 text-sm"><li><Link className="hover:text-white" to="/signup">Sign up</Link></li><li><Link className="hover:text-white" to="/login">Log in</Link></li></ul></div>
        </div>
        <p className="border-t border-slate-800 px-5 py-4 text-center text-xs text-slate-500">© {new Date().getFullYear()} Market-Strategist. All figures shown on this page are illustrative demo data.</p>
      </footer>
    </div>
  );
}