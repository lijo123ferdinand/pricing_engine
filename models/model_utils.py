# models/model_utils.py
"""
Utilities for saving/loading model artifacts, versions, and metadata.
"""

import os
import json
from datetime import datetime
import joblib
from typing import Dict

def ensure_dir(path):
    os.makedirs(path, exist_ok=True)

def save_model(model, path, name, metadata: dict):
    ensure_dir(path)
    model_path = os.path.join(path, f"{name}.joblib")
    meta_path = os.path.join(path, f"{name}.meta.json")
    joblib.dump(model, model_path)
    metadata['saved_at'] = datetime.utcnow().isoformat()
    with open(meta_path, "w") as f:
        json.dump(metadata, f, indent=2)
    return model_path, meta_path

def load_model(path, name):
    model_path = os.path.join(path, f"{name}.joblib")
    meta_path = os.path.join(path, f"{name}.meta.json")
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model file not found: {model_path}")
    model = joblib.load(model_path)
    metadata = {}
    if os.path.exists(meta_path):
        with open(meta_path, "r") as f:
            metadata = json.load(f)
    return model, metadata
