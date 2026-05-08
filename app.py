from fastapi import FastAPI

app = FastAPI(title="Titanium Revenue Engine")

@app.get("/")
def root():
    return {
        "status": "LIVE",
        "system": "Titanium Production Core",
        "mode": "stable",
        "monetization": "stripe_ready"
    }

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/api/status")
def status():
    return {
        "service": "titanium-core",
        "state": "running",
        "billing": "enabled",
        "deploy": "hf-ready"
    }
