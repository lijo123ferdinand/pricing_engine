# api/utils.py
"""
Small API helper utilities.
"""
from flask import request, jsonify
import uuid

def make_api_request_id():
    return str(uuid.uuid4())

def json_response(payload, status=200):
    return jsonify(payload), status
