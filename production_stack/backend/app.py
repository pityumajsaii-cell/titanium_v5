from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import uuid
import time

app = FastAPI(title="Titanium Revenue Engine")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

LEADS = {}
PAYMENTS = {}
EVENTS = []

@app.get("/")
def root():
    return {
        "status": "LIVE",
        "system": "Titanium Revenue Engine",
        "payments": "ACTIVE"
    }

@app.get("/health")
def health():
    return {
        "status": "ok",
        "leads": len(LEADS),
        "payments": len(PAYMENTS),
        "events": len(EVENTS)
    }

@app.post("/lead")
async def create_lead(request: Request):
    data = await request.json()

    lead_id = str(uuid.uuid4())

    LEADS[lead_id] = {
        "id": lead_id,
        "name": data.get("name"),
        "email": data.get("email"),
        "service": data.get("service", "AI SaaS"),
        "status": "NEW",
        "created": time.time()
    }

    EVENTS.append({
        "type": "lead_created",
        "lead_id": lead_id
    })

    return {
        "success": True,
        "lead_id": lead_id,
        "lead": LEADS[lead_id]
    }

@app.get("/lead/{lead_id}")
def get_lead(lead_id: str):
    return LEADS.get(lead_id, {"error": "not_found"})

@app.post("/create-checkout")
async def create_checkout(request: Request):
    data = await request.json()

    lead_id = data.get("lead_id")

    if not lead_id or lead_id not in LEADS:
        return {
            "error": "invalid_lead"
        }

    session_id = str(uuid.uuid4())

    PAYMENTS[session_id] = {
        "lead_id": lead_id,
        "status": "pending",
        "created": time.time()
    }

    EVENTS.append({
        "type": "checkout_created",
        "session_id": session_id
    })

    return {
        "success": True,
        "session_id": session_id,
        "payment_status": "pending",
        "checkout_url": "https://checkout.stripe.com/pay/demo_session"
    }

@app.post("/webhook")
async def webhook(request: Request):
    payload = await request.json()

    event_type = payload.get("type")

    if event_type == "checkout.session.completed":

        session_id = payload.get(
            "data", {}
        ).get(
            "object", {}
        ).get(
            "id"
        )

        if session_id in PAYMENTS:

            PAYMENTS[session_id]["status"] = "paid"

            lead_id = PAYMENTS[session_id]["lead_id"]

            if lead_id in LEADS:
                LEADS[lead_id]["status"] = "ACTIVE_CUSTOMER"

            EVENTS.append({
                "type": "payment_success",
                "lead_id": lead_id
            })

            return {
                "success": True,
                "payment": "completed"
            }

    return {
        "received": True
    }

@app.get("/stats")
def stats():

    active_customers = len([
        x for x in LEADS.values()
        if x["status"] == "ACTIVE_CUSTOMER"
    ])

    return {
        "total_leads": len(LEADS),
        "active_customers": active_customers,
        "payments": len(PAYMENTS),
        "events": len(EVENTS),
        "system": "ONLINE"
    }
