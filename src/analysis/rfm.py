"""RFM analysis and customer segmentation labels."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import plotly.express as px

from src.config import RFM_FILE, RFM_OUTPUT_DIR


SEGMENT_MAP = {
    (1, 1): "Lost Customers",
    (1, 2): "At Risk",
    (1, 3): "At Risk",
    (1, 4): "Potential Loyalists",
    (1, 5): "Champions",
    (2, 1): "Hibernating",
    (2, 2): "At Risk",
    (2, 3): "Potential Loyalists",
    (2, 4): "Loyal Customers",
    (2, 5): "Champions",
    (3, 1): "Hibernating",
    (3, 2): "Need Attention",
    (3, 3): "Potential Loyalists",
    (3, 4): "Loyal Customers",
    (3, 5): "Champions",
    (4, 1): "About to Sleep",
    (4, 2): "Need Attention",
    (4, 3): "Potential Loyalists",
    (4, 4): "Loyal Customers",
    (4, 5): "Champions",
    (5, 1): "Recent Customers",
    (5, 2): "Promising",
    (5, 3): "Potential Loyalists",
    (5, 4): "Loyal Customers",
    (5, 5): "Champions",
}


def calculate_rfm(transactions: pd.DataFrame) -> pd.DataFrame:
    """Compute RFM scores and customer segments."""
    reference_date = transactions["invoice_date"].max() + pd.Timedelta(days=1)

    order_level = (
        transactions.groupby(["customer_id", "invoice_no"], as_index=False)
        .agg(order_date=("invoice_date", "min"), order_revenue=("revenue", "sum"))
    )

    rfm = order_level.groupby("customer_id").agg(
        recency=("order_date", lambda x: (reference_date - x.max()).days),
        frequency=("invoice_no", "nunique"),
        monetary=("order_revenue", "sum"),
    )

    rfm["r_score"] = pd.qcut(
        rfm["recency"], 5, labels=False, duplicates="drop"
    )
    rfm["r_score"] = (6 - rfm["r_score"].fillna(0).astype(int)).clip(1, 5)
    rfm["f_score"] = pd.qcut(
        rfm["frequency"].rank(method="first"), 5, labels=False, duplicates="drop"
    ).fillna(0).astype(int) + 1
    rfm["m_score"] = pd.qcut(
        rfm["monetary"].rank(method="first"), 5, labels=False, duplicates="drop"
    ).fillna(0).astype(int) + 1
    rfm["rfm_score"] = (
        rfm["r_score"].astype(str)
        + rfm["f_score"].astype(str)
        + rfm["m_score"].astype(str)
    )
    rfm["rfm_combined"] = rfm["r_score"] + rfm["f_score"] + rfm["m_score"]
    rfm["segment"] = [
        _assign_segment(r, f) for r, f in zip(rfm["r_score"], rfm["f_score"])
    ]
    rfm["rank"] = rfm["rfm_combined"].rank(ascending=False, method="dense").astype(int)

    rfm = rfm.reset_index()
    rfm.to_csv(RFM_FILE, index=False)
    return rfm


def _assign_segment(r_score: int, f_score: int) -> str:
    return SEGMENT_MAP.get((int(r_score), int(f_score)), "Need Attention")


def visualize_rfm(rfm: pd.DataFrame, output_dir: Path = RFM_OUTPUT_DIR) -> None:
    """Create RFM visualizations."""
    output_dir.mkdir(parents=True, exist_ok=True)

    segment_counts = rfm["segment"].value_counts().reset_index()
    segment_counts.columns = ["segment", "count"]

    fig = px.bar(
        segment_counts,
        x="segment",
        y="count",
        color="segment",
        title="Customer Count by RFM Segment",
    )
    fig.update_layout(xaxis_tickangle=-45)
    fig.write_html(str(output_dir / "rfm_segment_distribution.html"))

    fig2, ax = plt.subplots(figsize=(8, 6))
    scatter = ax.scatter(
        rfm["frequency"],
        rfm["monetary"],
        c=rfm["recency"],
        cmap="viridis",
        alpha=0.6,
    )
    ax.set_xlabel("Frequency")
    ax.set_ylabel("Monetary")
    ax.set_title("RFM Scatter (color = Recency)")
    plt.colorbar(scatter, ax=ax, label="Recency (days)")
    plt.tight_layout()
    fig2.savefig(output_dir / "rfm_scatter.png", dpi=150)
    plt.close(fig2)

    heatmap_data = rfm.groupby(["r_score", "f_score"])["customer_id"].count().unstack(fill_value=0)
    fig3, ax = plt.subplots(figsize=(8, 6))
    im = ax.imshow(heatmap_data.values, cmap="Blues")
    ax.set_xticks(range(len(heatmap_data.columns)))
    ax.set_yticks(range(len(heatmap_data.index)))
    ax.set_xticklabels(heatmap_data.columns)
    ax.set_yticklabels(heatmap_data.index)
    ax.set_xlabel("Frequency Score")
    ax.set_ylabel("Recency Score")
    ax.set_title("RFM Heatmap")
    plt.colorbar(im, ax=ax)
    plt.tight_layout()
    fig3.savefig(output_dir / "rfm_heatmap.png", dpi=150)
    plt.close(fig3)
