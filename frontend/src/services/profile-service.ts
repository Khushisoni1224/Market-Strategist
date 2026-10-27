import { api, ApiError } from "./api-client";

export type BusinessModel = "product" | "service" | "both";
export interface BusinessProfile {
  id: number; user_id: number; business_name: string; industry: string;
  description: string | null; business_model: BusinessModel | null; sales_channels: string[];
  target_audience: string | null; website_url: string | null; location: string | null; goals: string | null;
  onboarding_completed: boolean;
}
export interface ProfileInput {
  business_name: string; industry: string; description: string; business_model: BusinessModel; sales_channels: string[];
  target_audience: string | null; website_url: string | null; location: string | null; goals: string | null;
}

/** Returns null when the user has no profile yet (backend answers 404). */
export async function getProfile(): Promise<BusinessProfile | null> {
  try { return await api<BusinessProfile>("/business-profile"); }
  catch (e) { if (e instanceof ApiError && e.status === 404) return null; throw e; }
}
/** PUT creates the profile if missing, otherwise replaces it. Send the full form. */
export const saveProfile = (input: ProfileInput) =>
  api<BusinessProfile>("/business-profile", { method: "PUT", headers: { "Content-Type": "application/json" }, body: JSON.stringify(input) });