"""LLM adapter. The rest of the app only ever calls provider.generate(prompt).

  * MockProvider  -> works offline, no API key, used for development and tests.
  * OpenAICompatibleProvider -> real model (any OpenAI-style /chat/completions API).

The API key lives ONLY in backend environment variables.
"""
import json
import logging
import urllib.error
import urllib.request
from abc import ABC, abstractmethod

from app.services.prompt_builder import LLMPrompt

logger = logging.getLogger(__name__)


class LLMProviderError(Exception):
    """Timeouts, network errors, bad HTTP responses..."""


class LLMProvider(ABC):
    name = "base"

    @abstractmethod
    def generate(self, prompt: LLMPrompt) -> str:
        """Return the model's raw text answer (expected to be JSON)."""


class MockProvider(LLMProvider):
    name = "mock"

    def generate(self, prompt: LLMPrompt) -> str:
        recommendations = []
        for item in prompt.evidence["products"]:
            name = item["product_name"]
            signals = item["signals"]
            interp = item["score_interpretation"].replace("_", " ")

            reasoning = f"{name} has an opportunity score of {item['opportunity_score']} out of 100 ({interp})."
            used = [f"Opportunity score {item['opportunity_score']}"]
            if signals["engagement_rate_percent"] is not None:
                reasoning += f" Its engagement rate is {signals['engagement_rate_percent']}%."
                used.append(f"Engagement rate {signals['engagement_rate_percent']}%")
            if signals["positive_feedback_percent"] is not None:
                reasoning += f" About {signals['positive_feedback_percent']}% of its feedback is positive."
                used.append(f"Positive feedback {signals['positive_feedback_percent']}%")
            if item["missing_signals"]:
                missing = ", ".join(m.replace("_", " ") for m in item["missing_signals"])
                reasoning += f" No data was available for: {missing}."

            if item["score_interpretation"] in ("high", "medium"):
                title = f"Promote {name} first" if item["priority_rank"] == 1 else f"Promote {name}"
            else:
                title = f"Build up evidence for {name} before promoting it"

            themes = item["top_themes"]
            theme_text = f" Highlight what customers mention: {', '.join(themes)}." if themes else ""
            recommendations.append({
                "product_id": item["product_id"],
                "title": title,
                "reasoning_summary": reasoning,
                "suggested_content": (
                    f"Short video or reel showing {name} in everyday use, with a clear call to action."
                    + theme_text
                ),
                "evidence_used": used,
                "caveats": ["Mock provider output: sample wording, not a real AI answer."],
            })
        return json.dumps({"recommendations": recommendations})


class OpenAICompatibleProvider(LLMProvider):
    name = "openai"

    def __init__(self, api_key: str, model: str, base_url: str, timeout: float):
        self.api_key = api_key
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def generate(self, prompt: LLMPrompt) -> str:
        body = json.dumps({
            "model": self.model,
            "messages": [
                {"role": "system", "content": prompt.system},
                {"role": "user", "content": prompt.user},
            ],
            "temperature": 0.2,
            "response_format": {"type": "json_object"},
        }).encode("utf-8")
        request = urllib.request.Request(
            f"{self.base_url}/chat/completions",
            data=body,
            headers={"Content-Type": "application/json", "Authorization": f"Bearer {self.api_key}"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                payload = json.loads(response.read().decode("utf-8"))
            return payload["choices"][0]["message"]["content"]
        except (urllib.error.URLError, TimeoutError, OSError, KeyError, IndexError, ValueError) as exc:
            # Only the error TYPE is reported: never the key, never the raw data.
            raise LLMProviderError(f"LLM request failed ({type(exc).__name__})") from exc


def get_provider(cfg) -> LLMProvider:
    """Pick the provider from settings. No key -> safe fallback to the mock."""
    if cfg.LLM_PROVIDER == "openai":
        if cfg.LLM_API_KEY:
            return OpenAICompatibleProvider(
                cfg.LLM_API_KEY, cfg.LLM_MODEL, cfg.LLM_BASE_URL, cfg.LLM_TIMEOUT_SECONDS
            )
        logger.warning("LLM_PROVIDER=openai but LLM_API_KEY is empty; using the mock provider.")
    return MockProvider()
