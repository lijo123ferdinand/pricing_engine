"""
API Test Script for Dynamic Pricing Engine
Tests the price suggestions endpoint
Run this after starting the server with: python app_debug.py
"""

import requests
import json

BASE_URL = "http://127.0.0.1:8002"

print("=" * 60)
print("Dynamic Pricing Engine API Test (Port 8002)")
print("=" * 60)

# Test price suggestion
print("\nGET /price-suggestions?sku=SKU_001")
print("-" * 60)

try:
    response = requests.get(
        f"{BASE_URL}/price-suggestions",
        params={'sku': 'SKU_001', 'vendor_id': 'V1'}
    )
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print("\nSUCCESS! API is working!")
        print("\nKey Results:")
        print(f"  SKU: {data.get('sku')}")
        print(f"  Current Price: ${data.get('current_price', 0):.2f}")
        print(f"  Suggested Price: ${data.get('suggested_price', 0):.2f}")
        print(f"  Expected Revenue: ${data.get('expected_revenue', 0):.2f}")
        print(f"  Expected Units: {data.get('expected_units', 0):.1f}")
        print(f"  Model Version: {data.get('model_version')}")
        print(f"  Elasticity: {data.get('elasticity')}")
        print(f"  Number of Candidates: {len(data.get('candidates', []))}")
    else:
        print(f"ERROR: {response.text[:200]}")

except requests.exceptions.ConnectionError:
    print("ERROR: Could not connect to server")
    print("\nStart the server with:")
    print("  python app_debug.py")
except Exception as e:
    print(f"ERROR: {e}")

print("\n" + "=" * 60)
print("Test Complete")
print("=" * 60)
