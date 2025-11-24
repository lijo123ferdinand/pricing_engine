# models/train_elasticity.py
"""
Train per-SKU elasticity using log-log OLS (statsmodels).
Saves results into elasticity_results table.
"""

import pandas as pd
import numpy as np
import statsmodels.api as sm
from services.db_pool import SimpleMySQLPool
from datetime import datetime
from models.model_utils import save_model
import os
import json

def compute_elasticity_for_sku(orders_df, sku, min_sales_threshold=20):
    """
    Uses aggregated daily sales per sku to fit: log(q) ~ log(price) + controls
    Returns: elasticity (coefficient), r_squared, p_value, sample_size
    """
    df = orders_df[orders_df['sku'] == sku].copy()
    if df.empty:
        return None

    # Aggregate at daily level
    df['order_date'] = pd.to_datetime(df['order_ts']).dt.date
    daily = df.groupby('order_date').agg({
        'quantity': 'sum',
        'price': lambda s: (s * df.loc[s.index, 'quantity']).sum() / s.sum() if s.sum() > 0 else np.nan
    }).rename(columns={'quantity': 'q', 'price': 'price'}).reset_index()
    daily = daily.dropna()
    if daily['q'].sum() < min_sales_threshold or daily.shape[0] < 5:
        return None

    # log transform, add small eps
    eps = 1e-6
    daily['log_q'] = np.log(daily['q'] + eps)
    daily['log_price'] = np.log(daily['price'] + eps)

    X = sm.add_constant(daily[['log_price']])
    y = daily['log_q']

    model = sm.OLS(y, X).fit()
    coef = float(model.params.get('log_price', np.nan))
    pval = float(model.pvalues.get('log_price', np.nan))
    r2 = float(model.rsquared)
    sample_size = len(daily)

    return dict(elasticity=coef, r_squared=r2, p_value=pval, sample_size=sample_size, model_summary=model.summary().as_text())

def persist_elasticity_results(results):
    """
    results: list of dict with keys sku, elasticity, r_squared, p_value, sample_size
    """
    pool = SimpleMySQLPool.instance()
    conn = pool.get_conn()
    try:
        with conn.cursor() as cur:
            for r in results:
                sql = """
                REPLACE INTO elasticity_results (sku, elasticity, r_squared, p_value, sample_size, last_computed)
                VALUES (%s,%s,%s,%s,%s,NOW())
                """
                cur.execute(sql, (r['sku'], r['elasticity'], r['r_squared'], r['p_value'], r['sample_size']))
        conn.commit()
    finally:
        pool.return_conn(conn)

def train_and_save_all(orders_df, output_dir="./models_artifacts/elasticity", min_sales_threshold=20):
    skus = orders_df['sku'].unique()
    results = []
    for sku in skus:
        try:
            res = compute_elasticity_for_sku(orders_df, sku, min_sales_threshold=min_sales_threshold)
            if res:
                res['sku'] = sku
                results.append(res)
        except Exception as e:
            print(f"Elasticity compute error for {sku}: {e}")

    persist_elasticity_results(results)
    # Optionally save a summary file
    os.makedirs(output_dir, exist_ok=True)
    with open(os.path.join(output_dir, "elasticity_summary.json"), "w") as f:
        json.dump(results, f, indent=2)
    return results

if __name__ == "__main__":
    # simple CLI runner for local training
    pool = SimpleMySQLPool.instance()
    conn = pool.get_conn()
    try:
        orders_df = pd.read_sql("SELECT * FROM orders", conn)
    finally:
        pool.return_conn(conn)
    res = train_and_save_all(orders_df)
    print("Elasticity results saved:", len(res))
