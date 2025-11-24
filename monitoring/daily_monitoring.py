# monitoring/daily_monitoring.py
"""
Daily monitoring script:
- Compute model MAPE on holdout or last-day data
- Elasticity drift: compare current elasticity stored vs computed this run
- Coverage: fraction of SKUs with elasticity
Stores results in monitoring_metrics
"""

import pandas as pd
from services.db_pool import SimpleMySQLPool
from datetime import datetime, timedelta
from sklearn.metrics import mean_absolute_percentage_error
import json
import logging

logger = logging.getLogger(__name__)

def compute_mape_for_model(model_meta):
    # For simplicity, compute MAPE using demand_predictions vs actual recent sales (join on sku)
    pool = SimpleMySQLPool.instance()
    conn = pool.get_conn()
    try:
        preds = pd.read_sql("SELECT sku, pred_ts, predicted_units FROM demand_predictions WHERE pred_ts >= DATE_SUB(NOW(), INTERVAL 7 DAY)", conn)
        if preds.empty:
            return None
        # Aggregate predicted units by sku
        preds_agg = preds.groupby('sku')['predicted_units'].sum().reset_index()
        actual = pd.read_sql("SELECT sku, SUM(quantity) as actual_units FROM orders WHERE order_ts >= DATE_SUB(NOW(), INTERVAL 7 DAY) GROUP BY sku", conn)
        df = preds_agg.merge(actual, on='sku', how='left').fillna(0)
        mape = mean_absolute_percentage_error(df['actual_units'], df['predicted_units'])
        return mape, df
    finally:
        pool.return_conn(conn)

def compute_elasticity_coverage():
    pool = SimpleMySQLPool.instance()
    conn = pool.get_conn()
    try:
        total_skus = pd.read_sql("SELECT COUNT(DISTINCT sku) as c FROM features_daily", conn).iloc[0]['c']
        with_elasticity = pd.read_sql("SELECT COUNT(*) as c FROM elasticity_results", conn).iloc[0]['c']
        coverage = float(with_elasticity)/float(total_skus or 1.0)
        return coverage, int(total_skus), int(with_elasticity)
    finally:
        pool.return_conn(conn)

def store_metric(metric_name, sku, value, details=None):
    pool = SimpleMySQLPool.instance()
    conn = pool.get_conn()
    try:
        with conn.cursor() as cur:
            sql = "INSERT INTO monitoring_metrics (metric_date, metric_name, sku, metric_value, details) VALUES (CURDATE(), %s, %s, %s, %s)"
            cur.execute(sql, (metric_name, sku, float(value) if value is not None else None, json.dumps(details) if details else None))
        conn.commit()
    finally:
        pool.return_conn(conn)

def run_daily_monitoring():
    # compute mape
    mape_res = compute_mape_for_model(None)
    if mape_res:
        mape, df = mape_res
        store_metric("demand_model_map e_7d", None, mape, {"rows": len(df)})
    coverage, total, with_elas = compute_elasticity_coverage()
    store_metric("elasticity_coverage", None, coverage, {"total_skus": total, "with_elasticity": with_elas})
    # Additional checks can be added: elasticity drift, feature coverage
    logger.info("Monitoring done - MAPE: %s, Elasticity coverage: %.2f", mape_res[0] if mape_res else None, coverage)

if __name__ == "__main__":
    run_daily_monitoring()
