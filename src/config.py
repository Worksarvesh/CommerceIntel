"""Central configuration for CommerceIntel Analytics Platform."""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
OUTPUTS_DIR = DATA_DIR / "outputs"
DATABASE_DIR = PROJECT_ROOT / "database"
MODELS_DIR = PROJECT_ROOT / "models"

RAW_DATA_FILE = RAW_DATA_DIR / "data.csv"
PROCESSED_TRANSACTIONS_FILE = PROCESSED_DATA_DIR / "transactions_clean.csv"
PROCESSED_CUSTOMERS_FILE = PROCESSED_DATA_DIR / "customers_features.csv"
RFM_FILE = PROCESSED_DATA_DIR / "rfm_scores.csv"
SEGMENTS_FILE = PROCESSED_DATA_DIR / "customer_segments.csv"
CHURN_FILE = PROCESSED_DATA_DIR / "churn_predictions.csv"
RECOMMENDATIONS_FILE = PROCESSED_DATA_DIR / "sample_recommendations.csv"

DB_PATH = DATABASE_DIR / "commerceintel.db"
SCHEMA_PATH = DATABASE_DIR / "schema.sql"
QUERIES_PATH = DATABASE_DIR / "queries.sql"

EDA_OUTPUT_DIR = OUTPUTS_DIR / "eda"
RFM_OUTPUT_DIR = OUTPUTS_DIR / "rfm"
SEGMENTATION_OUTPUT_DIR = OUTPUTS_DIR / "segmentation"
CHURN_OUTPUT_DIR = OUTPUTS_DIR / "churn"
RECOMMENDATION_OUTPUT_DIR = OUTPUTS_DIR / "recommendations"

CHURN_MODEL_PATH = MODELS_DIR / "churn_random_forest.joblib"
SEGMENTATION_MODEL_PATH = MODELS_DIR / "kmeans_segmentation.joblib"
SCALER_PATH = MODELS_DIR / "feature_scaler.joblib"

RANDOM_STATE = 42
CHURN_INACTIVE_DAYS = 90
TOP_N_RECOMMENDATIONS = 10
N_CLUSTERS = 5

KAGGLE_DATASET = "carrie1/ecommerce-data"
KAGGLE_FALLBACK_DATASET = "paulsamuelwe/e-commerce-customer-behaviour-dataset"

for directory in [
    RAW_DATA_DIR,
    PROCESSED_DATA_DIR,
    OUTPUTS_DIR,
    DATABASE_DIR,
    MODELS_DIR,
    EDA_OUTPUT_DIR,
    RFM_OUTPUT_DIR,
    SEGMENTATION_OUTPUT_DIR,
    CHURN_OUTPUT_DIR,
    RECOMMENDATION_OUTPUT_DIR,
]:
    directory.mkdir(parents=True, exist_ok=True)
