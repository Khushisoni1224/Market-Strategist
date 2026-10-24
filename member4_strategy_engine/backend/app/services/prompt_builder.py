"""Builds the AI prompt from a compact, structured evidence package.

Only small structured facts go to the model. NEVER raw uploaded files or raw feedback.
"""
import json
from dataclasses import dataclass

SYSTEM_PROMPT = """You are a marketing assistant for a small online seller.
Rules:
1. Use ONLY the numbers and facts in the evidence JSON. Never invent metrics, percentages or sales figures.
2. Do not promise or predict sales, revenue or growth.
3. If evidence is missing, say so plainly.
4. Reply with JSON only (no markdown, no commentary) in exactly this shape:
{"recommendations":[{"product_id":<integer from the evidence>,"title":"<short action title>","reasoning_summary":"<2-3 sentences using only evidence numbers>","suggested_content":"<one short-form content idea, text only>","evidence_used":["<fact copied from the evidence>"],"caveats":["<limitation>"]}]}
5. Write exactly one recommendation per product, in the same order as the evidence."""


@dataclass
class LLMPrompt:
    system: str
    user: str
    evidence: dict      # same data as inside `user`; kept for the mock provider + validator


def _percent(share: float | None) -> float | None:
    return None if share is None else round(share * 100, 1)


def build_evidence_package(scored: list, business_category: str | None, data_warnings: list) -> dict:
    products = []
    for rank, (p, r) in enumerate(scored, start=1):
        products.append({
            "product_id": p.product_id,
            "product_name": p.product_name,
            "category": p.category,
            "priority_rank": rank,
            "opportunity_score": r.score,
            "score_interpretation": r.interpretation,
            "signals": {
                "engagement_rate_percent": p.engagement_rate,
                "positive_feedback_percent": _percent(p.positive_share),
                "feedback_count": p.feedback_count,
                "enquiries": p.enquiries,
                "customer_requests": p.customer_requests,
                "seasonality_score": p.seasonality_score,
            },
            "top_themes": list(p.top_themes),
            "missing_signals": list(r.missing_signals),
        })
    return {
        "business_category": business_category,
        "data_warnings": list(data_warnings),
        "products": products,
    }


def build_prompt(scored: list, business_category: str | None, data_warnings: list) -> LLMPrompt:
    evidence = build_evidence_package(scored, business_category, data_warnings)
    user = "Evidence (JSON):\n" + json.dumps(evidence, indent=2) + "\n\nWrite the recommendations now."
    return LLMPrompt(system=SYSTEM_PROMPT, user=user, evidence=evidence)
