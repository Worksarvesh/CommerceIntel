"""Data loading utilities."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pandas as pd

from src.config import KAGGLE_DATASET, RAW_DATA_DIR, RAW_DATA_FILE


def download_kaggle_dataset(
    dataset_slug: str = KAGGLE_DATASET,
    output_dir: Path = RAW_DATA_DIR,
) -> Path:
    """Download dataset from Kaggle using the Kaggle CLI."""
    output_dir.mkdir(parents=True, exist_ok=True)
    cmd = [
        sys.executable,
        "-m",
        "kaggle",
        "datasets",
        "download",
        "-d",
        dataset_slug,
        "-p",
        str(output_dir),
        "--unzip",
    ]
    subprocess.run(cmd, check=True)
    return output_dir


def load_raw_transactions(path: Path = RAW_DATA_FILE) -> pd.DataFrame:
    """Load raw Online Retail CSV data."""
    if not path.exists():
        raise FileNotFoundError(
            f"Raw data not found at {path}. Run `python run_pipeline.py --download` first."
        )
    return pd.read_csv(path, encoding="latin-1")


def load_processed_transactions(path: Path | None = None) -> pd.DataFrame:
    """Load cleaned transaction data."""
    from src.config import PROCESSED_TRANSACTIONS_FILE

    file_path = path or PROCESSED_TRANSACTIONS_FILE
    if not file_path.exists():
        raise FileNotFoundError(
            f"Processed data not found at {file_path}. Run the pipeline first."
        )
    df = pd.read_csv(file_path, parse_dates=["invoice_date"])
    return df
