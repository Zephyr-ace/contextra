"""Configuration settings for GDELT analysis pipeline."""

import os
from datetime import datetime, timedelta
from typing import Dict, List

PROJECT_ID = "gdelt-bq"
DATASET_ID = "gdeltv2"

TABLES = {
    "events": "events",
    "mentions": "mentions", 
    "gkg": "gkg_partitioned"
}

DATA_DIR = "data"
CACHE_DIR = os.path.join(DATA_DIR, "cache")
EXPORT_DIR = os.path.join(DATA_DIR, "exports")

COMPANY_MAPPINGS = {
    "apple": [
        "Apple Inc",
        "Apple Computer", 
        "AAPL",
        "iPhone",
        "iPad",
        "Mac",
        "iTunes",
        "App Store"
    ],
    "google": [
        "Google",
        "Alphabet Inc",
        "GOOGL",
        "GOOG", 
        "YouTube",
        "Android",
        "Chrome",
        "Gmail",
        "Google Cloud"
    ]
}

DAYS_LOOKBACK = 90

def get_date_range():
    """Get date range for last 90 days."""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=DAYS_LOOKBACK)
    return start_date.strftime("%Y%m%d"), end_date.strftime("%Y%m%d")

def ensure_directories():
    """Create necessary directories if they don't exist."""
    os.makedirs(CACHE_DIR, exist_ok=True)
    os.makedirs(EXPORT_DIR, exist_ok=True)
    os.makedirs("vizuals/plots", exist_ok=True)
    os.makedirs("vizuals/graphs", exist_ok=True)