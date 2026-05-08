from flask import Flask, request, jsonify
import os, requests, sqlite3, jwt, datetime, stripe
from functools import wraps

app = Flask(__name__)

# --- CONFIG ---
VERSION = "TITANIUM-SAAS-V2-PRO"
SECRET_KEY = os.getenv("FLASK_SECRET", "titanium_ultra_secret_2026")
ADMIN_TOKEN = os.getenv("ADMIN_TOKEN", "dev")
STRIPE_SECRET = os.getenv("STRIPE_SECRET")
DB_PATH = "titanium_v2.db"

stripe.api_key = STRIPE_SECRET

# --- DB INIT ---
def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, email TEXT, plan TEXT, active INTEGER)")
    conn.execute("CREATE TABLE IF NOT EXISTS revenue (id INTEGER PRIMARY KEY, amount REAL, currency TEXT, date TEXT)")
    conn.commit()
    conn.close()

init_db()

# --- AUTH DECORATOR ---
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get("Authorization")
        if not token or "Bearer " not in token:
            return jsonify({"error": "Missing token"}), 401
        try:
            jwt.decode(token.split(" ")[1], SECRET_KEY, algorithms=["HS256"])
        except:
            return jsonify({"error": "Invalid token"}), 401
        return f(*args, **kwargs)
    return decorated

# --- ROUTES ---
@app.route("/")
def health():
    return jsonify({"engine": VERSION, "status": "gold_standard"})

@app.route("/auth/login", methods=["POST"])
def login():
    # Egyszerűsített login az admin tokeneddel
    auth_data = request.json
    if auth_data.get("token") == ADMIN_TOKEN:
        token = jwt.encode({
            "user": "admin",
            "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=24)
        }, SECRET_KEY, algorithm="HS256")
        return jsonify({"token": token})
    return jsonify({"error": "Forbidden"}), 403

@app.route("/admin/revenue")
@token_required
def get_revenue():
    conn = sqlite3.connect(DB_PATH)
    total = conn.execute("SELECT SUM(amount) FROM revenue").fetchone()[0] or 0
    conn.close()
    return jsonify({"total_revenue_eur": total, "currency": "EUR"})

@app.route("/webhook/stripe", methods=["POST"])
def stripe_webhook():
    # Ide jön a Stripe esemény feldolgozása
    data = request.json
    # Példa: ha sikeres a fizetés, rögzítjük a bevételt
    if data.get("type") == "checkout.session.completed":
        session = data["data"]["object"]
        amount = session["amount_total"] / 100
        conn = sqlite3.connect(DB_PATH)
        conn.execute("INSERT INTO revenue (amount, currency, date) VALUES (?, ?, ?)",
                     (amount, session["currency"], datetime.datetime.now().isoformat()))
        conn.commit()
        conn.close()
    return jsonify({"received": True})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
