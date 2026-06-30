"""Feature engineering for analytics and machine learning."""

from __future__ import annotations

import pandas as pd

from src.config import PROCESSED_CUSTOMERS_FILE


def build_customer_features(transactions: pd.DataFrame) -> pd.DataFrame:
    """Aggregate transaction-level data into customer-level features."""
    reference_date = transactions["invoice_date"].max() + pd.Timedelta(days=1)

    customer_orders = (
        transactions.groupby(["customer_id", "invoice_no"], as_index=False)
        .agg(order_revenue=("revenue", "sum"), order_date=("invoice_date", "min"))
    )

    features = customer_orders.groupby("customer_id").agg(
        recency_days=("order_date", lambda x: (reference_date - x.max()).days),
        frequency=("invoice_no", "nunique"),
        monetary=("order_revenue", "sum"),
        avg_order_value=("order_revenue", "mean"),
        total_items=("order_revenue", "count"),
        first_purchase=("order_date", "min"),
        last_purchase=("order_date", "max"),
    )

    country_map = transactions.groupby("customer_id")["country"].agg(
        lambda x: x.mode().iloc[0]
    )
    category_diversity = transactions.groupby("customer_id")["category"].nunique()
    product_diversity = transactions.groupby("customer_id")["stock_code"].nunique()

    features = features.join(country_map.rename("country"))
    features["category_diversity"] = category_diversity
    features["product_diversity"] = product_diversity
    features["customer_lifetime_days"] = (
        features["last_purchase"] - features["first_purchase"]
    ).dt.days.clip(lower=0)
    features["purchase_velocity"] = features["frequency"] / (
        features["customer_lifetime_days"].replace(0, 1)
    )

    features = features.reset_index()
    features.to_csv(PROCESSED_CUSTOMERS_FILE, index=False)
    return features


def build_product_features(transactions: pd.DataFrame) -> pd.DataFrame:
    """Aggregate product-level metrics."""
    return (
        transactions.groupby(["stock_code", "description", "category"], as_index=False)
        .agg(
            total_quantity=("quantity", "sum"),
            total_revenue=("revenue", "sum"),
            unique_customers=("customer_id", "nunique"),
            avg_unit_price=("unit_price", "mean"),
        )
        .sort_values("total_revenue", ascending=False)
    )


def build_monthly_sales(transactions: pd.DataFrame) -> pd.DataFrame:
    """Compute monthly revenue aggregates."""
    monthly = transactions.copy()
    monthly["year_month"] = monthly["invoice_date"].dt.to_period("M").astype(str)
    return (
        monthly.groupby("year_month", as_index=False)
        .agg(
            total_revenue=("revenue", "sum"),
            total_orders=("invoice_no", "nunique"),
            total_customers=("customer_id", "nunique"),
            avg_order_value=("revenue", "mean"),
        )
        .sort_values("year_month")
    )
