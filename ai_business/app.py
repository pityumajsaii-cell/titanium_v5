from fastapi import FastAPI
from pydantic import BaseModel
import time

app = FastAPI(title="AI Business Core")

start = time.time()

# --- REQUEST MODEL ---
class AskRequest(BaseModel):
    message: str

# --- FREE LIMIT (very simple demo logic) ---
FREE_LIMIT = 3
user_calls = {}

# --- AI CORE (placeholder logic, később OpenAI/Gemini ide jön) ---
def ai_engine(msg: str):
    return f"AI RESPONSE: {msg[::-1]}"

@app.get("/")
def root():
    return {
        "status": "LIVE",
        "system": "AI BUSINESS CORE",
        "uptime": int(time.time() - start)
    }

@app.get("/health")
def health():
    return {"status": "ok"}

# --- MAIN AI ENDPOINT ---
@app.post("/ask")
def ask(req: AskRequest):
    user_id = "global_user"

    count = user_calls.get(user_id, 0)

    if count >= FREE_LIMIT:
        return {
            "error": "LIMIT_REACHED",
            "message": "Upgrade required",
            "stripe": "not_connected_yet"
        }

    user_calls[user_id] = count + 1

    return {
        "input": req.message,
        "output": ai_engine(req.message),
        "usage": user_calls[user_id],
        "limit": FREE_LIMIT
    }

# --- STATUS / MONETIZATION READY ---
@app.get("/api/status")
def status():
    return {
        "system": "ai-business-core",
        "monetization": "stripe_ready_structure",
        "next_step": "connect_payment_gateway"
    }

