"""Tests for customer segmentation module."""

from src.ml.segmentation import run_segmentation


def test_run_segmentation(sample_customer_features):
    segmented, insights = run_segmentation(sample_customer_features, n_clusters=3)
    assert "cluster" in segmented.columns
    assert "cluster_label" in segmented.columns
    assert len(segmented) == len(sample_customer_features)
    assert "cluster_summary" in insights
    assert "business_recommendations" in insights
    assert segmented["cluster"].nunique() >= 3
