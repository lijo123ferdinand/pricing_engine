# services/feature_store.py
"""
Feature store utilities.
Builds daily features and writes to `features_daily`.
Assumes ETL extracts raw tables to DataFrames and then transforms.
"""

from datetime import datetime, timedelta, date
import pandas as pd
from services.db_pool import SimpleMySQLPool
import logging
import json

logger = logging.getLogger(__name__)

def write_features_to_db(df: pd.DataFrame):
    """
    Write the feature DataFrame to features_daily table.
    df must match schema fields.
    """
    pool = SimpleMySQLPool.instance()
    conn = pool.get_conn()
    try:
        with conn.cursor() as cur:
            insert_sql = """
            REPLACE INTO features_daily
            (feature_date, sku, sales_7d, sales_14d, sales_30d, avg_price_7d, avg_price_14d, avg_price_30d,
             views_7d, addtocart_7d, conversion_7d, inventory_qty, inventory_age_days, promo_active, last_price)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """
            for _, row in df.iterrows():
                cur.execute(insert_sql, (
                    row['feature_date'].strftime("%Y-%m-%d"),
                    row['sku'],
                    int(row.get('sales_7d', 0)),
                    int(row.get('sales_14d', 0)),
                    int(row.get('sales_30d', 0)),
                    float(row.get('avg_price_7d') or 0.0),
                    float(row.get('avg_price_14d') or 0.0),
                    float(row.get('avg_price_30d') or 0.0),
                    int(row.get('views_7d', 0)),
                    int(row.get('addtocart_7d', 0)),
                    float(row.get('conversion_7d', 0.0)),
                    int(row.get('inventory_qty', 0)),
                    int(row.get('inventory_age_days', 0)),
                    bool(row.get('promo_active', False)),
                    float(row.get('last_price') or 0.0),
                ))
        conn.commit()
    finally:
        pool.return_conn(conn)
