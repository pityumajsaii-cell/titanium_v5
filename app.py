from flask import Flask, request, jsonify, render_template_string
import os, sqlite3, datetime, json

app = Flask(__name__)
VERSION = "TITANIUM-TRINITY-V6.0"
DB_PATH = "titanium_core.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("CREATE TABLE IF NOT EXISTS core_vault (id INTEGER PRIMARY KEY AUTOINCREMENT, source TEXT, type TEXT, val REAL, timestamp DATETIME)")
    conn.commit()
    conn.close()

init_db()

@app.route("/api/bridge", methods=["POST"])
def bridge():
    data = request.get_json(silent=True) or {}
    val = data.get("value", 0)
    conn = sqlite3.connect(DB_PATH)
    conn.execute("INSERT INTO core_vault (source, type, val, timestamp) VALUES (?, ?, ?, ?)",
                 (data.get("source", "Titanium-Unit"), data.get("type", "DATA"), val, datetime.datetime.now()))
    conn.commit()
    conn.close()
    return jsonify({"status": "SUCCESS", "ai_analysis": "GOLD" if val > 200 else "SILVER"}), 202

@app.route("/admin")
def admin():
    conn = sqlite3.connect(DB_PATH)
    vault = conn.execute("SELECT * FROM core_vault ORDER BY timestamp DESC LIMIT 10").fetchall()
    conn.close()
    return render_template_string("<h1>Titanium Core Admin</h1><ul>{% for i in vault %}<li>{{ i[4] }} - {{ i[1] }}: {{ i[3] }} EUR</li>{% endfor %}</ul>", vault=vault)

@app.route("/")
def health():
    return "Titanium Trinity Engine: ONLINE", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=7860)
