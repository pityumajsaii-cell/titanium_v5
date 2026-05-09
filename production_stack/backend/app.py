from fastapi import FastAPI, Request
import stripe
import os

app = FastAPI(title="Titanium AI SaaS Engine")

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")

# ---- BASIC ----
@app.get("/")
def root():
    return {"status": "online", "system": "titanium_saas_engine"}

@app.get("/health")
def health():
    return {"status": "ok"}

# ---- PRICING CHECKOUT ----
@app.post("/create-checkout-session")
async def create_checkout():
    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        mode="subscription",
        line_items=[{
            "price": os.getenv("STRIPE_PRICE_ID"),
            "quantity": 1,
        }],
        success_url="https://example.com/success",
        cancel_url="https://example.com/cancel",
    )
    return {"url": session.url}

# ---- WEBHOOK (BILLING CORE) ----
@app.post("/webhook")
async def webhook(request: Request):
    payload = await request.body()
    sig = request.headers.get("stripe-signature")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig, WEBHOOK_SECRET
        )
    except Exception as e:
        return {"error": str(e)}

    # PAYMENT SUCCESS
    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        print("💰 NEW SUBSCRIPTION:", session.get("customer"))

    # SUBSCRIPTION UPDATED
    if event["type"] == "customer.subscription.created":
        print("📦 SUB CREATED")

    if event["type"] == "invoice.payment_failed":
        print("⚠️ PAYMENT FAILED")

    return {"status": "received"}
