from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI()

@app.get("/")
def home():
    return {
        "system": "Titanium SaaS Core",
        "status": "live",
        "monetization": "stripe_ready_placeholder"
    }

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/pricing", response_class=HTMLResponse)
def pricing():
    return """
    <h1>Titanium SaaS</h1>
    <p>Starter Plan: $9/month</p>
    <p>Pro Plan: $29/month</p>
    <button>Buy (Stripe placeholder)</button>
    """
