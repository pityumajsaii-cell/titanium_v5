from flask import Flask, render_template, request, jsonify
import json, os, requests, hmac, hashlib, time, psycopg2, stripe
from datetime import datetime
from queue import Queue
from threading import Thread

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET', 'titanium_v5_hardened_final')

# --- CONFIG ---
DB_URL = os.getenv('DATABASE_URL')
STRIPE_SECRET = os.getenv('STRIPE_SECRET')
STRIPE_WEBHOOK_SECRET = os.getenv('STRIPE_WEBHOOK_SECRET') # whsec_...
TG_TOKEN = os.getenv('TG_TOKEN')
TG_CHAT_ID = os.getenv('TG_CHAT_ID')
BRIDGE_SECRET = os.getenv('BRIDGE_SECRET', 'TITANIUM_SECURE_TOKEN_2026')

stripe.api_key = STRIPE_SECRET

def get_db_connection():
    if DB_URL: return psycopg2.connect(DB_URL)
    import sqlite3
    return sqlite3.connect("titanium_core.db")

# --- WEBHOOK ENDPOINT (SECURE) ---
@app.route('/webhook', methods=['POST'])
def webhook():
    payload = request.get_data()
    sig_header = request.headers.get('Stripe-Signature')

    try:
        # 🛡️ KRITIKUS BIZTONSÁGI LÉPÉS: Aláírás ellenőrzése
        event = stripe.Webhook.construct_event(
            payload, sig_header, STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        # Érvénytelen payload
        return jsonify({"error": "invalid_payload"}), 400
    except stripe.error.SignatureVerificationError as e:
        # Érvénytelen aláírás (Támadási kísérlet!)
        return jsonify({"error": "invalid_signature"}), 400

    # Ha idáig eljutott, a kérés GARANTÁLTAN a Stripe-tól jött
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        process_payment(session)

    return jsonify(success=True)

def process_payment(session):
    email = session.get('customer_details', {}).get('email')
    amount = session.get('amount_total', 0) / 100
    stripe_id = session.get('id')

    try:
        conn = get_db_connection()
        cur = conn.cursor()
        if DB_URL:
            cur.execute("INSERT INTO payments (stripe_id, amount, status, customer_email) VALUES (%s, %s, %s, %s)",
                        (stripe_id, str(amount), "paid", email))
        else:
            cur.execute("INSERT INTO payments (stripe_id, amount, status, customer_email) VALUES (?, ?, ?, ?)",
                        (stripe_id, str(amount), "paid", email))
        conn.commit()
        cur.close()
        conn.close()

        # Azonnali riasztás
        msg = f"💰 <b>VERIFIED REVENUE!</b>\n📧 {email}\n💵 {amount} EUR\n✅ Aláírás ellenőrizve."
        requests.post(f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage", 
                      json={"chat_id": TG_CHAT_ID, "text": msg, "parse_mode": "HTML"})
    except Exception as e:
        print(f"Payment Save Error: {e}")

@app.route('/admin/stats')
def stats():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM payments")
    count = cur.fetchone()[0]
    cur.close()
    conn.close()
    return f"<h1>Titanium Secure Admin</h1><p>Hitelesített tranzakciók: {count}</p>"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 7860)))
