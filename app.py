from flask import Flask, request, jsonify, render_template_string
import os, sqlite3, requests, datetime, json

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET', 'titanium_business_intelligence_2026')

# --- ÜZLETI KONFIGURÁCIÓ ---
VERSION = "BUSINESS-BRAIN-V4.0"
ADMIN_TOKEN = os.getenv("ADMIN_TOKEN", "dev")
DB_PATH = "business_vault.db"

# --- RENDSZER-SZINTŰ ÖSSZEKÖTÉS ---
def init_business_db():
    conn = sqlite3.connect(DB_PATH)
    # Üzleti események (Leadek, Tranzakciók, AI döntések)
    conn.execute("""CREATE TABLE IF NOT EXISTS business_flow 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  module TEXT, 
                  intent TEXT, 
                  value REAL, 
                  metadata TEXT, 
                  timestamp DATETIME)""")
    conn.commit()
    conn.close()

init_business_db()

# --- AZ AGY DÖNTÉSI LOGIKÁJA (The Multi-System Orchestrator) ---
def process_business_logic(data):
    # Itt dől el, hogy mi történjen az adattal
    source = data.get("source", "unknown")
    payload = data.get("payload", {})
    
    # Példa: Ha a Titanium One talált egy 'hot lead'-et
    if "lead" in payload:
        # 1. AI elemzés meghívása (Grok/OpenAI)
        # 2. Ha az érték > 100 EUR, azonnali értesítés küldése
        return {"action": "STORE_AND_NOTIFY", "priority": "HIGH"}
    
    return {"action": "ARCHIVE", "priority": "LOW"}

# --- KÖZPONTI ÜZLETI BRIDGE ---
@app.route("/api/bridge", methods=["POST"])
def bridge():
    data = request.get_json(silent=True) or {}
    
    # Az Agy elemzi az érkező adatot
    decision = process_business_logic(data)
    
    conn = sqlite3.connect(DB_PATH)
    conn.execute("INSERT INTO business_flow (module, intent, value, metadata, timestamp) VALUES (?, ?, ?, ?, ?)",
                 (data.get("source"), decision["action"], data.get("value", 0), json.dumps(data), datetime.datetime.now()))
    conn.commit()
    conn.close()
    
    return jsonify({
        "status": "PROCESSED",
        "brain_decision": decision,
        "engine": VERSION
    }), 202

# --- ÜZLETI DASHBOARD (Valós idejű kontroll) ---
@app.route("/admin")
def business_dashboard():
    conn = sqlite3.connect(DB_PATH)
    flows = conn.execute("SELECT * FROM business_flow ORDER BY timestamp DESC LIMIT 20").fetchall()
    total_val = conn.execute("SELECT SUM(value) FROM business_flow").fetchone()[0] or 0
    conn.close()
    
    return render_template_string("""
    <!DOCTYPE html>
    <html lang="hu">
    <head>
        <script src="https://cdn.tailwindcss.com"></script>
        <title>Titanium Business Brain</title>
    </head>
    <body class="bg-slate-900 text-white p-6 font-mono">
        <div class="max-w-6xl mx-auto">
            <header class="flex justify-between items-center border-b border-blue-500 pb-4 mb-8">
                <h1 class="text-4xl font-black text-blue-500">TITANIUM <span class="text-white">BRAIN</span></h1>
                <div class="text-right">
                    <p class="text-sm text-gray-400">Rendszer: {{ version }}</p>
                    <p class="text-2xl text-green-400 font-bold">VÁRHATÓ PROFIT: {{ total }} EUR</p>
                </div>
            </header>

            <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
                {% for item in flows %}
                <div class="bg-slate-800 p-4 rounded-lg border-l-4 {% if item[2] == 'STORE_AND_NOTIFY' %}border-green-500{% else %}border-blue-500{% endif %}">
                    <div class="flex justify-between text-xs text-gray-500 mb-2">
                        <span>{{ item[1] }}</span>
                        <span>{{ item[5][:16] }}</span>
                    </div>
                    <p class="font-bold text-lg">{{ item[2] }}</p>
                    <p class="text-sm text-gray-300 italic">Érték: {{ item[3] }} EUR</p>
                </div>
                {% endfor %}
            </div>
        </div>
    </body>
    </html>
    """, version=VERSION, total=total_val, flows=flows)

@app.route("/")
def health():
    return jsonify({"status": "Business Brain Active", "engine": VERSION})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
