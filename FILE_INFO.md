# File Information - Dynamic Pricing Engine

This document provides a detailed explanation of every file in the project, organized by component.

## 🚀 Main Executables

| File | Purpose | Usage |
|------|---------|-------|
| **`run_me.py`** | **Start Here!** Quick start script to launch the server. | `python run_me.py` |
| **`start_all.py`** | Complete setup script. Installs deps, sets up DB, seeds data, trains models, and starts server. | `python start_all.py` (First run only) |
| **`app_debug.py`** | Main Flask API application. Handles all HTTP requests. | `python app_debug.py` |
| **`test_final.py`** | Primary test script to verify the API is working correctly. | `python test_final.py` |

---

## 🔌 API Layer (`api/`)

| File | Description |
|------|-------------|
| **`api/routes.py`** | Defines Flask routes (`/price-suggestions`, `/price-feedback`). Maps URLs to service logic. |
| **`api/utils.py`** | Helper functions for the API, such as JSON response formatting and request ID generation. |
| **`api/__init__.py`** | Package initialization. |

---

## 🧠 Business Logic (`services/`)

| File | Description |
|------|-------------|
| **`services/pricing_engine.py`** | **Core Logic**. Orchestrates the pricing process: calls models, applies constraints, and selects the optimal price. |
| **`services/prediction_service.py`** | Handles loading ML models and generating predictions (demand & elasticity). |
| **`services/feedback_service.py`** | Manages saving vendor feedback to the database. |
| **`services/db_pool.py`** | Manages database connections efficiently using a connection pool. |

---

## 🤖 Machine Learning (`models/`)

| File | Description |
|------|-------------|
| **`models/train_demand.py`** | Trains the LightGBM demand forecasting model. |
| **`models/train_elasticity.py`** | Trains the OLS regression model for price elasticity. |
| **`models/model_utils.py`** | Utilities for saving and loading trained models (using joblib). |
| **`models_artifacts/`** | Directory where trained model files (`.joblib`) and metadata (`.json`) are stored. |

---

## 🔄 ETL Pipeline (`etl/`)

| File | Description |
|------|-------------|
| **`run_etl_debug.py`** | Script to manually trigger the ETL process. |
| **`etl/extract.py`** | Fetches raw data (orders, inventory, analytics) from the MySQL database. |
| **`etl/transform.py`** | **Feature Engineering**. Calculates rolling averages, lags, and other features for the models. |
| **`etl/load.py`** | Saves the computed features into the `features_daily` table. |

---

## 💾 Database (`db/`)

| File | Description |
|------|-------------|
| **`db/schema.sql`** | Complete SQL schema definition. Creates all tables (orders, inventory, features, etc.). |
| **`db/__init__.py`** | Package initialization. |

---

## 🔧 Configuration (`config/`)

| File | Description |
|------|-------------|
| **`.env`** | Environment variables for database credentials and server settings. |
| **`config/config.yaml`** | Configuration for model hyperparameters (e.g., learning rate) and business rules (e.g., min margin). |
| **`requirements.txt`** | List of Python dependencies required to run the project. |

---

## 📊 Monitoring (`monitoring/`)

| File | Description |
|------|-------------|
| **`monitoring/daily_monitoring.py`** | Script to collect and log system metrics (model performance, business KPIs). |

---

## 🧪 Testing & Debugging

| File | Description |
|------|-------------|
| **`test_direct.py`** | Tests the pricing engine logic directly, bypassing the API layer. Useful for debugging core logic. |
| **`run_training_debug.py`** | Script to manually trigger model retraining. |
| **`cleanup.py`** | Utility script to remove temporary files and clean up the directory. |

---

## 🗑️ Deprecated / Legacy Files

*These files may exist but are not core to the current system:*
- `app.py` (Old version)
- `app_standalone.py`
- `simple_test.py`
- `test_api.py`
