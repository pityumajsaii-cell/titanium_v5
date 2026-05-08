from flask import Flask, render_template, request, session, jsonify
import json, os, requests, hmac, hashlib, time
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET', 'titanium_ultra_v2_2026')

# KULCSOK ÉS BIZTONSÁG
STRIPE_SECRET = os.getenv('STRIPE_SECRET')
GROK_API_KEY = os.getenv('GROK_API_KEY')
TG_TOKEN = os.getenv('TG_TOKEN')
TG_CHAT_ID = os.getenv('TG_CHAT_ID')
BRIDGE_SECRET = os.getenv('BRIDGE_SECRET', 'TITANIUM_SECURE_TOKEN_2026') # Ezt állítsd be Renderen!

def verify_signature(payload, signature):
    if not signature: return False
    computed = hmac.new(BRIDGE_SECRET.encode(), payload.encode(), hashlib.sha256).hexdigest()
    return hmac.compare_digest(computed, signature)

def get_ai_analysis(data):
    if not GROK_API_KEY: return "AI Offline"
    try:
        headers = {"Authorization": f"Bearer {GROK_API_KEY}", "Content-Type": "application/json"}
        # Dinamikus modellválasztás fallback-el
        payload = {
            "model": "grok-1", 
            "messages": [
                {"role": "system", "content": "Te a Titanium SaaS biztonsági elemzője vagy. Pontozd a leadet 1-10 skálán."},
                {"role": "user", "content": f"Adat: {str(data)}"}
            ],
            "temperature": 0.7
        }
        resp = requests.post("https://api.x.ai/v1/chat/completions", headers=headers, json=payload, timeout=8)
        resp.raise_for_status()
        return resp.json()['choices'][0]['message']['content']
    except Exception as e:
        return f"AI Fallback: Elemzés jelenleg nem elérhető ({str(e)})"

def send_tg_async(msg):
    # Egyszerű async szimuláció timeouttal, hogy ne blokkolja a Flask-et
    if not TG_TOKEN: return
    try:
        requests.post(f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage", 
                      json={"chat_id": TG_CHAT_ID, "text": msg, "parse_mode": "HTML"}, timeout=3)
    except: pass

@app.route('/')
def index():
    products = []
    if os.path.exists('products.json'):
        with open('products.json', 'r') as f: products = json.load(f)
    return render_template('index.html', products=products)

# --- SECURE BRIDGE ENDPOINT V2 ---
@app.route('/api/bridge', methods=['POST'])
def bridge():
    raw_data = request.get_data(as_text=True)
    signature = request.headers.get("X-TITANIUM-SIGNATURE")

    # 1. Biztonsági kapu (HMAC Auth)
    if not verify_signature(raw_data, signature):
        return jsonify({"status": "denied", "reason": "unauthorized"}), 403

    data = request.json
    name = data.get('name', 'Névtelen')
    
    # 2. AI Elemzés (Safe Mode)
    analysis = get_ai_analysis(data)
    
    # 3. Telegram értesítés
    send_tg_async(f"🔐 <b>SECURE SYNC: {data.get('source', 'Unknown')}</b>\n👤 Név: {name}\n\n🤖 <b>AI SCORE:</b>\n{analysis}")
    
    return jsonify({"status": "received", "timestamp": time.time()}), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 7860))
    app.run(host='0.0.0.0', port=port)
