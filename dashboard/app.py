"""CommerceIntel Analytics Platform - Streamlit Dashboard."""

from __future__ import annotations

import sys
from pathlib import Path

import plotly.express as px
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from dashboard.utils.data_loader import compute_kpis, get_transactions  # noqa: E402

st.set_page_config(
    page_title="CommerceIntel Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("CommerceIntel Analytics Platform")
st.markdown(
    """
    **E-commerce Recommendation & Customer Segmentation Dashboard**

    Navigate using the sidebar to explore sales analytics, customer segments,
    product recommendations, and churn predictions.
    """
)

try:
    transactions = get_transactions()
    kpis = compute_kpis(transactions)

    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Total Revenue", f"£{kpis['total_revenue']:,.0f}")
    col2.metric("Total Orders", f"{kpis['total_orders']:,}")
    col3.metric("Customers", f"{kpis['total_customers']:,}")
    col4.metric("Products", f"{kpis['total_products']:,}")
    col5.metric("Avg Order Value", f"£{kpis['avg_order_value']:,.2f}")

    st.divider()

    monthly = transactions.copy()
    monthly["year_month"] = monthly["invoice_date"].dt.to_period("M").astype(str)
    monthly_agg = (
        monthly.groupby("year_month", as_index=False)
        .agg(revenue=("revenue", "sum"), orders=("invoice_no", "nunique"))
        .sort_values("year_month")
    )

    left, right = st.columns(2)
    with left:
        fig = px.line(
            monthly_agg,
            x="year_month",
            y="revenue",
            title="Revenue Trend",
            markers=True,
        )
        st.plotly_chart(fig, use_container_width=True)

    with right:
        category = (
            transactions.groupby("category", as_index=False)["revenue"]
            .sum()
            .sort_values("revenue", ascending=False)
        )
        fig2 = px.pie(category, names="category", values="revenue", title="Revenue by Category")
        st.plotly_chart(fig2, use_container_width=True)

    st.info(
        "Run `python run_pipeline.py` if data is missing. "
        "Use sidebar pages for detailed analytics modules."
    )

except FileNotFoundError as exc:
    st.error(str(exc))
    st.code("python run_pipeline.py", language="bash")
