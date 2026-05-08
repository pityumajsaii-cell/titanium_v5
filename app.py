from flask import Flask, render_template, request, jsonify
import json, os, requests, hmac, hashlib, time, sqlite3, stripe
from datetime import datetime
from queue import Queue
from threading import Thread

try:
    import psycopg2
except ImportError:
    psycopg2 = None

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET', 'titanium_v5_hardened_final')

# --- CONFIG ---
DB_URL = os.getenv('DATABASE_URL')
STRIPE_SECRET = os.getenv('STRIPE_SECRET')
STRIPE_WEBHOOK_SECRET = os.getenv('STRIPE_WEBHOOK_SECRET')
ADMIN_TOKEN = os.getenv("ADMIN_TOKEN", "TITANIUM_ADMIN_DEFAULT_2026")
TG_TOKEN = os.getenv('TG_TOKEN')
TG_CHAT_ID = os.getenv('TG_CHAT_ID')
BRIDGE_SECRET = os.getenv('BRIDGE_SECRET', 'TITANIUM_SECURE_TOKEN_2026')

stripe.api_key = STRIPE_SECRET

def get_db_connection():
    if DB_URL and psycopg2:
        return psycopg2.connect(DB_URL)
    return sqlite3.connect("titanium_core.db")

# --- ADMIN SECURITY HELPER ---
def verify_admin(req):
    auth = req.headers.get("Authorization", "")
    return auth == f"Bearer {ADMIN_TOKEN}"

# --- SECURE ADMIN ENDPOINT ---
@app.route('/admin/stats')
def stats():
    if not verify_admin(request):
        return jsonify({"error": "unauthorized"}), 401

    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Fizetések száma
        cur.execute("SELECT COUNT(*) FROM payments")
        payments_count = cur.fetchone()[0]

        # Összbevétel (Postgres/SQLite hibrid kezeléssel)
        if DB_URL:
            cur.execute("SELECT COALESCE(SUM(CAST(amount AS FLOAT)), 0) FROM payments")
        else:
            cur.execute("SELECT COALESCE(SUM(amount), 0) FROM payments")
        
        revenue = cur.fetchone()[0]

        cur.close()
        conn.close()

        return jsonify({
            "status": "online",
            "system": "Titanium V5.3 Enterprise",
            "metrics": {
                "total_payments": payments_count,
                "total_revenue_eur": revenue
            }
        })
    except Exception as e:
        return jsonify({"status": "db_error", "error": str(e)}), 500

# (Itt maradt a korábbi /webhook és /api/bridge logika...)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 7860))
    app.run(host='0.0.0.0', port=port)
