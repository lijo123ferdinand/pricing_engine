# etl/transform.py
"""
Transform stage: compute rolling windows, lags, promotion flags, inventory aging, etc.
Produces a DataFrame compatible with features_daily schema.
"""

from datetime import datetime, timedelta, date
import pandas as pd
import numpy as np

def build_features(orders_df, inventory_df, analytics_df, promotions_df, as_of_date=None):
    """
    orders_df: columns: order_id, sku, order_ts, quantity, price
    inventory_df: sku, snapshot_ts, qty_on_hand, qty_reserved
    analytics_df: sku, event_ts, views, add_to_cart, conversions
    promotions_df: promo_id, sku, start_ts, end_ts, discount_pct
    as_of_date: datetime.date
    """
    if as_of_date is None:
        as_of_date = datetime.utcnow().date()
    end_ts = pd.Timestamp(as_of_date) + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)
    start_30 = end_ts - pd.Timedelta(days=30)
    start_14 = end_ts - pd.Timedelta(days=14)
    start_7 = end_ts - pd.Timedelta(days=7)

    # Normalize dtypes
    orders_df['order_ts'] = pd.to_datetime(orders_df['order_ts'])
    analytics_df['event_ts'] = pd.to_datetime(analytics_df['event_ts'])
    inventory_df['snapshot_ts'] = pd.to_datetime(inventory_df['snapshot_ts'])
    promotions_df['start_ts'] = pd.to_datetime(promotions_df['start_ts'])
    promotions_df['end_ts'] = pd.to_datetime(promotions_df['end_ts'])

    skus = pd.Index(
        pd.concat([
            orders_df['sku'], analytics_df['sku'], inventory_df['sku'], promotions_df['sku'].dropna()
        ]).dropna().unique()
    )

    rows = []
    for sku in skus:
        # Sales totals
        o_sku = orders_df[orders_df['sku'] == sku]
        sales_7d = o_sku[(o_sku['order_ts'] >= start_7) & (o_sku['order_ts'] <= end_ts)]['quantity'].sum()
        sales_14d = o_sku[(o_sku['order_ts'] >= start_14) & (o_sku['order_ts'] <= end_ts)]['quantity'].sum()
        sales_30d = o_sku[(o_sku['order_ts'] >= start_30) & (o_sku['order_ts'] <= end_ts)]['quantity'].sum()

        # Average prices
        def avg_price_in_range(start):
            s = o_sku[(o_sku['order_ts'] >= start) & (o_sku['order_ts'] <= end_ts)]
            if len(s) == 0:
                return np.nan
            return (s['price'] * s['quantity']).sum() / s['quantity'].sum()

        avg_price_7d = avg_price_in_range(start_7)
        avg_price_14d = avg_price_in_range(start_14)
        avg_price_30d = avg_price_in_range(start_30)

        # Analytics rolling
        a_sku = analytics_df[analytics_df['sku'] == sku]
        views_7d = a_sku[(a_sku['event_ts'] >= start_7) & (a_sku['event_ts'] <= end_ts)]['views'].sum()
        addtocart_7d = a_sku[(a_sku['event_ts'] >= start_7) & (a_sku['event_ts'] <= end_ts)]['add_to_cart'].sum()
        conversions_7d = a_sku[(a_sku['event_ts'] >= start_7) & (a_sku['event_ts'] <= end_ts)]['conversions'].sum()
        conversion_rate_7d = (conversions_7d / views_7d) if views_7d > 0 else 0.0

        # Inventory
        inv_row = inventory_df[inventory_df['sku'] == sku]
        if not inv_row.empty:
            inv_row = inv_row.sort_values('snapshot_ts', ascending=False).iloc[0]
            inventory_qty = int(inv_row['qty_on_hand'] - inv_row.get('qty_reserved', 0))
            inventory_age_days = (end_ts - pd.to_datetime(inv_row['snapshot_ts'])).days
            last_price = None
        else:
            inventory_qty = 0
            inventory_age_days = None
            last_price = None

        # Last price in orders
        if not o_sku.empty:
            last_price = o_sku.sort_values('order_ts', ascending=False).iloc[0]['price']

        # Promo active
        promo_active = False
        p = promotions_df[(promotions_df['sku'].isnull()) | (promotions_df['sku'] == sku)]
        for _, promo in p.iterrows():
            if (promo['start_ts'] <= end_ts) and (promo['end_ts'] >= start_7):
                promo_active = True
                break

        rows.append({
            'feature_date': as_of_date,
            'sku': sku,
            'sales_7d': int(sales_7d),
            'sales_14d': int(sales_14d),
            'sales_30d': int(sales_30d),
            'avg_price_7d': float(avg_price_7d) if not pd.isna(avg_price_7d) else None,
            'avg_price_14d': float(avg_price_14d) if not pd.isna(avg_price_14d) else None,
            'avg_price_30d': float(avg_price_30d) if not pd.isna(avg_price_30d) else None,
            'views_7d': int(views_7d),
            'addtocart_7d': int(addtocart_7d),
            'conversion_7d': float(conversion_rate_7d),
            'inventory_qty': int(inventory_qty),
            'inventory_age_days': int(inventory_age_days) if inventory_age_days is not None else None,
            'promo_active': bool(promo_active),
            'last_price': float(last_price) if last_price is not None else None
        })

    features_df = pd.DataFrame(rows)
    # Fill NaNs where appropriate
    features_df = features_df.fillna({
        'avg_price_7d': 0.0,
        'avg_price_14d': 0.0,
        'avg_price_30d': 0.0,
        'inventory_age_days': 0,
        'last_price': 0.0
    })
    return features_df
