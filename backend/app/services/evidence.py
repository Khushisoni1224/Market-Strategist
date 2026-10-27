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


class DatabaseEvidenceSource:
    """Build product evidence from this seller's saved records.

    The current schema does not associate marketing posts, enquiries, requests,
    or seasonality with individual products, so those signals remain missing
    rather than being guessed or copied across every product.
    """
    def __init__(self, db):
        self.db = db

    def load(self, owner_id: int) -> EvidenceBundle:
        from collections import Counter
        from sqlalchemy import select
        from app.models.business_profile import BusinessProfile
        from app.models.customer_feedback import CustomerFeedback
        from app.models.product import Product

        products = list(self.db.scalars(
            select(Product).where(Product.user_id == owner_id).order_by(Product.id.asc())
        ).all())
        if not products:
            return EvidenceBundle(products=[], data_warnings=[
                "No products found. Add products before generating a strategy."
            ])

        feedback_rows = list(self.db.scalars(
            select(CustomerFeedback).where(
                CustomerFeedback.user_id == owner_id,
                CustomerFeedback.product_id.is_not(None),
            )
        ).all())
        feedback_by_product = {}
        for row in feedback_rows:
            feedback_by_product.setdefault(row.product_id, []).append(row)

        profile = self.db.scalar(
            select(BusinessProfile).where(BusinessProfile.user_id == owner_id)
        )
        evidence_products = []
        for product in products:
            rows = feedback_by_product.get(product.id, [])
            positive_share = (
                sum(1 for row in rows if row.sentiment == "Positive") / len(rows)
                if rows else None
            )
            theme_counts = Counter()
            for row in rows:
                theme_counts.update(set(row.themes or []))
            evidence_products.append(ProductEvidence(
                product_id=product.id,
                product_name=product.name,
                category=product.category,
                positive_share=positive_share,
                feedback_count=len(rows) if rows else None,
                top_themes=[theme for theme, _ in theme_counts.most_common(5)],
            ))

        warnings = [
            "Product-level engagement, enquiries, customer requests, and seasonality are not stored in the current data model; these signals are left missing.",
            "Customer feedback is used only when it is explicitly linked to a product.",
        ]
        if not feedback_rows:
            warnings.append("No product-linked customer feedback is available yet.")
        return EvidenceBundle(
            products=evidence_products,
            data_warnings=warnings,
            business_category=profile.industry if profile else None,
        )
