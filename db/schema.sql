-- Database schema for dynamic pricing engine

CREATE DATABASE IF NOT EXISTS pricing_db;
USE pricing_db;

-- Orders
CREATE TABLE IF NOT EXISTS orders (
    order_id BIGINT PRIMARY KEY AUTO_INCREMENT,
    sku VARCHAR(64) NOT NULL,
    order_ts DATETIME NOT NULL,
    quantity INT NOT NULL,
    price DECIMAL(10,4) NOT NULL,
    promo_id VARCHAR(64) NULL,
    vendor_id VARCHAR(64) NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_orders_sku_ts ON orders (sku, order_ts);

-- Inventory snapshots
CREATE TABLE IF NOT EXISTS inventory (
    snapshot_id BIGINT PRIMARY KEY AUTO_INCREMENT,
    sku VARCHAR(64) NOT NULL,
    snapshot_ts DATETIME NOT NULL,
    qty_on_hand INT NOT NULL,
    qty_reserved INT DEFAULT 0,
    vendor_id VARCHAR(64) NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_inventory_sku_ts ON inventory (sku, snapshot_ts);

-- Product analytics
CREATE TABLE IF NOT EXISTS product_analytics (
    analytics_id BIGINT PRIMARY KEY AUTO_INCREMENT,
    sku VARCHAR(64) NOT NULL,
    event_ts DATETIME NOT NULL,
    views INT DEFAULT 0,
    add_to_cart INT DEFAULT 0,
    conversions INT DEFAULT 0,
    avg_session_duration_sec INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_pa_sku_ts ON product_analytics (sku, event_ts);

-- Promotions
CREATE TABLE IF NOT EXISTS promotions (
    promo_id VARCHAR(64) PRIMARY KEY,
    sku VARCHAR(64) NULL,
    promo_type VARCHAR(64),
    start_ts DATETIME,
    end_ts DATETIME,
    discount_pct DECIMAL(5,4), -- 0.10 for 10%
    description TEXT
);

-- Vendor rules & constraints
CREATE TABLE IF NOT EXISTS vendor_rules (
    vendor_id VARCHAR(64) PRIMARY KEY,
    min_margin DECIMAL(5,4) DEFAULT 0.0, -- required min margin
    max_discount DECIMAL(5,4) DEFAULT 0.5, -- maximum allowed discount
    max_daily_price_change DECIMAL(5,4) DEFAULT 0.2,
    currency VARCHAR(8) DEFAULT 'USD',
    note TEXT
);

-- Features (daily feature store)
CREATE TABLE IF NOT EXISTS features_daily (
    feature_date DATE NOT NULL,
    sku VARCHAR(64) NOT NULL,
    sales_7d INT,
    sales_14d INT,
    sales_30d INT,
    avg_price_7d DECIMAL(10,4),
    avg_price_14d DECIMAL(10,4),
    avg_price_30d DECIMAL(10,4),
    views_7d INT,
    addtocart_7d INT,
    conversion_7d FLOAT,
    inventory_qty INT,
    inventory_age_days INT,
    promo_active BOOLEAN,
    last_price DECIMAL(10,4),
    PRIMARY KEY (feature_date, sku)
);

-- Elasticity results
CREATE TABLE IF NOT EXISTS elasticity_results (
    sku VARCHAR(64) PRIMARY KEY,
    elasticity FLOAT,
    r_squared FLOAT,
    p_value FLOAT,
    sample_size INT,
    last_computed TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Demand model predictions (history)
CREATE TABLE IF NOT EXISTS demand_predictions (
    pred_id BIGINT PRIMARY KEY AUTO_INCREMENT,
    sku VARCHAR(64),
    pred_ts DATETIME,
    predicted_units FLOAT,
    model_version VARCHAR(128),
    features_hash VARCHAR(64),
    price_tested DECIMAL(10,4),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Price suggestions & audit
CREATE TABLE IF NOT EXISTS price_suggestions (
    suggestion_id BIGINT PRIMARY KEY AUTO_INCREMENT,
    sku VARCHAR(64),
    request_ts DATETIME,
    current_price DECIMAL(10,4),
    suggested_price DECIMAL(10,4),
    expected_revenue DECIMAL(12,4),
    expected_units FLOAT,
    elasticity FLOAT,
    reason TEXT,
    constraints_applied TEXT,
    model_version VARCHAR(128),
    api_request_id VARCHAR(128),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_price_suggestions_sku_ts ON price_suggestions (sku, request_ts);

-- Vendor feedback (from /price-feedback)
CREATE TABLE IF NOT EXISTS vendor_feedback (
    feedback_id BIGINT PRIMARY KEY AUTO_INCREMENT,
    suggestion_id BIGINT,
    sku VARCHAR(64),
    vendor_id VARCHAR(64),
    feedback_ts DATETIME,
    accepted BOOLEAN,
    new_price DECIMAL(10,4),
    note TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Monitoring metrics
CREATE TABLE IF NOT EXISTS monitoring_metrics (
    metric_id BIGINT PRIMARY KEY AUTO_INCREMENT,
    metric_date DATE,
    metric_name VARCHAR(128),
    sku VARCHAR(64),
    metric_value FLOAT,
    details JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- API logs (optional lightweight)
CREATE TABLE IF NOT EXISTS api_logs (
    log_id BIGINT PRIMARY KEY AUTO_INCREMENT,
    endpoint VARCHAR(128),
    request_ts DATETIME,
    request_body JSON,
    response_body JSON,
    latency_ms INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
