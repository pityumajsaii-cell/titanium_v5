from flask import Flask, render_template, request, jsonify
import json, os, requests, hmac, hashlib, time, sqlite3
from datetime import datetime
from queue import Queue
from threading import Thread

# PostgreSQL import kezelése
try:
    import psycopg2
    from psycopg2.extras import Json
except ImportError:
    psycopg2 = None

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET', 'titanium_v5_hardened')

DB_URL = os.getenv('DATABASE_URL')
STRIPE_WEBHOOK_SECRET = os.getenv('STRIPE_WEBHOOK_SECRET')
TG_TOKEN = os.getenv('TG_TOKEN')
TG_CHAT_ID = os.getenv('TG_CHAT_ID')
BRIDGE_SECRET = os.getenv('BRIDGE_SECRET', 'TITANIUM_SECURE_TOKEN_2026')

# --- DB CONNECTION HELPER ---
def get_db_connection():
    if DB_URL and psycopg2:
        return psycopg2.connect(DB_URL)
    return sqlite3.connect("titanium_core.db")

# --- DB INITIALIZATION (HYBRID SUPPORT) ---
def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    if DB_URL and psycopg2:
        cur.execute('''CREATE TABLE IF NOT EXISTS events (
            id SERIAL PRIMARY KEY, type TEXT, data JSONB, status TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
        cur.execute('''CREATE TABLE IF NOT EXISTS payments (
            id SERIAL PRIMARY KEY, stripe_id TEXT, amount TEXT, status TEXT, customer_email TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    else:
        cur.execute('''CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT, type TEXT, data TEXT, status TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
        cur.execute('''CREATE TABLE IF NOT EXISTS payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT, stripe_id TEXT, amount TEXT, status TEXT, customer_email TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    cur.close()
    conn.close()

# --- WORKER SYSTEM (DATABASE SAVING) ---
task_queue = Queue()

def titanium_worker():
    while True:
        event = task_queue.get()
        if event is None: break
        
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            e_type, e_data = event['type'], event['data']
            
            # DB MENTÉS (Postgres vs SQLite)
            if DB_URL and psycopg2:
                cur.execute("INSERT INTO events (type, data, status) VALUES (%s, %s, %s)", 
                            (e_type, json.dumps(e_data), "processed"))
            else:
                cur.execute("INSERT INTO events (type, data, status) VALUES (?, ?, ?)", 
                            (e_type, json.dumps(e_data), "processed"))
            
            conn.commit()
            cur.close()
            conn.close()

            # Telegram riasztás
            msg = f"🛰️ <b>V5.1 WORKER:</b> {e_type.upper()}\nAdat mentve az adatbázisba."
            requests.post(f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage", 
                          json={"chat_id": TG_CHAT_ID, "text": msg, "parse_mode": "HTML"}, timeout=5)
        except Exception as e:
            print(f"Worker Error: {e}")
        
        task_queue.task_done()

Thread(target=titanium_worker, daemon=True).start()

# --- ROUTES ---
@app.route('/api/bridge', methods=['POST'])
def bridge():
    raw = request.get_data(as_text=True)
    sig = request.headers.get("X-TITANIUM-SIGNATURE")
    expected = hmac.new(BRIDGE_SECRET.encode(), raw.encode(), hashlib.sha256).hexdigest()
    
    if not hmac.compare_digest(expected, sig or ""):
        return jsonify({"status": "denied"}), 403

    data = request.json
    task_queue.put({"type": "lead_ingest", "data": data})
    return jsonify({"status": "accepted_v5.1"}), 202

@app.route('/admin/stats')
def stats():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM events")
        count = cur.fetchone()[0]
        cur.close()
        conn.close()
        return f"<h1>Titanium V5.1 Status</h1><p>Adatbázis események: {count}</p>"
    except:
        return "Admin DB Error"

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 7860)))
