from fastapi import FastAPI
import stripe
import uuid
import os

app = FastAPI(title="Titanium AI Sales Engine")
stripe.api_key = os.getenv("STRIPE_SECRET_KEY", "sk_test_mock")

LEADS = {}

# --- CORE AI LOGIC ---
def ai_offer(product):
    return {
        "headline": f"AI Optimized solutions for {product}",
        "pitch": f"Titanium V4 infrastructure scales {product} using quantum-resistant automation.",
        "cta": "Activate your Titanium Node now"
    }

# --- ENDPOINTS ---
@app.post("/lead")
def create_lead(name: str, email: str, interest: str):
    lead_id = str(uuid.uuid4())
    LEADS[lead_id] = {"name": name, "email": email, "interest": interest, "status": "new"}
    return {"lead_id": lead_id, "status": "stored"}

@app.get("/offer/{product}")
def get_offer(product: str):
    return ai_offer(product)

@app.post("/buy")
def buy(product: str):
    try:
        # Stripe Checkout session generálás
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            mode="payment",
            line_items=[{
                "price_data": {
                    "currency": "eur",
                    "product_data": {"name": f"Titanium Access: {product}"},
                    "unit_amount": 4900, # 49.00 EUR
                },
                "quantity": 1,
            }],
            success_url="http://localhost:8000/success",
            cancel_url="http://localhost:8000/cancel",
        )
        return {"checkout_url": session.url}
    except Exception as e:
        return {"error": str(e)}

@app.post("/outreach/{lead_id}")
def outreach(lead_id: str):
    lead = LEADS.get(lead_id)
    if not lead: return {"error": "Lead not found"}
    lead["status"] = "contacted"
    return {"message": f"AI outreach sent to {lead['email']}", "pitch": ai_offer(lead['interest'])}

@app.get("/health")
def health():
    return {"status": "active", "core": "Titanium V4 Engine"}
