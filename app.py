from flask import Flask, jsonify
import os

app = Flask(__name__)

VERSION = "V6-STABLE"

@app.route("/")
def home():
    return "TITANIUM LIVE OK", 200

@app.route("/version")
def version():
    return jsonify({
        "status": "online",
        "version": VERSION
    }), 200

@app.route("/admin/stats")
def stats():
    return jsonify({
        "status": "ok",
        "service": "titanium",
        "version": VERSION
    }), 200

# IMPORTANT: Render uses gunicorn, not this block
