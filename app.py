from flask import Flask, render_template, request, session
import json, os, requests
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET', 'titanium_ultra_v5')

# KULCSOK (Környezeti változókból)
STRIPE_SECRET = os.getenv('STRIPE_SECRET')
GROK_API_KEY = os.getenv('GROK_API_KEY')
TG_TOKEN = os.getenv('TG_TOKEN')
TG_CHAT_ID = os.getenv('TG_CHAT_ID')

def get_grok_analysis(user_msg):
    """Grok AI elemzés az ügyfél igényéről"""
    if not GROK_API_KEY: return "AI elemzés nem elérhető."
    try:
        headers = {"Authorization": f"Bearer {GROK_API_KEY}", "Content-Type": "application/json"}
        data = {
            "model": "grok-1",
            "messages": [
                {"role": "system", "content": "Te egy üzleti elemző vagy. Értékeld az ügyfél üzenetét profit szempontjából."},
                {"role": "user", "content": user_msg}
            ]
        }
        resp = requests.post("https://api.x.ai/v1/chat/completions", headers=headers, json=data)
        return resp.json()['choices'][0]['message']['content']
    except: return "Elemzési hiba történt."

def send_tg_alert(text):
    if not TG_TOKEN: return
    try:
        url = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"
        requests.post(url, json={"chat_id": TG_CHAT_ID, "text": text})
    except: pass

def load_db(file):
    if os.path.exists(file):
        with open(file, 'r', encoding='utf-8') as f:
            try: return json.load(f)
            except: return []
    return []

@app.route('/')
def index():
    products = load_db('products.json')
    return render_template('index.html', products=products)

@app.route('/lead', methods=['POST'])
def lead():
    name = request.form.get('name')
    email = request.form.get('email')
    msg = request.form.get('message')
    
    # Grok AI elemzés indítása
    ai_analysis = get_grok_analysis(msg)
    
    # Mentés az adatbázisba
    leads = load_db('leads.json')
    new_entry = {
        "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "name": name, "email": email, "msg": msg, "ai_score": ai_analysis
    }
    leads.append(new_entry)
    with open('leads.json', 'w') as f: json.dump(leads, f)
    
    # Telegram értesítés küldése az AI véleményével
    alert = f"🚀 ÚJ TITANIUM ÜGYFÉL!\n👤 Név: {name}\n📧 Email: {email}\n📝 Üzenet: {msg}\n\n🤖 AI ELEMZÉS:\n{ai_analysis}"
    send_tg_alert(alert)
    
    return "<h1>Aktiválva!</h1><p>A Titanium AI elemezte az igényét. Hamarosan jelentkezünk.</p><a href='/'>Vissza</a>"

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST' and request.form.get('password') == 'admin123':
        session['logged_in'] = True
    if not session.get('logged_in'):
        return '<div style="text-align:center;padding:50px;"><h2>Titanium Admin Panel</h2><form method="post"><input type="password" name="password"><button>Belépés</button></form></div>'
    leads = load_db('leads.json')
    return render_template('admin.html', leads=leads)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 7860))
    app.run(host='0.0.0.0', port=port)
