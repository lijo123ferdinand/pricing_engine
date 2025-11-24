# services/db_pool.py
"""
Simple DB pool manager using PyMySQL connection pooling semantics.
This uses a naive pool implemented in Python; in production use a tested pool library (SQLAlchemy pool or mysqlclient's pooling).
"""

from queue import Queue, Empty
import pymysql
import threading
import os
from loguru import logger
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
DB_PORT = int(os.getenv("DB_PORT", 3306))
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "pricing_db")
DB_MAX_CONN = int(os.getenv("DB_MAX_CONN", 10))

class SimpleMySQLPool:
    _instance = None
    _lock = threading.Lock()

    def __init__(self, size=10):
        self.size = size
        self._pool = Queue(maxsize=size)
        for _ in range(size):
            conn = pymysql.connect(host=DB_HOST, port=DB_PORT, user=DB_USER,
                                   password=DB_PASSWORD, database=DB_NAME,
                                   cursorclass=pymysql.cursors.DictCursor,
                                   autocommit=True)
            self._pool.put(conn)
        logger.info(f"MySQL pool initialized with {size} connections")

    @classmethod
    def instance(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = SimpleMySQLPool(size=DB_MAX_CONN)
            return cls._instance

    def get_conn(self, timeout=5):
        try:
            return self._pool.get(timeout=timeout)
        except Empty:
            raise RuntimeError("No DB connection available")

    def return_conn(self, conn):
        try:
            self._pool.put(conn, timeout=2)
        except Exception:
            try:
                conn.close()
            finally:
                pass

    def close_all(self):
        while not self._pool.empty():
            conn = self._pool.get_nowait()
            conn.close()
