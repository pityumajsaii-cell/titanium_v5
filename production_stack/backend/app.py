from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
import stripe

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

@app.get("/")
def root():
    return {
        "status": "LIVE",
        "system": "Titanium Revenue Engine",
        "payments": "ACTIVE"
    }

@app.post("/create-checkout")
def create_checkout():
    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[{
            "price_data": {
                "currency": "usd",
                "product_data": {
                    "name": "Titanium AI SaaS"
                },
                "unit_amount": 4900
            },
            "quantity": 1
        }],
        mode="payment",
        success_url="https://example.com/success",
        cancel_url="https://example.com/cancel"
    )

    return {"url": session.url}
