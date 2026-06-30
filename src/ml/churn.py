"""Customer churn prediction using Random Forest."""

from __future__ import annotations

from pathlib import Path

import joblib
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)
from sklearn.model_selection import train_test_split

from src.config import (
    CHURN_FILE,
    CHURN_INACTIVE_DAYS,
    CHURN_MODEL_PATH,
    CHURN_OUTPUT_DIR,
    RANDOM_STATE,
)


def build_churn_dataset(
    transactions: pd.DataFrame, inactive_days: int = CHURN_INACTIVE_DAYS
) -> pd.DataFrame:
    """Label customers as churned if inactive beyond threshold."""
    reference_date = transactions["invoice_date"].max()
    cutoff = reference_date - pd.Timedelta(days=inactive_days)

    order_stats = (
        transactions.groupby(["customer_id", "invoice_no"], as_index=False)
        .agg(order_date=("invoice_date", "max"), order_revenue=("revenue", "sum"))
    )

    features = order_stats.groupby("customer_id").agg(
        recency_days=("order_date", lambda x: (reference_date - x.max()).days),
        frequency=("invoice_no", "nunique"),
        monetary=("order_revenue", "sum"),
        avg_order_value=("order_revenue", "mean"),
        last_purchase=("order_date", "max"),
        first_purchase=("order_date", "min"),
    )

    category_div = transactions.groupby("customer_id")["category"].nunique()
    product_div = transactions.groupby("customer_id")["stock_code"].nunique()
    country = transactions.groupby("customer_id")["country"].agg(lambda x: x.mode().iloc[0])

    features["category_diversity"] = category_div
    features["product_diversity"] = product_div
    features["country"] = country
    features["customer_lifetime_days"] = (
        features["last_purchase"] - features["first_purchase"]
    ).dt.days.clip(lower=0)
    features["churned"] = (features["last_purchase"] < cutoff).astype(int)
    features = features.reset_index()
    return features


def train_churn_model(churn_df: pd.DataFrame) -> tuple[RandomForestClassifier, dict]:
    """Train and evaluate Random Forest churn classifier."""
    feature_cols = [
        "recency_days",
        "frequency",
        "monetary",
        "avg_order_value",
        "category_diversity",
        "product_diversity",
        "customer_lifetime_days",
    ]

    X = churn_df[feature_cols].fillna(0)
    y = churn_df["churned"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=RANDOM_STATE, stratify=y
    )

    model = RandomForestClassifier(
        n_estimators=200,
        max_depth=12,
        min_samples_leaf=4,
        random_state=RANDOM_STATE,
        class_weight="balanced",
    )
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)

    metrics = {
        "accuracy": float(accuracy_score(y_test, y_pred)),
        "precision": float(precision_score(y_test, y_pred, zero_division=0)),
        "recall": float(recall_score(y_test, y_pred, zero_division=0)),
        "f1_score": float(f1_score(y_test, y_pred, zero_division=0)),
        "classification_report": classification_report(y_test, y_pred, output_dict=True),
        "confusion_matrix": confusion_matrix(y_test, y_pred).tolist(),
        "feature_importance": dict(
            zip(feature_cols, model.feature_importances_.round(4).tolist())
        ),
    }

    joblib.dump(model, CHURN_MODEL_PATH)

    predictions = churn_df.copy()
    predictions["churn_probability"] = model.predict_proba(X)[:, 1]
    predictions["churn_prediction"] = (predictions["churn_probability"] >= 0.5).astype(int)
    predictions.to_csv(CHURN_FILE, index=False)

    _plot_confusion_matrix(metrics["confusion_matrix"], CHURN_OUTPUT_DIR)
    _plot_feature_importance(metrics["feature_importance"], CHURN_OUTPUT_DIR)

    return model, metrics


def _plot_confusion_matrix(matrix: list[list[int]], output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(6, 5))
    sns.heatmap(
        matrix,
        annot=True,
        fmt="d",
        cmap="Blues",
        xticklabels=["Active", "Churned"],
        yticklabels=["Active", "Churned"],
        ax=ax,
    )
    ax.set_xlabel("Predicted")
    ax.set_ylabel("Actual")
    ax.set_title("Churn Prediction Confusion Matrix")
    plt.tight_layout()
    fig.savefig(output_dir / "confusion_matrix.png", dpi=150)
    plt.close(fig)


def _plot_feature_importance(importance: dict[str, float], output_dir: Path) -> None:
    fig, ax = plt.subplots(figsize=(8, 5))
    features = list(importance.keys())
    values = list(importance.values())
    ax.barh(features, values, color="#ef4444")
    ax.set_title("Churn Model Feature Importance")
    ax.set_xlabel("Importance")
    plt.tight_layout()
    fig.savefig(output_dir / "feature_importance.png", dpi=150)
    plt.close(fig)
