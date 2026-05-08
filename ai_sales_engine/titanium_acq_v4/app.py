from fastapi import FastAPI
import json
import uuid
import os
import stripe
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Titanium Acquisition Engine v4")

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

DB_FILE = "leads.json"

# ---------------- STORAGE ----------------
def load_leads():
    try:
        return json.load(open(DB_FILE))
    except:
        return {}

def save_leads(data):
    json.dump(data, open(DB_FILE, "w"))

# ---------------- AI MESSAGE ENGINE (stub) ----------------
def ai_message(interest):
    return {
        "subject": f"Boost your {interest} with AI automation",
        "message": f"Hi! We built an AI system that improves {interest} conversion and automates sales."
    }

# ---------------- LEAD CAPTURE ----------------
@app.post("/lead")
def lead(name: str, email: str, interest: str):

    leads = load_leads()

    lead_id = str(uuid.uuid4())

    leads[lead_id] = {
        "name": name,
        "email": email,
        "interest": interest,
        "status": "new"
    }

    save_leads(leads)

    return {"lead_id": lead_id, "status": "captured"}

# ---------------- AI SALES MESSAGE ----------------
@app.get("/message/{lead_id}")
def message(lead_id: str):

    leads = load_leads()

    if lead_id not in leads:
        return {"error": "not found"}

    lead = leads[lead_id]

    return ai_message(lead["interest"])

# ---------------- STRIPE CHECKOUT ----------------
@app.post("/buy/{product}")
def buy(product: str):

    if not stripe.api_key:
        return {"error": "missing stripe key"}

    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        mode="payment",
        line_items=[{
            "price_data": {
                "currency": "eur",
                "product_data": {"name": product},
                "unit_amount": 4900,
            },
            "quantity": 1,
        }],
        success_url="http://localhost:8000/success",
        cancel_url="http://localhost:8000/cancel",
    )

    return {"checkout_url": session.url}

# ---------------- OUTREACH QUEUE ----------------
@app.get("/outreach")
def outreach():

    leads = load_leads()

    queue = []

    for lid, l in leads.items():
        if l["status"] == "new":
            queue.append({
                "lead_id": lid,
                "email": l["email"],
                "message": ai_message(l["interest"])
            })

            l["status"] = "queued"

    save_leads(leads)

    return {"queue": queue}

# ---------------- ANALYTICS ----------------
@app.get("/stats")
def stats():
    leads = load_leads()

    return {
        "total_leads": len(leads),
        "new": len([l for l in leads.values() if l["status"] == "new"]),
        "queued": len([l for l in leads.values() if l["status"] == "queued"])
    }

# ---------------- SYSTEM ----------------
@app.get("/health")
def health():
    return {
        "status": "ok",
        "engine": "acquisition-v4",
        "stripe": "active" if stripe.api_key else "missing"
    }
