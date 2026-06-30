"""Shared utilities for Streamlit dashboard."""

from __future__ import annotations

from functools import lru_cache

import pandas as pd

from src.config import (
    CHURN_FILE,
    PROCESSED_CUSTOMERS_FILE,
    PROCESSED_TRANSACTIONS_FILE,
    RECOMMENDATIONS_FILE,
    RFM_FILE,
    SEGMENTS_FILE,
)
from src.data.loader import load_processed_transactions
from src.ml.recommendation import RecommendationEngine


@lru_cache(maxsize=1)
def get_transactions() -> pd.DataFrame:
    return load_processed_transactions()


@lru_cache(maxsize=1)
def get_customer_features() -> pd.DataFrame:
    return pd.read_csv(PROCESSED_CUSTOMERS_FILE)


@lru_cache(maxsize=1)
def get_rfm() -> pd.DataFrame:
    return pd.read_csv(RFM_FILE)


@lru_cache(maxsize=1)
def get_segments() -> pd.DataFrame:
    return pd.read_csv(SEGMENTS_FILE)


@lru_cache(maxsize=1)
def get_churn() -> pd.DataFrame:
    return pd.read_csv(CHURN_FILE)


@lru_cache(maxsize=1)
def get_recommendations() -> pd.DataFrame:
    return pd.read_csv(RECOMMENDATIONS_FILE)


@lru_cache(maxsize=1)
def get_recommendation_engine() -> RecommendationEngine:
    return RecommendationEngine(get_transactions())


def compute_kpis(transactions: pd.DataFrame) -> dict:
    return {
        "total_revenue": transactions["revenue"].sum(),
        "total_orders": transactions["invoice_no"].nunique(),
        "total_customers": transactions["customer_id"].nunique(),
        "total_products": transactions["stock_code"].nunique(),
        "avg_order_value": transactions.groupby("invoice_no")["revenue"].sum().mean(),
    }
