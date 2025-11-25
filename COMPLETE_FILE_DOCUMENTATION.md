# Complete File Documentation - Dynamic Pricing Engine

## 📁 Project Structure (After Cleanup)

This document provides detailed information about every file in the project.

---

## 🚀 MAIN EXECUTABLE FILES

### 1. **start_all.py**
- **Purpose**: Complete setup and initialization script
- **When to use**: First time setup only
- **What it does**:
  - Checks and installs dependencies
  - Connects to MySQL database
  - Creates database schema
  - Seeds sample data (2000+ orders, 5000+ analytics events)
  - Runs ETL to build features
  - Trains ML models (demand + elasticity)
  - Starts Flask API server on port 8002
- **How to run**: `python start_all.py`
- **Output**: Fully configured system with running API server

### 2. **run_me.py**
- **Purpose**: Quick start script for daily use
- **When to use**: Every time you want to start the server
- **What it does**: Starts `app_debug.py` with a nice banner
- **How to run**: `python run_me.py`
- **Output**: Flask server running on http://127.0.0.1:8002

### 3. **app_debug.py**
- **Purpose**: Main Flask API server application
- **When to use**: Started automatically by `run_me.py` or `start_all.py`
- **What it does**:
  - Serves REST API endpoints
  - Handles price suggestion requests
  - Processes feedback submissions
  - Logs all requests
  - Debug mode enabled for detailed error messages
- **Port**: 8002
- **Endpoints**:
  - `GET /test` - Health check
  - `GET /price-suggestions?sku=SKU_001` - Get price recommendations
  - `POST /price-feedback` - Submit feedback
- **How to run directly**: `python app_debug.py`

### 4. **test_final.py**
- **Purpose**: API testing script
- **When to use**: After starting the server to verify it's working
- **What it does**:
  - Tests GET /price-suggestions endpoint
  - Displays key metrics (SKU, prices, revenue, units)
  - Shows success/error status
- **How to run**: `python test_final.py`
- **Expected output**: Status Code 200 with price suggestions

### 5. **test_direct.py**
- **Purpose**: Direct pricing engine test (bypasses API)
- **When to use**: To test pricing logic without running the server
- **What it does**:
  - Loads demand model directly
  - Tests pricing engine with sample features
  - Shows suggested price and revenue
- **How to run**: `python test_direct.py`

### 6. **run_etl_debug.py**
- **Purpose**: ETL pipeline execution script
- **When to use**: Daily or when you add new order data
- **What it does**:
  - Extracts data from MySQL (orders, inventory, analytics, promotions)
  - Transforms data into features (rolling windows, aggregations)
  - Loads features into `features_daily` table
- **How to run**: `python run_etl_debug.py`
- **Output**: Updated features in database

### 7. **run_training_debug.py**
- **Purpose**: Model training script
- **When to use**: Weekly or when you want to retrain models
- **What it does**:
  - Reads features and orders from database
  - Trains elasticity model (OLS regression)
  - Trains demand model (LightGBM)
  - Saves models to `models_artifacts/` directory
- **How to run**: `python run_training_debug.py`
- **Output**: Updated model files in `models_artifacts/`

### 8. **cleanup.py**
- **Purpose**: Removes duplicate and debug files
- **When to use**: Already run, can delete this file now
- **What it does**: Deletes unnecessary files to clean up the project
- **How to run**: `python cleanup.py`

---

## 📚 DOCUMENTATION FILES

### 1. **README.md**
- **Purpose**: Complete project documentation
- **Contents**:
  - Project overview and features
  - Architecture diagram
  - Quick start guide
  - API endpoint documentation
  - Configuration guide
  - Database schema
  - Workflows and operations
  - Testing instructions
  - Troubleshooting
  - Production deployment guide
- **When to read**: First time and for reference

