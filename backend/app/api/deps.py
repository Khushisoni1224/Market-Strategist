"""Strategy engine dependencies using the main API's JWT authentication."""
from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.dependencies import CurrentUser
from app.db.session import get_db
from app.services.evidence import DatabaseEvidenceSource, EvidenceSource
from app.services.llm_provider import LLMProvider, get_provider


def get_current_user_id(current_user: CurrentUser) -> int:
    """Return the authenticated seller's ID; never trust a client-supplied ID."""
    return current_user.id


def get_evidence_source(db: Session = Depends(get_db)) -> EvidenceSource:
    return DatabaseEvidenceSource(db)


def get_llm_provider() -> LLMProvider:
    return get_provider(settings)
