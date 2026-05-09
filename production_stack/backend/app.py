from fastapi import FastAPI, Request
import os

app = FastAPI(title="Titanium Revenue Engine")

# ---------------- HEALTH ----------------
@app.get("/")
def root():
    return {"system": "titanium_revenue_engine", "status": "online"}

@app.get("/health")
def health():
    return {"status": "ok"}

# ---------------- LEAD INTAKE (SAFE) ----------------
@app.post("/leads/import")
async def import_leads(request: Request):
    data = await request.json()
    return {
        "status": "received",
        "leads_count": len(data.get("leads", []))
    }

# ---------------- AI SALES MESSAGE ----------------
@app.post("/ai/offer")
async def ai_offer(request: Request):
    data = await request.json()
    company = data.get("company", "Company")

    message = f"""
Hi {company},

We help automate your sales and customer acquisition using AI systems.

This includes:
- lead handling automation
- follow-up sequences
- conversion tracking

Would you like a demo?

- Titanium AI Revenue Engine
"""
    return {"message": message}

# ---------------- FOLLOW-UP ENGINE (LOGIC ONLY) ----------------
@app.post("/followup/sequence")
async def followup(request: Request):
    return {
        "sequence": [
            "Day 1: Intro email",
            "Day 3: Follow-up",
            "Day 7: Case study",
            "Day 14: Final offer"
        ]
    }

# ---------------- STRIPE ----------------
@app.post("/checkout")
async def checkout():
    return {
        "url": "https://stripe-checkout-session-placeholder"
    }

@app.post("/webhook")
async def webhook(request: Request):
    body = await request.body()
    print("PAYMENT EVENT:", body)
    return {"status": "ok"}
