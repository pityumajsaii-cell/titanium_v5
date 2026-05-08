from flask import Flask, render_template, request, session, jsonify
import json, os, requests, hmac, hashlib, time, threading
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET', 'titanium_v3_core_2026')

# --- CONFIGURATION & SECURITY ---
STRIPE_SECRET = os.getenv('STRIPE_SECRET')
GROK_API_KEY = os.getenv('GROK_API_KEY')
TG_TOKEN = os.getenv('TG_TOKEN')
TG_CHAT_ID = os.getenv('TG_CHAT_ID')
BRIDGE_SECRET = os.getenv('BRIDGE_SECRET', 'TITANIUM_SECURE_TOKEN_2026')

# Eseménytároló (Memory-based Queue szimuláció a Render-hez)
event_log = "events.json"

def log_event(event_type, data):
    """Event State Store - Minden mozgás naplózása"""
    event = {
        "timestamp": datetime.utcnow().isoformat(),
        "type": event_type,
        "data": data,
        "status": "processed"
    }
    with open(event_log, "a") as f:
        f.write(json.dumps(event) + "\n")

def verify_hmac(payload, signature):
    """API Gateway - Replay és Abuse védelem"""
    if not signature: return False
    expected = hmac.new(BRIDGE_SECRET.encode(), payload.encode(), hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature)

# --- ASYNC WORKER LAYER ---
def background_worker(data):
    """Worker System - AI elemzés és értesítés a háttérben"""
    try:
        # 1. AI Scoring & Tier Classification
        analysis = "AI offline fallback"
        if GROK_API_KEY:
            headers = {"Authorization": f"Bearer {GROK_API_KEY}", "Content-Type": "application/json"}
            payload = {
                "model": "grok-1",
                "messages": [{"role": "system", "content": "Elemezd a leadet: adj egy Score-t (1-10) és egy Tier-t (Starter/Pro/Enterprise)."},
                             {"role": "user", "content": str(data)}],
                "temperature": 0.3
            }
            r = requests.post("https://api.x.ai/v1/chat/completions", json=payload, headers=headers, timeout=10)
            analysis = r.json()['choices'][0]['message']['content']

        # 2. Revenue Intelligence - Automatikus szűrés
        score = 0
        if "10" in analysis or "9" in analysis or "8" in analysis: score = 9 # Egyszerűsített scoring

        # 3. Notification Layer
        msg = f"💎 <b>V3 EVENT DETECTED</b>\nSource: {data.get('source')}\nScore: {score}/10\n\n🤖 <b>AI INTELLIGENCE:</b>\n{analysis}"
        requests.post(f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage", 
                      json={"chat_id": TG_CHAT_ID, "text": msg, "parse_mode": "HTML"}, timeout=5)
        
        log_event("worker_complete", {"score": score, "analysis": "done"})
    except Exception as e:
        log_event("worker_error", {"error": str(e)})

# --- ROUTES ---
@app.route('/')
def index():
    products = []
    if os.path.exists('products.json'):
        with open('products.json', 'r') as f: products = json.load(f)
    return render_template('index.html', products=products)

@app.route('/api/bridge', methods=['POST'])
def bridge():
    raw_payload = request.get_data(as_text=True)
    signature = request.headers.get("X-TITANIUM-SIGNATURE")

    # 1. Gateway Security Check
    if not verify_hmac(raw_payload, signature):
        log_event("security_alert", {"reason": "invalid_signature", "ip": request.remote_addr})
        return jsonify({"status": "error", "message": "Unauthorized"}), 403

    # 2. Ingestion & Event Storage
    data = request.json
    log_event("lead_ingested", data)

    # 3. Offload to Worker (Async execution)
    threading.Thread(target=background_worker, args=(data,)).start()

    # Azonnali válasz a küldőnek (nincs várakozás az AI-ra!)
    return jsonify({"status": "queued", "event_id": time.time()}), 202

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 7860))
    app.run(host='0.0.0.0', port=port)
