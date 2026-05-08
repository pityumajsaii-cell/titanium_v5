from fastapi import FastAPI
import stripe
import uuid

app = FastAPI(title="AI Sales Engine")

stripe.api_key = "PUT_STRIPE_KEY_HERE"

LEADS = {}

# ---------------- CORE AI (simple sales logic) ----------------
def ai_offer(product):
    return {
        "headline": f"AI optimized offer for {product}",
        "pitch": f"This system helps you scale {product} with automation, AI and conversion optimization.",
        "cta": "Click to activate instant access"
    }

# ---------------- LEAD GENERATION ----------------
@app.post("/lead")
def create_lead(name: str, email: str, interest: str):
    lead_id = str(uuid.uuid4())
    LEADS[lead_id] = {
        "name": name,
        "email": email,
        "interest": interest,
        "status": "new"
    }
    return {"lead_id": lead_id, "status": "stored"}

# ---------------- AI SALES PAGE ----------------
@app.get("/offer/{product}")
def offer(product: str):
    return ai_offer(product)

# ---------------- STRIPE CHECKOUT ----------------
@app.post("/buy")
def buy(product: str):
    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        mode="payment",
        line_items=[{
            "price_data": {
                "currency": "eur",
                "product_data": {
                    "name": f"AI Access: {product}"
                },
                "unit_amount": 4900,
            },
            "quantity": 1,
        }],
        success_url="http://localhost:8000/success",
        cancel_url="http://localhost:8000/cancel",
    )
    return {"checkout_url": session.url}

# ---------------- OUTREACH SIMULATOR ----------------
@app.post("/outreach/{lead_id}")
def outreach(lead_id: str):
    lead = LEADS.get(lead_id)
    if not lead:
        return {"error": "lead not found"}

    lead["status"] = "contacted"

    return {
        "message": f"Email sent to {lead[email]}",
        "offer": ai_offer(lead["interest"])
    }

@app.get("/leads")
def leads():
    return LEADS

@app.get("/health")
def health():
    return {"status": "ok", "system": "ai_sales_engine"}
