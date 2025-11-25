"""
Direct test of pricing engine service
"""

import sys
import os
from dotenv import load_dotenv

load_dotenv()

# Test loading the demand model
from services.prediction_service import load_demand_model

try:
    print("Loading demand model...")
    model, meta = load_demand_model()
    print(f"Model loaded successfully!")
    print(f"Metadata: {meta}")
except Exception as e:
    print(f"Error loading model: {e}")
    import traceback
    traceback.print_exc()

# Test the pricing engine
from services.pricing_engine import suggest_price_for_sku

try:
    print("\nTesting pricing engine...")
    base_features = {
        'last_price': 50.0,
        'avg_price_7d': 48.0,
        'views_7d': 100,
        'addtocart_7d': 20,
        'conversion_7d': 0.05,
        'inventory_qty': 50,
        'inventory_age_days': 10,
        'promo_active': False
    }
    
    result = suggest_price_for_sku('SKU_001', base_features=base_features, vendor_id='V1')
    print(f"Success! Suggested price: ${result.get('suggested_price'):.2f}")
    print(f"Expected revenue: ${result.get('expected_revenue'):.2f}")
    
except Exception as e:
    print(f"Error in pricing engine: {e}")
    import traceback
    traceback.print_exc()
