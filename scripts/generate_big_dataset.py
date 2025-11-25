import random
import numpy as np
import pandas as pd
import pymysql
from datetime import datetime, timedelta

DB = {
    "host": "127.0.0.1",
    "user": "root",
    "password": "thbs123!",
    "database": "pricing_db",
    "cursorclass": pymysql.cursors.DictCursor
}

def connect():
    return pymysql.connect(**DB)

# -------------------------------------------------------
# CONFIG: How much data to generate
# -------------------------------------------------------
NUM_SKUS = 10
DAYS = 180
ORDERS_PER_DAY = (30, 120)            # min/max orders/day across all SKUs
ANALYTICS_EVENTS_PER_DAY = (80, 200)
SEED = 42
random.seed(SEED)
np.random.seed(SEED)

# -------------------------------------------------------
# PRODUCT LIST
# -------------------------------------------------------
SKUS = [f"SKU-{i+1:03d}" for i in range(NUM_SKUS)]
VENDORS = ["vendor_1", "vendor_2"]

def simulate_price(base_price):
    """Add some realistic noise to price evolution."""
    return max(5, base_price * random.uniform(0.9, 1.1))

def simulate_quantity(base_qty, price, elasticity):
    """Quantity following demand curve Q = A * P^elasticity"""
    q = base_qty * (price ** elasticity)
    q = q + np.random.normal(0, 0.2 * base_qty)  # noise
    return max(0, int(q))

def insert_large_data():
    conn = connect()
    cur = conn.cursor()

    print("Cleaning old data...")
    cur.execute("DELETE FROM orders")
    cur.execute("DELETE FROM inventory")
    cur.execute("DELETE FROM product_analytics")
    cur.execute("DELETE FROM promotions")
    conn.commit()

    print("Inserting vendor rules...")
    cur.execute("DELETE FROM vendor_rules")
    cur.execute("""
        INSERT INTO vendor_rules (vendor_id,min_margin,max_discount,max_daily_price_change)
        VALUES
        ('vendor_1',0.12,0.25,0.15),
        ('vendor_2',0.08,0.35,0.20)
    """)
    conn.commit()

    today = datetime.now()

    # -------------------------------------------------------
    # Generate promotions
    # -------------------------------------------------------
    print("Inserting promotions...")
    for sku in SKUS:
        start = today - timedelta(days=random.randint(20, 60))
        cur.execute("""
            INSERT INTO promotions (promo_id, sku, promo_type, start_ts, end_ts, discount_pct, description)
            VALUES (%s, %s, 'Seasonal', %s, %s, %s, 'seasonal promo')
        """, (f"promo_{sku}", sku, start, start + timedelta(days=10), random.uniform(0.05, 0.15)))
    conn.commit()

    # -------------------------------------------------------
    # INVENTORY (daily snapshots)
    # -------------------------------------------------------
    print("Inserting inventory snapshots...")
    for sku in SKUS:
        qty = random.randint(200, 800)
        for d in range(DAYS):
            ts = today - timedelta(days=d)
            qty_on_hand = max(0, qty - random.randint(-2, 5))
            cur.execute("""
                INSERT INTO inventory (sku, snapshot_ts, qty_on_hand, qty_reserved, vendor_id)
                VALUES (%s, %s, %s, %s, %s)
            """, (sku, ts, qty_on_hand, random.randint(0, 15), random.choice(VENDORS)))

    conn.commit()

    print("Generating orders + analytics...")

    for d in range(DAYS):
        ts = today - timedelta(days=d)
        total_orders_today = random.randint(*ORDERS_PER_DAY)
        total_analytics_today = random.randint(*ANALYTICS_EVENTS_PER_DAY)

        # Generate analytics events
        for _ in range(total_analytics_today):
            sku = random.choice(SKUS)
            views = random.randint(5, 50)
            add_to_cart = int(views * random.uniform(0.05, 0.20))
            conversions = int(add_to_cart * random.uniform(0.10, 0.40))

            cur.execute("""
                INSERT INTO product_analytics (sku,event_ts,views,add_to_cart,conversions)
                VALUES (%s,%s,%s,%s,%s)
            """, (sku, ts, views, add_to_cart, conversions))

        # Orders
        for _ in range(total_orders_today):
            sku = random.choice(SKUS)
            base_price = random.uniform(10, 400)
            elasticity = random.uniform(-1.8, -0.3)
            price = simulate_price(base_price)
            quantity = simulate_quantity(base_qty=3, price=price, elasticity=elasticity)

            if quantity > 0:
                cur.execute("""
                    INSERT INTO orders (sku,order_ts,quantity,price,vendor_id)
                    VALUES (%s,%s,%s,%s,%s)
                """, (sku, ts, quantity, round(price, 2), random.choice(VENDORS)))

        if d % 10 == 0:
            print(f"Inserted day {d}/{DAYS}")

    conn.commit()
    cur.close()
    conn.close()
    print("SUCCESS: Large dataset inserted.")

if __name__ == "__main__":
    insert_large_data()
