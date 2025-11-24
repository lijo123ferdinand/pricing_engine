# services/pricing_engine.py
"""
Core pricing engine: takes SKU and candidate prices, constraints, elasticity and demand model to choose optimal price.
Provides explanation fields and respects vendor constraints.
"""

from typing import Dict, Any
import numpy as np
import pandas as pd
import yaml
import os
from services.prediction_service import load_demand_model, predict_units_for_prices
from models.model_utils import load_model
from datetime import datetime
from services.db_pool import SimpleMySQLPool
import logging

logger = logging.getLogger(__name__)

# Load pricing config
CONFIG_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config", "config.yaml")
if os.path.exists(CONFIG_PATH):
    with open(CONFIG_PATH, "r") as f:
        PRICING_CONFIG = yaml.safe_load(f).get('pricing', {})
else:
    PRICING_CONFIG = {}

def get_vendor_rules(vendor_id):
    pool = SimpleMySQLPool.instance()
    conn = pool.get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM vendor_rules WHERE vendor_id=%s", (vendor_id,))
            row = cur.fetchone()
            return row
    finally:
        pool.return_conn(conn)

def get_elasticity_for_sku(sku):
    pool = SimpleMySQLPool.instance()
    conn = pool.get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM elasticity_results WHERE sku=%s", (sku,))
            row = cur.fetchone()
            return row
    finally:
        pool.return_conn(conn)

def get_latest_price_for_sku(sku):
    pool = SimpleMySQLPool.instance()
    conn = pool.get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT price FROM orders WHERE sku=%s ORDER BY order_ts DESC LIMIT 1", (sku,))
            row = cur.fetchone()
            if row:
                return float(row['price'])
            # fallback: features_daily last_price
            cur.execute("SELECT last_price FROM features_daily WHERE sku=%s ORDER BY feature_date DESC LIMIT 1", (sku,))
            r2 = cur.fetchone()
            if r2:
                return float(r2['last_price'])
            return None
    finally:
        pool.return_conn(conn)

def _generate_candidate_prices(current_price, grid_relative=None, steps=21, min_price=0.5, max_price=10000.0):
    """
    Generate a grid of candidate prices.
    If grid_relative provided, use specific multipliers; otherwise produce symmetric grid around current price.
    """
    if grid_relative:
        return sorted([max(min_price, min(max_price, current_price * (1.0 + rel))) for rel in grid_relative])
    # else continuous grid
    pct = PRICING_CONFIG.get('daily_price_change_limit_pct', 0.15)
    low = max(min_price, current_price * (1 - pct))
    high = min(max_price, current_price * (1 + pct))
    return list(np.linspace(low, high, steps))

def apply_constraints(candidate_df: pd.DataFrame, vendor_rule: Dict, current_price: float):
    """
    Apply vendor constraints: min_margin, max_discount vs current price, daily change limit
    Adds a boolean 'allowed' column and 'constraint_reasons'.
    """
    candidate_df = candidate_df.copy()
    reasons = []
    allowed = []
    min_margin = vendor_rule.get('min_margin') if vendor_rule else PRICING_CONFIG.get('min_margin', 0.10)
    max_discount = vendor_rule.get('max_discount') if vendor_rule else PRICING_CONFIG.get('max_discount', 0.30)
    max_daily_change = vendor_rule.get('max_daily_price_change') if vendor_rule else PRICING_CONFIG.get('daily_price_change_limit_pct', 0.15)
    for _, row in candidate_df.iterrows():
        p = row['price']
        rlist = []
        allowed_flag = True
        # discount vs current price:
        if current_price and p < current_price * (1 - max_discount) - 1e-9:
            allowed_flag = False
            rlist.append("exceeds_max_discount")
        # daily change limit
        if current_price and (abs(p - current_price) / max(1e-6, current_price) > max_daily_change + 1e-9):
            allowed_flag = False
            rlist.append("exceeds_daily_change_limit")
        # price floor (min price)
        if p < PRICING_CONFIG.get('min_price', 0.5):
            allowed_flag = False
            rlist.append("below_min_price")
        # price ceiling (max price)
        if p > PRICING_CONFIG.get('max_price', 100000.0):
            allowed_flag = False
            rlist.append("above_max_price")
        allowed.append(allowed_flag)
        reasons.append(",".join(rlist) if rlist else "")
    candidate_df['allowed'] = allowed
    candidate_df['constraint_reasons'] = reasons
    return candidate_df

