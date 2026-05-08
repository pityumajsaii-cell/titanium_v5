from flask import Flask, request, jsonify, render_template_string
import os, sqlite3, requests, datetime, json

app = Flask(__name__)

# --- KONFIGURÁCIÓ ---
VERSION = "TITANIUM-GENESIS-V5"
DB_PATH = "titanium_vault.db"
ADMIN_TOKEN = os.getenv("ADMIN_TOKEN", "dev")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("CREATE TABLE IF NOT EXISTS system_logs (id INTEGER PRIMARY KEY AUTOINCREMENT, source TEXT, type TEXT, val REAL, data TEXT, time DATETIME)")
    conn.commit()
    conn.close()

init_db()

@app.route("/api/bridge", methods=["POST"])
def bridge():
    data = request.get_json(silent=True) or {}
    conn = sqlite3.connect(DB_PATH)
    conn.execute("INSERT INTO system_logs (source, type, val, data, time) VALUES (?, ?, ?, ?, ?)",
                 (data.get("source"), data.get("type", "DATA"), data.get("value", 0), str(data), datetime.datetime.now()))
    conn.commit()
    conn.close()
    return jsonify({"status": "SUCCESS", "engine": VERSION}), 202

@app.route("/admin")
def dashboard():
    conn = sqlite3.connect(DB_PATH)
    logs = conn.execute("SELECT * FROM system_logs ORDER BY time DESC LIMIT 15").fetchall()
    total = conn.execute("SELECT SUM(val) FROM system_logs").fetchone()[0] or 0
    conn.close()
    return render_template_string("""
    <body style="background:#000; color:#0f0; font-family:monospace; padding:20px;">
        <h1>💎 TITANIUM GENESIS DASHBOARD</h1>
        <hr border="1" color="#0f0">
        <h3>VÁRHATÓ ÖSSZES BEVÉTEL: {{ total }} EUR</h3>
        <ul>{% for l in logs %}<li>[{{ l[5][:19] }}] <b>{{ l[1] }}</b> -> {{ l[2] }} ({{ l[3] }} EUR)</li>{% endfor %}</ul>
    </body>
    """, logs=logs, total=total)

@app.route("/")
def health():
    return f"Titanium System V5: ONLINE", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
