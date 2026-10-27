import { api, setToken } from "./api-client";
export interface User { id: number; email: string; is_active: boolean; onboarding_completed: boolean }
export const register = (email: string, password: string) =>
  api("/auth/register", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ email, password }) });
export async function login(email: string, password: string) {
  // Backend login is OAuth2 form-encoded: username = email
  const r = await api<{ access_token: string }>("/auth/login", { method: "POST", body: new URLSearchParams({ username: email, password }) });
  setToken(r.access_token);
}
export const me = () => api<User>("/auth/me");
export const logout = () => setToken(null);
