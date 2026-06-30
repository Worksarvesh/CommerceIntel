"""Expanded pytest fixtures."""

import pandas as pd
import pytest


@pytest.fixture
def sample_transactions() -> pd.DataFrame:
    rows = []
    products = [
        ("P1", "RED BAG", "Bags & Accessories", 10.0),
        ("P2", "WHITE MUG", "Kitchen", 5.0),
        ("P3", "GARDEN LIGHT", "Garden", 20.0),
        ("P4", "GIFT BOX", "Gifts", 15.0),
        ("P5", "PARTY SET", "Party Supplies", 8.0),
        ("P6", "TOY CAR", "Toys & Games", 12.0),
    ]
    dates = pd.date_range("2011-01-01", periods=12, freq="W")
    for idx, customer_id in enumerate(range(101, 121)):
        for j, (stock_code, desc, category, price) in enumerate(products):
            if (idx + j) % 3 == 0:
                continue
            order_date = dates[j % len(dates)]
            qty = 1 + (idx % 4)
            rows.append(
                {
                    "invoice_no": f"ORD-{customer_id}-{j}",
                    "stock_code": stock_code,
                    "description": desc,
                    "quantity": qty,
                    "invoice_date": order_date,
                    "unit_price": price,
                    "customer_id": customer_id,
                    "country": "UK",
                    "revenue": qty * price,
                    "category": category,
                }
            )
    return pd.DataFrame(rows)


@pytest.fixture
def sample_customer_features(sample_transactions) -> pd.DataFrame:
    from src.data.feature_engineering import build_customer_features

    return build_customer_features(sample_transactions)
