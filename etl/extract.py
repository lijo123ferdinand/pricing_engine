# etl/extract.py
"""
ETL extract module: read raw tables from MySQL and return pandas DataFrames.
"""

from services.db_pool import SimpleMySQLPool
import pandas as pd
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

def fetch_orders(since_days=60):
    pool = SimpleMySQLPool.instance()
    conn = pool.get_conn()
    try:
        sql = f"SELECT * FROM orders WHERE order_ts >= DATE_SUB(NOW(), INTERVAL {since_days} DAY)"
        df = pd.read_sql(sql, conn)
        return df
    finally:
        pool.return_conn(conn)

def fetch_inventory_snapshot(latest_only=True):
    pool = SimpleMySQLPool.instance()
    conn = pool.get_conn()
    try:
        if latest_only:
            sql = """
            SELECT i1.* FROM inventory i1
            JOIN (
                SELECT sku, MAX(snapshot_ts) as mx FROM inventory GROUP BY sku
            ) i2 ON i1.sku = i2.sku AND i1.snapshot_ts = i2.mx
            """
            df = pd.read_sql(sql, conn)
        else:
            df = pd.read_sql("SELECT * FROM inventory", conn)
        return df
    finally:
        pool.return_conn(conn)

def fetch_product_analytics(since_days=60):
    pool = SimpleMySQLPool.instance()
    conn = pool.get_conn()
    try:
        sql = f"SELECT * FROM product_analytics WHERE event_ts >= DATE_SUB(NOW(), INTERVAL {since_days} DAY)"
        df = pd.read_sql(sql, conn)
        return df
    finally:
        pool.return_conn(conn)

def fetch_promotions():
    pool = SimpleMySQLPool.instance()
    conn = pool.get_conn()
    try:
        df = pd.read_sql("SELECT * FROM promotions", conn)
        return df
    finally:
        pool.return_conn(conn)
