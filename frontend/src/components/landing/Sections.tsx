import { KeyboardEvent, ReactNode, useState } from "react";
import { Link } from "react-router-dom";
import { AnimatePresence, motion } from "framer-motion";
import { ArrowRight, Compass, Database, Eye, FileText, Megaphone, MessageSquareText, Pencil, Scale, ShieldCheck, Target, type LucideIcon } from "lucide-react";

const reveal = (i = 0) => ({ initial: { opacity: 0, y: 28 }, whileInView: { opacity: 1, y: 0 }, viewport: { once: true, amount: 0.2 }, transition: { duration: 0.5, delay: i * 0.1 } });
const Tag = ({ children }: { children: ReactNode }) => <span className="inline-block rounded-full bg-amber-100 px-3 py-1 text-xs font-medium text-amber-800">{children}</span>;
const Title = ({ children, sub }: { children: ReactNode; sub?: string }) => (
  <div className="mx-auto max-w-3xl text-center"><h2 className="text-3xl font-bold leading-tight md:text-4xl">{children}</h2>{sub && <p className="mt-3 text-slate-600">{sub}</p>}</div>);

function RackArt() {
  const colors = ["#c4b5fd", "#7dd3fc", "#a78bfa", "#bae6fd"];
  return (
    <svg viewBox="0 0 400 320" className="h-full w-full bg-gradient-to-br from-violet-100 to-sky-100" role="img" aria-label="Illustration of clothes on a rack">
      <line x1="30" y1="70" x2="370" y2="70" stroke="#6d28d9" strokeWidth="4" strokeLinecap="round" />
      {colors.map((c, i) => (<g key={c} transform={`translate(${60 + i * 80} 70)`}><path d="M0 0 v-12" stroke="#6d28d9" strokeWidth="3" /><path d="M-26 14 L0 0 L26 14 L26 30 L16 30 L16 150 h-32 v-120 h-10z" fill={c} opacity={0.9 - i * 0.05} /></g>))}
      <rect x="40" y="250" width="320" height="10" rx="5" fill="#ddd6fe" />
    </svg>);
}
function StoryImage() {
  const [bad, setBad] = useState(false);
  return bad ? <RackArt /> : (
    <img src="https://images.unsplash.com/photo-1441984904996-e0b6ba687e04?auto=format&fit=crop&w=900&q=70" alt="Clothing boutique with garments displayed on racks" loading="lazy" onError={() => setBad(true)} className="h-full w-full object-cover" />);
}

export function StorySection() {
  const callouts = ["Reviews mention fit and sizing", "Attention on the new collection, unclear sales", "Limited time and marketing budget"];
  return (
    <section id="story" className="mx-auto grid max-w-6xl items-center gap-12 px-5 py-20 md:grid-cols-2">
      <motion.div {...reveal()}>
        <Tag>Illustrative business scenario</Tag>
        <h2 className="mt-4 text-3xl font-bold leading-tight md:text-4xl">Every business has data. The challenge is knowing what to do with it.</h2>
        <p className="mt-4 text-slate-600">Imagine running a growing clothing brand. Your latest collection is attracting attention, customers are leaving reviews, and your marketing campaigns are generating activity. But which products deserve more attention? What are customers really telling you? And where should your next marketing effort go?</p>
        <p className="mt-3 text-slate-600">Useful signals may already exist across reviews, product details and campaign metrics. Interpreting them together, with limited time, is the hard part.</p>
      </motion.div>
      <motion.div {...reveal(1)} className="relative">
        <div className="aspect-[4/3] overflow-hidden rounded-3xl shadow-xl shadow-violet-100"><StoryImage /></div>
        <div className="mt-4 flex flex-wrap gap-2 md:absolute md:-bottom-6 md:left-4 md:right-4 md:mt-0">
          {callouts.map((c) => <span key={c} className="rounded-xl bg-white px-3 py-2 text-xs font-medium shadow-lg">{c}</span>)}</div>
      </motion.div>
    </section>);
}

