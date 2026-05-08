from flask import Flask, render_template, request, session, jsonify
import json, os, requests
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET', 'titanium_unified_2026')

# KULCSOK (Render Environment-ből)
STRIPE_SECRET = os.getenv('STRIPE_SECRET')
GROK_API_KEY = os.getenv('GROK_API_KEY')
TG_TOKEN = os.getenv('TG_TOKEN')
TG_CHAT_ID = os.getenv('TG_CHAT_ID')

def get_ai_analysis(data):
    """Grok AI mélyelemzés az összekapcsolt rendszerekhez"""
    if not GROK_API_KEY: return "AI Offline"
    try:
        headers = {"Authorization": f"Bearer {GROK_API_KEY}", "Content-Type": "application/json"}
        payload = {
            "model": "grok-1",
            "messages": [
                {"role": "system", "content": "Te a Titanium Birodalom központi AI-ja vagy. Elemezd a Titanium One-ból érkező leadet."},
                {"role": "user", "content": f"Ügyfél adatai: {data}"}
            ]
        }
        resp = requests.post("https://api.x.ai/v1/chat/completions", headers=headers, json=payload, timeout=10)
        return resp.json()['choices'][0]['message']['content']
    except: return "Elemzési hiba."

def send_tg(msg):
    if not TG_TOKEN: return
    requests.post(f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage", 
                  json={"chat_id": TG_CHAT_ID, "text": msg, "parse_mode": "HTML"})

@app.route('/')
def index():
    products = []
    if os.path.exists('products.json'):
        with open('products.json', 'r') as f: products = json.load(f)
    return render_template('index.html', products=products)

# --- TITANIUM ONE BRIDGE ---
@app.route('/api/bridge', methods=['POST'])
def bridge():
    """Ide küldi a Titanium One az ügyfeleket"""
    data = request.json
    source = data.get('source', 'Titanium One')
    name = data.get('name', 'Névtelen')
    email = data.get('email', 'Nincs email')
    
    # Grok AI elemzés
    analysis = get_ai_analysis(data)
    
    # Riasztás küldése
    alert = f"🔗 <b>TITANIUM SYNC: {source}</b>\n👤 Név: {name}\n📧 Email: {email}\n\n🤖 <b>AI STRATÉGIA:</b>\n{analysis}"
    send_tg(alert)
    
    return jsonify({"status": "success", "message": "Lead synced to V5.5"}), 200

@app.route('/lead', methods=['POST'])
def lead():
    # Helyi lead kezelés (weboldalról)
    name, email, msg = request.form.get('name'), request.form.get('email'), request.form.get('message')
    analysis = get_ai_analysis(f"Név: {name}, Üzenet: {msg}")
    send_tg(f"🚀 <b>WEB LEAD</b>\nNév: {name}\nÜzenet: {msg}\n\n🤖 <b>AI:</b> {analysis}")
    return "<h1>Sikeres regisztráció!</h1><a href='/'>Vissza</a>"

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 7860))
    app.run(host='0.0.0.0', port=port)
