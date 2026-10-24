import json

import pytest

from app.services.evidence import FixtureEvidenceSource
from app.services.llm_provider import MockProvider
from app.services.prompt_builder import build_prompt
from app.services.response_validator import ResponseValidationError, validate_llm_response
from app.services.scoring_service import rank_products


@pytest.fixture()
def prompt():
    bundle = FixtureEvidenceSource().load(1)
    ranked = rank_products(bundle.products)
    scored = [pair for pair in ranked if pair[1].score is not None]
    return build_prompt(scored, bundle.business_category, bundle.data_warnings)


def good_rec(product_id=1, reasoning="Handmade Candle Set has a score of 70.1 out of 100.", **extra):
    rec = {"product_id": product_id, "title": "Promote it", "reasoning_summary": reasoning,
           "suggested_content": "A short reel.", "evidence_used": ["Engagement rate 7.0%"], "caveats": []}
    rec.update(extra)
    return rec


def wrap(*recs):
    return json.dumps({"recommendations": list(recs)})


def test_mock_provider_output_passes_validation(prompt):
    out = validate_llm_response(MockProvider().generate(prompt), prompt.evidence)
    assert [r.product_id for r in out.recommendations] == [1, 3, 2]


def test_markdown_code_fence_is_tolerated(prompt):
    raw = "```json\n" + wrap(good_rec()) + "\n```"
    assert validate_llm_response(raw, prompt.evidence).recommendations[0].product_id == 1


@pytest.mark.parametrize("raw", ["", "not json at all", "[]", '{"recommendations": []}', '{"foo": 1}'])
def test_malformed_or_wrong_shape_is_rejected(prompt, raw):
    with pytest.raises(ResponseValidationError):
        validate_llm_response(raw, prompt.evidence)


def test_unknown_product_is_rejected(prompt):
    with pytest.raises(ResponseValidationError):
        validate_llm_response(wrap(good_rec(product_id=999)), prompt.evidence)


def test_duplicate_product_is_rejected(prompt):
    with pytest.raises(ResponseValidationError):
        validate_llm_response(wrap(good_rec(), good_rec()), prompt.evidence)


def test_invented_number_is_rejected(prompt):
    bad = good_rec(reasoning="Sales jumped by 450% last month for this product.")
    with pytest.raises(ResponseValidationError):
        validate_llm_response(wrap(bad), prompt.evidence)


def test_numbers_that_exist_in_evidence_are_accepted(prompt):
    ok = good_rec(reasoning="Engagement is 7.0% and 72.0% of the 14 feedback entries are positive.")
    assert validate_llm_response(wrap(ok), prompt.evidence)


def test_promises_are_rejected(prompt):
    bad = good_rec(reasoning="This is guaranteed to work.")
    with pytest.raises(ResponseValidationError):
        validate_llm_response(wrap(bad), prompt.evidence)
