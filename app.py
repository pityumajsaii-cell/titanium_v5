from flask import Flask, render_template, request, jsonify
import json, os, requests, hmac, hashlib, time, psycopg2
from datetime import datetime
from queue import Queue
from threading import Thread

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET', 'titanium_v5_ultra_secure')

# --- CONFIG ---
DB_URL = os.getenv('DATABASE_URL') # Ide jön a PostgreSQL elérése
STRIPE_SECRET = os.getenv('STRIPE_SECRET')
TG_TOKEN = os.getenv('TG_TOKEN')
TG_CHAT_ID = os.getenv('TG_CHAT_ID')
BRIDGE_SECRET = os.getenv('BRIDGE_SECRET', 'TITANIUM_SECURE_TOKEN_2026')

# --- DATABASE LAYER (POSTGRESQL) ---
def get_db_connection():
    # Fallback SQLite-ra, ha nincs megadva DATABASE_URL, de productionban Postgres kell!
    if DB_URL:
        return psycopg2.connect(DB_URL)
    import sqlite3
    return sqlite3.connect("titanium_core.db")

def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS events 
        (id SERIAL PRIMARY KEY, type TEXT, data JSONB, status TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    cur.execute('''CREATE TABLE IF NOT EXISTS payments 
        (id SERIAL PRIMARY KEY, stripe_id TEXT, amount TEXT, status TEXT, customer_email TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    cur.close()
    conn.close()

# --- WORKER & BUSINESS LOGIC ---
task_queue = Queue()

def titanium_worker():
    while True:
        event = task_queue.get()
        if event is None: break
        try:
            # Itt fut az AI scoring és a Telegram értesítés
            msg = f"🚀 <b>TITANIUM V5:</b> {event['type']}\nAdat: {json.dumps(event['data'])}"
            requests.post(f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage", 
                          json={"chat_id": TG_CHAT_ID, "text": msg, "parse_mode": "HTML"}, timeout=5)
        except: pass
        task_queue.task_done()

Thread(target=titanium_worker, daemon=True).start()

# --- ROUTES ---
@app.route('/api/bridge', methods=['POST'])
def bridge():
    raw = request.get_data(as_text=True)
    sig = request.headers.get("X-TITANIUM-SIGNATURE")
    
    # HMAC Check
    expected = hmac.new(BRIDGE_SECRET.encode(), raw.encode(), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(expected, sig or ""):
        return jsonify({"status": "denied"}), 403

    data = request.json
    task_queue.put({"type": "lead", "data": data})
    return jsonify({"status": "queued_in_v5"}), 202

@app.route('/admin/stats')
def stats():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM events")
    count = cur.fetchone()[0]
    cur.close()
    conn.close()
    return f"<h1>Titanium V5 Enterprise Dashboard</h1><p>Adatbázis: PostgreSQL</p><p>Események: {count}</p>"

if __name__ == '__main__':
    init_db()
    port = int(os.environ.get('PORT', 7860))
    app.run(host='0.0.0.0', port=port)
