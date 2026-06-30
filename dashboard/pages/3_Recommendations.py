"""Recommendations dashboard page."""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from dashboard.utils.data_loader import (  # noqa: E402
    get_recommendation_engine,
    get_recommendations,
    get_transactions,
)

st.set_page_config(page_title="Recommendations", layout="wide")
st.title("Product Recommendations")

transactions = get_transactions()
engine = get_recommendation_engine()
sample_recs = get_recommendations()

customer_ids = sorted(transactions["customer_id"].unique().tolist())
selected_customer = st.selectbox("Select Customer ID", customer_ids)
method = st.selectbox(
    "Recommendation Method",
    ["hybrid", "collaborative", "content_based", "popular"],
)
top_n = st.slider("Top N Recommendations", min_value=3, max_value=20, value=10)

if method == "hybrid":
    recs = engine.hybrid_recommendations(selected_customer, top_n=top_n)
elif method == "collaborative":
    recs = engine.collaborative_recommendations(selected_customer, top_n=top_n)
elif method == "content_based":
    recent = (
        transactions[transactions["customer_id"] == selected_customer]
        .sort_values("invoice_date", ascending=False)["stock_code"]
        .iloc[0]
    )
    st.caption(f"Content-based anchor product: {recent}")
    recs = engine.content_based_recommendations(recent, top_n=top_n)
else:
    recs = engine.popular_recommendations(top_n=top_n)

if recs:
    st.subheader(f"Top {top_n} Recommendations for Customer {selected_customer}")
    st.dataframe(pd.DataFrame(recs), use_container_width=True)
else:
    st.warning("No recommendations available for this selection.")

st.divider()
st.subheader("Sample Pre-computed Recommendations")
search_customer = st.number_input("Search Customer ID in sample set", min_value=0, step=1)
filtered = sample_recs
if search_customer:
    filtered = sample_recs[sample_recs["customer_id"] == search_customer]
st.dataframe(filtered.head(100), use_container_width=True)
