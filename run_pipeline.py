#!/usr/bin/env python
"""CLI entry point for CommerceIntel Analytics Platform."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.pipeline import run_full_pipeline  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(
        description="CommerceIntel Analytics Platform - End-to-End Pipeline"
    )
    parser.add_argument(
        "--download",
        action="store_true",
        help="Download dataset from Kaggle before processing",
    )
    args = parser.parse_args()

    report = run_full_pipeline(download=args.download)
    print("Pipeline completed successfully.")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