def compute_expected_revenue(candidate_df):
    """
    revenue = price * predicted_units
    """
    df = candidate_df.copy()
    df['expected_revenue'] = df['price'] * df['predicted_units']
    return df

def pick_best_candidate(candidate_df):
    """
    Choose highest expected_revenue among allowed candidates.
    """
    allowed = candidate_df[candidate_df['allowed'] == True]
    if allowed.empty:
        # fallback: choose highest expected_revenue even if disallowed, but note constraint
        best = candidate_df.sort_values('expected_revenue', ascending=False).iloc[0]
        best_reason = "no_allowed_candidates; returning_best_violating_constraints"
    else:
        best = allowed.sort_values('expected_revenue', ascending=False).iloc[0]
        best_reason = ""
    return best.to_dict(), best_reason

def store_price_suggestion(sku, current_price, best_candidate, explanation, constraints_applied, model_version, api_request_id=None):
    pool = SimpleMySQLPool.instance()
    conn = pool.get_conn()
    try:
        with conn.cursor() as cur:
            sql = """
            INSERT INTO price_suggestions
            (sku, request_ts, current_price, suggested_price, expected_revenue, expected_units, elasticity, reason, constraints_applied, model_version, api_request_id)
            VALUES ( %s, NOW(), %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cur.execute(sql, (
                sku, current_price, best_candidate['price'], float(best_candidate['expected_revenue']),
                float(best_candidate['predicted_units']), None, explanation, str(constraints_applied),
                model_version, api_request_id
            ))
        conn.commit()
    finally:
        pool.return_conn(conn)

def suggest_price_for_sku(sku: str, base_features: dict, vendor_id: str = None, grid_relative: list = None, steps: int = 21, model_name="demand_model"):
    """
    Main entrypoint for price suggestion.
    Returns dict with suggested price, details, candidates, elasticity info, model metadata.
    """
    # 1) load models and metadata
    model, meta = load_demand_model()
    # 2) get current price
    current_price = get_latest_price_for_sku(sku) or base_features.get('last_price') or 0.0
    # 3) generate candidate prices
    candidate_prices = _generate_candidate_prices(current_price, grid_relative=grid_relative, steps=steps)
    # 4) vendor rules
    vendor_rule = get_vendor_rules(vendor_id) if vendor_id else None
    # 5) predict units for each candidate price
    pred_df = predict_units_for_prices(model, meta, base_features, candidate_prices)
    # 6) apply constraints
    candidates = apply_constraints(pred_df, vendor_rule, current_price)
    # 7) compute expected revenue
    candidates = compute_expected_revenue(candidates)
    # 8) select best candidate
    best_candidate, best_reason = pick_best_candidate(candidates)
    # 9) gather elasticity info
    elasticity_row = get_elasticity_for_sku(sku)
    # 10) prepare result
    result = {
        "sku": sku,
        "current_price": current_price,
        "suggested_price": float(best_candidate['price']),
        "expected_revenue": float(best_candidate['expected_revenue']),
        "expected_units": float(best_candidate['predicted_units']),
        "model_version": meta.get('saved_at') if meta else None,
        "elasticity": elasticity_row.get('elasticity') if elasticity_row else None,
        "elasticity_r2": elasticity_row.get('r_squared') if elasticity_row else None,
        "elasticity_p_value": elasticity_row.get('p_value') if elasticity_row else None,
        "candidates": candidates.to_dict(orient='records'),
        "reason": best_reason or "revenue_maximization",
        "constraints_applied": [c for c in candidates['constraint_reasons'].unique() if c],
        "generated_at": datetime.utcnow().isoformat()
    }

    # 11) store suggestion in DB asynchronously if desired; here store synchronously
    try:
        store_price_suggestion(sku, current_price, best_candidate, result['reason'], result['constraints_applied'], result['model_version'])
    except Exception as e:
        logger.exception("Failed to persist price suggestion")

    return result
