"""K-Means customer segmentation."""

from __future__ import annotations

from pathlib import Path

import joblib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly.express as px
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

from src.config import (
    MODELS_DIR,
    N_CLUSTERS,
    RANDOM_STATE,
    SCALER_PATH,
    SEGMENTATION_MODEL_PATH,
    SEGMENTATION_OUTPUT_DIR,
    SEGMENTS_FILE,
)


CLUSTER_LABELS = {
    0: "Budget Shoppers",
    1: "Occasional Buyers",
    2: "High-Value Loyalists",
    3: "At-Risk Spenders",
    4: "Emerging Champions",
}


def run_segmentation(
    customer_features: pd.DataFrame,
    n_clusters: int = N_CLUSTERS,
) -> tuple[pd.DataFrame, dict]:
    """Perform K-Means clustering with elbow analysis."""
    feature_cols = [
        "recency_days",
        "frequency",
        "monetary",
        "avg_order_value",
        "category_diversity",
        "product_diversity",
        "purchase_velocity",
    ]
    X = customer_features[feature_cols].fillna(0)

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    inertias = []
    k_range = range(2, 11)
    for k in k_range:
        model = KMeans(n_clusters=k, random_state=RANDOM_STATE, n_init=10)
        model.fit(X_scaled)
        inertias.append(model.inertia_)

    optimal_k = _select_optimal_k(list(k_range), inertias, default=n_clusters)
    kmeans = KMeans(n_clusters=optimal_k, random_state=RANDOM_STATE, n_init=10)
    clusters = kmeans.fit_predict(X_scaled)

    segmented = customer_features.copy()
    segmented["cluster"] = clusters
    segmented["cluster_label"] = segmented["cluster"].map(
        lambda c: CLUSTER_LABELS.get(c, f"Cluster {c}")
    )

    segmented.to_csv(SEGMENTS_FILE, index=False)
    joblib.dump(kmeans, SEGMENTATION_MODEL_PATH)
    joblib.dump(scaler, SCALER_PATH)

    _plot_elbow(list(k_range), inertias, SEGMENTATION_OUTPUT_DIR)
    _plot_clusters(segmented, SEGMENTATION_OUTPUT_DIR)

    insights = _generate_insights(segmented, feature_cols)
    return segmented, insights


def _select_optimal_k(k_values: list[int], inertias: list[float], default: int) -> int:
    if len(inertias) < 3:
        return default
    deltas = np.diff(inertias)
    delta2 = np.diff(deltas)
    elbow_idx = int(np.argmax(delta2)) + 2
    selected = k_values[min(elbow_idx, len(k_values) - 1)]
    return max(3, min(selected, 6))


def _plot_elbow(k_values: list[int], inertias: list[float], output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(k_values, inertias, marker="o", color="#7c3aed")
    ax.set_title("Elbow Method for Optimal Cluster Selection")
    ax.set_xlabel("Number of Clusters (k)")
    ax.set_ylabel("Inertia")
    plt.tight_layout()
    fig.savefig(output_dir / "elbow_method.png", dpi=150)
    plt.close(fig)


def _plot_clusters(segmented: pd.DataFrame, output_dir: Path) -> None:
    fig = px.scatter(
        segmented,
        x="frequency",
        y="monetary",
        color="cluster_label",
        size="avg_order_value",
        hover_data=["customer_id", "recency_days"],
        title="Customer Segments (K-Means)",
    )
    fig.write_html(str(output_dir / "customer_clusters.html"))


def _generate_insights(segmented: pd.DataFrame, feature_cols: list[str]) -> dict:
    summary = (
        segmented.groupby("cluster_label")[feature_cols]
        .mean()
        .round(2)
        .reset_index()
    )
    recommendations = {
        "Budget Shoppers": "Offer bundle discounts and low-AOV promotions to increase basket size.",
        "Occasional Buyers": "Deploy re-engagement email campaigns with personalized category offers.",
        "High-Value Loyalists": "Launch VIP loyalty program with early access and premium support.",
        "At-Risk Spenders": "Trigger win-back campaigns with limited-time offers before churn.",
        "Emerging Champions": "Upsell complementary products and encourage subscription models.",
    }
    return {
        "cluster_summary": summary.to_dict(orient="records"),
        "business_recommendations": recommendations,
        "cluster_counts": segmented["cluster_label"].value_counts().to_dict(),
    }
