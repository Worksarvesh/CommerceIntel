"""Tests for recommendation engine."""

from src.ml.recommendation import RecommendationEngine


def test_recommendation_engine_popular(sample_transactions):
    engine = RecommendationEngine(sample_transactions)
    recs = engine.popular_recommendations(top_n=5)
    assert len(recs) <= 5
    assert all("stock_code" in rec for rec in recs)
    assert all("score" in rec for rec in recs)


def test_collaborative_recommendations(sample_transactions):
    engine = RecommendationEngine(sample_transactions)
    customer_id = sample_transactions["customer_id"].iloc[0]
    recs = engine.collaborative_recommendations(customer_id, top_n=5)
    assert isinstance(recs, list)


def test_content_based_recommendations(sample_transactions):
    engine = RecommendationEngine(sample_transactions)
    product_id = sample_transactions["stock_code"].iloc[0]
    recs = engine.content_based_recommendations(product_id, top_n=5)
    assert isinstance(recs, list)
    if recs:
        assert recs[0]["stock_code"] != product_id


def test_hybrid_recommendations(sample_transactions):
    engine = RecommendationEngine(sample_transactions)
    customer_id = sample_transactions["customer_id"].iloc[0]
    recs = engine.hybrid_recommendations(customer_id, top_n=5)
    assert isinstance(recs, list)
