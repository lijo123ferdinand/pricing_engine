"""
Complete Startup Script for Dynamic Pricing Engine
Handles all setup, seeding, ETL, training, and server startup
"""

import os
import sys
import time
import subprocess
import shutil
import logging
import random
from datetime import datetime, timedelta

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_dependencies():
    """Check if all required packages are installed"""
    logger.info("Checking dependencies...")
    try:
        import pymysql
        import pandas
        import flask
        import dotenv
        import lightgbm
        import sklearn
        logger.info("All dependencies are installed.")
        return True
    except ImportError as e:
        logger.error(f"Missing dependency: {e}")
        logger.info("Installing dependencies from requirements.txt...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        return True

def setup_env():
    """Setup environment variables"""
    if not os.path.exists(".env"):
        if os.path.exists("config/.env.example"):
            shutil.copy("config/.env.example", ".env")
            logger.info("Created .env from config/.env.example")
    
    from dotenv import load_dotenv
    load_dotenv()

def wait_for_db(retries=30, delay=2):
    """Wait for MySQL database to be available"""
    import pymysql
    
    host = os.getenv("DB_HOST", "127.0.0.1")
    port = int(os.getenv("DB_PORT", 3306))
    user = os.getenv("DB_USER", "root")
    password = os.getenv("DB_PASSWORD", "thbs123!")
    
    logger.info(f"Connecting to MySQL at {host}:{port}...")
    
    for i in range(retries):
        try:
            conn = pymysql.connect(host=host, port=port, user=user, password=password)
            conn.close()
            logger.info("Database connection successful.")
            return True
        except pymysql.MySQLError as e:
            logger.info(f"Waiting for database... (attempt {i+1}/{retries})")
            time.sleep(delay)
    
    return False

def init_db():
    """Initialize database schema"""
    import pymysql
    
    host = os.getenv("DB_HOST", "127.0.0.1")
    port = int(os.getenv("DB_PORT", 3306))
    user = os.getenv("DB_USER", "root")
    password = os.getenv("DB_PASSWORD", "thbs123!")
    db_name = os.getenv("DB_NAME", "pricing_db")
    
    conn = pymysql.connect(host=host, port=port, user=user, password=password)
    try:
        with conn.cursor() as cursor:
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
            cursor.execute(f"USE {db_name}")
            
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            if not tables:
                logger.info("Initializing schema...")
                with open("db/schema.sql", "r") as f:
                    schema = f.read()
                    statements = schema.split(';')
                    for stmt in statements:
                        if stmt.strip():
                            cursor.execute(stmt)
                logger.info("Schema initialized.")
                return True
            else:
                logger.info("Tables already exist.")
                return False
    finally:
        conn.close()

def seed_db():
    """Seed database with sample data"""
    import pymysql
    
    host = os.getenv("DB_HOST", "127.0.0.1")
    port = int(os.getenv("DB_PORT", 3306))
    user = os.getenv("DB_USER", "root")
    password = os.getenv("DB_PASSWORD", "thbs123!")
    db_name = os.getenv("DB_NAME", "pricing_db")
    
    conn = pymysql.connect(host=host, port=port, user=user, password=password, database=db_name, 
                          autocommit=True, cursorclass=pymysql.cursors.DictCursor)
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) as cnt FROM orders")
            res = cursor.fetchone()
            if res['cnt'] > 0:
                logger.info("Data already exists. Skipping seeding.")
                return

            logger.info("Seeding database with sample data...")
            
            skus = [f"SKU_{i:03d}" for i in range(1, 11)]  # More SKUs
            vendors = ["V1", "V2"]
            
            # Vendor Rules
            for v in vendors:
                cursor.execute("INSERT IGNORE INTO vendor_rules (vendor_id, min_margin, max_discount) VALUES (%s, 0.1, 0.5)", (v,))
            
            # Inventory
            for sku in skus:
                cursor.execute("INSERT INTO inventory (sku, snapshot_ts, qty_on_hand, vendor_id) VALUES (%s, NOW(), %s, %s)", 
                               (sku, random.randint(10, 100), random.choice(vendors)))
            
            # Orders (last 90 days) - More data
            start_date = datetime.now() - timedelta(days=90)
            for _ in range(2000):  # Increased from 500
                sku = random.choice(skus)
                ts = start_date + timedelta(days=random.randint(0, 90), hours=random.randint(0, 23))
                qty = random.randint(1, 10)
                price = random.uniform(20.0, 100.0)
                cursor.execute("INSERT INTO orders (sku, order_ts, quantity, price, vendor_id) VALUES (%s, %s, %s, %s, %s)",
                               (sku, ts, qty, price, random.choice(vendors)))
            
            # Analytics - More data
            for _ in range(5000):  # Increased from 1000
                sku = random.choice(skus)
                ts = start_date + timedelta(days=random.randint(0, 90), hours=random.randint(0, 23))
                cursor.execute("INSERT INTO product_analytics (sku, event_ts, views, add_to_cart, conversions) VALUES (%s, %s, %s, %s, %s)",
                               (sku, ts, random.randint(1, 50), random.randint(0, 10), random.randint(0, 5)))
            
            logger.info("Seeding complete.")
    finally:
        conn.close()