### 2. **PROJECT_SUMMARY.md**
- **Purpose**: Quick reference guide
- **Contents**:
  - Project status
  - System components
  - How to use
  - Key files
  - API endpoints
  - Sample data
  - Configuration
  - Performance metrics
  - Troubleshooting
  - Next steps
- **When to read**: For quick lookups

### 3. **FILE_INDEX.md**
- **Purpose**: Complete file structure guide
- **Contents**:
  - All files with descriptions
  - When to use each file
  - Database tables
  - Configuration files
  - Dependencies
  - Essential vs optional files
- **When to read**: To understand project structure

### 4. **START_HERE.md**
- **Purpose**: Quick start guide
- **Contents**:
  - Which script to use and when
  - Typical workflow
  - Files to keep vs delete
- **When to read**: When you're confused about which script to run

---

## ⚙️ CONFIGURATION FILES

### 1. **.env**
- **Purpose**: Environment variables configuration
- **Location**: Root directory
- **Contents**:
  ```env
  DB_HOST=127.0.0.1
  DB_PORT=3306
  DB_USER=root
  DB_PASSWORD=root
  DB_NAME=pricing_db
  DB_MAX_CONN=10
  FLASK_HOST=0.0.0.0
  FLASK_PORT=8002
  FLASK_DEBUG=False
  LOG_LEVEL=INFO
  ```
- **When to edit**: To change database credentials or server port

### 2. **config/.env.example**
- **Purpose**: Template for .env file
- **When to use**: Reference for required environment variables

### 3. **config/config.yaml**
- **Purpose**: Model and pricing configuration
- **Contents**:
  ```yaml
  models:
    demand:
      model_type: lightgbm
      params:
        num_boost_round: 500
        early_stopping_rounds: 50
        learning_rate: 0.05
        num_leaves: 31
  
  pricing:
    min_price: 0.5
    max_price: 100000.0
    daily_price_change_limit_pct: 0.15
    min_margin: 0.10
    max_discount: 0.30
  ```
- **When to edit**: To tune model hyperparameters or pricing constraints

### 4. **requirements.txt**
- **Purpose**: Python package dependencies
- **Contents**: List of required packages with versions
- **When to use**: `pip install -r requirements.txt`

---

## 📂 DIRECTORY STRUCTURE

### **api/** - API Layer
```
api/
├── __init__.py          # Package initialization
├── routes.py            # Flask route definitions
│                        # - GET /price-suggestions
│                        # - POST /price-feedback
└── utils.py             # Helper functions
                         # - json_response()
                         # - make_api_request_id()
```

### **services/** - Business Logic
```
services/
├── __init__.py          # Package initialization
├── db_pool.py           # Database connection pool
│                        # - SimpleMySQLPool class
│                        # - get_conn() / return_conn()
│                        # - get_pandas_conn() for pandas operations
├── pricing_engine.py    # Core pricing logic
│                        # - suggest_price_for_sku()
│                        # - apply_constraints()
│                        # - compute_expected_revenue()
├── prediction_service.py # Model loading and prediction
│                        # - load_demand_model()
│                        # - predict_units_for_prices()
└── feedback_service.py  # Feedback persistence
                         # - save_feedback()
```

### **models/** - Machine Learning
```
models/
├── __init__.py          # Package initialization
├── train_demand.py      # Demand forecasting model
│                        # - LightGBM regression
│                        # - Predicts units at different prices
│                        # - train_and_save()
├── train_elasticity.py  # Price elasticity model
│                        # - OLS regression
│                        # - Calculates price sensitivity
│                        # - train_and_save_all()
└── model_utils.py       # Model persistence utilities
                         # - save_model()
                         # - load_model()
```

### **models_artifacts/** - Trained Models
```
models_artifacts/
├── demand/
│   ├── demand_model.joblib      # Trained LightGBM model
│   └── demand_model.meta.json   # Model metadata
│                                # - model_type
│                                # - mape, mse
│                                # - feature_columns
│                                # - trained_at
└── elasticity/
    └── (results stored in database)
```

