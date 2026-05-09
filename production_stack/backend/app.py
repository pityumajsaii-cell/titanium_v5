from fastapi import FastAPI, Request
import os
import stripe
from typing import Dict

app = FastAPI(title="Titanium Stable Revenue Engine")

# ENV
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")
PRICE_ID = os.getenv("STRIPE_PRICE_ID")

# =========================
# PERSISTENT SAFE CRM (IN MEMORY SAFE VERSION)
# =========================
USERS: Dict[str, dict] = {}

# =========================
# CORE
# =========================
@app.get("/")
def root():
    return {"system": "titanium_stable", "status": "online"}

@app.get("/health")
def health():
    return {"status": "ok"}

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
# WEBHOOK (FIXED + SAFE)
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

    # PAYMENT SUCCESS
    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]

        session_id = session.get("id")
        email = session.get("customer_details", {}).get("email")

        if session_id:
            USERS[session_id] = {
                "email": email,
                "status": "paid"
            }

        print("PAYMENT SUCCESS:", email)

    # PAYMENT FAILED
    elif event["type"] == "invoice.payment_failed":
        print("PAYMENT FAILED")

    return {"status": "received"}

# =========================
# CRM
# =========================
@app.get("/users")
def users():
    return USERS
