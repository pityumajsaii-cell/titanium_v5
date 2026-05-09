from fastapi import FastAPI, Request
import sqlite3
import uuid
import os
import stripe

app = FastAPI(title="Titanium V6 Clean Growth Engine")

# =========================
# STRIPE CONFIG
# =========================
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")
PRICE_ID = os.getenv("STRIPE_PRICE_ID")

# =========================
# DB CORE (CLEAN STATE)
# =========================
DB = sqlite3.connect("titanium_v6.db", check_same_thread=False)
CUR = DB.cursor()

CUR.execute("""
CREATE TABLE IF NOT EXISTS leads (
    id TEXT,
    email TEXT,
    company TEXT,
    status TEXT
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
# LEAD SOURCE (PLUGIN READY)
# =========================
def get_leads():
    return [
        {"email": "demo@company.com", "company": "DemoCorp"}
    ]

# =========================
# AI DECISION ENGINE
# =========================
def ai_decide(msg: str):
    msg = msg.lower()
    if "yes" in msg or "interested" in msg:
        return "close"
    if "maybe" in msg:
        return "follow_up"
    return "nurture"

# =========================
# LEADS
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
# AI MESSAGE
# =========================
@app.post("/ai/message")
async def ai_message(req: Request):
    data = await req.json()
    return {
        "email": f"Hi {data.get(company)} - AI automation can increase your revenue."
    }

# =========================
# AI REPLY
# =========================
@app.post("/ai/reply")
async def ai_reply(req: Request):
    data = await req.json()
    return {"decision": ai_decide(data.get("message", ""))}

# =========================
# CHECKOUT
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
# WEBHOOK (CLEAN + SAFE)
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
            (str(uuid.uuid4()), "payment", email)
        )
        DB.commit()

        print("CLOSED:", email)

    return {"status": "ok"}

# =========================
# CRM
# =========================
@app.get("/crm")
def crm():
    leads = CUR.execute("SELECT * FROM leads").fetchall()
    events = CUR.execute("SELECT * FROM events").fetchall()
    return {"leads": leads, "events": events}
