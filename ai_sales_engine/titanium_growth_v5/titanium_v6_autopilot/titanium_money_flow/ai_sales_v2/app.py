import os, json, uuid, time
from fastapi import FastAPI, Request
import stripe

# =====================
# CONFIG
# =====================
app = FastAPI(title="AI Sales Machine V2")

stripe.api_key = os.getenv("STRIPE_SECRET_KEY", "test_key")

DB_FILE = "db.json"

def load():
    try:
        return json.load(open(DB_FILE))
    except:
        return {}

def save(db):
    json.dump(db, open(DB_FILE, "w"), indent=2)

# =====================
# CORE ROUTES
# =====================

@app.get("/")
def home():
    return {"status": "LIVE", "system": "AI SALES MACHINE V2"}

# ---------------- LEAD CAPTURE ----------------
@app.get("/lead")
def lead(name: str, email: str, interest: str):
    db = load()
    lid = str(uuid.uuid4())

    db[lid] = {
        "name": name,
        "email": email,
        "interest": interest,
        "status": "lead",
        "created": time.time()
    }

    save(db)

    return {
        "lead_id": lid,
        "landing": f"/landing/{lid}"
    }

# ---------------- LANDING ----------------
@app.get("/landing/{lead_id}")
def landing(lead_id: str):
    db = load()
    lead = db.get(lead_id)

    if not lead:
        return {"error": "not_found"}

    return {
        "message": f"Hey {lead['name']}, AI detected interest in {lead['interest']}",
        "buy_link": f"/checkout/{lead_id}"
    }

# ---------------- STRIPE CHECKOUT ----------------
@app.get("/checkout/{lead_id}")
def checkout(lead_id: str):
    db = load()
    lead = db.get(lead_id)

    if not lead:
        return {"error": "lead_not_found"}

    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        mode="payment",
        line_items=[{
            "price_data": {
                "currency": "eur",
                "product_data": {"name": lead["interest"]},
                "unit_amount": 4900
            },
            "quantity": 1
        }],
        success_url="http://localhost:8000/success",
        cancel_url="http://localhost:8000/cancel"
    )

    return {"checkout_url": session.url}

# ---------------- STRIPE WEBHOOK ----------------
@app.post("/webhook")
async def webhook(request: Request):
    payload = await request.body()

    # NOTE: simplified (production = signature verification needed)
    event = json.loads(payload)

    db = load()

    # simulate payment success
    if "checkout.session.completed" in str(event):
        lead_id = event.get("lead_id", None)

        if lead_id and lead_id in db:
            db[lead_id]["status"] = "paid"
            db[lead_id]["paid_at"] = time.time()
            save(db)

    return {"ok": True}

# ---------------- PIPELINE ----------------
@app.get("/pipeline")
def pipeline():
    db = load()

    return {
        "total": len(db),
        "leads": len([x for x in db.values() if x["status"] == "lead"]),
        "paid": len([x for x in db.values() if x["status"] == "paid"]),
        "data": db
    }

# ---------------- SIMPLE AI FOLLOW-UP ----------------
@app.get("/followup")
def followup():
    db = load()

    for lid, lead in db.items():
        if lead["status"] == "lead":
            lead["ai_message"] = f"Hey {lead['name']}, still interested in {lead['interest']}?"
    
    save(db)

    return {"status": "followup_sent"}

