"""Scoring tests. Plain asserts, no libraries needed."""
from app.services.evidence import FixtureEvidenceSource, ProductEvidence
from app.services.scoring_service import (
    DEFAULT_WEIGHTS,
    action_type_for,
    build_supporting_evidence,
    calculate_score,
    rank_products,
    validate_weights,
)


def close(a, b, tol=0.06):
    return abs(a - b) <= tol


def full_product():
    return ProductEvidence(
        product_id=1, product_name="Full",
        engagement_rate=7.0, positive_share=0.72, feedback_count=14,
        enquiries=9, customer_requests=3, seasonality_score=80,
    )


def test_default_weights_add_up_to_one():
    assert close(sum(DEFAULT_WEIGHTS.values()), 1.0, 1e-9)


def test_complete_signals():
    r = calculate_score(full_product())
    # 0.35*70 + 0.30*72 + 0.20*60 + 0.15*80 = 70.1
    assert close(r.score, 70.1)
    assert r.interpretation == "high"
    assert r.missing_signals == []
    assert close(sum(r.weights_used.values()), 1.0, 1e-9)


def test_partial_signals_are_renormalised():
    p = ProductEvidence(product_id=3, product_name="Soap", engagement_rate=4.8,
                        enquiries=5, seasonality_score=40)
    r = calculate_score(p)
    assert r.missing_signals == ["customer_interest"]
    assert close(sum(r.weights_used.values()), 1.0, 1e-9)
    assert close(r.score, 39.7)
    assert any("customer interest" in c for c in r.caveats)


def test_missing_everything_gives_no_score():
    r = calculate_score(ProductEvidence(product_id=4, product_name="Mug"))
    assert r.score is None
    assert r.interpretation == "insufficient_evidence"
    assert len(r.missing_signals) == 4
    assert action_type_for(r) == "collect_more_data"


def test_zero_is_not_the_same_as_missing():
    zero = calculate_score(ProductEvidence(product_id=1, product_name="A", engagement_rate=0.0))
    none = calculate_score(ProductEvidence(product_id=2, product_name="B", engagement_rate=None))
    assert zero.score == 0.0          # real zero -> a score of 0
    assert none.score is None         # missing    -> no score at all


def test_zero_enquiries_counts_as_evidence_but_none_does_not():
    zero = calculate_score(ProductEvidence(product_id=1, product_name="A", enquiries=0, customer_requests=0))
    none = calculate_score(ProductEvidence(product_id=2, product_name="B"))
    assert zero.score == 0.0
    assert none.score is None


def test_same_input_same_output():
    a = calculate_score(full_product())
    b = calculate_score(full_product())
    assert a.score == b.score and a.weights_used == b.weights_used


def test_values_are_clamped_to_0_100():
    p = ProductEvidence(product_id=1, product_name="X", engagement_rate=55.0, positive_share=1.4)
    r = calculate_score(p)
    assert r.signal_scores["performance"] == 100.0
    assert r.signal_scores["customer_interest"] == 100.0
    assert r.score == 100.0


def test_single_signal_is_limited_evidence():
    r = calculate_score(ProductEvidence(product_id=1, product_name="X", engagement_rate=9.0))
    assert r.interpretation == "limited_evidence"
    assert action_type_for(r) == "collect_more_data"


def test_small_feedback_sample_warning():
    p = ProductEvidence(product_id=1, product_name="X", engagement_rate=5.0,
                        positive_share=0.9, feedback_count=3)
    r = calculate_score(p)
    assert any("only 3" in c for c in r.caveats)


def test_custom_weights_change_the_score():
    p = full_product()
    only_perf = {"performance": 1, "customer_interest": 0, "demand": 0, "context": 0}
    assert close(calculate_score(p, only_perf).score, 70.0)


def test_bad_weights_rejected():
    for bad in ({"performance": 1}, {"performance": -1, "customer_interest": 1, "demand": 1, "context": 1},
                {"performance": 0, "customer_interest": 0, "demand": 0, "context": 0}):
        try:
            validate_weights(bad)
        except ValueError:
            continue
        raise AssertionError(f"weights should have been rejected: {bad}")


def test_ranking_order_and_unscored_last():
    bundle = FixtureEvidenceSource().load(owner_id=1)
    ranked = rank_products(bundle.products)
    ids = [p.product_id for p, _ in ranked]
    assert ids == [1, 3, 2, 4]
    assert ranked[-1][1].score is None


def test_ranking_is_deterministic_on_ties():
    a = ProductEvidence(product_id=7, product_name="A", engagement_rate=5.0, positive_share=0.5)
    b = ProductEvidence(product_id=2, product_name="B", engagement_rate=5.0, positive_share=0.5)
    ids = [p.product_id for p, _ in rank_products([a, b])]
    assert ids == [2, 7]


def test_supporting_evidence_only_lists_available_facts():
    p = ProductEvidence(product_id=3, product_name="Soap", engagement_rate=4.8, enquiries=5)
    facts = build_supporting_evidence(p, calculate_score(p))
    text = " | ".join(facts)
    assert "Engagement rate: 4.8%" in text
    assert "Enquiries: 5, customer requests: not recorded" in text
    assert "Positive feedback" not in text
