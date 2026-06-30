"""End-to-end analytics pipeline orchestrator."""

from __future__ import annotations

import json
from pathlib import Path

from src.analysis.eda import run_eda
from src.analysis.rfm import calculate_rfm, visualize_rfm
from src.config import OUTPUTS_DIR, PROJECT_ROOT
from src.data.cleaner import clean_transactions, get_cleaning_report, save_cleaned_data
from src.data.feature_engineering import build_customer_features
from src.data.loader import download_kaggle_dataset, load_raw_transactions
from src.db.loader import load_data_to_db
from src.ml.churn import build_churn_dataset, train_churn_model
from src.ml.recommendation import generate_sample_recommendations
from src.ml.segmentation import run_segmentation


def run_full_pipeline(download: bool = False) -> dict:
    """Execute complete CommerceIntel analytics pipeline."""
    if download:
        download_kaggle_dataset()

    raw_df = load_raw_transactions()
    clean_df = clean_transactions(raw_df)
    save_cleaned_data(clean_df)

    cleaning_report = get_cleaning_report(raw_df, clean_df)
    eda_summary = run_eda(clean_df)
    customer_features = build_customer_features(clean_df)
    rfm_df = calculate_rfm(clean_df)
    visualize_rfm(rfm_df)
    segmented_df, segmentation_insights = run_segmentation(customer_features)
    churn_df = build_churn_dataset(clean_df)
    _, churn_metrics = train_churn_model(churn_df)
    recommendations_df = generate_sample_recommendations(clean_df)
    db_stats = load_data_to_db(clean_df)

    report = {
        "cleaning": cleaning_report,
        "eda": eda_summary,
        "segmentation": segmentation_insights,
        "churn_metrics": {
            k: v for k, v in churn_metrics.items() if k != "classification_report"
        },
        "database": db_stats,
        "recommendations_generated": len(recommendations_df),
    }

    report_path = OUTPUTS_DIR / "pipeline_report.json"
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report


if __name__ == "__main__":
    summary = run_full_pipeline()
    print(json.dumps(summary, indent=2))
