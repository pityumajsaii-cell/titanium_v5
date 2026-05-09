from fastapi import FastAPI, Request
import os
import stripe

app = FastAPI(title="Titanium Stripe Revenue Engine")

# ENV
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")
PRICE_ID = os.getenv("STRIPE_PRICE_ID")

# MEMORY CRM
USERS = {}

# ---------------- CORE ----------------
@app.get("/")
def root():
    return {"status": "online", "system": "titanium_stripe_engine"}

@app.get("/health")
def health():
    return {"status": "ok"}

# ---------------- CHECKOUT ----------------
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

# ---------------- WEBHOOK (CRITICAL) ----------------
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
        customer = session.get("customer")

        USERS[customer] = {
            "status": "paid",
            "session": session
        }

        print("PAYMENT SUCCESS:", customer)

    # PAYMENT FAILED
    if event["type"] == "invoice.payment_failed":
        print("PAYMENT FAILED")

    return {"status": "received"}

# ---------------- STATUS CHECK ----------------
@app.get("/users")
def users():
    return USERS
