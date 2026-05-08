from flask import Flask, request, jsonify
import os, json, hmac, hashlib, sqlite3, requests, stripe

try:
    import psycopg2
except:
    psycopg2 = None

app = Flask(__name__)

# =====================
# CONFIG
# =====================
DB_URL = os.getenv("DATABASE_URL")
STRIPE_SECRET = os.getenv("STRIPE_SECRET")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")
ADMIN_TOKEN = os.getenv("ADMIN_TOKEN", "CHANGE_ME_ADMIN")

TG_TOKEN = os.getenv("TG_TOKEN")
TG_CHAT_ID = os.getenv("TG_CHAT_ID")

stripe.api_key = STRIPE_SECRET

# =====================
# DB
# =====================
def db():
    if DB_URL and psycopg2:
        return psycopg2.connect(DB_URL)
    return sqlite3.connect("titanium.db")

def init():
    conn = db()
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS payments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        stripe_id TEXT,
        amount TEXT,
        email TEXT
    )
    """)
    conn.commit()
    conn.close()

# =====================
# HEALTH (Render fix)
# =====================
@app.route("/")
def home():
    return "Titanium ONLINE", 200

@app.route("/health")
def health():
    return jsonify({"status": "ok"}), 200

@app.route("/version")
def version():
    return jsonify({"version": "zero-drift-v1"}), 200

# =====================
# ADMIN (SECURE)
# =====================
@app.route("/admin/stats")
def stats():
    if request.headers.get("Authorization") != f"Bearer {ADMIN_TOKEN}":
        return jsonify({"error": "unauthorized"}), 401

    conn = db()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM payments")
    count = c.fetchone()[0]
    conn.close()

    return jsonify({
        "payments": count
    })

# =====================
# STRIPE WEBHOOK (SECURE)
# =====================
@app.route("/webhook", methods=["POST"])
def webhook():
    payload = request.get_data()
    sig = request.headers.get("Stripe-Signature")

    try:
        event = stripe.Webhook.construct_event(
            payload,
            sig,
            STRIPE_WEBHOOK_SECRET
        )
    except:
        return "invalid", 400

    if event["type"] == "checkout.session.completed":
        s = event["data"]["object"]
        email = s.get("customer_details", {}).get("email")
        amount = s.get("amount_total", 0) / 100
        sid = s.get("id")

        conn = db()
        c = conn.cursor()
        c.execute(
            "INSERT INTO payments (stripe_id, amount, email) VALUES (?, ?, ?)",
            (sid, str(amount), email)
        )
        conn.commit()
        conn.close()

        if TG_TOKEN:
            requests.post(
                f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage",
                json={
                    "chat_id": TG_CHAT_ID,
                    "text": f"💰 Payment: {amount} EUR\n{email}"
                }
            )

    return "ok", 200

# =====================
# STARTUP
# =====================
if __name__ == "__main__":
    init()
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
