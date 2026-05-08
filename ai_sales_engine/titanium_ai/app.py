import os
from fastapi import FastAPI
import stripe
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Titanium Autonomous Sales AI v3")

STRIPE_KEY = os.getenv("STRIPE_SECRET_KEY")

# SAFE INIT
stripe.api_key = STRIPE_KEY if STRIPE_KEY else None


# ---------------- HEALTH ----------------
@app.get("/health")
def health():
    return {
        "status": "online",
        "stripe": "connected" if STRIPE_KEY else "missing_key",
        "ai_core": "ready"
    }


# ---------------- AI OFFER ENGINE ----------------
@app.get("/offer/{product}")
def offer(product: str):
    return {
        "product": product,
        "headline": f"AI-optimized offer for {product}",
        "pitch": f"This system automates growth, sales and scaling for {product}.",
        "cta": "Activate now via Stripe checkout"
    }


# ---------------- STRIPE CHECKOUT ----------------
@app.post("/buy/{product}")
def buy(product: str):

    if not STRIPE_KEY:
        return {"error": "Stripe key missing (.env not configured)"}

    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        mode="payment",
        line_items=[{
            "price_data": {
                "currency": "eur",
                "product_data": {"name": f"AI Access: {product}"},
                "unit_amount": 4900,
            },
            "quantity": 1,
        }],
        success_url="http://localhost:8000/success",
        cancel_url="http://localhost:8000/cancel",
    )

    return {"checkout_url": session.url}


@app.get("/success")
def success():
    return {"payment": "success", "access": "granted"}

@app.get("/cancel")
def cancel():
    return {"payment": "cancelled"}


# ---------------- AI STATUS ----------------
@app.get("/system")
def system():
    return {
        "core": "Titanium AI Sales Engine v3",
        "mode": "autonomous_ready",
        "monetization": "stripe_enabled" if STRIPE_KEY else "not_ready"
    }
