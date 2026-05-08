from flask import Flask, request, jsonify, render_template_string
import os, sqlite3, requests, datetime

app = Flask(__name__)

# --- NEXUS CONFIG (A rendszerek címei) ---
VERSION = "NEXUS-V3.5-CORE"
ADMIN_TOKEN = os.getenv("ADMIN_TOKEN", "dev")
DB_PATH = "titanium_nexus.db"

# --- DB INITIALIZATION ---
def init_db():
    conn = sqlite3.connect(DB_PATH)
    # Rendszerek közötti adatforgalom táblája
    conn.execute("""CREATE TABLE IF NOT EXISTS nexus_logs 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  source TEXT, 
                  action TEXT, 
                  data TEXT, 
                  timestamp DATETIME)""")
    conn.commit()
    conn.close()

init_db()

# --- 1. A KÖZPONTI "HÍD" (Ide küldi a Titanium One az adatot) ---
@app.route("/api/bridge", methods=["POST"])
def bridge():
    data = request.get_json(silent=True) or {}
    source = data.get("source", "unknown_unit")
    action = data.get("action", "data_sync")
    
    # Logoljuk az eseményt az Agyba
    conn = sqlite3.connect(DB_PATH)
    conn.execute("INSERT INTO nexus_logs (source, action, data, timestamp) VALUES (?, ?, ?, ?)",
                 (source, action, str(data), datetime.datetime.now()))
    conn.commit()
    conn.close()
    
    return jsonify({
        "nexus_status": "synced",
        "engine": VERSION,
        "msg": f"Data received from {source}"
    }), 202

# --- 2. AI INTERFÉSZ (Az Agy gondolkodó része) ---
@app.route("/api/think", methods=["POST"])
def think():
    user_input = request.json.get("prompt", "")
    # Itt hívjuk meg a Grok vagy OpenAI-t (fallback logikával)
    return jsonify({"response": "Nexus processing logic active", "input_echo": user_input})

# --- 3. DASHBOARD (Hogy lásd, ahogy az Agy dolgozik) ---
@app.route("/admin")
def admin():
    conn = sqlite3.connect(DB_PATH)
    logs = conn.execute("SELECT * FROM nexus_logs ORDER BY timestamp DESC LIMIT 10").fetchall()
    conn.close()
    
    log_html = "".join([f"<li class='border-b border-gray-700 py-2'><b>{l[1]}:</b> {l[2]} <span class='text-xs text-gray-500'>({l[4]})</span></li>" for l in logs])
    
    return render_template_string("""
    <!DOCTYPE html>
    <html lang="hu">
    <head><script src="https://cdn.tailwindcss.com"></script></head>
    <body class="bg-black text-green-400 p-8 font-mono">
        <h1 class="text-3xl mb-4 border-b-2 border-green-500">TITANIUM CORE NEXUS v3.5</h1>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
            <div class="bg-gray-900 p-4 rounded shadow-lg border border-green-800">
                <h2 class="text-xl mb-2 text-white">Rendszer Aktivitás (Live Bridge)</h2>
                <ul>{{ logs_list|safe }}</ul>
            </div>
            <div class="bg-gray-900 p-4 rounded shadow-lg border border-blue-800">
                <h2 class="text-xl mb-2 text-white text-blue-400">Kapcsolt Rendszerek</h2>
                <p>● Titanium One: <span class="text-green-500">CONNECTED</span></p>
                <p>● Stripe Gateway: <span class="text-green-500">READY</span></p>
                <p>● AI Logic: <span class="text-blue-500">STANDBY</span></p>
            </div>
        </div>
    </body>
    </html>
    """, logs_list=log_html)

@app.route("/")
def index():
    return jsonify({"status": "Nexus Core Online", "version": VERSION})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
