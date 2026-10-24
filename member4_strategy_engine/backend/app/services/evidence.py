"""Evidence that the strategy engine consumes (pure Python, no libraries).

HOW THIS CONNECTS TO THE TEAM
  * Products come from Member 2.
  * Feedback insights + performance summaries come from Member 3.
  * Until they are ready, FixtureEvidenceSource gives realistic demo data.

RULE: None means "missing" and 0 means "really zero". Never mix them up.
"""
from dataclasses import dataclass, field
from typing import Protocol


@dataclass
class ProductEvidence:
    product_id: int
    product_name: str
    category: str | None = None
    engagement_rate: float | None = None      # percent, e.g. 6.2 means 6.2 %
    positive_share: float | None = None       # 0..1 share of positive feedback
    feedback_count: int | None = None         # how many feedback entries the share is based on
    enquiries: int | None = None
    customer_requests: int | None = None
    seasonality_score: float | None = None    # 0..100 from seller-provided / documented context
    top_themes: list[str] = field(default_factory=list)


@dataclass
class EvidenceBundle:
    products: list[ProductEvidence]
    data_warnings: list[str] = field(default_factory=list)
    business_category: str | None = None


class EvidenceSource(Protocol):
    def load(self, owner_id: int) -> EvidenceBundle:  # pragma: no cover - interface
        ...


class FixtureEvidenceSource:
    """Demo data used until Member 2 and Member 3 endpoints are integrated."""

    def load(self, owner_id: int) -> EvidenceBundle:
        products = [
            ProductEvidence(
                product_id=1, product_name="Handmade Candle Set", category="Home decor",
                engagement_rate=7.0, positive_share=0.72, feedback_count=14,
                enquiries=9, customer_requests=3, seasonality_score=80,
                top_themes=["scent", "gift packaging"],
            ),
            ProductEvidence(
                product_id=2, product_name="Cotton Tote Bag", category="Accessories",
                engagement_rate=3.1, positive_share=0.55, feedback_count=22,
                enquiries=2, customer_requests=0, seasonality_score=None,
                top_themes=["stitching quality"],
            ),
            ProductEvidence(
                product_id=3, product_name="Herbal Soap", category="Personal care",
                engagement_rate=4.8, positive_share=None, feedback_count=None,
                enquiries=5, customer_requests=None, seasonality_score=40,
                top_themes=[],
            ),
            ProductEvidence(product_id=4, product_name="Ceramic Mug", category="Kitchen"),
        ]
        return EvidenceBundle(
            products=products,
            data_warnings=["Demo data is being used (fixture), not real seller data."],
            business_category="Handmade gifts",
        )
