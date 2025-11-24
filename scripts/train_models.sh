#!/usr/bin/env bash
set -e
python - <<'PY'
from services.db_pool import SimpleMySQLPool
import pandas as pd
from models.train_elasticity import train_and_save_all
from models.train_demand import train_and_save
import yaml, os, json

pool = SimpleMySQLPool.instance()
conn = pool.get_conn()
try:
    orders = pd.read_sql("SELECT * FROM orders WHERE order_ts >= DATE_SUB(NOW(), INTERVAL 180 DAY)", conn)
    features = pd.read_sql("SELECT * FROM features_daily", conn)
finally:
    pool.return_conn(conn)

# train elasticity
print("Training elasticity")
el_res = train_and_save_all(orders)

# train demand model
print("Training demand model")
# config - read from config file
cfg_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config", "config.yaml")
cfg = {}
if os.path.exists(cfg_path):
    cfg = yaml.safe_load(open(cfg_path))['models']['demand']
model, meta = train_and_save(features, orders, cfg)
print("Model trained:", meta)
PY
