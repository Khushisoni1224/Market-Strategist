// Central API client. Real backend only; the base URL comes from VITE_API_BASE_URL.
const BASE: string = import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000/api/v1";
let token: string | null = sessionStorage.getItem("ms_token"); // access token only, never passwords
export function setToken(t: string | null) {
  token = t;
  if (t) sessionStorage.setItem("ms_token", t); else sessionStorage.removeItem("ms_token");
}
export class ApiError extends Error {
  constructor(message: string, public status: number) { super(message); }
}
export const hasToken = () => token !== null;
export async function api<T>(path: string, init: RequestInit = {}): Promise<T> {
  const headers = new Headers(init.headers);
  if (token) headers.set("Authorization", `Bearer ${token}`);
  let res: Response;
  try { res = await fetch(`${BASE}${path}`, { ...init, headers }); }
  catch { throw new Error("Cannot reach the server. Is the backend running?"); }
  if (!res.ok) {
    const body = await res.json().catch(() => null);
    const d = body?.detail;
    throw new ApiError(typeof d === "string" ? d : Array.isArray(d) ? d.map((e: { msg: string }) => e.msg).join(", ") : "Request failed", res.status);
  }
  return res.status === 204 ? (undefined as T) : ((await res.json()) as T);
}