export function ChallengeSection() {
  const qs: { icon: LucideIcon; q: string; a: string; tone: string }[] = [
    { icon: Megaphone, q: "What should I promote?", a: "Product-level data and marketing-performance indicators can help you spot potential opportunities and decide where to focus attention.", tone: "from-violet-500 to-violet-600" },
    { icon: MessageSquareText, q: "What are my customers telling me?", a: "Sentiment analysis and recurring complaint themes help you understand feedback, preferences and possible areas for improvement.", tone: "from-sky-500 to-blue-600" },
    { icon: Compass, q: "Where should my marketing effort go next?", a: "Campaign metrics and available business signals can inform prioritization instead of relying only on intuition.", tone: "from-indigo-500 to-purple-600" },
  ];
  return (
    <section className="bg-gradient-to-b from-white via-violet-50/60 to-white py-20">
      <Title>Three questions every growing business faces.</Title>
      <div className="mx-auto mt-12 grid max-w-6xl gap-6 px-5 md:grid-cols-3">
        {qs.map((c, i) => (
          <motion.article key={c.q} {...reveal(i)} whileHover={{ y: -6 }} className="overflow-hidden rounded-3xl border border-slate-100 bg-white shadow-sm hover:shadow-xl hover:shadow-violet-100">
            <div className={`flex items-center gap-3 bg-gradient-to-r ${c.tone} p-5 text-white`}><c.icon size={22} /><span className="text-xs font-semibold opacity-80">QUESTION {i + 1}</span></div>
            <div className="p-6"><h3 className="text-lg font-semibold">{c.q}</h3><p className="mt-2 text-sm text-slate-600">{c.a}</p></div>
          </motion.article>))}
      </div>
    </section>);
}

export function SolutionSection() {
  const stages: { icon: LucideIcon; t: string; d: string }[] = [
    { icon: Database, t: "Understand the data", d: "Analyze available customer feedback, product information and marketing-performance metrics." },
    { icon: Scale, t: "Prioritize opportunities", d: "Use analytical indicators and a scoring framework to prioritize potential actions." },
    { icon: FileText, t: "Explain the strategy", d: "Generate recommendations with supporting evidence and explanations, so you can judge their relevance." },
  ];
  return (
    <section className="bg-gradient-to-br from-violet-700 via-violet-600 to-indigo-700 py-20 text-white">
      <div className="mx-auto max-w-6xl px-5">
        <div className="mx-auto max-w-3xl text-center"><h2 className="text-3xl font-bold leading-tight md:text-4xl">Meet Market-Strategist: from scattered signals to strategic direction.</h2></div>
        <ol className="mt-14 grid gap-6 md:grid-cols-3">
          {stages.map((s, i) => (
            <motion.li key={s.t} {...reveal(i)} className="relative rounded-3xl bg-white/10 p-6 ring-1 ring-white/20 backdrop-blur-sm">
              <span className="grid h-12 w-12 place-items-center rounded-2xl bg-white text-violet-700"><s.icon size={22} /></span>
              <p className="mt-4 text-xs font-semibold text-violet-200">STAGE {i + 1}</p><h3 className="text-xl font-semibold">{s.t}</h3><p className="mt-2 text-sm text-violet-100">{s.d}</p>
              {i < 2 && <ArrowRight aria-hidden className="absolute -right-5 top-1/2 hidden -translate-y-1/2 text-white/70 md:block" />}
            </motion.li>))}
        </ol>
        <p className="mt-8 text-center text-sm text-violet-200">Recommendations are decision support with evidence, not guarantees of results.</p>
      </div>
    </section>);
}

const signal: { label: string; icon: LucideIcon; title: string; body: string }[] = [
  { label: "Evidence", icon: Eye, title: "Business signal", body: "Customers repeatedly mention inconsistent sizing in reviews of a clothing collection." },
  { label: "Analysis", icon: Database, title: "What the system examines", body: "The system examines recurring feedback themes alongside the available product and marketing-performance information." },
  { label: "Recommendation", icon: Target, title: "Potential recommendation", body: "Review the sizing information and product descriptions before increasing promotional spend on the collection." },
  { label: "Rationale", icon: ShieldCheck, title: "Why this recommendation?", body: "It addresses a recurring customer concern before the business invests additional effort in promoting the collection." },
];
export function SignalSection() {
  const [i, setI] = useState(0);
  const onKey = (e: KeyboardEvent) => {
    if (e.key === "ArrowRight") setI((v) => Math.min(v + 1, signal.length - 1));
    if (e.key === "ArrowLeft") setI((v) => Math.max(v - 1, 0));
  };
  const cur = signal[i];
  return (
    <section className="mx-auto max-w-5xl px-5 py-20">
      <Title>See how a business signal becomes a strategy.</Title>
      <div className="mt-4 text-center"><Tag>Illustrative example. Not real customer data or a real generated recommendation.</Tag></div>
      <div role="tablist" aria-label="Signal to strategy stages" onKeyDown={onKey} className="relative mt-10 grid grid-cols-4 gap-2">
        <div aria-hidden className="absolute left-[12.5%] right-[12.5%] top-5 h-0.5 bg-violet-100"><motion.div className="h-full bg-violet-500" animate={{ width: `${(i / (signal.length - 1)) * 100}%` }} /></div>
        {signal.map((s, n) => (
          <button key={s.label} role="tab" aria-selected={n === i} tabIndex={n === i ? 0 : -1} onClick={() => setI(n)} className="relative flex flex-col items-center gap-2 rounded-xl p-1 focus-visible:outline focus-visible:outline-2 focus-visible:outline-violet-500">
            <span className={`grid h-10 w-10 place-items-center rounded-full transition ${n <= i ? "bg-violet-600 text-white" : "bg-violet-100 text-violet-500"}`}><s.icon size={18} /></span>
            <span className={`text-xs font-medium sm:text-sm ${n === i ? "text-violet-700" : "text-slate-500"}`}>{s.label}</span>
          </button>))}
      </div>
      <div role="tabpanel" className="mt-8 min-h-[9rem] rounded-3xl border border-violet-100 bg-gradient-to-br from-white to-violet-50 p-8 shadow-lg shadow-violet-100">
        <AnimatePresence mode="wait"><motion.div key={i} initial={{ opacity: 0, x: 16 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0 }}>
          <p className="flex items-center gap-2 text-xs font-semibold uppercase text-violet-500"><cur.icon size={14} />Step {i + 1} of {signal.length}</p>
          <h3 className="mt-2 text-xl font-semibold">{cur.title}</h3><p className="mt-2 text-lg text-slate-700">{cur.body}</p>
        </motion.div></AnimatePresence>
      </div>
      <div className="mt-4 flex justify-center gap-3 text-sm">
        <button disabled={i === 0} onClick={() => setI(i - 1)} className="rounded-full border border-slate-200 px-4 py-1.5 disabled:opacity-40">Previous</button>
        <button disabled={i === signal.length - 1} onClick={() => setI(i + 1)} className="rounded-full bg-violet-600 px-4 py-1.5 text-white disabled:opacity-40">Next</button>
      </div>
    </section>);
}

