# File Index - Dynamic Pricing Engine

## 🚀 MAIN FILES (Start Here!)

### To Run the System:
1. **run_me.py** - One-command startup (runs app_debug.py)
2. **app_debug.py** - Main Flask API server ⭐ **USE THIS**
3. **test_final.py** - Test the API ⭐ **USE THIS**

### Quick Start:
```bash
# Terminal 1: Start server
python run_me.py

# Terminal 2: Test it
python test_final.py
```

---

## 📁 Complete File Structure

### Core Application Files
```
├── app_debug.py              ⭐ Main Flask server (port 8002)
├── run_me.py                 ⭐ Quick start script
├── test_final.py             ⭐ API test script
├── start_all.py              Complete setup (run once)
├── requirements.txt          Python dependencies
├── .env                      Environment configuration
```

### API Layer
```
├── api/
│   ├── __init__.py
│   ├── routes.py             Flask routes (price suggestions, feedback)
│   └── utils.py              Helper functions (JSON response, request ID)
```

### Business Logic Services
```
├── services/
│   ├── __init__.py
│   ├── db_pool.py            Database connection pool
│   ├── pricing_engine.py    Core pricing logic
│   ├── prediction_service.py Model loading and prediction
│   └── feedback_service.py   Feedback persistence
```

### Machine Learning Models
```
├── models/
│   ├── __init__.py
│   ├── train_demand.py       Demand forecasting (LightGBM)
│   ├── train_elasticity.py  Price elasticity (OLS regression)
│   └── model_utils.py        Model save/load utilities
```

### Trained Model Artifacts
```
├── models_artifacts/
│   ├── demand/
│   │   ├── demand_model.joblib      ⭐ Trained LightGBM model
│   │   └── demand_model.meta.json   Model metadata
│   └── elasticity/
│       └── (elasticity results stored in DB)
```

### ETL Pipeline
```
├── etl/
│   ├── __init__.py
│   ├── extract.py            Data extraction from MySQL
│   ├── transform.py          Feature engineering
│   └── load.py               Load features to database
```

### Database
```
├── db/
│   ├── __init__.py
│   └── schema.sql            ⭐ Complete database schema
```

### Configuration
```
├── config/
│   ├── .env.example          Environment template
│   └── config.yaml           Model hyperparameters
```

### Monitoring
```
├── monitoring/
│   ├── __init__.py
│   └── daily_monitoring.py   Metrics collection
```

### Testing & Debugging
```
├── test_final.py             ⭐ Main test script
├── test_direct.py            Direct pricing engine test
├── test_working.py           Port 8002 test
├── test_detailed.py          Detailed error test
├── run_etl_debug.py          ETL debugging
├── run_training_debug.py     Training debugging
```

### Alternative/Legacy Files
```
├── app.py                    Original app (has caching issues)
├── app_standalone.py         Standalone version
├── simple_test.py            Simple test (port 8000)
├── test_api.py               Comprehensive test
├── restart_server.py         Server restart utility
```

### Documentation
```
├── README.md                 ⭐ Complete project documentation
├── PROJECT_SUMMARY.md        ⭐ Quick reference guide
├── API_USAGE.md              Detailed API documentation
├── QUICKSTART.md             Quick start guide
├── WORKING_SOLUTION.md       Troubleshooting guide
├── SETUP_COMPLETE.md         Setup instructions
├── RESTART.md                Restart instructions
├── USE_STANDALONE.md         Standalone app guide
├── FILE_INDEX.md             This file
```

### Scripts
```
├── scripts/
│   ├── run_etl.sh            ETL shell script (Linux/Mac)
│   ├── train_models.sh       Training shell script (Linux/Mac)
│   └── monitor_daily.sh      Monitoring shell script (Linux/Mac)
```

### Data
```
├── data/
│   └── (sample data files if any)
```

### Logs
```
├── logs/
│   └── (application logs)
```

---

## 🎯 File Purpose Quick Reference

