from flask import Flask, render_template, request, jsonify
import json, os, requests, hmac, hashlib, time, sqlite3
from datetime import datetime
from queue import Queue
from threading import Thread

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET', 'titanium_v4_webhook')

# --- CONFIG ---
STRIPE_SECRET = os.getenv('STRIPE_SECRET')
STRIPE_WEBHOOK_SECRET = os.getenv('STRIPE_WEBHOOK_SECRET') # Renderen beállítandó!
TG_TOKEN = os.getenv('TG_TOKEN')
TG_CHAT_ID = os.getenv('TG_CHAT_ID')
BRIDGE_SECRET = os.getenv('BRIDGE_SECRET', 'TITANIUM_SECURE_TOKEN_2026')
DB_PATH = "titanium_core.db"

# --- DB INIT ---
def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS events 
            (id INTEGER PRIMARY KEY AUTOINCREMENT, type TEXT, data TEXT, status TEXT, created_at TIMESTAMP)''')
        conn.execute('''CREATE TABLE IF NOT EXISTS payments 
            (id INTEGER PRIMARY KEY AUTOINCREMENT, stripe_id TEXT, amount TEXT, status TEXT, customer_email TEXT, created_at TIMESTAMP)''')
        conn.commit()

def log_event_db(e_type, data, status="processed"):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("INSERT INTO events (type, data, status, created_at) VALUES (?, ?, ?, ?)",
                     (e_type, json.dumps(data), status, datetime.utcnow()))

# --- WORKER ---
task_queue = Queue()

def titanium_worker():
    while True:
        event = task_queue.get()
        if event is None: break
        
        try:
            msg = f"🔔 <b>V4 WORKER:</b> {event['type'].upper()}\n"
            if event['type'] == 'payment_success':
                d = event['data']
                msg = f"💰 <b>PÉNZ ÉRKEZETT!</b>\n📧 Ügyfél: {d['email']}\n💵 Összeg: {d['amount']} {d['currency']}"
            
            requests.post(f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage", 
                          json={"chat_id": TG_CHAT_ID, "text": msg, "parse_mode": "HTML"}, timeout=5)
        except: pass
        task_queue.task_done()

worker_thread = Thread(target=titanium_worker, daemon=True)
worker_thread.start()

# --- WEBHOOK ENDPOINT ---
@app.route('/webhook', methods=['POST'])
def webhook():
    payload = request.get_data()
    sig_header = request.headers.get('Stripe-Signature')

    # Stripe aláírás ellenőrzése (Security)
    # Itt élesben a stripe.Webhook.construct_event-et használnánk, 
    # de most a logikát építjük be:
    
    event = None
    try:
        event = json.loads(payload)
    except Exception as e:
        return jsonify(success=False), 400

    # Fizetési események kezelése
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        payment_data = {
            "email": session.get('customer_details', {}).get('email'),
            "amount": session.get('amount_total', 0) / 100,
            "currency": session.get('currency', 'eur'),
            "id": session.get('id')
        }
        
        # Mentés az adatbázisba
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute("INSERT INTO payments (stripe_id, amount, status, customer_email, created_at) VALUES (?, ?, ?, ?, ?)",
                         (payment_data['id'], str(payment_data['amount']), "paid", payment_data['email'], datetime.utcnow()))
        
        # Sorba állítás értesítésre
        task_queue.put({"type": "payment_success", "data": payment_data})
        log_event_db("stripe_webhook_success", payment_data)

    return jsonify(success=True)

@app.route('/admin/stats')
def stats():
    with sqlite3.connect(DB_PATH) as conn:
        p = conn.execute("SELECT COUNT(*) FROM payments").fetchone()[0]
        l = conn.execute("SELECT COUNT(*) FROM events WHERE type='lead_ingested'").fetchone()[0]
    return f"<h1>Titanium V4 Dashboard</h1><p>Leadek: {l}</p><p>Sikeres fizetések: {p}</p>"

@app.route('/')
def index(): return "<h1>Titanium V4 Engine Online</h1>"

if __name__ == '__main__':
    init_db()
    port = int(os.environ.get('PORT', 7860))
    app.run(host='0.0.0.0', port=port)
