# services/feedback_service.py
"""
Handle incoming feedback from vendors about suggested prices.
"""

from services.db_pool import SimpleMySQLPool
from datetime import datetime
import json
import logging

logger = logging.getLogger(__name__)

def save_feedback(payload: dict):
    """
    payload:
    {
        'suggestion_id': int,
        'sku': str,
        'vendor_id': str,
        'accepted': bool,
        'new_price': float,
        'note': str
    }
    """
    pool = SimpleMySQLPool.instance()
    conn = pool.get_conn()
    try:
        with conn.cursor() as cur:
            sql = """
            INSERT INTO vendor_feedback (suggestion_id, sku, vendor_id, feedback_ts, accepted, new_price, note)
            VALUES (%s,%s,%s,NOW(),%s,%s,%s)
            """
            cur.execute(sql, (
                payload.get('suggestion_id'),
                payload.get('sku'),
                payload.get('vendor_id'),
                bool(payload.get('accepted', False)),
                payload.get('new_price'),
                payload.get('note')
            ))
        conn.commit()
    finally:
        pool.return_conn(conn)
    logger.info("Saved feedback for sku %s", payload.get('sku'))
