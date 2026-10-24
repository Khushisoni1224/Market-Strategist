"""Dependencies used by the Member 4 endpoints.

TEMPORARY PARTS (replace when Member 2 / Member 3 finish):
  * get_current_user_id  -> use Member 2's real "current user" dependency.
  * get_evidence_source  -> return the real Member 3 based source (see README).
get_llm_provider is YOURS and stays.
"""
from typing import Annotated

from fastapi import Header, HTTPException

from app.core.config import settings
from app.services.evidence import EvidenceSource, FixtureEvidenceSource
from app.services.llm_provider import LLMProvider, get_provider


def get_current_user_id(x_user_id: Annotated[int | None, Header()] = None) -> int:
    """TEMPORARY fake login: send the header  X-User-Id: 1  with each request."""
    if x_user_id is None:
        raise HTTPException(status_code=401, detail="Not authenticated.")
    return x_user_id


def get_evidence_source() -> EvidenceSource:
    return FixtureEvidenceSource()


def get_llm_provider() -> LLMProvider:
    return get_provider(settings)
