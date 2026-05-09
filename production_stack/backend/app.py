from fastapi import FastAPI, Request
import uuid

app = FastAPI(title="Titanium Autonomous Sales Agent")

# ---------------- MEMORY (simple in-memory CRM) ----------------
LEADS = {}
CONVERSATIONS = {}

# ---------------- HEALTH ----------------
@app.get("/")
def root():
    return {"system": "titanium_sales_agent", "status": "online"}

@app.get("/health")
def health():
    return {"status": "ok"}

# ---------------- LEAD INTAKE ----------------
@app.post("/lead/new")
async def new_lead(request: Request):
    data = await request.json()
    lead_id = str(uuid.uuid4())

    LEADS[lead_id] = {
        "email": data.get("email"),
        "company": data.get("company"),
        "status": "new"
    }

    return {"lead_id": lead_id, "status": "created"}

# ---------------- AI EMAIL GENERATOR ----------------
@app.post("/agent/email")
async def generate_email(request: Request):
    data = await request.json()
    company = data.get("company", "Company")

    email = f"""
Subject: AI automation for {company}

Hi {company},

We help companies automate their sales process using AI agents.

This includes:
- lead generation
- follow-up automation
- conversion optimization

Would you like a quick demo?

Best,
Titanium AI Sales Agent
"""
    return {"email": email}

# ---------------- SEND EMAIL (SIMULATED HOOK) ----------------
@app.post("/agent/send")
async def send_email(request: Request):
    data = await request.json()
    lead_id = data.get("lead_id")

    if lead_id in LEADS:
        LEADS[lead_id]["status"] = "contacted"

    return {"status": "sent", "lead_id": lead_id}

# ---------------- INBOUND REPLY HANDLER ----------------
@app.post("/agent/reply")
async def handle_reply(request: Request):
    data = await request.json()
    lead_id = data.get("lead_id")
    message = data.get("message")

    CONVERSATIONS.setdefault(lead_id, []).append({
        "from": "client",
        "message": message
    })

    # simple AI decision logic
    if "yes" in message.lower() or "interested" in message.lower():
        LEADS[lead_id]["status"] = "qualified"
        return {"action": "send_checkout"}

    return {"action": "follow_up"}

# ---------------- FOLLOW UP ENGINE ----------------
@app.get("/agent/followups")
def followups():
    return {
        "sequence": [
            "Day 1: Intro email",
            "Day 3: Value follow-up",
            "Day 7: Case study",
            "Day 14: Final offer"
        ]
    }

# ---------------- STRIPE CLOSE ----------------
@app.post("/agent/close")
async def close_deal(request: Request):
    data = await request.json()
    lead_id = data.get("lead_id")

    if lead_id in LEADS:
        LEADS[lead_id]["status"] = "closed"

    return {
        "checkout_url": "https://stripe-checkout-session-placeholder",
        "status": "closing"
    }

# ---------------- CRM VIEW ----------------
@app.get("/crm")
def crm():
    return {
        "leads": LEADS,
        "conversations": CONVERSATIONS
    }
