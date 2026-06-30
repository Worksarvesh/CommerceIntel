"""Churn Prediction dashboard page."""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from dashboard.utils.data_loader import get_churn  # noqa: E402

st.set_page_config(page_title="Churn Prediction", layout="wide")
st.title("Customer Churn Prediction")

churn = get_churn()

threshold = st.slider("Churn Probability Threshold", min_value=0.1, max_value=0.9, value=0.5, step=0.05)
churn["predicted_churn"] = (churn["churn_probability"] >= threshold).astype(int)

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Customers", f"{len(churn):,}")
col2.metric("Predicted Churners", f"{churn['predicted_churn'].sum():,}")
col3.metric("Churn Rate", f"{100 * churn['predicted_churn'].mean():.1f}%")
col4.metric("Avg Churn Probability", f"{churn['churn_probability'].mean():.2f}")

left, right = st.columns(2)
with left:
    st.plotly_chart(
        px.histogram(
            churn,
            x="churn_probability",
            nbins=40,
            title="Churn Probability Distribution",
            color_discrete_sequence=["#ef4444"],
        ),
        use_container_width=True,
    )
with right:
    risk = churn.copy()
    risk["risk_band"] = pd.cut(
        risk["churn_probability"],
        bins=[0, 0.3, 0.6, 1.0],
        labels=["Low", "Medium", "High"],
    )
    risk_counts = risk["risk_band"].value_counts().reset_index()
    risk_counts.columns = ["risk_band", "count"]
    st.plotly_chart(
        px.pie(risk_counts, names="risk_band", values="count", title="Churn Risk Bands"),
        use_container_width=True,
    )

search_id = st.number_input("Search Customer ID", min_value=0, step=1)
display = churn.sort_values("churn_probability", ascending=False)
if search_id:
    display = display[display["customer_id"] == search_id]

st.subheader("High-Risk Customers")
st.dataframe(
    display.head(100)[
        [
            "customer_id",
            "country",
            "recency_days",
            "frequency",
            "monetary",
            "churn_probability",
            "predicted_churn",
        ]
    ],
    use_container_width=True,
)
