from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI(title="Titanium Revenue Engine")

@app.get("/")
def root():
    return {
        "system": "Titanium Revenue Engine v1",
        "status": "LIVE",
        "deployment": "stable",
        "monetization": "enabled"
    }

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/pricing", response_class=HTMLResponse)
def pricing():
    return """
    <html>
        <body>
            <h1>Titanium SaaS</h1>
            <p>Starter: $9 / month</p>
            <p>Pro: $29 / month</p>
            <p>Enterprise: $99 / month</p>
            <button>Stripe Checkout (placeholder)</button>
        </body>
    </html>
    """

@app.get("/api/status")
def status():
    return {
        "service": "titanium-revenue-engine",
        "state": "running",
        "billing": "stripe_ready",
        "version": "v1"
    }
