import os
import sys
import logging
import traceback
from etl.extract import fetch_orders, fetch_inventory_snapshot, fetch_product_analytics, fetch_promotions
from etl.transform import build_features
from etl.load import load_features
from datetime import date
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_etl_process():
    logger.info("Running ETL...")
    
    try:
        orders = fetch_orders(since_days=90)
        logger.info(f"Orders: {orders.shape}")
        logger.info(orders.dtypes)
        logger.info(orders.head())

        
        inventory = fetch_inventory_snapshot(latest_only=True)
        logger.info(f"Inventory: {inventory.shape}")
        
        analytics = fetch_product_analytics(since_days=90)
        logger.info(f"Analytics: {analytics.shape}")
        
        promos = fetch_promotions()
        logger.info(f"Promos: {promos.shape}")
        
        features = build_features(orders, inventory, analytics, promos, as_of_date=date.today())
        logger.info(f"Features built: {features.shape}")
        logger.info(features.head())
        
        if not features.empty:
            load_features(features)
            logger.info("Features loaded into DB")
        else:
            logger.warning("No features to load.")
            
    except Exception:
        traceback.print_exc()

if __name__ == "__main__":
    run_etl_process()
