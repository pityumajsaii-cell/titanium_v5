from fastapi import FastAPI

app = FastAPI(title="Titanium SaaS Core", version="1.0")

@app.get("/")
def root():
    return {
        "status": "ONLINE",
        "system": "Titanium CLEAN CORE SAAS",
        "version": "v1",
        "mode": "production_ready"
    }

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/api/status")
def status():
    return {
        "service": "titanium-core",
        "state": "running",
        "deployment": "hf-space"
    }
