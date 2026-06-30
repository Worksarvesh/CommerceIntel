"""Exploratory data analysis and visualization."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from src.config import EDA_OUTPUT_DIR
from src.data.feature_engineering import build_monthly_sales, build_product_features


def run_eda(transactions: pd.DataFrame, output_dir: Path = EDA_OUTPUT_DIR) -> dict:
    """Generate EDA charts and return summary metrics."""
    output_dir.mkdir(parents=True, exist_ok=True)

    monthly = build_monthly_sales(transactions)
    products = build_product_features(transactions)
    customer_revenue = (
        transactions.groupby("customer_id", as_index=False)["revenue"]
        .sum()
        .sort_values("revenue", ascending=False)
    )
    category_perf = (
        transactions.groupby("category", as_index=False)["revenue"]
        .sum()
        .sort_values("revenue", ascending=False)
    )
    purchase_freq = (
        transactions.groupby("customer_id")["invoice_no"]
        .nunique()
        .reset_index(name="order_count")
    )
    clv = customer_revenue.rename(columns={"revenue": "customer_lifetime_value"})

    _plot_revenue_trends(monthly, output_dir)
    _plot_monthly_sales(monthly, output_dir)
    _plot_top_products(products, output_dir)
    _plot_top_customers(customer_revenue, output_dir)
    _plot_category_performance(category_perf, output_dir)
    _plot_purchase_frequency(purchase_freq, output_dir)
    _plot_clv(clv, output_dir)

    return {
        "total_revenue": float(transactions["revenue"].sum()),
        "total_orders": int(transactions["invoice_no"].nunique()),
        "total_customers": int(transactions["customer_id"].nunique()),
        "avg_monthly_revenue": float(monthly["total_revenue"].mean()),
        "top_product": products.iloc[0]["description"],
        "top_category": category_perf.iloc[0]["category"],
    }


def _plot_revenue_trends(monthly: pd.DataFrame, output_dir: Path) -> None:
    fig, ax = plt.subplots(figsize=(12, 5))
    ax.plot(monthly["year_month"], monthly["total_revenue"], marker="o", color="#2563eb")
    ax.set_title("Revenue Trends Over Time")
    ax.set_xlabel("Month")
    ax.set_ylabel("Revenue")
    ax.tick_params(axis="x", rotation=45)
    plt.tight_layout()
    fig.savefig(output_dir / "revenue_trends.png", dpi=150)
    plt.close(fig)

    plotly_fig = px.line(
        monthly,
        x="year_month",
        y="total_revenue",
        title="Interactive Revenue Trends",
        markers=True,
    )
    plotly_fig.write_html(str(output_dir / "revenue_trends.html"))


def _plot_monthly_sales(monthly: pd.DataFrame, output_dir: Path) -> None:
    fig = px.bar(
        monthly,
        x="year_month",
        y=["total_revenue", "total_orders"],
        barmode="group",
        title="Monthly Sales Performance",
    )
    fig.write_html(str(output_dir / "monthly_sales.html"))

    fig2, ax = plt.subplots(figsize=(12, 5))
    ax.bar(monthly["year_month"], monthly["total_orders"], color="#10b981")
    ax.set_title("Monthly Order Volume")
    ax.tick_params(axis="x", rotation=45)
    plt.tight_layout()
    fig2.savefig(output_dir / "monthly_orders.png", dpi=150)
    plt.close(fig2)


def _plot_top_products(products: pd.DataFrame, output_dir: Path, top_n: int = 15) -> None:
    top = products.head(top_n)
    fig = px.bar(
        top,
        x="total_revenue",
        y="description",
        orientation="h",
        title=f"Top {top_n} Products by Revenue",
        color="category",
    )
    fig.update_layout(yaxis={"categoryorder": "total ascending"})
    fig.write_html(str(output_dir / "top_products.html"))


def _plot_top_customers(customers: pd.DataFrame, output_dir: Path, top_n: int = 15) -> None:
    top = customers.head(top_n)
    fig = go.Figure(
        data=[
            go.Bar(
                x=top["customer_id"].astype(str),
                y=top["revenue"],
                marker_color="#f59e0b",
            )
        ]
    )
    fig.update_layout(title=f"Top {top_n} Customers by Revenue", xaxis_title="Customer ID", yaxis_title="Revenue")
    fig.write_html(str(output_dir / "top_customers.html"))


def _plot_category_performance(categories: pd.DataFrame, output_dir: Path) -> None:
    fig = px.pie(
        categories,
        names="category",
        values="revenue",
        title="Category Revenue Share",
        hole=0.35,
    )
    fig.write_html(str(output_dir / "category_performance.html"))


def _plot_purchase_frequency(freq: pd.DataFrame, output_dir: Path) -> None:
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.hist(freq["order_count"], bins=30, color="#6366f1", edgecolor="white")
    ax.set_title("Customer Purchase Frequency Distribution")
    ax.set_xlabel("Number of Orders")
    ax.set_ylabel("Customers")
    plt.tight_layout()
    fig.savefig(output_dir / "purchase_frequency.png", dpi=150)
    plt.close(fig)


def _plot_clv(clv: pd.DataFrame, output_dir: Path) -> None:
    fig = px.histogram(
        clv,
        x="customer_lifetime_value",
        nbins=40,
        title="Customer Lifetime Value Distribution",
    )
    fig.write_html(str(output_dir / "customer_lifetime_value.html"))
