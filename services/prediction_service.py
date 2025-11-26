# services/prediction_service.py
"""
Load model and produce predictions for candidate prices.
This module is used by pricing_engine and API.
"""

import os
import sys
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
        if 'last_price' in feat:
            feat['last_price'] = p
        if 'avg_price_7d' in feat:
            feat['avg_price_7d'] = p
        X_row = [feat.get(c, 0.0) for c in feature_cols]
        rows.append(X_row)
    X = pd.DataFrame(rows, columns=feature_cols)
    try:
        preds = model.predict(X)
    except Exception as e:
        print(f"ERROR: Model predict failed: {e}", file=sys.stderr)
        preds = model.predict(X)
    
    df = pd.DataFrame({'price': candidate_prices, 'predicted_units': np.maximum(preds, 0.0)})

    std_dev = df['predicted_units'].std()
    print(f"DEBUG: Prediction std dev: {std_dev}", file=sys.stderr)
    
    if std_dev < 1e-6:
        current_price = base_features.get('last_price')
        base_units = df['predicted_units'].mean()
        print(f"DEBUG: Fallback triggered. Current price: {current_price}, Base units: {base_units}", file=sys.stderr)
        
        if current_price and current_price > 0 and base_units > 0:
            elasticity = -2.0
            prices = df['price'].values
            adjusted_units = base_units * (prices / current_price) ** elasticity
            df['predicted_units'] = np.maximum(adjusted_units, 0.0)
            print(f"DEBUG: Applied heuristic elasticity {elasticity}", file=sys.stderr)
        else:
            print("DEBUG: Fallback skipped", file=sys.stderr)

    return df
