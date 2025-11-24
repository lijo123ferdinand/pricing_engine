# Dynamic Pricing Engine (Backend)

This repository implements a production-ready backend for an internal-data–powered Dynamic Pricing Engine.

## Features

- ETL: ingest orders, inventory, product analytics, promotions
- Feature store: rolling windows, lags, promo flags
- Elasticity per-SKU using log-log OLS (StatsModels)
- Demand prediction using LightGBM / XGBoost
- Price optimization engine (grid-search + constraints)
- Flask REST API:
  - `GET /price-suggestions?sku=...`
  - `POST /price-feedback`
- Monitoring: daily batch script for model drift, coverage, MAPE
- DB schema & seed data
- Docker + docker-compose, systemd service

---

## Quickstart (local)

### Prerequisites

- Python 3.12
- MySQL (or run via docker-compose)
- `pip install -r requirements.txt`

### Setup DB

1. Start MySQL and create DB/schema:

```bash
# using local mysql (adjust env variables in config/.env.example)
mysql -u root -p
# then run:
mysql> SOURCE db/schema.sql;
mysql> SOURCE data/sample_data.sql;