### **etl/** - ETL Pipeline
```
etl/
├── __init__.py          # Package initialization
├── extract.py           # Data extraction
│                        # - fetch_orders()
│                        # - fetch_inventory_snapshot()
│                        # - fetch_product_analytics()
│                        # - fetch_promotions()
├── transform.py         # Feature engineering
│                        # - build_features()
│                        # - Rolling windows (7d, 14d, 30d)
│                        # - Aggregations
│                        # - Lag features
└── load.py              # Load to database
                         # - load_features()
                         # - Upserts to features_daily table
```

### **db/** - Database
```
db/
├── __init__.py          # Package initialization
└── schema.sql           # Complete database schema
                         # Creates 11 tables:
                         # - orders
                         # - inventory
                         # - product_analytics
                         # - promotions
                         # - vendor_rules
                         # - features_daily
                         # - elasticity_results
                         # - demand_predictions
                         # - price_suggestions
                         # - vendor_feedback
                         # - monitoring_metrics
                         # - api_logs
```

### **config/** - Configuration
```
config/
├── .env.example         # Environment template
└── config.yaml          # Model and pricing configuration
```

### **monitoring/** - Monitoring
```
monitoring/
├── __init__.py          # Package initialization
└── daily_monitoring.py  # Metrics collection script
                         # - Collects daily metrics
                         # - Stores in monitoring_metrics table
```

### **scripts/** - Shell Scripts (Linux/Mac)
```
scripts/
├── run_etl.sh           # ETL execution script
├── train_models.sh      # Model training script
└── monitor_daily.sh     # Daily monitoring script
```

### **logs/** - Application Logs
```
logs/
└── (log files created at runtime)
```

### **data/** - Data Files
```
data/
└── (optional data files)
```

---

## 🗄️ DATABASE TABLES

### Core Data Tables

**1. orders**
- Purpose: Historical order transactions
- Columns: order_id, sku, order_ts, quantity, price, promo_id, vendor_id, created_at
- Indexes: (sku, order_ts)

**2. inventory**
- Purpose: Product inventory snapshots
- Columns: snapshot_id, sku, snapshot_ts, qty_on_hand, qty_reserved, vendor_id, created_at
- Indexes: (sku, snapshot_ts)

**3. product_analytics**
- Purpose: Customer behavior data
- Columns: analytics_id, sku, event_ts, views, add_to_cart, conversions, avg_session_duration_sec, created_at
- Indexes: (sku, event_ts)

**4. promotions**
- Purpose: Active promotions
- Columns: promo_id, sku, promo_type, start_ts, end_ts, discount_pct, description

**5. vendor_rules**
- Purpose: Vendor-specific constraints
- Columns: vendor_id, min_margin, max_discount, max_daily_price_change, currency, note

### Feature Store

**6. features_daily**
- Purpose: Engineered features for ML models
- Columns: feature_date, sku, sales_7d, sales_14d, sales_30d, avg_price_7d, avg_price_14d, avg_price_30d, views_7d, addtocart_7d, conversion_7d, inventory_qty, inventory_age_days, promo_active, last_price
- Primary Key: (feature_date, sku)

### Model Results

**7. elasticity_results**
- Purpose: Price elasticity by SKU
- Columns: sku, elasticity, r_squared, p_value, sample_size, last_computed

**8. demand_predictions**
- Purpose: Historical demand predictions
- Columns: pred_id, sku, pred_ts, predicted_units, model_version, features_hash, price_tested, created_at

### Audit & Logging

**9. price_suggestions**
- Purpose: All price recommendations
- Columns: suggestion_id, sku, request_ts, current_price, suggested_price, expected_revenue, expected_units, elasticity, reason, constraints_applied, model_version, api_request_id, created_at
- Indexes: (sku, request_ts)

