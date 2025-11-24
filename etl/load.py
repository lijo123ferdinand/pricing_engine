# etl/load.py
"""
Load stage: convenience wrapper to write feature DF using feature_store.write_features_to_db
"""

from services.feature_store import write_features_to_db

def load_features(df):
    write_features_to_db(df)
