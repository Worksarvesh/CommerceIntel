"""Sales Analytics dashboard page."""

from __future__ import annotations

import sys
from pathlib import Path

import plotly.express as px
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from dashboard.utils.data_loader import get_transactions  # noqa: E402

st.set_page_config(page_title="Sales Analytics", layout="wide")
st.title("Sales Analytics")

transactions = get_transactions()

country_filter = st.multiselect(
    "Filter by Country",
    options=sorted(transactions["country"].unique()),
    default=sorted(transactions["country"].unique())[:5],
)
category_filter = st.multiselect(
    "Filter by Category",
    options=sorted(transactions["category"].unique()),
)

filtered = transactions[transactions["country"].isin(country_filter)]
if category_filter:
    filtered = filtered[filtered["category"].isin(category_filter)]

search_term = st.text_input("Search product description")
if search_term:
    filtered = filtered[
        filtered["description"].str.contains(search_term, case=False, na=False)
    ]

monthly = filtered.copy()
monthly["year_month"] = monthly["invoice_date"].dt.to_period("M").astype(str)
monthly_agg = (
    monthly.groupby("year_month", as_index=False)
    .agg(revenue=("revenue", "sum"), orders=("invoice_no", "nunique"))
    .sort_values("year_month")
)

col1, col2 = st.columns(2)
with col1:
    st.plotly_chart(
        px.bar(monthly_agg, x="year_month", y="revenue", title="Monthly Revenue"),
        use_container_width=True,
    )
with col2:
    st.plotly_chart(
        px.line(monthly_agg, x="year_month", y="orders", title="Monthly Orders", markers=True),
        use_container_width=True,
    )

top_products = (
    filtered.groupby(["stock_code", "description"], as_index=False)["revenue"]
    .sum()
    .sort_values("revenue", ascending=False)
    .head(20)
)
st.plotly_chart(
    px.bar(
        top_products,
        x="revenue",
        y="description",
        orientation="h",
        title="Top Products by Revenue",
    ),
    use_container_width=True,
)

top_customers = (
    filtered.groupby("customer_id", as_index=False)["revenue"]
    .sum()
    .sort_values("revenue", ascending=False)
    .head(20)
)
st.plotly_chart(
    px.bar(top_customers, x="customer_id", y="revenue", title="Top Customers by Revenue"),
    use_container_width=True,
)
