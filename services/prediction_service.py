# services/prediction_service.py
"""
Load model and produce predictions for candidate prices.
This module is used by pricing_engine and API.
"""

import os
import numpy as np
import pandas as pd
from models.model_utils import load_model
from typing import Dict, Any
from loguru import logger

DEFAULT_DEMAND_MODEL_DIR = os.getenv("DEMAND_MODEL_DIR", "./models_artifacts/demand")
DEFAULT_ELASTICITY_DIR = os.getenv("ELASTICITY_MODEL_DIR", "./models_artifacts/elasticity")

def load_demand_model(model_dir=DEFAULT_DEMAND_MODEL_DIR, model_name="demand_model"):
    model, meta = load_model(model_dir, model_name)
    return model, meta

def predict_units_for_prices(model, meta, base_features: Dict[str, Any], candidate_prices: list):
    """
    base_features: dict of feature_name -> value (includes last_price etc.)
    candidate_prices: list of floats to test
    Returns DataFrame with columns: price, predicted_units
    """
    feature_cols = meta.get('feature_columns', None)
    if feature_cols is None:
        raise ValueError("Model metadata must contain 'feature_columns' list")
    rows = []
    for p in candidate_prices:
        feat = base_features.copy()
        # set price features; we assume model uses last_price/avg_price_7d fields; set last_price = tested price
        if 'last_price' in feat:
            feat['last_price'] = p
        if 'avg_price_7d' in feat:
            # for simple approach, scale average by relative change
            feat['avg_price_7d'] = feat.get('avg_price_7d', p)
        # Keep other fields as-is, fill zeros for missing
        X_row = [feat.get(c, 0.0) for c in feature_cols]
        rows.append(X_row)
    X = pd.DataFrame(rows, columns=feature_cols)
    # Model might be LightGBM or sklearn wrapper
    try:
        preds = model.predict(X)
    except Exception as e:
        # Try joblib loaded raw LightGBM model with predict
        logger.exception("Model predict failed")
        preds = model.predict(X)
    df = pd.DataFrame({'price': candidate_prices, 'predicted_units': np.maximum(preds, 0.0)})
    return df
