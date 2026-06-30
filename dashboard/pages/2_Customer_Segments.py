"""Customer Segments dashboard page."""

from __future__ import annotations

import sys
from pathlib import Path

import plotly.express as px
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from dashboard.utils.data_loader import get_rfm, get_segments  # noqa: E402

st.set_page_config(page_title="Customer Segments", layout="wide")
st.title("Customer Segmentation")

rfm = get_rfm()
segments = get_segments()

tab1, tab2 = st.tabs(["RFM Analysis", "K-Means Clusters"])

with tab1:
    segment_filter = st.multiselect(
        "RFM Segment Filter",
        options=sorted(rfm["segment"].unique()),
        default=sorted(rfm["segment"].unique()),
    )
    rfm_filtered = rfm[rfm["segment"].isin(segment_filter)]

    col1, col2 = st.columns(2)
    with col1:
        counts = rfm_filtered["segment"].value_counts().reset_index()
        counts.columns = ["segment", "count"]
        st.plotly_chart(
            px.bar(counts, x="segment", y="count", color="segment", title="RFM Segment Distribution"),
            use_container_width=True,
        )
    with col2:
        st.plotly_chart(
            px.scatter(
                rfm_filtered,
                x="frequency",
                y="monetary",
                color="segment",
                size="recency",
                hover_data=["customer_id"],
                title="RFM Scatter Plot",
            ),
            use_container_width=True,
        )

    st.dataframe(
        rfm_filtered.sort_values("rank").head(100)[
            ["customer_id", "recency", "frequency", "monetary", "rfm_score", "segment", "rank"]
        ],
        use_container_width=True,
    )

with tab2:
    cluster_filter = st.multiselect(
        "Cluster Filter",
        options=sorted(segments["cluster_label"].unique()),
        default=sorted(segments["cluster_label"].unique()),
    )
    seg_filtered = segments[segments["cluster_label"].isin(cluster_filter)]

    st.plotly_chart(
        px.scatter(
            seg_filtered,
            x="frequency",
            y="monetary",
            color="cluster_label",
            size="avg_order_value",
            hover_data=["customer_id", "recency_days"],
            title="K-Means Customer Clusters",
        ),
        use_container_width=True,
    )

    cluster_summary = (
        seg_filtered.groupby("cluster_label")
        .agg(
            customers=("customer_id", "count"),
            avg_recency=("recency_days", "mean"),
            avg_frequency=("frequency", "mean"),
            avg_monetary=("monetary", "mean"),
        )
        .reset_index()
    )
    st.subheader("Cluster Summary")
    st.dataframe(cluster_summary, use_container_width=True)

    st.subheader("Business Recommendations")
    recommendations = {
        "Budget Shoppers": "Offer bundle discounts and low-AOV promotions.",
        "Occasional Buyers": "Deploy re-engagement campaigns with personalized offers.",
        "High-Value Loyalists": "Launch VIP loyalty program with premium perks.",
        "At-Risk Spenders": "Trigger win-back campaigns before churn.",
        "Emerging Champions": "Upsell complementary products and subscriptions.",
    }
    for label, action in recommendations.items():
        st.markdown(f"- **{label}**: {action}")
