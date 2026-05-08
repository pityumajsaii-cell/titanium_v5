from fastapi import FastAPI, Request
import os
import stripe

app = FastAPI(title="Titanium Monetization Core")

stripe.api_key = os.getenv("STRIPE_SECRET_KEY", "test_key")

# ---------------- CORE ----------------
@app.get("/")
def root():
    return {"status": "LIVE", "system": "Titanium Monetization Core"}

@app.get("/health")
def health():
    return {"status": "ok"}

# ---------------- PRICING ----------------
@app.get("/pricing")
def pricing():
    return {
        "starter": "9 EUR / month",
        "pro": "29 EUR / month",
        "enterprise": "99 EUR / month"
    }

# ---------------- STRIPE CHECKOUT ----------------
@app.post("/create-checkout-session")
async def create_checkout():
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            mode="payment",
            line_items=[{
                "price_data": {
                    "currency": "eur",
                    "product_data": {"name": "Titanium Access"},
                    "unit_amount": 900,
                },
                "quantity": 1,
            }],
            success_url="https://example.com/success",
            cancel_url="https://example.com/cancel",
        )
        return {"checkout_url": session.url}
    except Exception as e:
        return {"error": str(e)}

# ---------------- WEBHOOK ----------------
@app.post("/webhook")
async def webhook(request: Request):
    payload = await request.body()
    return {"received": True}

# ---------------- SIMPLE GATE ----------------
@app.get("/api/gate")
def gate(api_key: str = ""):
    if api_key == "titanium_free_key":
        return {"access": "granted"}
    return {"access": "denied"}
