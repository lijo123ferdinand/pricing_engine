import os
import sys
import logging
import traceback
from services.db_pool import SimpleMySQLPool
import pandas as pd
from models.train_elasticity import train_and_save_all
from models.train_demand import train_and_save
import yaml
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_training_process():
    logger.info("Running Model Training...")
    
    pool = SimpleMySQLPool.instance()
    conn = pool.get_pandas_conn()
    try:
        orders = pd.read_sql("SELECT * FROM orders WHERE order_ts >= DATE_SUB(NOW(), INTERVAL 180 DAY)", conn)
        features = pd.read_sql("SELECT * FROM features_daily", conn)
        logger.info(f"Orders shape: {orders.shape}")
        logger.info(f"Features shape: {features.shape}")
    finally:
        pool.close_pandas_conn(conn)

    if orders.empty:
        logger.warning("No orders for training.")
    else:
        logger.info("Training elasticity")
        try:
            train_and_save_all(orders)
            logger.info("Elasticity training success.")
        except Exception:
            traceback.print_exc()

    if features.empty:
        logger.warning("No features for demand model training.")
    else:
        logger.info("Training demand model")
        cfg_path = os.path.join("config", "config.yaml")
        cfg = {}
        if os.path.exists(cfg_path):
            with open(cfg_path) as f:
                 cfg = yaml.safe_load(f)['models']['demand']
        
        try:
            train_and_save(features, orders, cfg)
            logger.info("Demand training success.")
        except Exception:
            traceback.print_exc()

if __name__ == "__main__":
    run_training_process()
