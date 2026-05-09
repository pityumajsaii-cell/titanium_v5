from fastapi import FastAPI, Request
import os
import stripe

app = FastAPI(title="Titanium Master Stable System")

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")
PRICE_ID = os.getenv("STRIPE_PRICE_ID")

# =========================
# SAFE CRM (memory based)
# =========================
CRM = {}

# =========================
# CORE
# =========================
@app.get("/")
def root():
    return {"status": "online", "system": "titanium_master"}

@app.get("/health")
def health():
    return {"status": "ok"}

# =========================
# CHECKOUT
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
# WEBHOOK (STABLE)
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

        session_id = session.get("id")
        email = session.get("customer_details", {}).get("email")

        CRM[session_id] = {
            "email": email,
            "status": "paid"
        }

        print("PAYMENT OK:", email)

    return {"status": "received"}

# =========================
# CRM VIEW
# =========================
@app.get("/crm")
def crm():
    return CRM
