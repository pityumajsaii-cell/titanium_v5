from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import datetime

app = FastAPI(title="Titanium V44 Clean Core")

@app.get("/")
def root():
    return {
        "status": "RUNNING",
        "system": "Titanium V44 CLEAN",
        "time": str(datetime.datetime.now())
    }

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/api/bridge")
def bridge(payload: dict = {}):
    return {
        "status": "success",
        "received": payload,
        "timestamp": str(datetime.datetime.now())
    }

@app.get("/admin", response_class=HTMLResponse)
def admin():
    return """
    <html>
        <body style='background:#111;color:#0f0;font-family:monospace'>
            <h1>💎 TITANIUM V44 CLEAN DEPLOY</h1>
            <p>STATUS: ONLINE</p>
        </body>
    </html>
    """
