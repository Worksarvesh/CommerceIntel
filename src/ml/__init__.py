"""Machine learning package."""

from src.ml.churn import build_churn_dataset, train_churn_model
from src.ml.recommendation import RecommendationEngine, generate_sample_recommendations
from src.ml.segmentation import run_segmentation

__all__ = [
    "build_churn_dataset",
    "train_churn_model",
    "RecommendationEngine",
    "generate_sample_recommendations",
    "run_segmentation",
]