**10. vendor_feedback**
- Purpose: Feedback on suggestions
- Columns: feedback_id, suggestion_id, sku, vendor_id, feedback_ts, accepted, new_price, note, created_at

**11. monitoring_metrics**
- Purpose: System metrics
- Columns: metric_id, metric_date, metric_name, sku, metric_value, details, created_at

**12. api_logs**
- Purpose: API request logs
- Columns: log_id, endpoint, request_ts, request_body, response_body, latency_ms, created_at

---

## 📦 DEPENDENCIES (requirements.txt)

### Web Framework
- **Flask >= 2.2**: Web framework for API
- **python-dotenv >= 1.0.0**: Environment variable management

### Database
- **PyMySQL >= 1.0.2**: MySQL database connector
- **PyYAML >= 6.0**: YAML configuration parser

### Data Science
- **pandas >= 2.2**: Data manipulation
- **numpy >= 1.26**: Numerical computing
- **scikit-learn >= 1.3**: Machine learning utilities
- **lightgbm >= 4.0**: Gradient boosting (demand model)
- **xgboost >= 2.1**: Gradient boosting (alternative)
- **statsmodels >= 0.14**: Statistical models (elasticity)
- **joblib >= 1.3**: Model serialization

### Monitoring & Utilities
- **prometheus-client >= 0.17**: Metrics collection
- **loguru >= 0.7.0**: Advanced logging
- **requests >= 2.31**: HTTP client (for testing)

### Optional
- **pydantic >= 2.0**: Data validation

---

## 🔄 TYPICAL WORKFLOWS

### First Time Setup
```bash
1. python start_all.py
   - Sets up everything
   - Starts server on port 8002

2. (In new terminal) python test_final.py
   - Tests the API
```

### Daily Operations
```bash
# Start server
python run_me.py

# Test API (in new terminal)
python test_final.py

# Get price suggestion
curl "http://127.0.0.1:8002/price-suggestions?sku=SKU_001"
```

### Weekly Maintenance
```bash
# Update features
python run_etl_debug.py

# Retrain models
python run_training_debug.py
```

---

## 🎯 QUICK REFERENCE

| Task | Command |
|------|---------|
| **First setup** | `python start_all.py` |
| **Start server** | `python run_me.py` |
| **Test API** | `python test_final.py` |
| **Update features** | `python run_etl_debug.py` |
| **Retrain models** | `python run_training_debug.py` |
| **Direct test** | `python test_direct.py` |

---

## 📊 SAMPLE DATA

After running `start_all.py`, the database contains:
- **10 SKUs**: SKU_001 through SKU_010
- **2 Vendors**: V1, V2
- **2000+ Orders**: Last 90 days
- **5000+ Analytics Events**: Views, add-to-cart, conversions
- **Inventory Snapshots**: Current stock levels
- **Vendor Rules**: Margin and discount constraints

---

## 🔧 CONFIGURATION SUMMARY

### Environment (.env)
- Database: MySQL on localhost:3306
- Server: Flask on 0.0.0.0:8002
- Logging: INFO level

### Model (config.yaml)
- Demand Model: LightGBM with 500 rounds
- Learning Rate: 0.05
- Early Stopping: 50 rounds

### Pricing Constraints
- Min Price: $0.50
- Max Price: $100,000
- Daily Change Limit: 15%
- Min Margin: 10%
- Max Discount: 30%

---

## ✅ SUCCESS CRITERIA

Your system is working if:
- ✅ `python run_me.py` starts without errors
- ✅ Server shows "Running on http://127.0.0.1:8002"
- ✅ `python test_final.py` returns Status Code: 200
- ✅ API returns valid JSON with `suggested_price` field
- ✅ Models exist in `models_artifacts/demand/` directory

---

**This document contains complete information about all files in the project.**

For quick start, see **START_HERE.md**  
For detailed documentation, see **README.md**  
For quick reference, see **PROJECT_SUMMARY.md**
