"""Pipeline orchestration (the "chef"):

  load evidence -> score (maths) -> build prompt -> call AI -> validate ->
  save run + recommendations -> return

If the AI fails or answers badly we DO NOT crash: we save rule-based
explanations instead and tell the seller (used_fallback + a warning).
"""
import logging

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.recommendation import Recommendation
from app.models.strategy import StrategyRun
from app.services.errors import NoDataError, PersistenceError
from app.services.evidence import EvidenceSource
from app.services.llm_provider import LLMProvider, LLMProviderError
from app.services.prompt_builder import build_prompt
from app.services.response_validator import ResponseValidationError, validate_llm_response
from app.services.scoring_service import (
    SIGNAL_NAMES,
    action_type_for,
    build_supporting_evidence,
    get_scoring_weights,
    rank_products,
)

logger = logging.getLogger(__name__)

STANDARD_CAVEAT = "Opportunity scores use initial weights that are design assumptions, not validated predictions."
FALLBACK_WARNING = "AI-written suggestions were unavailable, so rule-based explanations are shown instead."
NO_EVIDENCE_WARNING = "None of your products has enough data to be scored yet."

_FALLBACK_TITLES = {
    "promote_product": "Promote {name}",
    "improve_before_promoting": "Improve {name} before promoting it",
    "collect_more_data": "Collect more data about {name}",
}


def _dedupe(items) -> list:
    seen, out = set(), []
    for item in items:
        if item and item not in seen:
            seen.add(item)
            out.append(item)
    return out


def _fallback_text(product, priority, result, action_type) -> dict:
    interp = result.interpretation.replace("_", " ")
    return {
        "title": _FALLBACK_TITLES[action_type].format(name=product.product_name),
        "reasoning": (
            f"{product.product_name} ranks #{priority} with an opportunity score of {result.score} out of 100 "
            f"({interp}). This ranking comes from the measured evidence listed below."
        ),
        "suggested_content": (
            f"Consider a short post or video featuring {product.product_name}; "
            "review the evidence below before you decide."
        ),
    }


def generate_strategy(
    db: Session,
    owner_id: int,
    source: EvidenceSource,
    provider: LLMProvider,
    max_recommendations: int | None = None,
) -> StrategyRun:
    limit = max_recommendations or settings.MAX_RECOMMENDATIONS

    # 1) evidence
    bundle = source.load(owner_id)
    if not bundle.products:
        raise NoDataError("Add at least one product before generating a strategy.")
    warnings = list(bundle.data_warnings)

    # 2) deterministic scoring
    weights = get_scoring_weights()
    ranked = rank_products(bundle.products, weights)
    scored = [pair for pair in ranked if pair[1].score is not None][:limit]
    unscored = [pair for pair in ranked if pair[1].score is None]

    # 3) AI wording (optional; failures are handled)
    llm_by_product: dict = {}
    used_fallback = False
    if scored:
        prompt = build_prompt(scored, bundle.business_category, warnings)
        try:
            raw = provider.generate(prompt)
            output = validate_llm_response(raw, prompt.evidence)
            llm_by_product = {rec.product_id: rec for rec in output.recommendations}
        except (LLMProviderError, ResponseValidationError) as exc:
            logger.warning("AI step failed (%s); using rule-based text.", type(exc).__name__)
            used_fallback = True
    else:
        warnings.append(NO_EVIDENCE_WARNING)

    # 4) assemble rows (facts + scores from code, wording from AI or fallback)
    rows: list = []
    for priority, (product, result) in enumerate(scored, start=1):
        action_type = action_type_for(result)
        llm = llm_by_product.get(product.product_id)
        fallback = _fallback_text(product, priority, result, action_type)
        if llm is None:
            used_fallback = True
        rows.append({
            "target_product_id": product.product_id,
            "title": llm.title if llm else fallback["title"],
            "action_type": action_type,
            "priority": priority,
            "score": result.score,
            "score_interpretation": result.interpretation,
            "reasoning_summary": llm.reasoning_summary if llm else fallback["reasoning"],
            "supporting_evidence": build_supporting_evidence(product, result),
            "suggested_content": (llm.suggested_content if llm else fallback["suggested_content"]),
            "data_gaps": list(result.missing_signals),
            "caveats": _dedupe(result.caveats + (llm.caveats if llm else []) + [STANDARD_CAVEAT]),
        })

    if unscored:
        names = [p.product_name for p, _ in unscored]
        rows.append({
            "target_product_id": None,
            "title": f"Add data for {len(names)} product(s) before promoting them",
            "action_type": "collect_more_data",
            "priority": len(rows) + 1,
            "score": None,
            "score_interpretation": "insufficient_evidence",
            "reasoning_summary": (
                "No usable performance, feedback, demand or seasonality data was found for: "
                + ", ".join(names) + ". Import data for these products so they can be scored."
            ),
            "supporting_evidence": [f"{name}: no usable evidence yet" for name in names],
            "suggested_content": None,
            "data_gaps": list(SIGNAL_NAMES),
            "caveats": [STANDARD_CAVEAT],
        })

    if used_fallback:
        warnings.append(FALLBACK_WARNING)

    # 5) save (one transaction)
    try:
        run = StrategyRun(
            owner_id=owner_id,
            llm_provider=provider.name,
            used_fallback=used_fallback,
            data_warnings=warnings,
            weights_used=weights,
        )
        db.add(run)
        db.flush()
        for row in rows:
            run.recommendations.append(Recommendation(owner_id=owner_id, **row))
        db.commit()
        db.refresh(run)
        return run
    except SQLAlchemyError as exc:
        db.rollback()
        logger.error("Could not save strategy run (%s)", type(exc).__name__)
        raise PersistenceError("Could not save the strategy run. Please try again.") from exc
