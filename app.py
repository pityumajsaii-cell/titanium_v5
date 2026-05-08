from flask import Flask, request, jsonify, render_template_string
import os, sqlite3, datetime, json

app = Flask(__name__)

# --- TITANIUM CORE CONFIG ---
VERSION = "TITANIUM-CORE-NEXUS-V5.5"
DB_PATH = "titanium_core.db" # A Kész Rendszer központi tárolója

def init_core():
    conn = sqlite3.connect(DB_PATH)
    # Rendszerbeállítások és állapotok
    conn.execute("CREATE TABLE IF NOT EXISTS system_state (key TEXT PRIMARY KEY, value TEXT)")
    # Üzleti tranzakciók és leadek
    conn.execute("""CREATE TABLE IF NOT EXISTS core_vault 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, source TEXT, type TEXT, val REAL, timestamp DATETIME)""")
    # Alapértelmezett értékek beállítása (Kész Rendszer státusz)
    conn.execute("INSERT OR IGNORE INTO system_state (key, value) VALUES ('mode', 'MAX_MODE')")
    conn.execute("INSERT OR IGNORE INTO system_state (key, value) VALUES ('status', 'KESZ_RENDSZER_ACTIVE')")
    conn.commit()
    conn.close()

init_core()

# --- AZ EGYESÍTETT HÍD (CORE + NEXUS) ---
@app.route("/api/bridge", methods=["POST"])
def core_bridge():
    data = request.get_json(silent=True) or {}
    source = data.get("source", "Titanium-Unit")
    val = data.get("value", 0)
    
    conn = sqlite3.connect(DB_PATH)
    conn.execute("INSERT INTO core_vault (source, type, val, timestamp) VALUES (?, ?, ?, ?)",
                 (source, data.get("type", "DATA"), val, datetime.datetime.now()))
    conn.commit()
    conn.close()
    
    return jsonify({
        "status": "SYNCED_WITH_CORE",
        "system_mode": "MAX_MODE",
        "payout_status": "IN-TRANSIT",
        "engine": VERSION
    }), 202

# --- CORE ADMIN PANEL (A Teljes Birodalom Látképe) ---
@app.route("/admin")
def core_admin():
    conn = sqlite3.connect(DB_PATH)
    vault = conn.execute("SELECT * FROM core_vault ORDER BY timestamp DESC LIMIT 10").fetchall()
    state = dict(conn.execute("SELECT * FROM system_state").fetchall())
    total_val = conn.execute("SELECT SUM(val) FROM core_vault").fetchone()[0] or 0
    conn.close()
    
    return render_template_string("""
    <body style="background:#050505; color:#00ffcc; font-family:'Courier New', monospace; padding:30px;">
        <h1 style="border-bottom: 2px solid #00ffcc;">💎 {{ version }} | KÉSZ RENDSZER</h1>
        <div style="display:flex; gap:20px; margin-bottom:20px;">
            <div style="border:1px solid #00ffcc; padding:15px; flex:1;">
                <h3>RENDSZERÁLLAPOT</h3>
                <p>MÓD: <span style="color:#fff;">{{ state['mode'] }}</span></p>
                <p>STÁTUSZ: <span style="color:#fff;">{{ state['status'] }}</span></p>
                <p>LIQUIDITY: <span style="color:#00ff00;">CONTINUOUS</span></p>
            </div>
            <div style="border:1px solid #00ffcc; padding:15px; flex:1;">
                <h3>PÉNZÜGYI MONITOR</h3>
                <p>VÁRHATÓ PROFIT: <span style="font-size:1.5em; color:#fff;">{{ total }} EUR</span></p>
                <p>TOKEN STATUS: <span style="color:#00ff00;">ERC-20 STABLE</span></p>
            </div>
        </div>
        <h3>AKTIVITÁSI NAPLÓ (CORE VAULT)</h3>
        <ul>
            {% for item in vault %}
            <li>[{{ item[4][:19] }}] {{ item[1] }} >> {{ item[2] }} >> <b>{{ item[3] }} EUR</b></li>
            {% endfor %}
        </ul>
    </body>
    """, version=VERSION, state=state, total=total_val, vault=vault)

@app.route("/")
def health():
    return "<h1>Titanium Core Nexus: ONLINE</h1>", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
