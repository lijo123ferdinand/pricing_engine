-- Sample seed data for quick local testing
USE pricing_db;

INSERT INTO vendor_rules (vendor_id, min_margin, max_discount, max_daily_price_change) VALUES
('vendor_1', 0.12, 0.25, 0.15),
('vendor_2', 0.08, 0.35, 0.2);

INSERT INTO promotions (promo_id, sku, promo_type, start_ts, end_ts, discount_pct, description) VALUES
('promo_10_sku_A', 'SKU-A', 'Seasonal', '2025-11-01', '2025-11-30', 0.10, 'Nov seasonal promo'),
('promo_5_all', NULL, 'Sitewide', '2025-11-20', '2025-11-25', 0.05, 'Short site promo');

-- Add a few product analytics rows
INSERT INTO product_analytics (sku, event_ts, views, add_to_cart, conversions) VALUES
('SKU-A', '2025-11-20 01:00:00', 100, 10, 2),
('SKU-A', '2025-11-21 01:00:00', 120, 15, 3),
('SKU-B', '2025-11-21 01:00:00', 50, 4, 1);

-- Some inventory snapshots
INSERT INTO inventory (sku, snapshot_ts, qty_on_hand, qty_reserved, vendor_id) VALUES
('SKU-A', '2025-11-21 00:00:00', 500, 10, 'vendor_1'),
('SKU-B', '2025-11-21 00:00:00', 20, 2, 'vendor_2');

-- Orders (historical)
INSERT INTO orders (sku, order_ts, quantity, price, vendor_id) VALUES
('SKU-A', '2025-11-10 12:00:00', 2, 19.99, 'vendor_1'),
('SKU-A', '2025-11-11 12:00:00', 1, 19.99, 'vendor_1'),
('SKU-A', '2025-11-18 18:00:00', 3, 18.00, 'vendor_1'),
('SKU-B', '2025-11-20 19:00:00', 1, 150.00, 'vendor_2');

