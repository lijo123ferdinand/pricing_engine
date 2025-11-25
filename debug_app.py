"""
Debug Flask API issue
"""
import sys
from flask import Flask, request
from api.utils import json_response, make_api_request_id
from services.pricing_engine import suggest_price_for_sku
from services.db_pool import SimpleMySQLPool
import traceback

app = Flask(__name__)

@app.route("/price-suggestions", methods=["GET"])
def price_suggestions():
    try:
        sku = request.args.get('sku')
        vendor_id = request.args.get('vendor_id')
        
        print(f"Request: sku={sku}, vendor_id={vendor_id}")
        
        if not sku:
            return json_response({"error": "sku is required"}, status=400)

        # Fetch features from database
        pool = SimpleMySQLPool.instance()
        conn = pool.get_conn()
        base_features = {}
        
        try:
            with conn.cursor() as cur:
                print("Executing query...")
                cur.execute("SELECT * FROM features_daily WHERE sku=%s ORDER BY feature_date DESC LIMIT 1", (sku,))
                row = cur.fetchone()
                print(f"Row fetched: {row}")
                
                if row:
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
                    print(f"Base features: {base_features}")
                else:
                    print("No features found, using defaults")
                    base_features = {
                        'last_price': 50.0,
                        'avg_price_7d': 50.0,
                        'views_7d': 100,
                        'addtocart_7d': 10,
                        'conversion_7d': 0.1,
                        'inventory_qty': 50,
                        'inventory_age_days': 5,
                        'promo_active': False,
                    }
        finally:
            pool.return_conn(conn)

        print("Calling pricing engine...")
        api_request_id = make_api_request_id()
        suggestion = suggest_price_for_sku(sku, base_features=base_features, vendor_id=vendor_id, grid_relative=None, steps=21)
        suggestion['api_request_id'] = api_request_id
        
        print(f"Suggestion: {suggestion}")
        return json_response(suggestion)
        
    except Exception as e:
        print(f"ERROR: {e}")
        traceback.print_exc()
        return json_response({"error": str(e)}, status=500)

if __name__ == "__main__":
    print("=== ROUTES LOADED ===")
    print(app.url_map)
    print("======================")
    app.run(host="0.0.0.0", port=8002, debug=True)
