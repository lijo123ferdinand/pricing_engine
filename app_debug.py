"""
Minimal Flask app with debug mode to see actual errors
"""
from flask import Flask, request, jsonify
import traceback
import sys

app = Flask(__name__)
from api.routes import bp as api_bp
app.register_blueprint(api_bp)

app.config['DEBUG'] = True
app.config['PROPAGATE_EXCEPTIONS'] = True

@app.route("/test", methods=["GET"])
def test():
    return jsonify({"status": "ok", "message": "Flask is working"})

@app.route("/price-suggestions", methods=["GET"])
def price_suggestions():
    try:
        sku = request.args.get('sku')
        target_price_str = request.args.get('price')
        target_price = float(target_price_str) if target_price_str else None
        print(f"\n=== Request received for SKU: {sku} ===", file=sys.stderr)
        
        if not sku:
            return jsonify({"error": "sku is required"}), 400
        
        # Try to import and use the pricing engine
        print("Importing SimpleMySQLPool...", file=sys.stderr)
        from services.db_pool import SimpleMySQLPool
        
        print("Getting pool instance...", file=sys.stderr)
        pool = SimpleMySQLPool.instance()
        
        print("Getting connection...", file=sys.stderr)
        conn = pool.get_conn()
        
        print("Connection obtained successfully", file=sys.stderr)
        
        # Try a simple query
        try:
            with conn.cursor() as cur:
                print("Executing query...", file=sys.stderr)
                cur.execute("SELECT 1 as test")
                result = cur.fetchone()
                print(f"Query result: {result}", file=sys.stderr)
        finally:
            pool.return_conn(conn)
        
        print("Importing pricing_engine...", file=sys.stderr)
        from services.pricing_engine import suggest_price_for_sku
        
        print("Creating base features...", file=sys.stderr)
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
        
        print("Calling suggest_price_for_sku...", file=sys.stderr)
        suggestion = suggest_price_for_sku(sku, base_features=base_features, vendor_id=None, grid_relative=None, steps=21, target_price=target_price)
        
        print(f"Suggestion generated: {suggestion.get('suggested_price')}", file=sys.stderr)
        
        return jsonify(suggestion)
        
    except Exception as e:
        print(f"\n=== ERROR ===", file=sys.stderr)
        print(f"Error type: {type(e).__name__}", file=sys.stderr)
        print(f"Error message: {str(e)}", file=sys.stderr)
        print(f"\nFull traceback:", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        print(f"=== END ERROR ===\n", file=sys.stderr)
        
        return jsonify({
            "error": str(e),
            "type": type(e).__name__,
            "sku": request.args.get('sku')
        }), 500

if __name__ == "__main__":
    print("\n" + "="*60)
    print("MINIMAL DEBUG SERVER")
    print("="*60)
    print("Test endpoint: http://127.0.0.1:8002/test")
    print("Price endpoint: http://127.0.0.1:8002/price-suggestions?sku=SKU_001")
    print("="*60 + "\n")
    
    app.run(host="0.0.0.0", port=8002, debug=True)
