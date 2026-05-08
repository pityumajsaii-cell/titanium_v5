from flask import Flask, render_template, request, session
import json, os, requests
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET', 'titanium_v5_fallback')

# KULCSOK KIOLVASÁSA A RENDSZERBŐL (Biztonságos mód)
STRIPE_SECRET_KEY = os.getenv('STRIPE_SECRET')
TG_TOKEN = os.getenv('TG_TOKEN')
TG_CHAT_ID = os.getenv('TG_CHAT_ID')

def send_tg_msg(text):
    if not TG_TOKEN: return
    try:
        url = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"
        requests.post(url, json={"chat_id": TG_CHAT_ID, "text": text})
    except: pass

def load_json(file):
    if os.path.exists(file):
        with open(file, 'r', encoding='utf-8') as f:
            try: return json.load(f)
            except: return []
    return []

@app.route('/')
def index():
    products = load_json('products.json')
    return render_template('index.html', products=products)

@app.route('/lead', methods=['POST'])
def lead():
    name = request.form.get('name')
    email = request.form.get('email')
    msg = request.form.get('message')
    leads = load_json('leads.json')
    leads.append({"date": datetime.now().strftime("%Y-%m-%d %H:%M"), "name": name, "email": email, "msg": msg})
    with open('leads.json', 'w') as f: json.dump(leads, f)
    send_tg_msg(f"🚀 TITANIUM LEAD!\nNév: {name}\nEmail: {email}\nÜzenet: {msg}")
    return "<h1>Köszönjük!</h1><p>A rendszer rögzítette az igényét.</p><a href='/'>Vissza</a>"

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST' and request.form.get('password') == 'admin123':
        session['logged_in'] = True
    if not session.get('logged_in'):
        return '<div style="text-align:center;padding:50px;"><h2>Admin Panel</h2><form method="post"><input type="password" name="password"><button>Belépés</button></form></div>'
    leads = load_json('leads.json')
    return render_template('admin.html', leads=leads)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 7860))
    app.run(host='0.0.0.0', port=port)
