"""Checks the AI's answer BEFORE anything is saved. Bad answers are rejected.

Checks:
  1. valid JSON (markdown code fences are tolerated)
  2. matches the Pydantic schema
  3. only product ids that exist in our evidence, no duplicates
  4. no invented numbers in the reasoning / evidence text
  5. no promises such as "guaranteed" sales
"""
import json
import re

from pydantic import ValidationError

from app.schemas.strategy import LLMOutput


class ResponseValidationError(Exception):
    pass


FORBIDDEN_PHRASES = ("guaranteed", "will double", "100% success", "will definitely increase")
_NUMBER_RE = re.compile(r"\d+(?:\.\d+)?")
_FENCE_RE = re.compile(r"^```(?:json)?\s*|\s*```$", re.IGNORECASE)


def parse_llm_json(raw: str) -> dict:
    if not isinstance(raw, str) or not raw.strip():
        raise ResponseValidationError("Model response was empty.")
    cleaned = _FENCE_RE.sub("", raw.strip()).strip()
    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError as exc:
        raise ResponseValidationError("Model response was not valid JSON.") from exc
    if not isinstance(data, dict):
        raise ResponseValidationError("Model response must be a JSON object.")
    return data


def _collect_numbers(value, bucket: set) -> None:
    if isinstance(value, bool):
        return
    if isinstance(value, (int, float)):
        bucket.add(float(value))
    elif isinstance(value, str):
        bucket.update(float(m) for m in _NUMBER_RE.findall(value))
    elif isinstance(value, dict):
        for item in value.values():
            _collect_numbers(item, bucket)
    elif isinstance(value, (list, tuple)):
        for item in value:
            _collect_numbers(item, bucket)


def _is_supported(number: float, allowed: set) -> bool:
    if number.is_integer() and number <= 10:      # tiny counts like "#1" or "3 signals"
        return True
    return any(
        abs(number - a) <= 0.051 or (number.is_integer() and number == round(a))
        for a in allowed
    )


def validate_llm_response(raw: str, evidence: dict) -> LLMOutput:
    data = parse_llm_json(raw)
    try:
        output = LLMOutput.model_validate(data)
    except ValidationError as exc:
        raise ResponseValidationError("Model response did not match the required schema.") from exc

    valid_ids = {p["product_id"] for p in evidence["products"]}
    allowed: set = {100.0}                          # "out of 100"
    _collect_numbers(evidence, allowed)

    seen: set = set()
    for rec in output.recommendations:
        if rec.product_id not in valid_ids:
            raise ResponseValidationError("Model referred to a product that is not in the evidence.")
        if rec.product_id in seen:
            raise ResponseValidationError("Model returned the same product twice.")
        seen.add(rec.product_id)

        prose = " ".join([rec.title, rec.reasoning_summary, rec.suggested_content or ""]).lower()
        for phrase in FORBIDDEN_PHRASES:
            if phrase in prose:
                raise ResponseValidationError("Model made a promise about results.")

        for text in [rec.reasoning_summary, *rec.evidence_used]:
            for match in _NUMBER_RE.findall(text):
                if not _is_supported(float(match), allowed):
                    raise ResponseValidationError(f"Model used a number not found in the evidence: {match}")
    return output
