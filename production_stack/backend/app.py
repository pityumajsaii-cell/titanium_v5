from fastapi import FastAPI, Request
import os
import stripe
import uuid

app = FastAPI(title="Titanium AI Revenue SaaS V2")

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")
PRICE_ID = os.getenv("STRIPE_PRICE_ID")

# ---------------- CRM MEMORY ----------------
LEADS = {}
PAID_USERS = {}

# ---------------- CORE ----------------
@app.get("/")
def root():
    return {"system": "titanium_v2", "status": "active"}

@app.get("/health")
def health():
    return {"status": "ok"}

# =========================
# 1. LEAD CREATION
# =========================
@app.post("/lead/new")
async def lead_new(request: Request):
    data = await request.json()
    lead_id = str(uuid.uuid4())

    LEADS[lead_id] = {
        "email": data.get("email"),
        "company": data.get("company"),
        "status": "new"
    }

    return {"lead_id": lead_id, "status": "created"}

# =========================
# 2. AI SALES MESSAGE
# =========================
@app.post("/ai/message")
async def ai_message(request: Request):
    data = await request.json()
    company = data.get("company", "Company")

    msg = f"""
Hi {company},

We help automate your sales process using AI agents.

This includes:
- lead qualification
- follow-ups
- conversion automation

Interested in a demo?
"""
    return {"message": msg}

# =========================
# 3. AI REPLY HANDLER (DECISION ENGINE)
# =========================
@app.post("/ai/reply")
async def ai_reply(request: Request):
    data = await request.json()
    lead_id = data.get("lead_id")
    message = data.get("message", "").lower()

    if lead_id not in LEADS:
        return {"error": "lead not found"}

    if "yes" in message or "interested" in message:
        LEADS[lead_id]["status"] = "qualified"
        return {"action": "checkout"}

    LEADS[lead_id]["status"] = "follow_up"
    return {"action": "follow_up"}

# =========================
# 4. STRIPE CHECKOUT
# =========================
@app.post("/checkout")
async def checkout(request: Request):
    data = await request.json()
    lead_id = data.get("lead_id")

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

    LEADS[lead_id]["status"] = "checkout_started"

    return {"url": session.url}

# =========================
# 5. STRIPE WEBHOOK (CLOSE LOOP)
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
        customer = session.get("customer")

        PAID_USERS[customer] = {
            "status": "paid",
            "session": session
        }

        print("USER PAID:", customer)

    return {"status": "ok"}

# =========================
# 6. CRM DASHBOARD
# =========================
@app.get("/crm")
def crm():
    return {
        "leads": LEADS,
        "paid_users": PAID_USERS
    }

# =========================
# 7. FOLLOW UP LOGIC
# =========================
@app.get("/followups")
def followups():
    return {
        "sequence": [
            "Day 1: Intro",
            "Day 3: Value proof",
            "Day 7: Case study",
            "Day 14: Closing offer"
        ]
    }
