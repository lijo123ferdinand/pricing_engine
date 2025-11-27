# Dynamic Pricing Engine - Project Details

## 🎯 Overview

The Dynamic Pricing Engine is a machine learning-powered system designed to provide optimal price recommendations. It leverages historical order data, inventory levels, and customer analytics to predict demand and calculate price elasticity, ensuring that generated prices maximize revenue while respecting business constraints.

### Key Features
- **🤖 Machine Learning Models**: Uses LightGBM for demand forecasting and OLS regression for price elasticity.
- **📊 Price Elasticity Analysis**: statistically analyzes how sensitive demand is to price changes.
- **🔒 Business Constraints**: Enforces rules such as minimum margins, maximum discounts, and daily price change limits.
- **🚀 REST API**: Provides real-time pricing recommendations via a Flask-based API.
- **📈 Feature Engineering**: Automated ETL pipeline to transform raw data into model-ready features.
- **📝 Audit Trail**: Complete logging of all suggestions, feedback, and system metrics.

---

## 🏗️ Architecture

The system follows a service-oriented architecture:

```mermaid
graph TD
    Client[Client / Dashboard] -->|HTTP| API[Flask API]
    API -->|Request| Engine[Pricing Engine Service]
    
    subgraph "Core Logic"
        Engine -->|Apply Rules| Constraints[Constraint Service]
        Engine -->|Predict| Demand[Demand Model (LightGBM)]
        Engine -->|Analyze| Elasticity[Elasticity Model (OLS)]
    end
    
    subgraph "Data Layer"
        ETL[ETL Pipeline] -->|Updates| FeatureStore[(Feature Store)]
        FeatureStore --> Demand
        MySQL[(MySQL Database)] -->|Raw Data| ETL
        MySQL -->|Persist| Audit[Audit Logs]
    end
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- MySQL 5.7+

### 1. Initial Setup
Run the complete setup script to install dependencies, set up the database, seed data, and train models:
```bash
python start_all.py
```

### 2. Daily Usage
To start the API server (runs on port 8002):
```bash
python run_me.py
```
*Alternatively, you can run `python app_debug.py` directly.*

### 3. Testing
To verify the system is working:
```bash
python test_final.py
```

---

## 🔌 API Endpoints

### 1. Get Price Suggestions
**GET** `/price-suggestions`

Returns optimal price recommendations for a specific SKU.

**Parameters:**
- `sku` (required): Product identifier (e.g., `SKU_001`)
- `vendor_id` (optional): Vendor identifier for specific rules

**Example Request:**
```bash
curl "http://127.0.0.1:8002/price-suggestions?sku=SKU_001"
```

**Example Response:**
```json
{
  "sku": "SKU_001",
  "current_price": 50.0,
  "suggested_price": 42.5,
  "expected_revenue": 1200.0,
  "model_version": "2025-11-25...",
  "reason": "revenue_maximization"
}
```

### 2. Submit Feedback
**POST** `/price-feedback`

Allows vendors to accept or reject price suggestions.

**Body:**
```json
{
  "sku": "SKU_001",
  "vendor_id": "V1",
  "accepted": true,
  "new_price": 42.50,
  "note": "Accepted AI suggestion"
}
```

---

## 🔧 Configuration

### Environment Variables (`.env`)
| Variable | Description | Default |
|----------|-------------|---------|
| `DB_HOST` | MySQL Host | 127.0.0.1 |
| `DB_PORT` | MySQL Port | 3306 |
| `DB_USER` | MySQL User | root |
| `DB_NAME` | Database Name | pricing_db |
| `FLASK_PORT` | API Port | 8002 |

### Model Configuration (`config/config.yaml`)
Adjust model hyperparameters and pricing rules here.
```yaml
pricing:
  min_price: 0.5
  max_price: 100000.0
  daily_price_change_limit_pct: 0.15
  min_margin: 0.10
```

---

## 📊 Database Schema

The system uses a MySQL database with the following key tables:

### Core Data
- **`orders`**: Historical transaction data.
- **`inventory`**: Daily inventory snapshots.
- **`product_analytics`**: Web traffic and conversion metrics.
- **`promotions`**: Active marketing campaigns.

### Feature Store
- **`features_daily`**: Pre-computed features (rolling sales, average prices) used for model inference.

### Audit & Logs
- **`price_suggestions`**: History of all API recommendations.
- **`vendor_feedback`**: User feedback on prices.
- **`monitoring_metrics`**: System health and performance metrics.

---

## 🔄 Workflows

### Daily ETL
Updates features based on new data. Run this daily:
```bash
python run_etl_debug.py
```

### Model Retraining
Retrains the LightGBM and Elasticity models. Run this weekly:
```bash
python run_training_debug.py
```

### Monitoring
Collects system metrics. Run this daily:
```bash
python monitoring/daily_monitoring.py
```

---

## 🐛 Troubleshooting

### Common Issues

**1. API returns 500 Error**
- Check if the database is running.
- Ensure models are trained (`models_artifacts/` should not be empty).
- Run `python app_debug.py` to see detailed logs.

**2. Database Connection Failed**
- Verify credentials in `.env`.
- Ensure MySQL service is active.

**3. Expected Revenue is $0**
- This is normal with synthetic data if the model predicts 0 demand at the tested price points.
- Add real data and retrain models to fix.

---

## 🚀 Deployment

For production deployment:
1. **WSGI Server**: Use Gunicorn instead of the Flask dev server.
   ```bash
   gunicorn -w 4 -b 0.0.0.0:8000 app_debug:app
   ```
2. **Reverse Proxy**: Set up Nginx to forward requests to Gunicorn.
3. **Automation**: Use cron jobs for ETL and training scripts.

---

## 🤝 Contributing
1. Fork the repository.
2. Create a feature branch.
3. Submit a Pull Request with tests.

## 📄 License
See the LICENSE file for details.
