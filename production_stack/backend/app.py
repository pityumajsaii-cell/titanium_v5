from fastapi import FastAPI, Request
import sqlite3
import uuid
import os
import stripe

app = FastAPI(title="Titanium V9 Autonomous Sales Core")

# =========================
# STRIPE CONFIG
# =========================
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")
PRICE_ID = os.getenv("STRIPE_PRICE_ID")

# =========================
# DATABASE (STATEFUL CRM)
# =========================
DB = sqlite3.connect("titanium_v9.db", check_same_thread=False)
CUR = DB.cursor()

CUR.execute("""
CREATE TABLE IF NOT EXISTS leads (
    id TEXT,
    email TEXT,
    company TEXT,
    stage TEXT
)
""")

CUR.execute("""
CREATE TABLE IF NOT EXISTS events (
    id TEXT,
    type TEXT,
    data TEXT
)
""")

DB.commit()

# =========================
# LEAD SOURCE (PLUG-IN)
# =========================
def get_leads():
    return [
        {"email": "demo@company.com", "company": "DemoCorp"}
    ]

# =========================
# AI SALES DECISION ENGINE
# =========================
def ai_decide(msg: str):
    msg = msg.lower()
    if "yes" in msg or "interested" in msg:
        return "close"
    if "price" in msg:
        return "nurture"
    if "no" in msg:
        return "stop"
    return "follow_up"

# =========================
# LEAD INGEST
# =========================
@app.get("/leads/auto")
def leads_auto():
    leads = get_leads()

    for l in leads:
        CUR.execute(
            "INSERT INTO leads VALUES (?, ?, ?, ?)",
            (str(uuid.uuid4()), l["email"], l["company"], "new")
        )

    DB.commit()
    return {"generated": len(leads)}

# =========================
# AI EMAIL GENERATION (HOOK ONLY)
# =========================
@app.post("/ai/message")
async def ai_message(req: Request):
    data = await req.json()
    return {
        "email": f"Hi {data.get(company)}, AI automation can increase your revenue."
    }

# =========================
# AI REPLY DECISION
# =========================
@app.post("/ai/reply")
async def ai_reply(req: Request):
    data = await req.json()
    decision = ai_decide(data.get("message", ""))

    return {"decision": decision}

# =========================
# STRIPE CHECKOUT (CLOSING)
# =========================
@app.post("/checkout")
async def checkout():
    session = stripe.checkout.Session.create(
        mode="subscription",
        payment_method_types=["card"],
        line_items=[{"price": PRICE_ID, "quantity": 1}],
        success_url="https://example.com/success",
        cancel_url="https://example.com/cancel"
    )

    return {"url": session.url}

# =========================
# WEBHOOK (REVENUE LOOP)
# =========================
@app.post("/webhook")
async def webhook(req: Request):
    payload = await req.body()
    sig = req.headers.get("stripe-signature")

    event = stripe.Webhook.construct_event(payload, sig, WEBHOOK_SECRET)

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        email = session.get("customer_details", {}).get("email")

        CUR.execute(
            "INSERT INTO events VALUES (?, ?, ?)",
            (str(uuid.uuid4()), "paid", email)
        )

        DB.commit()
        print("💰 CLOSED DEAL:", email)

    return {"status": "ok"}

# =========================
# CRM VIEW
# =========================
@app.get("/crm")
def crm():
    return {
        "leads": CUR.execute("SELECT * FROM leads").fetchall(),
        "events": CUR.execute("SELECT * FROM events").fetchall()
    }

# =========================
# FOLLOW-UP SYSTEM (LOGIC)
# =========================
@app.get("/followups")
def followups():
    return {
        "flow": [
            "Day 1: Intro email",
            "Day 3: Value proof",
            "Day 7: Case study",
            "Day 14: Closing offer"
        ]
    }
