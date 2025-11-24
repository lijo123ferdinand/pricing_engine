# models/train_demand.py
"""
Train demand model (LightGBM or XGBoost) to predict units given features including price.
Saves model artifact and metadata.
"""

import pandas as pd
import numpy as np
import os
from models.model_utils import save_model
import json
from datetime import datetime
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_percentage_error, mean_squared_error
import joblib

# Choose backend as lightgbm
try:
    import lightgbm as lgb
except Exception:
    lgb = None
try:
    import xgboost as xgb
except Exception:
    xgb = None

DEFAULT_PARAMS = {
    'num_boost_round': 500,
    'early_stopping_rounds': 50,
}

def prepare_training_data(features_df, orders_df):
    """
    Merge features with label (units sold next day or next period). For simplicity label = sales_7d (or 1-day ahead in production).
    Here we'll train to predict weekly units (sales_7d).
    """
    df = features_df.copy()
    # label = sales_7d
    df['label'] = df['sales_7d'].astype(float)
    # features: last_price, avg_price_7d, views_7d, addtocart_7d, conversion_7d, inventory_qty, promo_active, inventory_age_days
    feature_cols = ['last_price', 'avg_price_7d', 'views_7d', 'addtocart_7d', 'conversion_7d', 'inventory_qty', 'promo_active', 'inventory_age_days']
    # ensure types
    for c in feature_cols:
        if c in df.columns:
            df[c] = df[c].fillna(0)
    df = df.dropna(subset=['label'])
    X = df[feature_cols]
    y = df['label']
    return X, y, feature_cols

def train_lightgbm(X, y, params, model_name="demand_model", model_dir="./models_artifacts/demand"):
    import lightgbm as lgb
    X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42)
    dtrain = lgb.Dataset(X_train, label=y_train)
    dvalid = lgb.Dataset(X_val, label=y_val, reference=dtrain)
    lgb_params = {
        'objective': 'regression',
        'metric': 'l2',
        'verbosity': -1,
        'boosting_type': 'gbdt',
        'learning_rate': params.get('learning_rate', 0.05),
        'num_leaves': int(params.get('num_leaves', 31))
    }
    model = lgb.train(
        lgb_params,
        dtrain,
        num_boost_round=int(params.get('num_boost_round', 500)),
        valid_sets=[dvalid],
        early_stopping_rounds=int(params.get('early_stopping_rounds', 50)),
        verbose_eval=False
    )
    y_pred = model.predict(X_val, num_iteration=model.best_iteration)
    mape = mean_absolute_percentage_error(y_val, y_pred)
    mse = mean_squared_error(y_val, y_pred)
    meta = {
        'model_type': 'lightgbm',
        'mape': float(mape),
        'mse': float(mse),
        'trained_at': datetime.utcnow().isoformat(),
        'feature_columns': X.columns.tolist()
    }
    os.makedirs(model_dir, exist_ok=True)
    model_path, meta_path = save_model(model, model_dir, model_name, meta)
    return model, meta

def train_xgboost(X, y, params, model_name="demand_xgb", model_dir="./models_artifacts/demand"):
    import xgboost as xgb
    X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42)
    dtrain = xgb.DMatrix(X_train, label=y_train)
    dvalid = xgb.DMatrix(X_val, label=y_val)
    xgb_params = {
        'objective': 'reg:squarederror',
        'learning_rate': params.get('learning_rate', 0.05),
        'max_depth': int(params.get('max_depth', 6))
    }
    evals_result = {}
    model = xgb.train(
        xgb_params,
        dtrain,
        num_boost_round=int(params.get('num_boost_round', 500)),
        evals=[(dvalid, 'eval')],
        early_stopping_rounds=int(params.get('early_stopping_rounds', 50)),
        evals_result=evals_result,
        verbose_eval=False
    )
    y_pred = model.predict(dvalid)
    mape = mean_absolute_percentage_error(y_val, y_pred)
    mse = mean_squared_error(y_val, y_pred)
    meta = {
        'model_type': 'xgboost',
        'mape': float(mape),
        'mse': float(mse),
        'trained_at': datetime.utcnow().isoformat(),
        'feature_columns': X.columns.tolist()
    }
    os.makedirs(model_dir, exist_ok=True)
    # xgboost objects are not picklable via joblib by default; use save_model
    model_path = os.path.join(model_dir, f"{model_name}.xgb")
    model.save_model(model_path)
    with open(os.path.join(model_dir, f"{model_name}.meta.json"), "w") as f:
        json.dump(meta, f, indent=2)
    return model, meta

def train_and_save(features_df, orders_df, config):
    X, y, feature_cols = prepare_training_data(features_df, orders_df)
    model_type = config.get('model_type', 'lightgbm')
    params = config.get('params', {})
    if model_type == 'lightgbm':
        model, meta = train_lightgbm(X, y, params)
    else:
        model, meta = train_xgboost(X, y, params)
    return model, meta

if __name__ == "__main__":
    # CLI training example. This expects features_daily to be populated in DB.
    from services.db_pool import SimpleMySQLPool
    pool = SimpleMySQLPool.instance()
    conn = pool.get_conn()
    try:
        features_df = pd.read_sql("SELECT * FROM features_daily", conn)
        orders_df = pd.read_sql("SELECT * FROM orders WHERE order_ts >= DATE_SUB(NOW(), INTERVAL 90 DAY)", conn)
    finally:
        pool.return_conn(conn)

    cfg = {
        'model_type': 'lightgbm',
        'params': {
            'num_boost_round': 500,
            'early_stopping_rounds': 30,
            'learning_rate': 0.05,
            'num_leaves': 31
        }
    }
    model, meta = train_and_save(features_df, orders_df, cfg)
    print("Trained model metadata:", meta)