### When to Use Each File:

| Task | File to Use |
|------|-------------|
| **Start the server** | `python run_me.py` or `python app_debug.py` |
| **Test the API** | `python test_final.py` |
| **Initial setup** | `python start_all.py` |
| **Update features** | `python run_etl_debug.py` |
| **Retrain models** | `python run_training_debug.py` |
| **Read documentation** | `README.md` |
| **Quick reference** | `PROJECT_SUMMARY.md` |
| **API examples** | `API_USAGE.md` |
| **Troubleshooting** | `WORKING_SOLUTION.md` |

---

## 📊 Database Tables

Created by `db/schema.sql`:

### Core Data Tables
- **orders** - Historical order data
- **inventory** - Product inventory snapshots
- **product_analytics** - Customer behavior data
- **promotions** - Active promotions
- **vendor_rules** - Vendor-specific constraints

### Feature Store
- **features_daily** - Engineered features for ML

### Model Results
- **elasticity_results** - Price elasticity by SKU
- **demand_predictions** - Historical predictions

### Audit & Logging
- **price_suggestions** - All price recommendations
- **vendor_feedback** - Feedback on suggestions
- **api_logs** - API request logs
- **monitoring_metrics** - System metrics

---

## 🔧 Configuration Files

### .env (Environment Variables)
```env
DB_HOST=127.0.0.1
DB_PORT=3306
DB_USER=root
DB_PASSWORD=thbs123!
DB_NAME=pricing_db
FLASK_PORT=8002
LOG_LEVEL=INFO
```

### config/config.yaml (Model Configuration)
```yaml
models:
  demand:
    model_type: lightgbm
    params:
      num_boost_round: 500
      learning_rate: 0.05

pricing:
  min_price: 0.5
  max_price: 100000.0
  daily_price_change_limit_pct: 0.15
```

---

## 🗑️ Files You Can Ignore

These files exist for debugging/alternative approaches but are not needed:

- `app.py` - Use `app_debug.py` instead
- `app_standalone.py` - Use `app_debug.py` instead
- `simple_test.py` - Use `test_final.py` instead
- `test_api.py` - Use `test_final.py` instead
- `test_working.py` - Use `test_final.py` instead
- `test_detailed.py` - Debugging only
- `debug_app.py` - Same as `app_debug.py`
- `restart_server.py` - Not needed
- Various `.md` files - Consolidated in README.md

---

## 📦 Dependencies (requirements.txt)

### Web Framework
- Flask >= 2.2
- python-dotenv >= 1.0.0

### Database
- PyMySQL >= 1.0.2
- PyYAML >= 6.0

### Machine Learning
- pandas >= 2.2
- numpy >= 1.26
- scikit-learn >= 1.3
- lightgbm >= 4.0
- xgboost >= 2.1
- statsmodels >= 0.14
- joblib >= 1.3

### Monitoring
- prometheus-client >= 0.17
- loguru >= 0.7.0
- requests >= 2.31

### Optional
- pydantic >= 2.0

---

## 🎯 Essential Files Only

If you want to keep only essential files:

**Keep:**
- `app_debug.py`
- `run_me.py`
- `test_final.py`
- `start_all.py`
- `requirements.txt`
- `.env`
- `README.md`
- `PROJECT_SUMMARY.md`
- All folders: `api/`, `services/`, `models/`, `etl/`, `db/`, `config/`
- `models_artifacts/` folder with trained models

**Can delete:**
- All other `.py` test files
- All other `.md` documentation files (info is in README.md)
- `scripts/` folder (if not using shell scripts)

---

## 📝 Notes

- **Port 8002** is used to avoid conflicts and caching issues
- **app_debug.py** has debug logging enabled for troubleshooting
- **Models** are automatically trained by `start_all.py`
- **Sample data** is automatically seeded on first run

---

**For quick start, just run:**
```bash
python run_me.py
```

Then test with:
```bash
python test_final.py
```

That's it! 🎉
