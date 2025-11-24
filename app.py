# app.py
"""
Flask app entrypoint for Pricing Engine
"""

from flask import Flask
import logging
from api.routes import bp as pricing_bp
from loguru import logger
import os
from dotenv import load_dotenv

load_dotenv()

def create_app():
    app = Flask(__name__)
    # Register blueprints
    app.register_blueprint(pricing_bp)
    # Logging config
    logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
    return app

if __name__ == "__main__":
    app = create_app()
    host = os.getenv("FLASK_HOST", "0.0.0.0")
    port = int(os.getenv("FLASK_PORT", 8000))
    debug = os.getenv("FLASK_DEBUG", "False").lower() in ("true","1","yes")
    app.run(host=host, port=port, debug=debug)
