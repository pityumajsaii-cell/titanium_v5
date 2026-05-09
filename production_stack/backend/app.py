from fastapi import FastAPI, Request
import os
import json

app = FastAPI(title="Titanium AI Sales Engine")

# ---------------- CORE ----------------
@app.get("/")
def root():
    return {"system": "titanium_ai_sales_engine", "status": "online"}

@app.get("/health")
def health():
    return {"status": "ok"}

# ---------------- LEAD GENERATION ----------------
@app.get("/leads/generate")
def generate_leads():
    leads = [
        {"name": "Startup A", "email": "contact@startupa.com", "interest": "AI automation"},
        {"name": "Company B", "email": "hello@companyb.com", "interest": "SaaS scaling"},
        {"name": "Agency C", "email": "info@agencyc.com", "interest": "lead generation"},
    ]
    return {"leads": leads}

# ---------------- AI SALES MESSAGE ----------------
@app.post("/sales/message")
async def sales_message(request: Request):
    data = await request.json()
    company = data.get("company", "Unknown")

    message = f"""
Hi {company},

We help automate your sales pipeline using AI agents that generate leads, qualify prospects, and close deals automatically.

Would you like a demo?

- Titanium AI Sales Engine
"""

    return {"message": message}

# ---------------- CRM LOG ----------------
SALES_LOG = []

@app.post("/crm/log")
async def crm_log(request: Request):
    data = await request.json()
    SALES_LOG.append(data)
    return {"status": "logged", "total": len(SALES_LOG)}

@app.get("/crm/all")
def crm_all():
    return {"crm": SALES_LOG}
