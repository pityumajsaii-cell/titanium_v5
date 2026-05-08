from fastapi import FastAPI
import os
import stripe

app = FastAPI()

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

DOMAIN = "http://localhost:8000"

@app.get("/")
def root():
    return {"status": "live", "system": "titanium-stripe-core"}

@app.post("/create-checkout")
def create_checkout():
    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        mode="payment",
        line_items=[{
            "price_data": {
                "currency": "eur",
                "product_data": {
                    "name": "Titanium AI Access"
                },
                "unit_amount": 5000,
            },
            "quantity": 1,
        }],
        success_url=DOMAIN + "/success",
        cancel_url=DOMAIN + "/cancel",
    )
    return {"url": session.url}

@app.get("/success")
def success():
    return {"paid": True}

@app.get("/cancel")
def cancel():
    return {"paid": False}
