from fastapi import FastAPI, Request
import os

app = FastAPI(title="Titanium SaaS")

@app.get("/")
def root():
    return {"status": "online", "system": "titanium_v5"}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/webhook")
async def webhook(request: Request):
    body = await request.body()
    print("WEBHOOK RECEIVED:", body)
    return {"status": "received"}
