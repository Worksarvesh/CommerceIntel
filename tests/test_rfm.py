"""Tests for RFM analysis module."""

import pandas as pd

from src.analysis.rfm import calculate_rfm, _assign_segment


def test_assign_segment_champions():
    assert _assign_segment(5, 5) == "Champions"


def test_assign_segment_at_risk():
    assert _assign_segment(1, 2) == "At Risk"


def test_calculate_rfm_columns(sample_transactions):
    rfm = calculate_rfm(sample_transactions)
    expected_cols = {
        "customer_id",
        "recency",
        "frequency",
        "monetary",
        "r_score",
        "f_score",
        "m_score",
        "rfm_score",
        "segment",
        "rank",
    }
    assert expected_cols.issubset(set(rfm.columns))
    assert len(rfm) == sample_transactions["customer_id"].nunique()


def test_rfm_scores_in_valid_range(sample_transactions):
    rfm = calculate_rfm(sample_transactions)
    for col in ["r_score", "f_score", "m_score"]:
        assert rfm[col].min() >= 1
        assert rfm[col].max() <= 5
