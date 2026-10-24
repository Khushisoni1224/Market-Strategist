"""Prompt builder, mock provider and provider factory. Plain asserts."""
import json
from types import SimpleNamespace

from app.services.evidence import FixtureEvidenceSource
from app.services.llm_provider import MockProvider, OpenAICompatibleProvider, get_provider
from app.services.prompt_builder import build_prompt
from app.services.scoring_service import rank_products


def make_prompt():
    bundle = FixtureEvidenceSource().load(1)
    ranked = rank_products(bundle.products)
    scored = [pair for pair in ranked if pair[1].score is not None]
    return build_prompt(scored, bundle.business_category, bundle.data_warnings)


def test_prompt_contains_only_structured_evidence():
    prompt = make_prompt()
    assert "Evidence (JSON)" in prompt.user
    assert "Never invent" in prompt.system
    ids = [p["product_id"] for p in prompt.evidence["products"]]
    assert ids == [1, 3, 2]          # unscored product 4 is not sent to the AI
    first = prompt.evidence["products"][0]
    assert first["priority_rank"] == 1
    assert first["signals"]["positive_feedback_percent"] == 72.0


def test_missing_values_stay_null_in_the_prompt():
    prompt = make_prompt()
    soap = [p for p in prompt.evidence["products"] if p["product_id"] == 3][0]
    assert soap["signals"]["positive_feedback_percent"] is None
    assert soap["signals"]["customer_requests"] is None
    assert "customer_interest" in soap["missing_signals"]


def test_mock_provider_returns_valid_json_for_every_product():
    prompt = make_prompt()
    data = json.loads(MockProvider().generate(prompt))
    assert [r["product_id"] for r in data["recommendations"]] == [1, 3, 2]
    for rec in data["recommendations"]:
        assert rec["title"] and rec["reasoning_summary"]


def test_factory_without_key_falls_back_to_mock():
    cfg = SimpleNamespace(LLM_PROVIDER="openai", LLM_API_KEY="", LLM_MODEL="m",
                          LLM_BASE_URL="http://x", LLM_TIMEOUT_SECONDS=5)
    assert isinstance(get_provider(cfg), MockProvider)


def test_factory_default_is_mock():
    cfg = SimpleNamespace(LLM_PROVIDER="mock", LLM_API_KEY="", LLM_MODEL="m",
                          LLM_BASE_URL="http://x", LLM_TIMEOUT_SECONDS=5)
    assert isinstance(get_provider(cfg), MockProvider)


def test_factory_with_key_builds_real_provider():
    cfg = SimpleNamespace(LLM_PROVIDER="openai", LLM_API_KEY="k", LLM_MODEL="m",
                          LLM_BASE_URL="http://x/", LLM_TIMEOUT_SECONDS=5)
    provider = get_provider(cfg)
    assert isinstance(provider, OpenAICompatibleProvider)
    assert provider.base_url == "http://x"
