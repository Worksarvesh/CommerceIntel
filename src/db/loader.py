"""Load cleaned data into SQLite database."""

from __future__ import annotations

import pandas as pd

from src.config import DB_PATH
from src.db.connection import db_session, initialize_schema


def load_data_to_db(transactions: pd.DataFrame, db_path=DB_PATH) -> dict:
    """Populate SQLite tables from cleaned transactions dataframe."""
    initialize_schema(db_path)

    customers = (
        transactions.groupby("customer_id", as_index=False)
        .agg(
            country=("country", "first"),
            first_purchase_date=("invoice_date", "min"),
            last_purchase_date=("invoice_date", "max"),
            total_orders=("invoice_no", "nunique"),
            total_revenue=("revenue", "sum"),
        )
    )

    products = (
        transactions.groupby("stock_code", as_index=False)
        .agg(
            description=("description", lambda x: x.mode().iloc[0]),
            category=("category", lambda x: x.mode().iloc[0]),
            avg_unit_price=("unit_price", "mean"),
            total_quantity_sold=("quantity", "sum"),
            total_revenue=("revenue", "sum"),
        )
    )

    orders = (
        transactions.groupby(["invoice_no", "customer_id"], as_index=False)
        .agg(
            order_date=("invoice_date", "min"),
            order_total=("revenue", "sum"),
            country=("country", "first"),
        )
        .rename(columns={"invoice_no": "order_id"})
    )

    with db_session(db_path) as conn:
        customers.to_sql("customers", conn, if_exists="append", index=False)
        products.to_sql("products", conn, if_exists="append", index=False)
        orders.to_sql("orders", conn, if_exists="append", index=False)

        tx = transactions.copy()
        tx = tx.rename(
            columns={
                "invoice_no": "order_id",
                "invoice_date": "transaction_date",
            }
        )
        tx = tx[
            [
                "order_id",
                "customer_id",
                "stock_code",
                "description",
                "category",
                "quantity",
                "unit_price",
                "revenue",
                "transaction_date",
            ]
        ]
        tx.to_sql("transactions", conn, if_exists="append", index=False)

    return {
        "customers": len(customers),
        "products": len(products),
        "orders": len(orders),
        "transactions": len(transactions),
    }
