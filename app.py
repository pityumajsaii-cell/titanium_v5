from fastapi import FastAPI

app = FastAPI(title="Titanium Central Brain")

# --- CORE STATUS ---
@app.get("/")
def root():
    return {
        "status": "LIVE",
        "system": "Titanium CENTRAL BRAIN",
        "mode": "production",
        "core": "active"
    }

@app.get("/health")
def health():
    return {"status": "ok", "brain": "stable"}

# --- MODULE ROUTER (future expansion) ---
@app.get("/api/modules")
def modules():
    return {
        "orchestrator": "linked",
        "gateway": "linked",
        "brain": "central",
        "billing": "ready"
    }

# --- REVENUE CORE (stub but valid) ---
@app.get("/api/revenue/status")
def revenue():
    return {
        "stripe": "prepared",
        "checkout": "pending_webhook",
        "state": "inactive_but_ready"
    }
