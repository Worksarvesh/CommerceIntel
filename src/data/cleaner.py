"""Data cleaning, outlier handling, and preprocessing."""

from __future__ import annotations

import numpy as np
import pandas as pd

from src.config import PROCESSED_TRANSACTIONS_FILE


def _derive_category(description: str) -> str:
    """Map product descriptions to coarse categories."""
    text = str(description).upper()
    mapping = {
        "BAG": "Bags & Accessories",
        "BOX": "Storage & Packaging",
        "CARD": "Cards & Stationery",
        "LIGHT": "Home & Lighting",
        "CANDLE": "Home & Lighting",
        "GIFT": "Gifts",
        "TOY": "Toys & Games",
        "PARTY": "Party Supplies",
        "KITCHEN": "Kitchen",
        "BATH": "Bathroom",
        "GARDEN": "Garden",
        "CHRISTMAS": "Seasonal",
        "HEART": "Gifts",
        "METAL": "Decor",
        "WOOD": "Decor",
        "GLASS": "Decor",
        "CUP": "Kitchen",
        "MUG": "Kitchen",
        "PLATE": "Kitchen",
        "SET": "Sets & Bundles",
    }
    for keyword, category in mapping.items():
        if keyword in text:
            return category
    return "General Merchandise"


def clean_transactions(df: pd.DataFrame) -> pd.DataFrame:
    """Apply full cleaning pipeline to raw Online Retail data."""
    cleaned = df.copy()
    cleaned.columns = [
        "invoice_no",
        "stock_code",
        "description",
        "quantity",
        "invoice_date",
        "unit_price",
        "customer_id",
        "country",
    ]

    cleaned["invoice_no"] = cleaned["invoice_no"].astype(str).str.strip()
    cleaned["stock_code"] = cleaned["stock_code"].astype(str).str.strip()
    cleaned["description"] = cleaned["description"].astype(str).str.strip()
    cleaned["country"] = cleaned["country"].astype(str).str.strip()

    cleaned["invoice_date"] = pd.to_datetime(cleaned["invoice_date"], errors="coerce")
    cleaned["quantity"] = pd.to_numeric(cleaned["quantity"], errors="coerce")
    cleaned["unit_price"] = pd.to_numeric(cleaned["unit_price"], errors="coerce")
    cleaned["customer_id"] = pd.to_numeric(cleaned["customer_id"], errors="coerce")

    cleaned = cleaned.dropna(subset=["invoice_date", "quantity", "unit_price"])
    cleaned = cleaned.drop_duplicates()

    cleaned = cleaned[cleaned["quantity"] > 0]
    cleaned = cleaned[cleaned["unit_price"] >= 0]
    cleaned = cleaned[~cleaned["invoice_no"].str.startswith("C", na=False)]
    cleaned = cleaned[cleaned["customer_id"].notna()]

    cleaned["customer_id"] = cleaned["customer_id"].astype(int)
    cleaned["revenue"] = cleaned["quantity"] * cleaned["unit_price"]
    cleaned["category"] = cleaned["description"].map(_derive_category)

    cleaned = _treat_outliers(cleaned)
    return cleaned.reset_index(drop=True)


def _treat_outliers(df: pd.DataFrame) -> pd.DataFrame:
    """Cap extreme revenue and quantity values using IQR method."""
    treated = df.copy()
    for column in ["quantity", "revenue"]:
        q1 = treated[column].quantile(0.25)
        q3 = treated[column].quantile(0.75)
        iqr = q3 - q1
        upper = q3 + 3 * iqr
        treated[column] = treated[column].clip(upper=upper)
        if column == "quantity":
            treated["revenue"] = treated["quantity"] * treated["unit_price"]
    return treated


def get_cleaning_report(raw_df: pd.DataFrame, clean_df: pd.DataFrame) -> dict:
    """Return summary statistics for cleaning stage."""
    return {
        "raw_rows": len(raw_df),
        "clean_rows": len(clean_df),
        "rows_removed": len(raw_df) - len(clean_df),
        "duplicate_rows_removed": int(raw_df.duplicated().sum()),
        "missing_customer_rows_removed": int(raw_df["CustomerID"].isna().sum()),
        "cancelled_invoices_removed": int(raw_df["InvoiceNo"].astype(str).str.startswith("C").sum()),
        "unique_customers": clean_df["customer_id"].nunique(),
        "unique_products": clean_df["stock_code"].nunique(),
        "date_range": (
            clean_df["invoice_date"].min().strftime("%Y-%m-%d"),
            clean_df["invoice_date"].max().strftime("%Y-%m-%d"),
        ),
        "total_revenue": float(clean_df["revenue"].sum()),
    }


def save_cleaned_data(df: pd.DataFrame, path=PROCESSED_TRANSACTIONS_FILE) -> None:
    """Persist cleaned transactions."""
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)
