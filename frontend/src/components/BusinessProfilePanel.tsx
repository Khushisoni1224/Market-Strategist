import { FormEvent, ReactNode, useEffect, useState } from "react";
import { motion } from "framer-motion";
import { CheckCircle2, Loader2, Save } from "lucide-react";
import { BusinessModel, getProfile, saveProfile } from "../services/profile-service";

const channelOptions: [string, string][] = [
  ["own_website", "Own website"], ["marketplace", "Marketplace (Amazon, Etsy…)"], ["social_commerce", "Social media / commerce"],
  ["physical_store", "Physical store"], ["wholesale", "Wholesale / B2B"], ["direct_sales", "Direct sales"], ["other", "Other"],
];
const models: [BusinessModel, string, string][] = [
  ["product", "Product-based", "You sell goods"], ["service", "Service-based", "You sell expertise or time"], ["both", "Both", "Products and services"],
];
interface Form {
  business_name: string; industry: string; description: string; business_model: BusinessModel | "";
  sales_channels: string[]; target_audience: string; website_url: string; location: string; goals: string;
}
const empty: Form = { business_name: "", industry: "", description: "", business_model: "", sales_channels: [], target_audience: "", website_url: "", location: "", goals: "" };
const input = "w-full rounded-xl border border-slate-200 bg-white px-4 py-2.5 text-sm outline-none transition focus:border-violet-500 focus:ring-4 focus:ring-violet-100";

function validate(f: Form): Record<string, string> {
  const e: Record<string, string> = {};
  if (!f.business_name.trim()) e.business_name = "Enter your brand or business name.";
  if (!f.industry.trim()) e.industry = "Enter your industry or business domain.";
  if (f.description.trim().length < 10) e.description = "Describe your business in at least 10 characters.";
  if (!f.business_model) e.business_model = "Choose a business model.";
  if (f.sales_channels.length === 0) e.sales_channels = "Select at least one sales channel.";
  const url = f.website_url.trim();
  if (url) { try { if (!["http:", "https:"].includes(new URL(url).protocol)) throw 0; } catch { e.website_url = "Enter a valid http:// or https:// URL."; } }
  return e;
}

function Field({ label, error, required, children }: { label: string; error?: string; required?: boolean; children: ReactNode }) {
  return (<label className="block text-sm"><span className="mb-1 block font-medium">{label}{required && <span className="text-rose-500"> *</span>}</span>{children}
    {error && <span role="alert" className="mt-1 block text-xs text-rose-600">{error}</span>}</label>);
}

