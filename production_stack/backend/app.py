from fastapi import FastAPI, Request
import sqlite3
import uuid
import stripe
import os
import requests
from bs4 import BeautifulSoup

app = FastAPI(title="Titanium V4 Autonomous Engine")

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")
PRICE_ID = os.getenv("STRIPE_PRICE_ID")

# =========================
# DB
# =========================
DB = sqlite3.connect("titanium_v4.db", check_same_thread=False)
CUR = DB.cursor()

CUR.execute("CREATE TABLE IF NOT EXISTS leads (id TEXT, email TEXT, company TEXT, status TEXT)")
CUR.execute("CREATE TABLE IF NOT EXISTS events (id TEXT, type TEXT, data TEXT)")
DB.commit()

# =========================
# SCRAPER (SIMPLE BASE)
# =========================
def scrape_leads():
    return [{"email": "demo@company.com", "company": "DemoCorp"}]

# =========================
# AI LOGIC
# =========================
def ai_decision(msg: str):
    msg = msg.lower()
    if "yes" in msg or "interested" in msg:
        return "close"
    if "maybe" in msg:
        return "follow_up"
    return "nurture"

# =========================
# LEADS AUTO
# =========================
@app.get("/leads/auto")
def leads_auto():
    leads = scrape_leads()

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
async def ai_message(request: Request):
    data = await request.json()
    return {"message": f"Hi {data.get(company)} - AI automation can grow your revenue."}

# =========================
# AI REPLY
# =========================
@app.post("/ai/reply")
async def ai_reply(request: Request):
    data = await request.json()
    return {"decision": ai_decision(data.get("message", ""))}

# =========================
# STRIPE CHECKOUT
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
# WEBHOOK
# =========================
@app.post("/webhook")
async def webhook(request: Request):
    payload = await request.body()
    sig = request.headers.get("stripe-signature")

    event = stripe.Webhook.construct_event(payload, sig, WEBHOOK_SECRET)

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        email = session.get("customer_details", {}).get("email")

        CUR.execute(
            "INSERT INTO events VALUES (?, ?, ?)",
            (str(uuid.uuid4()), "payment", email)
        )
        DB.commit()

        print("PAYMENT CLOSED:", email)

    return {"status": "ok"}

# =========================
# CRM
# =========================
@app.get("/crm")
def crm():
    leads = CUR.execute("SELECT * FROM leads").fetchall()
    events = CUR.execute("SELECT * FROM events").fetchall()

    return {"leads": leads, "events": events}
