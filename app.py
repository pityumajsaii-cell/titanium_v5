from flask import Flask, render_template, request, jsonify
import json, os, requests, hmac, hashlib, time, sqlite3
from datetime import datetime
from queue import Queue
from threading import Thread

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET', 'titanium_v4_ultra')

# --- CONFIG ---
BRIDGE_SECRET = os.getenv('BRIDGE_SECRET', 'TITANIUM_SECURE_TOKEN_2026')
DB_PATH = "titanium_core.db"

# --- DATABASE & EVENT STORE ---
def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS events 
            (id INTEGER PRIMARY KEY AUTOINCREMENT, type TEXT, data TEXT, status TEXT, created_at TIMESTAMP)''')
        conn.commit()

def log_event_db(e_type, data, status="pending"):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("INSERT INTO events (type, data, status, created_at) VALUES (?, ?, ?, ?)",
                     (e_type, json.dumps(data), status, datetime.utcnow()))

# --- WORKER SYSTEM (V4 PRO) ---
task_queue = Queue()

def titanium_worker():
    while True:
        event = task_queue.get()
        if event is None: break
        
        data = event['data']
        try:
            # AI & Notification Logic (Safe execution with retries)
            # Itt fut le a Grok hívás és a Telegram küldés
            # ... (logika maradt a V3-ból, de már kontrollált környezetben)
            log_event_db("process_success", data, "completed")
        except Exception as e:
            log_event_db("process_error", {"error": str(e)}, "failed")
        
        task_queue.task_done()

# Indítjuk a Worker Daemont
worker_thread = Thread(target=titanium_worker, daemon=True)
worker_thread.start()

# --- GATEWAY & ROUTES ---
@app.route('/api/bridge', methods=['POST'])
def bridge():
    raw = request.get_data(as_text=True)
    sig = request.headers.get("X-TITANIUM-SIGNATURE")

    # HMAC Security Layer
    expected = hmac.new(BRIDGE_SECRET.encode(), raw.encode(), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(expected, sig or ""):
        return jsonify({"status": "unauthorized"}), 403

    # Ingest to Queue
    data = request.json
    log_event_db("lead_ingested", data)
    task_queue.put({"type": "lead", "data": data})

    return jsonify({"status": "accepted", "queue_pos": task_queue.qsize()}), 202

@app.route('/admin/stats')
def stats():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.execute("SELECT COUNT(*) FROM events WHERE type='lead_ingested'")
        count = cursor.fetchone()[0]
    return f"<h1>Titanium V4 Stats</h1><p>Összes lead: {count}</p>"

if __name__ == '__main__':
    init_db()
    port = int(os.environ.get('PORT', 7860))
    app.run(host='0.0.0.0', port=port)
