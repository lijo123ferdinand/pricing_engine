# api/routes.py
"""
Flask routes for pricing engine
"""
from flask import Blueprint, request, current_app
from api.utils import json_response, make_api_request_id
from services.pricing_engine import suggest_price_for_sku
from services.feedback_service import save_feedback
import logging
from datetime import datetime

bp = Blueprint('pricing', __name__)
logger = logging.getLogger(__name__)

@bp.route("/price-suggestions", methods=["GET"])
def price_suggestions():
    """
    GET /price-suggestions?sku=SKU-A&vendor_id=vendor_1
    Returns JSON with suggestion and full metadata.
    """
    sku = request.args.get('sku')
    vendor_id = request.args.get('vendor_id')
    if not sku:
        return json_response({"error": "sku is required"}, status=400)

    # Ideally we'd fetch base features from feature store; for simplicity we fetch last features:
    from services.db_pool import SimpleMySQLPool
    pool = SimpleMySQLPool.instance()
    conn = pool.get_conn()
    base_features = {}
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM features_daily WHERE sku=%s ORDER BY feature_date DESC LIMIT 1", (sku,))
            row = cur.fetchone()
            if row:
                # Convert row to base_features dict
                base_features = {
                    'last_price': float(row.get('last_price') or 0.0),
                    'avg_price_7d': float(row.get('avg_price_7d') or 0.0),
                    'views_7d': int(row.get('views_7d') or 0),
                    'addtocart_7d': int(row.get('addtocart_7d') or 0),
                    'conversion_7d': float(row.get('conversion_7d') or 0.0),
                    'inventory_qty': int(row.get('inventory_qty') or 0),
                    'inventory_age_days': int(row.get('inventory_age_days') or 0),
                    'promo_active': bool(row.get('promo_active') or False),
                }
    finally:
        pool.return_conn(conn)

    api_request_id = make_api_request_id()
    suggestion = suggest_price_for_sku(sku, base_features=base_features, vendor_id=vendor_id, grid_relative=None, steps=21)
    suggestion['api_request_id'] = api_request_id

    # Log API call in DB (api_logs)
    try:
        with pool.get_conn().cursor() as cur:
            sql = "INSERT INTO api_logs (endpoint, request_ts, request_body, response_body, latency_ms) VALUES (%s, NOW(), %s, %s, %s)"
            cur.execute(sql, ("/price-suggestions", str({'sku': sku, 'vendor_id': vendor_id}), str(suggestion), 0))
            pool.get_conn().commit()
    except Exception:
        pass

    return json_response(suggestion)

@bp.route("/price-feedback", methods=["POST"])
def price_feedback():
    """
    POST /price-feedback
    Body JSON:
    {
        suggestion_id: int,
        sku: str,
        vendor_id: str,
        accepted: bool,
        new_price: float,
        note: str
    }
    """
    payload = request.get_json(force=True)
    if not payload or 'sku' not in payload:
        return json_response({"error": "sku is required in payload"}, status=400)
    # Save feedback
    save_feedback(payload)
    return json_response({"status": "ok", "received_at": datetime.utcnow().isoformat()})