def run_etl():
    """Run ETL process"""
    logger.info("Running ETL process...")
    try:
        from etl.extract import fetch_orders, fetch_inventory_snapshot, fetch_product_analytics, fetch_promotions
        from etl.transform import build_features
        from etl.load import load_features
        from datetime import date
        
        orders = fetch_orders(since_days=90)
        inventory = fetch_inventory_snapshot(latest_only=True)
        analytics = fetch_product_analytics(since_days=90)
        promos = fetch_promotions()
        
        features = build_features(orders, inventory, analytics, promos, as_of_date=date.today())
        logger.info(f"Features built: {features.shape}")
        
        if not features.empty:
            load_features(features)
            logger.info("Features loaded into DB")
        return True
    except Exception as e:
        logger.error(f"ETL failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def run_training():
    """Run model training"""
    logger.info("Running model training...")
    try:
        from services.db_pool import SimpleMySQLPool
        import pandas as pd
        from models.train_elasticity import train_and_save_all
        from models.train_demand import train_and_save
        import yaml
        
        pool = SimpleMySQLPool.instance()
        conn = pool.get_pandas_conn()
        try:
            orders = pd.read_sql("SELECT * FROM orders WHERE order_ts >= DATE_SUB(NOW(), INTERVAL 180 DAY)", conn)
            features = pd.read_sql("SELECT * FROM features_daily", conn)
        finally:
            pool.close_pandas_conn(conn)

        if not orders.empty:
            logger.info("Training elasticity model...")
            train_and_save_all(orders)
        
        if not features.empty:
            logger.info("Training demand model...")
            cfg_path = os.path.join("config", "config.yaml")
            cfg = {}
            if os.path.exists(cfg_path):
                with open(cfg_path) as f:
                    cfg = yaml.safe_load(f)['models']['demand']
            train_and_save(features, orders, cfg)
            logger.info("Models trained successfully.")
        return True
    except Exception as e:
        logger.error(f"Training failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def start_flask():
    """Start Flask application"""
    logger.info("Starting Flask application...")
    logger.info("API will be available at http://127.0.0.1:8002")
    logger.info("Press CTRL+C to stop")
    subprocess.run([sys.executable, "app_debug.py"])

def main():
    """Main startup sequence"""
    print("\n" + "="*60)
    print("DYNAMIC PRICING ENGINE - STARTUP")
    print("="*60 + "\n")
    
    # Step 1: Check dependencies
    check_dependencies()
    
    # Step 2: Setup environment
    setup_env()
    
    # Step 3: Wait for database
    if not wait_for_db(retries=5):
        logger.error("Could not connect to database.")
        logger.info("Please ensure MySQL is running and accessible.")
        return
    
    # Step 4: Initialize database
    init_db()
    
    # Step 5: Seed database
    seed_db()
    
    # Step 6: Run ETL
    run_etl()
    
    # Step 7: Train models
    run_training()
    
    # Step 8: Start Flask
    print("\n" + "="*60)
    print("SETUP COMPLETE - STARTING API SERVER")
    print("="*60 + "\n")
    start_flask()

if __name__ == "__main__":
    main()
