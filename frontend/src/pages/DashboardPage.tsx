import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { AnimatePresence, animate, motion } from "framer-motion";
import { BarChart3, Bell, Building2, Check, Construction, History, LayoutDashboard, LogOut, MessageSquareText, Package, Settings, Sparkles, X, type LucideIcon } from "lucide-react";
import { Area, AreaChart, Bar, BarChart, Cell, Pie, PieChart, ResponsiveContainer, Tooltip, XAxis } from "recharts";
import { actions, activity, inProgress, sentiment, traffic } from "../data/demo-data";
import { logout, me, User } from "../services/auth-service";
import BusinessProfilePanel from "../components/BusinessProfilePanel";

const icons: Record<string, LucideIcon> = {
  Overview: LayoutDashboard, "Business Profile": Building2, Products: Package, "Customer Insights": MessageSquareText,
  "Marketing Analytics": BarChart3, "AI Recommendations": Sparkles, "Recommendation History": History, Settings,
};
const pieColors = ["#34d399", "#cbd5e1", "#fb7185"];
const channels = [{ c: "Website", v: 42 }, { c: "Market", v: 31 }, { c: "Social", v: 19 }, { c: "Store", v: 8 }];
const card = "rounded-2xl border border-slate-100 bg-white p-5 shadow-sm transition hover:shadow-md";

function Counter({ to, suffix = "" }: { to: number; suffix?: string }) {
  const [n, setN] = useState(0);
  useEffect(() => { const c = animate(0, to, { duration: 1.1, onUpdate: (v) => setN(Math.round(v)) }); return () => c.stop(); }, [to]);
  return <>{n.toLocaleString()}{suffix}</>;
}

function Ring({ pct }: { pct: number }) {
  const r = 30, c = 2 * Math.PI * r;
  return (
    <svg width="76" height="76" viewBox="0 0 76 76" className="-rotate-90">
      <circle cx="38" cy="38" r={r} fill="none" stroke="#ede9fe" strokeWidth="8" />
      <motion.circle cx="38" cy="38" r={r} fill="none" stroke="#7c3aed" strokeWidth="8" strokeLinecap="round" strokeDasharray={c}
        initial={{ strokeDashoffset: c }} animate={{ strokeDashoffset: c * (1 - pct / 100) }} transition={{ duration: 1.2 }} />
    </svg>
  );
}

