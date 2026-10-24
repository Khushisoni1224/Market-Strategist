import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import app.models  # noqa: F401
from app.api.deps import get_evidence_source, get_llm_provider
from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.services.evidence import FixtureEvidenceSource
from app.services.llm_provider import LLMProvider, LLMProviderError, MockProvider

USER_1 = {"X-User-Id": "1"}
USER_2 = {"X-User-Id": "2"}


class FailingProvider(LLMProvider):
    name = "failing"

    def generate(self, prompt):
        raise LLMProviderError("simulated timeout")


class FixedProvider(LLMProvider):
    """Returns whatever text we give it (used to simulate bad AI answers)."""
    name = "fixed"

    def __init__(self, text):
        self.text = text

    def generate(self, prompt):
        return self.text


@pytest.fixture()
def make_client():
    """Factory so a test can choose which provider the app should use."""
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    TestingSession = sessionmaker(bind=engine, autoflush=False, autocommit=False)

    def override_get_db():
        db = TestingSession()
        try:
            yield db
        finally:
            db.close()

    def _make(provider=None):
        app.dependency_overrides[get_db] = override_get_db
        app.dependency_overrides[get_evidence_source] = lambda: FixtureEvidenceSource()
        app.dependency_overrides[get_llm_provider] = lambda: provider or MockProvider()
        return TestClient(app)    # no "with": we do not run the dev startup hook

    yield _make
    app.dependency_overrides.clear()


@pytest.fixture()
def client(make_client):
    return make_client()
