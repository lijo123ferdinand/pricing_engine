#!/usr/bin/env bash
set -e
# Simple orchestrator to run ETL (extract, transform, load)
python - <<'PY'
from etl.extract import fetch_orders, fetch_inventory_snapshot, fetch_product_analytics, fetch_promotions
from etl.transform import build_features
from etl.load import load_features
from datetime import date
orders = fetch_orders(since_days=90)
inventory = fetch_inventory_snapshot(latest_only=True)
analytics = fetch_product_analytics(since_days=90)
promos = fetch_promotions()
features = build_features(orders, inventory, analytics, promos, as_of_date=date.today())
print("Features built:", features.shape)
load_features(features)
print("Features loaded into DB")
PY