export default function DashboardPage() {
  const nav = useNavigate();
  const [user, setUser] = useState<User | null>(null);
  const [error, setError] = useState("");
  const [active, setActive] = useState("Overview");
  const [menu, setMenu] = useState(false);
  const [decided, setDecided] = useState<Record<string, "accepted" | "rejected">>({});

  useEffect(() => {
    me().then((u) => { setUser(u); if (!u.onboarding_completed) setActive("Business Profile"); }).catch((e: Error) => { setError(e.message); logout(); nav("/login"); });
  }, [nav]);

  if (!user) return <div className="grid min-h-screen place-items-center text-slate-500">{error || "Loading…"}</div>;
  const items = ["Overview", ...Object.keys(inProgress)];
  const name = user.email.split("@")[0];
  const today = new Date().toLocaleDateString(undefined, { weekday: "long", day: "numeric", month: "long" });
  const kpis: [string, number, string, string][] = [["Total products", 12, "", "Demo"], ["Positive sentiment", 68, "%", "Demo"], ["Weekly sessions", 4200, "", "Demo"]];
  const done = user.onboarding_completed;
  const stagger = (i: number) => ({ initial: { opacity: 0, y: 16 }, animate: { opacity: 1, y: 0 }, transition: { delay: i * 0.06 } });

  return (
    <div className="flex min-h-screen flex-col bg-gradient-to-br from-slate-50 to-violet-50/40 md:flex-row">
      <aside className="flex flex-col border-b border-slate-100 bg-white md:w-64 md:border-b-0 md:border-r">
        <div className="hidden items-center gap-2 px-5 py-5 font-semibold md:flex"><img src="/logo.png" alt="" className="h-8 w-8" />Market-Strategist</div>
        <nav className="flex flex-1 gap-1 overflow-x-auto p-3 md:flex-col">
          {items.map((i) => { const Icon = icons[i]; return (
            <button key={i} onClick={() => setActive(i)} className={`flex items-center gap-2 whitespace-nowrap rounded-xl px-3 py-2.5 text-left text-sm transition ${active === i ? "bg-violet-600 font-medium text-white shadow-md shadow-violet-200" : "text-slate-600 hover:bg-violet-50"}`}>
              <Icon size={16} /><span className="flex-1">{i}</span>
              {!["Overview", "Business Profile"].includes(i) && <span className={`rounded px-1.5 text-[10px] ${active === i ? "bg-white/25 text-white" : "bg-amber-100 text-amber-700"}`}>In Progress</span>}
            </button>); })}
        </nav>
        <div className="hidden items-center gap-3 border-t border-slate-100 p-4 md:flex">
          <span className="grid h-9 w-9 place-items-center rounded-full bg-violet-600 text-sm text-white">{name[0].toUpperCase()}</span>
          <div className="min-w-0 flex-1"><p className="truncate text-sm font-medium">{name}</p><p className="truncate text-xs text-slate-400">{user.email}</p></div>
        </div>
      </aside>

      <main className="flex-1 p-5 md:p-8">
        <div className="mb-6 flex items-start justify-between">
          <div><p className="text-xs text-slate-400">{today}</p><h1 className="text-2xl font-bold">Welcome back, {name} 👋</h1><p className="text-sm text-slate-500">Demo business workspace</p></div>
          <div className="relative flex items-center gap-3">
            <button aria-label="Notifications" className="rounded-full bg-white p-2 shadow-sm"><Bell size={16} className="text-slate-500" /></button>
            <button onClick={() => setMenu(!menu)} className="grid h-9 w-9 place-items-center rounded-full bg-violet-600 text-sm text-white">{name[0].toUpperCase()}</button>
            <AnimatePresence>{menu && (
              <motion.div initial={{ opacity: 0, y: -6 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }} className="absolute right-0 top-12 z-10 w-44 rounded-xl border border-slate-100 bg-white p-1 shadow-lg">
                <p className="truncate px-3 py-2 text-xs text-slate-400">{user.email}</p>
                <button onClick={() => { logout(); nav("/"); }} className="flex w-full items-center gap-2 rounded-lg px-3 py-2 text-sm hover:bg-slate-50"><LogOut size={14} />Log out</button>
              </motion.div>)}</AnimatePresence>
          </div>
        </div>

        <AnimatePresence mode="wait">
          <motion.div key={active} initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }}>
            {active === "Business Profile" ? (<BusinessProfilePanel onSaved={() => { me().then(setUser).catch(() => undefined); }} />) : active !== "Overview" ? (
              <div className="grid place-items-center rounded-2xl border border-dashed border-violet-200 bg-white/70 py-24 text-center">
                <span className="grid h-14 w-14 place-items-center rounded-2xl bg-violet-100 text-violet-600"><Construction size={26} /></span>
                <h2 className="mt-4 text-xl font-semibold">{active}</h2>
                <span className="mt-2 rounded bg-amber-100 px-2 py-0.5 text-xs text-amber-700">In Progress</span>
                <p className="mt-3 max-w-sm text-sm text-slate-500">{inProgress[active]} Coming soon.</p></div>
            ) : (
              <div className="space-y-5">
                <p className="text-xs text-slate-400">Metrics, charts and recommendations below are illustrative demo data.</p>
                {!done && <div className="flex items-center justify-between rounded-xl bg-violet-100/70 p-4 text-sm"><span>Your business profile setup is incomplete.</span><button onClick={() => setActive("Business Profile")} className="rounded-lg bg-violet-600 px-3 py-1.5 text-white">Complete profile</button></div>}

                <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
                  {kpis.map(([l, v, s, tag], i) => (
                    <motion.div key={l} {...stagger(i)} className={card}><div className="flex justify-between text-sm text-slate-500">{l}<span className="rounded bg-slate-100 px-1.5 text-[10px]">{tag}</span></div>
                      <p className="mt-2 text-3xl font-bold"><Counter to={v} suffix={s} /></p></motion.div>))}
                  <motion.div {...stagger(3)} className={`${card} flex items-center gap-4`}><div className="relative"><Ring pct={done ? 100 : 0} /><span className="absolute inset-0 grid place-items-center text-sm font-semibold">{done ? "100%" : "0%"}</span></div>
                    <div><p className="text-sm text-slate-500">Business profile</p><p className="font-semibold">{done ? "Complete" : "Not finished"}</p></div></motion.div>
                </div>

                <div className="grid gap-4 lg:grid-cols-3">
                  <div className={`${card} lg:col-span-2`}><p className="mb-2 text-sm font-medium">Marketing performance: weekly sessions (demo)</p>
                    <div className="h-56"><ResponsiveContainer width="100%" height="100%"><AreaChart data={traffic}><defs><linearGradient id="ar" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stopColor="#7c3aed" stopOpacity={0.35} /><stop offset="1" stopColor="#7c3aed" stopOpacity={0} /></linearGradient></defs>
                      <XAxis dataKey="d" axisLine={false} tickLine={false} /><Tooltip /><Area dataKey="v" stroke="#7c3aed" strokeWidth={2.5} fill="url(#ar)" /></AreaChart></ResponsiveContainer></div></div>
                  <div className={card}><p className="text-sm font-medium">Customer sentiment (demo)</p>
                    <div className="h-40"><ResponsiveContainer width="100%" height="100%"><PieChart><Pie data={sentiment.map((s) => ({ name: s.label, value: s.pct }))} dataKey="value" innerRadius={42} outerRadius={64} paddingAngle={3}>
                      {sentiment.map((s, i) => <Cell key={s.label} fill={pieColors[i]} />)}</Pie><Tooltip /></PieChart></ResponsiveContainer></div>
                    <div className="flex justify-center gap-3 text-xs text-slate-500">{sentiment.map((s, i) => <span key={s.label} className="flex items-center gap-1"><i className="h-2 w-2 rounded-full" style={{ background: pieColors[i] }} />{s.label} {s.pct}%</span>)}</div></div>
                </div>

                <div className="grid gap-4 lg:grid-cols-3">
                  <motion.div whileHover={{ y: -3 }} className="rounded-2xl bg-gradient-to-br from-violet-600 to-indigo-600 p-5 text-white shadow-lg shadow-violet-200">
                    <p className="flex items-center gap-2 text-xs uppercase tracking-wide text-violet-200"><Sparkles size={14} />Top marketing opportunity (demo)</p>
                    <p className="mt-3 text-lg font-semibold">{actions[0].t}</p><p className="mt-2 text-sm text-violet-100">{actions[0].why}</p></motion.div>
                  <div className={card}><p className="mb-2 text-sm font-medium">Channel mix (demo)</p>
                    <div className="h-36"><ResponsiveContainer width="100%" height="100%"><BarChart data={channels}><XAxis dataKey="c" axisLine={false} tickLine={false} fontSize={11} /><Tooltip /><Bar dataKey="v" radius={[6, 6, 0, 0]}>{channels.map((c, i) => <Cell key={c.c} fill={i === 0 ? "#7c3aed" : "#c4b5fd"} />)}</Bar></BarChart></ResponsiveContainer></div></div>
                  <div className={card}><p className="mb-3 text-sm font-medium">Recent activity (demo)</p><ol className="space-y-3 border-l-2 border-violet-100 pl-4">{activity.map((a) => <li key={a} className="relative text-sm text-slate-600"><i className="absolute -left-[22px] top-1.5 h-2.5 w-2.5 rounded-full bg-violet-500" />{a}</li>)}</ol></div>
                </div>

                <div className={card}><p className="mb-3 text-sm font-medium">Recommended next actions (demo)</p>
                  <div className="space-y-3">{actions.map((a, i) => { const d = decided[a.t]; return (
                    <motion.div layout key={a.t} className={`flex flex-wrap items-center gap-3 rounded-xl p-4 transition ${d === "accepted" ? "bg-emerald-50" : d === "rejected" ? "bg-slate-50 opacity-60" : "bg-violet-50"}`}>
                      <span className="grid h-7 w-7 place-items-center rounded-full bg-white text-xs font-bold text-violet-600">{i + 1}</span>
                      <div className="min-w-0 flex-1"><p className="text-sm font-medium">{a.t}</p><p className="text-xs text-slate-500">{a.why}</p></div>
                      {d ? <span className="text-xs font-medium capitalize text-slate-500">{d}</span> : <div className="flex gap-2">
                        <button onClick={() => setDecided({ ...decided, [a.t]: "accepted" })} className="flex items-center gap-1 rounded-lg bg-emerald-500 px-3 py-1.5 text-xs text-white hover:bg-emerald-600"><Check size={12} />Accept</button>
                        <button onClick={() => setDecided({ ...decided, [a.t]: "rejected" })} className="flex items-center gap-1 rounded-lg bg-white px-3 py-1.5 text-xs text-slate-600 hover:bg-slate-100"><X size={12} />Reject</button></div>}
                    </motion.div>); })}</div></div>
              </div>)}
          </motion.div>
        </AnimatePresence>
      </main>
    </div>
  );
}