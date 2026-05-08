from flask import Flask, request, jsonify
import os, requests, sqlite3

app = Flask(__name__)

# =====================
# CONFIG
# =====================
VERSION = "TITANIUM-SAAS-V1-STABLE"
ADMIN_TOKEN = os.getenv("ADMIN_TOKEN", "dev")
GROK_KEY = os.getenv("GROK_API_KEY")
OPENAI_KEY = os.getenv("OPENAI_API_KEY")
DB_PATH = "titanium.db"

# =====================
# DB INIT
# =====================
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS payments (id INTEGER PRIMARY KEY AUTOINCREMENT, amount TEXT, email TEXT)")
    conn.commit()
    conn.close()

init_db()

# =====================
# ROUTES
# =====================
@app.route("/")
def home():
    return jsonify({"status": "online", "engine": VERSION, "author": "Titanium"})

@app.route("/admin/stats")
def admin():
    if request.headers.get("Authorization") != f"Bearer {ADMIN_TOKEN}":
        return jsonify({"error": "unauthorized"}), 401
    conn = sqlite3.connect(DB_PATH)
    count = conn.execute("SELECT COUNT(*) FROM payments").fetchone()[0]
    conn.close()
    return jsonify({"status": "ok", "total_payments": count})

@app.route("/ai", methods=["POST"])
def ai():
    prompt = request.json.get("prompt", "Hello")
    # GROK -> OPENAI Fallback logic
    if GROK_KEY:
        try:
            r = requests.post("https://api.x.ai/v1/chat/completions",
                headers={"Authorization": f"Bearer {GROK_KEY}"},
                json={"messages": [{"role": "user", "content": prompt}]}, timeout=10)
            return jsonify({"source": "grok", "data": r.json()})
        except: pass
    if OPENAI_KEY:
        try:
            r = requests.post("https://api.openai.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {OPENAI_KEY}"},
                json={"model": "gpt-4o-mini", "messages": [{"role": "user", "content": prompt}]})
            return jsonify({"source": "openai", "data": r.json()})
        except: pass
    return jsonify({"error": "AI engines offline"}), 500

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json(silent=True) or {}
    conn = sqlite3.connect(DB_PATH)
    conn.execute("INSERT INTO payments (amount, email) VALUES (?, ?)", 
                 (str(data.get("amount", "0")), data.get("email", "unknown")))
    conn.commit()
    conn.close()
    return jsonify({"status": "success"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
