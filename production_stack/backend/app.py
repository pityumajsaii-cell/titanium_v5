from fastapi import FastAPI, Request
import os
import stripe
import sqlite3
import uuid

app = FastAPI(title="Titanium V3 Autonomous Revenue Engine")

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")
PRICE_ID = os.getenv("STRIPE_PRICE_ID")

# =========================
# DATABASE (PERSISTENT CRM)
# =========================
conn = sqlite3.connect("crm.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS leads (
    id TEXT PRIMARY KEY,
    email TEXT,
    company TEXT,
    status TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS payments (
    id TEXT PRIMARY KEY,
    email TEXT,
    status TEXT
)
""")

conn.commit()

# =========================
# AI LOGIC (SIMPLE AUTONOMOUS DECISION ENGINE)
# =========================
def ai_decision(message: str):
    msg = message.lower()
    if "interested" in msg or "yes" in msg:
        return "close"
    return "follow_up"

# =========================
# ROOT
# =========================
@app.get("/")
def root():
    return {"system": "titanium_v3", "status": "autonomous"}

# =========================
# LEAD CREATE
# =========================
@app.post("/lead/new")
async def lead_new(request: Request):
    data = await request.json()
    lead_id = str(uuid.uuid4())

    cursor.execute(
        "INSERT INTO leads VALUES (?, ?, ?, ?)",
        (lead_id, data.get("email"), data.get("company"), "new")
    )
    conn.commit()

    return {"lead_id": lead_id, "status": "created"}

# =========================
# AI MESSAGE GENERATOR
# =========================
@app.post("/ai/message")
async def ai_message(request: Request):
    data = await request.json()
    company = data.get("company", "Company")

    return {
        "message": f"Hi {company}, we help automate your sales using AI agents. Interested?"
    }

# =========================
# AI REPLY ENGINE
# =========================
@app.post("/ai/reply")
async def ai_reply(request: Request):
    data = await request.json()

    decision = ai_decision(data.get("message", ""))

    return {"decision": decision}

# =========================
# STRIPE CHECKOUT
# =========================
@app.post("/checkout")
async def checkout():
    session = stripe.checkout.Session.create(
        mode="subscription",
        payment_method_types=["card"],
        line_items=[{
            "price": PRICE_ID,
            "quantity": 1
        }],
        success_url="https://example.com/success",
        cancel_url="https://example.com/cancel"
    )

    return {"url": session.url}

# =========================
# WEBHOOK (AUTONOM CLOSING LOOP)
# =========================
@app.post("/webhook")
async def webhook(request: Request):
    payload = await request.body()
    sig = request.headers.get("stripe-signature")

    try:
        event = stripe.Webhook.construct_event(
            payload,
            sig,
            WEBHOOK_SECRET
        )
    except Exception as e:
        return {"error": str(e)}

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        email = session.get("customer_details", {}).get("email")

        payment_id = str(uuid.uuid4())

        cursor.execute(
            "INSERT INTO payments VALUES (?, ?, ?)",
            (payment_id, email, "paid")
        )
        conn.commit()

        print("AUTO CLOSE:", email)

    return {"status": "ok"}

# =========================
# CRM VIEW
# =========================
@app.get("/crm")
def crm():
    cursor.execute("SELECT * FROM leads")
    leads = cursor.fetchall()

    cursor.execute("SELECT * FROM payments")
    payments = cursor.fetchall()

    return {
        "leads": leads,
        "payments": payments
    }
