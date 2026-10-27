import { FormEvent, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { Eye, EyeOff } from "lucide-react";
import { login, register } from "../services/auth-service";
import { Blobs, FlowArt } from "../components/Art";

export default function AuthPage({ mode }: { mode: "signup" | "login" }) {
  const signup = mode === "signup";
  const nav = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirm, setConfirm] = useState("");
  const [show, setShow] = useState(false);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [done, setDone] = useState(false);

  function validate(): string {
    if (!/^\S+@\S+\.\S+$/.test(email)) return "Enter a valid email address.";
    if (signup) {
      if (password.length < 8 || !/[A-Za-z]/.test(password) || !/\d/.test(password)) return "Password needs 8+ characters with a letter and a digit.";
      if (password !== confirm) return "Passwords do not match.";
    } else if (!password) return "Enter your password.";
    return "";
  }

  async function submit(e: FormEvent) {
    e.preventDefault();
    const problem = validate();
    if (problem) return setError(problem);
    setError(""); setLoading(true);
    try {
      if (signup) await register(email.trim().toLowerCase(), password);
      await login(email.trim().toLowerCase(), password);
      setDone(true);
      setTimeout(() => nav("/dashboard"), 600);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong.");
    } finally { setLoading(false); }
  }

  const input = "w-full rounded-xl border border-slate-200 px-4 py-3 outline-none transition focus:border-violet-500 focus:ring-4 focus:ring-violet-100";
  return (
    <div className="relative grid min-h-screen overflow-hidden bg-gradient-to-br from-violet-50 via-white to-sky-50 md:grid-cols-2">
      <Blobs className="absolute inset-0 h-full w-full opacity-40" />
      <div className="relative z-10 grid place-items-center px-5 py-10">
      <motion.form onSubmit={submit} noValidate initial={{ opacity: 0, y: 24 }} animate={{ opacity: 1, y: 0 }}
        className="w-full max-w-md space-y-4 rounded-2xl border border-slate-100 bg-white p-8 shadow-xl shadow-violet-100">
        <h1 className="text-2xl font-bold">{signup ? "Create your account" : "Welcome back"}</h1>
        <input className={input} type="email" placeholder="Email" value={email} onChange={(e) => setEmail(e.target.value)} autoComplete="email" />
        <div className="relative">
          <input className={input} type={show ? "text" : "password"} placeholder="Password" value={password} onChange={(e) => setPassword(e.target.value)} autoComplete={signup ? "new-password" : "current-password"} />
          <button type="button" aria-label="Toggle password visibility" onClick={() => setShow(!show)} className="absolute right-3 top-3.5 text-slate-400">{show ? <EyeOff size={18} /> : <Eye size={18} />}</button>
        </div>
        {signup && <input className={input} type={show ? "text" : "password"} placeholder="Confirm password" value={confirm} onChange={(e) => setConfirm(e.target.value)} autoComplete="new-password" />}
        {error && <p role="alert" className="rounded-lg bg-rose-50 px-3 py-2 text-sm text-rose-600">{error}</p>}
        {done && <p className="rounded-lg bg-emerald-50 px-3 py-2 text-sm text-emerald-700">Success! Redirecting…</p>}
        <motion.button whileTap={{ scale: 0.98 }} disabled={loading} className="w-full rounded-xl bg-violet-600 py-3 font-medium text-white disabled:opacity-60">
          {loading ? "Please wait…" : signup ? "Sign up" : "Log in"}</motion.button>
        <p className="text-center text-sm text-slate-500">{signup ? "Already have an account? " : "New here? "}
          <Link className="font-medium text-violet-600" to={signup ? "/login" : "/signup"}>{signup ? "Log in" : "Sign up"}</Link></p>
      </motion.form>
      </div>
      <aside className="relative z-10 hidden place-items-center p-10 md:grid"><div className="max-w-md text-center"><FlowArt className="w-full drop-shadow-xl" /><p className="mt-6 text-lg font-semibold">From your data to smarter marketing</p><p className="mt-1 text-sm text-slate-500">Illustrative artwork. Not live business data.</p></div></aside>
    </div>
  );
}