export default function BusinessProfilePanel({ onSaved }: { onSaved: () => void }) {
  const [form, setForm] = useState<Form>(empty);
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState("");
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [saving, setSaving] = useState(false);
  const [saveError, setSaveError] = useState("");
  const [saved, setSaved] = useState(false);
  const [exists, setExists] = useState(false);
  const [complete, setComplete] = useState(false);

  function load() {
    setLoading(true); setLoadError("");
    getProfile().then((p) => {
      if (!p) return;
      setExists(true); setComplete(p.onboarding_completed);
      setForm({
        business_name: p.business_name, industry: p.industry, description: p.description ?? "", business_model: p.business_model ?? "",
        sales_channels: p.sales_channels.filter((c) => channelOptions.some(([v]) => v === c)),
        target_audience: p.target_audience ?? "", website_url: p.website_url ?? "", location: p.location ?? "", goals: p.goals ?? "",
      });
    }).catch((e: Error) => setLoadError(e.message)).finally(() => setLoading(false));
  }
  useEffect(() => { load(); }, []);

  function set<K extends keyof Form>(k: K, v: Form[K]) { setForm((f) => ({ ...f, [k]: v })); setSaved(false); setErrors((e) => ({ ...e, [k]: "" })); }
  const toggle = (c: string) => set("sales_channels", form.sales_channels.includes(c) ? form.sales_channels.filter((x) => x !== c) : [...form.sales_channels, c]);

  async function submit(e: FormEvent) {
    e.preventDefault();
    const errs = validate(form); setErrors(errs);
    if (Object.keys(errs).length) return;
    setSaving(true); setSaveError("");
    try {
      const p = await saveProfile({
        business_name: form.business_name.trim(), industry: form.industry.trim(), description: form.description.trim(),
        business_model: form.business_model as BusinessModel, sales_channels: form.sales_channels,
        target_audience: form.target_audience.trim() || null, website_url: form.website_url.trim() || null,
        location: form.location.trim() || null, goals: form.goals.trim() || null,
      });
      setExists(true); setComplete(p.onboarding_completed); setSaved(true); onSaved();
    } catch (err) { setSaveError(err instanceof Error ? err.message : "Could not save your profile."); }
    finally { setSaving(false); }
  }

  if (loading) return <div className="space-y-4" aria-busy>{[0, 1, 2].map((i) => <div key={i} className="h-28 animate-pulse rounded-2xl bg-white" />)}</div>;
  if (loadError) return (
    <div className="rounded-2xl border border-rose-100 bg-white p-8 text-center"><p className="text-rose-600">{loadError}</p>
      <button onClick={load} className="mt-4 rounded-xl bg-violet-600 px-5 py-2 text-sm text-white">Try again</button></div>);

  return (
    <motion.form onSubmit={submit} noValidate initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} className="space-y-5">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div><h2 className="text-xl font-bold">{exists ? "Business profile" : "Set up your business profile"}</h2>
          <p className="text-sm text-slate-500">This information helps tailor future marketing recommendations to your business.</p></div>
        <span className={`rounded-full px-3 py-1 text-xs font-medium ${complete ? "bg-emerald-100 text-emerald-700" : "bg-amber-100 text-amber-700"}`}>{complete ? "Profile complete" : "Setup incomplete"}</span>
      </div>

      <section className="space-y-4 rounded-2xl border border-slate-100 bg-white p-5 shadow-sm">
        <h3 className="font-semibold">About your business</h3>
        <div className="grid gap-4 md:grid-cols-2">
          <Field label="Brand / entity name" required error={errors.business_name}><input className={input} maxLength={200} value={form.business_name} onChange={(e) => set("business_name", e.target.value)} /></Field>
          <Field label="Industry / business domain" required error={errors.industry}><input className={input} maxLength={100} placeholder="e.g. Home decor" value={form.industry} onChange={(e) => set("industry", e.target.value)} /></Field>
        </div>
        <Field label="Business description" required error={errors.description}>
          <textarea className={input} rows={3} maxLength={2000} value={form.description} onChange={(e) => set("description", e.target.value)} />
          <span className="text-xs text-slate-400">{form.description.length}/2000</span></Field>
      </section>

      <section className="space-y-4 rounded-2xl border border-slate-100 bg-white p-5 shadow-sm">
        <div><h3 className="mb-2 font-semibold">Business model <span className="text-rose-500">*</span></h3>
          <div className="grid gap-3 sm:grid-cols-3">{models.map(([v, t, d]) => (
            <button type="button" key={v} onClick={() => set("business_model", v)} aria-pressed={form.business_model === v}
              className={`rounded-xl border p-4 text-left transition hover:-translate-y-0.5 ${form.business_model === v ? "border-violet-500 bg-violet-50 ring-2 ring-violet-200" : "border-slate-200 hover:border-violet-300"}`}>
              <p className="text-sm font-semibold">{t}</p><p className="text-xs text-slate-500">{d}</p></button>))}</div>
          {errors.business_model && <p role="alert" className="mt-1 text-xs text-rose-600">{errors.business_model}</p>}</div>
        <div><h3 className="mb-2 font-semibold">Sales channels <span className="text-rose-500">*</span> <span className="text-xs font-normal text-slate-400">select all that apply</span></h3>
          <div className="flex flex-wrap gap-2">{channelOptions.map(([v, l]) => (
            <button type="button" key={v} onClick={() => toggle(v)} aria-pressed={form.sales_channels.includes(v)}
              className={`rounded-full border px-4 py-1.5 text-sm transition ${form.sales_channels.includes(v) ? "border-violet-600 bg-violet-600 text-white" : "border-slate-200 bg-white hover:border-violet-300"}`}>{l}</button>))}</div>
          {errors.sales_channels && <p role="alert" className="mt-1 text-xs text-rose-600">{errors.sales_channels}</p>}</div>
      </section>

      <section className="space-y-4 rounded-2xl border border-slate-100 bg-white p-5 shadow-sm">
        <h3 className="font-semibold">Optional details</h3>
        <div className="grid gap-4 md:grid-cols-2">
          <Field label="Website or public social profile" error={errors.website_url}><input className={input} placeholder="https://" value={form.website_url} onChange={(e) => set("website_url", e.target.value)} /></Field>
          <Field label="Location / target market"><input className={input} maxLength={200} value={form.location} onChange={(e) => set("location", e.target.value)} /></Field>
        </div>
        <Field label="Target audience"><textarea className={input} rows={2} maxLength={2000} value={form.target_audience} onChange={(e) => set("target_audience", e.target.value)} /></Field>
        <Field label="Marketing goals"><textarea className={input} rows={2} maxLength={2000} value={form.goals} onChange={(e) => set("goals", e.target.value)} /></Field>
      </section>

      {saveError && <p role="alert" className="rounded-xl bg-rose-50 px-4 py-3 text-sm text-rose-600">{saveError}</p>}
      {saved && <motion.p initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="flex items-center gap-2 rounded-xl bg-emerald-50 px-4 py-3 text-sm text-emerald-700"><CheckCircle2 size={16} />Profile saved.</motion.p>}
      <motion.button whileTap={{ scale: 0.98 }} disabled={saving} className="flex items-center gap-2 rounded-xl bg-violet-600 px-6 py-3 font-medium text-white shadow-lg shadow-violet-200 disabled:opacity-60">
        {saving ? <Loader2 size={16} className="animate-spin" /> : <Save size={16} />}{saving ? "Saving…" : exists ? "Save changes" : "Save profile"}</motion.button>
    </motion.form>
  );
}