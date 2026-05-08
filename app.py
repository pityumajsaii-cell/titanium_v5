from fastapi import FastAPI, Header, HTTPException
import time
import uuid

app = FastAPI(title="Titanium Revenue Engine v2")

# simple in-memory usage store
USAGE = {}

API_KEYS = {
    "demo-key": "free-user"
}

@app.get("/")
def root():
    return {
        "system": "Titanium Revenue Engine v2",
        "status": "LIVE",
        "billing": "stripe_ready",
        "auth": "api_key_required"
    }

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/api/key")
def get_key():
    # demo key generator (replace with Stripe webhook later)
    key = str(uuid.uuid4())
    API_KEYS[key] = "paid-user"
    USAGE[key] = 0
    return {"api_key": key}

@app.get("/api/data")
def protected(api_key: str = Header(None)):
    if not api_key or api_key not in API_KEYS:
        raise HTTPException(status_code=401, detail="Invalid API Key")

    # usage tracking
    USAGE[api_key] = USAGE.get(api_key, 0) + 1

    return {
        "data": "premium_ai_response",
        "usage_count": USAGE[api_key],
        "billing_model": "per_request"
    }

@app.get("/api/usage")
def usage(api_key: str):
    return {
        "api_key": api_key,
        "requests": USAGE.get(api_key, 0)
    }

@app.get("/pricing")
def pricing():
    return {
        "starter": "9$/month",
        "pro": "29$/month",
        "enterprise": "99$/month",
        "note": "Stripe integration ready (webhook step needed)"
    }
