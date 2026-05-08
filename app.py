from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
import sqlite3, datetime, os

app = FastAPI()
DB_PATH = "titanium_core.db"

def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("CREATE TABLE IF NOT EXISTS core_vault (id INTEGER PRIMARY KEY AUTOINCREMENT, source TEXT, val REAL, timestamp DATETIME)")

init_db()

@app.get("/", response_class=HTMLResponse)
async def root():
    return "<h1>Titanium Trinity Engine: ONLINE</h1><p>Status: KESZ_RENDSZER_ACTIVE</p>"

@app.post("/api/bridge")
async def bridge(request: Request):
    data = await request.json()
    val = data.get("value", 0)
    source = data.get("source", "Titanium-Unit")
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("INSERT INTO core_vault (source, val, timestamp) VALUES (?, ?, ?)",
                     (source, val, datetime.datetime.now()))
    return {"status": "SUCCESS", "vault": "SYNCED"}

@app.get("/admin", response_class=HTMLResponse)
async def admin():
    with sqlite3.connect(DB_PATH) as conn:
        logs = conn.execute("SELECT * FROM core_vault ORDER BY timestamp DESC LIMIT 5").fetchall()
    log_html = "".join([f"<li>{l[3]} - {l[1]}: {l[2]} EUR</li>" for l in logs])
    return f"<html><body style='background:#050505;color:#00ffcc;font-family:monospace;'><h1>💎 CORE ADMIN</h1><ul>{log_html}</ul></body></html>"
