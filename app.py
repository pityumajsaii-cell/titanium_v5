from flask import Flask, request, jsonify
import os, hmac, hashlib

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET', 'titanium_final_stable_2026')

ADMIN_TOKEN = os.getenv("ADMIN_TOKEN", "TITANIUM_ADMIN_DEFAULT_2026")
VERSION = "5.3.2-STABLE"

@app.route('/')
def index():
    return f"<h1>Titanium V5.3 Online</h1><p>Version: {VERSION}</p>", 200

@app.route('/admin/stats')
def stats():
    auth = request.headers.get("Authorization", "")
    if auth != f"Bearer {ADMIN_TOKEN}":
        return jsonify({"error": "unauthorized"}), 401
    return jsonify({"status": "ok", "version": VERSION, "message": "Admin Access Granted"})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
