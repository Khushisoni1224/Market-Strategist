"""Deterministic promotion-opportunity scoring. NO AI here, only maths.

Same input -> same output, always.

Weights (initial DESIGN ASSUMPTIONS, not validated predictions):
    performance 35 %, customer interest 30 %, demand 20 %, context/seasonality 15 %

If a signal is missing, it is dropped and the remaining weights are
re-scaled to add up to 1 (renormalisation). Missing is NOT treated as zero.
"""
import json
from dataclasses import dataclass, field

from app.core.config import settings
from app.services.evidence import ProductEvidence

SIGNAL_NAMES = ("performance", "customer_interest", "demand", "context")
SIGNAL_LABELS = {
    "performance": "performance",
    "customer_interest": "customer interest",
    "demand": "demand",
    "context": "seasonality/context",
}
DEFAULT_WEIGHTS = {"performance": 0.35, "customer_interest": 0.30, "demand": 0.20, "context": 0.15}

# Tunable normalisation constants (documented assumptions)
ENGAGEMENT_RATE_FULL_MARKS = 10.0   # an engagement rate of 10 % or more = 100 points
DEMAND_FULL_MARKS = 20.0            # 20 or more enquiries+requests = 100 points
SMALL_SAMPLE_THRESHOLD = 10         # fewer feedback entries than this -> warn
HIGH_THRESHOLD = 70.0
MEDIUM_THRESHOLD = 40.0


@dataclass
class ScoreResult:
    score: float | None
    signal_scores: dict
    weights_used: dict
    missing_signals: list
    interpretation: str   # high | medium | low | limited_evidence | insufficient_evidence
    caveats: list = field(default_factory=list)


def _clamp(value: float, low: float = 0.0, high: float = 100.0) -> float:
    return max(low, min(high, value))


# ---------------------------------------------------------------- weights
def validate_weights(weights: dict) -> None:
    if set(weights) != set(SIGNAL_NAMES):
        raise ValueError(f"Weights must have exactly these keys: {list(SIGNAL_NAMES)}")
    for name, value in weights.items():
        if isinstance(value, bool) or not isinstance(value, (int, float)) or value < 0:
            raise ValueError(f"Weight '{name}' must be a number >= 0")
    if sum(weights.values()) <= 0:
        raise ValueError("At least one weight must be greater than 0")


def get_scoring_weights() -> dict:
    raw = settings.SCORING_WEIGHTS_JSON
    if not raw:
        return dict(DEFAULT_WEIGHTS)
    try:
        weights = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError("SCORING_WEIGHTS_JSON is not valid JSON") from exc
    validate_weights(weights)
    return {name: float(weights[name]) for name in SIGNAL_NAMES}


# ---------------------------------------------------------------- signals (each 0..100 or None)
def performance_signal(p: ProductEvidence) -> float | None:
    if p.engagement_rate is None:
        return None
    return _clamp(p.engagement_rate / ENGAGEMENT_RATE_FULL_MARKS * 100)


def customer_interest_signal(p: ProductEvidence) -> float | None:
    if p.positive_share is None:
        return None
    return _clamp(p.positive_share * 100)


def demand_signal(p: ProductEvidence) -> float | None:
    parts = [v for v in (p.enquiries, p.customer_requests) if v is not None]
    if not parts:
        return None
    return _clamp(sum(parts) / DEMAND_FULL_MARKS * 100)


def context_signal(p: ProductEvidence) -> float | None:
    if p.seasonality_score is None:
        return None
    return _clamp(p.seasonality_score)


# ---------------------------------------------------------------- main calculation
def calculate_score(product: ProductEvidence, weights: dict | None = None) -> ScoreResult:
    weights = dict(DEFAULT_WEIGHTS) if weights is None else weights
    validate_weights(weights)

    signal_scores = {
        "performance": performance_signal(product),
        "customer_interest": customer_interest_signal(product),
        "demand": demand_signal(product),
        "context": context_signal(product),
    }
    available = {k: v for k, v in signal_scores.items() if v is not None}
    missing = [k for k in SIGNAL_NAMES if signal_scores[k] is None]

    total_weight = sum(weights[k] for k in available)
    if not available or total_weight <= 0:
        return ScoreResult(
            score=None, signal_scores=signal_scores, weights_used={},
            missing_signals=missing, interpretation="insufficient_evidence",
            caveats=["No usable evidence is available for this product yet."],
        )

    used = {k: weights[k] / total_weight for k in available}      # renormalised
    score = round(sum(used[k] * available[k] for k in available), 1)

    caveats = [
        f"No {SIGNAL_LABELS[k]} data available; the score uses the remaining signals."
        for k in missing
    ]
    if product.feedback_count is not None and product.feedback_count < SMALL_SAMPLE_THRESHOLD:
        caveats.append(f"Customer feedback is based on only {product.feedback_count} entries.")

    if len(available) < 2:
        interpretation = "limited_evidence"
        caveats.append("Only one type of evidence is available, so treat this score as a rough guide.")
    elif score >= HIGH_THRESHOLD:
        interpretation = "high"
    elif score >= MEDIUM_THRESHOLD:
        interpretation = "medium"
    else:
        interpretation = "low"

    return ScoreResult(score, signal_scores, used, missing, interpretation, caveats)


def rank_products(products: list, weights: dict | None = None) -> list:
    """Return [(product, ScoreResult)] best first. Unscorable products go last."""
    weights = get_scoring_weights() if weights is None else weights
    pairs = [(p, calculate_score(p, weights)) for p in products]
    scored = sorted(
        [x for x in pairs if x[1].score is not None],
        key=lambda x: (-x[1].score, x[0].product_id),       # deterministic tie-break
    )
    unscored = sorted([x for x in pairs if x[1].score is None], key=lambda x: x[0].product_id)
    return scored + unscored


def action_type_for(result: ScoreResult) -> str:
    """The ACTION is decided by rules, never by the AI."""
    if result.score is None or result.interpretation == "limited_evidence":
        return "collect_more_data"
    if result.interpretation == "low":
        return "improve_before_promoting"
    return "promote_product"


def build_supporting_evidence(p: ProductEvidence, result: ScoreResult) -> list:
    """Observed FACTS only (taken straight from the data, not written by AI)."""
    facts = []
    if p.engagement_rate is not None:
        facts.append(f"Engagement rate: {p.engagement_rate}%")
    if p.positive_share is not None:
        suffix = f" (based on {p.feedback_count} feedback entries)" if p.feedback_count is not None else ""
        facts.append(f"Positive feedback: {round(p.positive_share * 100, 1)}%{suffix}")
    if p.enquiries is not None or p.customer_requests is not None:
        enq = "not recorded" if p.enquiries is None else p.enquiries
        req = "not recorded" if p.customer_requests is None else p.customer_requests
        facts.append(f"Enquiries: {enq}, customer requests: {req}")
    if p.seasonality_score is not None:
        facts.append(f"Seasonality/context score: {p.seasonality_score}/100")
    if p.top_themes:
        facts.append("Top feedback themes: " + ", ".join(p.top_themes))
    if result.score is not None:
        facts.append(f"Opportunity score: {result.score}/100 ({result.interpretation.replace('_', ' ')})")
    return facts
