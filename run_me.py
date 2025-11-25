#!/usr/bin/env python
"""
RUN ME - Quick Start Script for Dynamic Pricing Engine

This script starts the API server on port 8002.
After running this, test with: python test_final.py
"""

import subprocess
import sys
import os

def main():
    print("\n" + "="*70)
    print("  DYNAMIC PRICING ENGINE - QUICK START")
    print("="*70)
    print("\nStarting the API server...")
    print("\nOnce started, you can:")
    print("  1. Test with: python test_final.py")
    print("  2. Use API at: http://127.0.0.1:8002/price-suggestions?sku=SKU_001")
    print("  3. Stop with: CTRL+C")
    print("\n" + "="*70 + "\n")
    
    # Start the server
    try:
        subprocess.run([sys.executable, "app_debug.py"])
    except KeyboardInterrupt:
        print("\n\nServer stopped.")
        print("To restart, run: python run_me.py")

if __name__ == "__main__":
    main()
