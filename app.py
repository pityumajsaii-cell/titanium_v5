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
app.secret_key = os.getenv('FLASK_SECRET', 'titanium_v5_hardened_2026')

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

def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    if DB_URL and psycopg2:
        cur.execute('''CREATE TABLE IF NOT EXISTS events (id SERIAL PRIMARY KEY, type TEXT, data JSONB, status TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
        cur.execute('''CREATE TABLE IF NOT EXISTS payments (id SERIAL PRIMARY KEY, stripe_id TEXT, amount TEXT, status TEXT, customer_email TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    else:
        cur.execute('''CREATE TABLE IF NOT EXISTS events (id INTEGER PRIMARY KEY AUTOINCREMENT, type TEXT, data TEXT, status TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
        cur.execute('''CREATE TABLE IF NOT EXISTS payments (id INTEGER PRIMARY KEY AUTOINCREMENT, stripe_id TEXT, amount TEXT, status TEXT, customer_email TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    cur.close()
    conn.close()

# --- ADMIN SECURITY ---
def verify_admin(req):
    auth = req.headers.get("Authorization", "")
    return auth == f"Bearer {ADMIN_TOKEN}"

# --- ROUTES ---
@app.route('/')
def health_check():
    return "<h1>Titanium V5.3 Online</h1><p>Status: Healthy</p>", 200

@app.route('/admin/stats')
def stats():
    if not verify_admin(request):
        return jsonify({"error": "unauthorized"}), 401
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM payments")
        count = cur.fetchone()[0]
        if DB_URL:
            cur.execute("SELECT COALESCE(SUM(CAST(amount AS FLOAT)), 0) FROM payments")
        else:
            cur.execute("SELECT COALESCE(SUM(amount), 0) FROM payments")
        rev = cur.fetchone()[0]
        cur.close()
        conn.close()
        return jsonify({"status": "online", "payments": count, "revenue_eur": rev})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/webhook', methods=['POST'])
def webhook():
    payload = request.get_data()
    sig_header = request.headers.get('Stripe-Signature')
    try:
        event = stripe.Webhook.construct_event(payload, sig_header, STRIPE_WEBHOOK_SECRET)
        if event['type'] == 'checkout.session.completed':
            session = event['data']['object']
            # Payment process logic here...
            msg = f"💰 <b>PÉNZ ÉRKEZETT!</b>\n📧 {session.get('customer_details', {}).get('email')}"
            requests.post(f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage", json={"chat_id": TG_CHAT_ID, "text": msg, "parse_mode": "HTML"})
        return jsonify(success=True)
    except Exception as e:
        return jsonify(error=str(e)), 400

if __name__ == '__main__':
    init_db()
    # Render-kompatibilis port kezelés
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
