// ILLUSTRATIVE DEMO DATA ONLY. Not real business data.
export const traffic = [
  { d: "Mon", v: 320 }, { d: "Tue", v: 410 }, { d: "Wed", v: 380 }, { d: "Thu", v: 520 },
  { d: "Fri", v: 610 }, { d: "Sat", v: 570 }, { d: "Sun", v: 690 },
];
export const sentiment = [
  { label: "Positive", pct: 68, color: "bg-emerald-400" },
  { label: "Neutral", pct: 22, color: "bg-slate-300" },
  { label: "Negative", pct: 10, color: "bg-rose-400" },
];
export const steps: [string, string][] = [
  ["Create an account", "Sign up with an email and password."],
  ["Set up the business profile", "Brand name, industry, business model, sales channels and optional goals."],
  ["Add products", "Product cards with categories and pricing."],
  ["Understand feedback and performance", "Sentiment, recurring themes, sales and traffic charts."],
  ["Generate AI recommendations", "Business data, feedback and performance converge into ranked, explained recommendations."],
  ["Review and take action", "Accept, edit or reject each recommendation."],
  ["Track results and improve", "Outcomes feed back into better future recommendations."],
];
export const actions = [
  { t: "Highlight your fastest-selling category in email", why: "Strongest demo traffic trend" },
  { t: "Address the most repeated complaint in listings", why: "Recurring negative theme" },
  { t: "Test a bundle offer for top products", why: "Cross-product interest signal" },
];
export const activity = ["Account created", "Business profile started", "Demo data loaded"];
export const inProgress: Record<string, string> = {
  "Business Profile": "View and edit your business portfolio.",
  Products: "Manage your product catalogue.",
  "Customer Insights": "Analyse customer feedback and themes.",
  "Marketing Analytics": "Track marketing performance.",
  "AI Recommendations": "Ranked, explainable marketing recommendations.",
  "Recommendation History": "Review past recommendations and outcomes.",
  Settings: "Account and workspace preferences.",
};
