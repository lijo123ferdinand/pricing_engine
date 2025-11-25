# 🚀 WHICH SCRIPT TO USE?

## Quick Answer:

### **First Time Setup:**
```bash
python start_all.py
```
This will:
- Setup database
- Seed sample data
- Train models
- Start the server

### **Daily Use (After Setup):**
```bash
python run_me.py
```
OR
```bash
python app_debug.py
```

### **Test the API:**
```bash
python test_final.py
```

---

## Script Purposes:

| Script | When to Use | What It Does |
|--------|-------------|--------------|
| **start_all.py** | First time only | Complete setup + starts server |
| **run_me.py** | Daily use | Starts server (port 8002) |
| **app_debug.py** | Daily use | Server itself (port 8002) |
| **test_final.py** | After starting server | Tests the API |
| **run_etl_debug.py** | Daily/weekly | Updates features |
| **run_training_debug.py** | Weekly | Retrains models |

---

## Typical Workflow:

### First Time:
```bash
# 1. Setup everything
python start_all.py

# 2. In new terminal, test
python test_final.py
```

### Daily Use:
```bash
# Terminal 1: Start server
python run_me.py

# Terminal 2: Test
python test_final.py
```

---

## Files to Keep:

### ✅ Essential Files:
- `app_debug.py` - Main server
- `run_me.py` - Quick start
- `start_all.py` - Complete setup
- `test_final.py` - API test
- `test_direct.py` - Direct test
- `run_etl_debug.py` - ETL
- `run_training_debug.py` - Training
- `README.md` - Documentation
- `PROJECT_SUMMARY.md` - Quick reference
- `FILE_INDEX.md` - File guide
- All folders: `api/`, `services/`, `models/`, `etl/`, `db/`, `config/`

### ❌ Can Delete (if they exist):
- `app.py` - Old version
- `app_standalone.py` - Duplicate
- `simple_test.py` - Duplicate
- `test_api.py` - Duplicate
- `test_working.py` - Duplicate
- `test_detailed.py` - Debug only
- `inspect_orders.py` - Debug only
- `reproduce_pandas.py` - Debug only
- `restart_server.py` - Not needed
- `QUICKSTART.md` - Info in README
- `API_USAGE.md` - Info in README
- `WORKING_SOLUTION.md` - Info in README
- `SETUP_COMPLETE.md` - Info in README
- `RESTART.md` - Info in README
- `USE_STANDALONE.md` - Info in README
- Any `.txt` output files

---

## Summary:

**Use `start_all.py` ONCE for setup.**  
**Use `run_me.py` DAILY to start the server.**  
**Use `test_final.py` to test the API.**

That's it! 🎉
