from flask import Flask, request, jsonify
import os, sqlite3, hmac, hashlib, json

app = Flask(__name__)

# --- CONFIG ---
ADMIN_TOKEN = os.getenv("ADMIN_TOKEN", "TITANIUM_ADMIN_DEFAULT_2026")
VERSION = "5.3.1-STABLE"

# --- GUARANTEED ROUTING ---
@app.route('/')
def index():
    # Ezzel ellenőrizzük, hogy EZ a kód fut-e
    return f"<h1>Titanium Engine v{VERSION}</h1><p>Status: Running</p>"

@app.route('/version')
def get_version():
    return jsonify({"version": VERSION, "deploy_status": "synchronized"})

@app.route('/admin/stats')
def stats():
    auth = request.headers.get("Authorization", "")
    if auth != f"Bearer {ADMIN_TOKEN}":
        return jsonify({"error": "unauthorized"}), 401
    return jsonify({"status": "active", "msg": "Database connected"})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