export function HumanLoopSection() {
  const steps: [LucideIcon, string][] = [[Eye, "Review the recommendation"], [FileText, "Understand the evidence and rationale"], [Pencil, "Approve, edit or reject it"], [Target, "Execute the chosen action independently"], [ShieldCheck, "Record outcomes where supported by the application"]];
  return (
    <section className="bg-gradient-to-b from-sky-50 to-white py-20">
      <div className="mx-auto grid max-w-6xl items-center gap-12 px-5 md:grid-cols-2">
        <motion.div {...reveal()} className="rounded-3xl bg-white p-6 shadow-xl shadow-violet-100">
          <Tag>Illustrative example</Tag>
          <p className="mt-4 text-xs font-semibold text-violet-500">RECOMMENDATION</p>
          <p className="mt-1 font-semibold">Review the sizing information and product descriptions before increasing promotional spend on the collection.</p>
          <p className="mt-3 text-sm text-slate-600"><b>Evidence:</b> recurring sizing feedback in reviews.</p>
          <div aria-hidden className="mt-5 grid grid-cols-3 gap-2 text-center text-xs font-medium"><span className="rounded-lg bg-emerald-50 py-2 text-emerald-700">Approve</span><span className="rounded-lg bg-violet-50 py-2 text-violet-700">Edit</span><span className="rounded-lg bg-slate-100 py-2 text-slate-600">Reject</span></div>
          <p className="mt-3 text-xs text-slate-400">Static preview. These are not working buttons.</p>
        </motion.div>
        <div>
          <h2 className="text-3xl font-bold md:text-4xl">AI recommends. You decide.</h2>
          <p className="mt-3 text-slate-600">Market-Strategist supports your judgment rather than replacing it. It does not publish content or run campaigns for you.</p>
          <ol className="mt-6 space-y-3">{steps.map(([Icon, t], n) => (
            <motion.li key={t} {...reveal(n * 0.5)} className="flex items-center gap-3 rounded-xl bg-white p-3 shadow-sm"><span className="grid h-9 w-9 place-items-center rounded-lg bg-violet-100 text-violet-600"><Icon size={16} /></span><span className="text-sm font-medium">{t}</span></motion.li>))}</ol>
        </div>
      </div>
    </section>);
}

export function FinalCTA() {
  return (
    <section className="bg-gradient-to-b from-white to-violet-100 px-5 py-20 text-center">
      <h2 className="mx-auto max-w-2xl text-3xl font-bold md:text-4xl">Make your next marketing decision more informed.</h2>
      <Link to="/signup" className="mt-8 inline-flex items-center gap-2 rounded-full bg-violet-600 px-8 py-3.5 font-medium text-white shadow-lg shadow-violet-200 transition hover:bg-violet-700 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-violet-600">Create Your Account <ArrowRight size={16} /></Link>
      <p className="mt-4 text-sm text-slate-500">Already have an account? <Link to="/login" className="font-medium text-violet-600 underline">Log in</Link></p>
    </section>);
}