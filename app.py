from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
import sqlite3, datetime, os

app = FastAPI(title="Titanium Core Nexus")
DB_PATH = "titanium_core.db"

# Adatbázis inicializálás
def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("CREATE TABLE IF NOT EXISTS core_vault (id INTEGER PRIMARY KEY AUTOINCREMENT, source TEXT, val REAL, timestamp DATETIME)")
    conn.commit()
    conn.close()

init_db()

@app.get("/")
async def root():
    return {"system": "Titanium Core", "status": "ONLINE", "mode": "MAX_MODE"}

@app.get("/health")
async def health():
    return {"status": "ok", "timestamp": datetime.datetime.now().isoformat()}

@app.post("/api/bridge")
async def bridge(request: Request):
    try:
        data = await request.json()
        val = data.get("value", 0)
        source = data.get("source", "Titanium-Unit")
        conn = sqlite3.connect(DB_PATH)
        conn.execute("INSERT INTO core_vault (source, val, timestamp) VALUES (?, ?, ?)",
                     (source, val, datetime.datetime.now()))
        conn.commit()
        conn.close()
        return {"status": "SUCCESS", "vault": "SYNCED"}
    except Exception as e:
        return {"status": "ERROR", "message": str(e)}

@app.get("/admin", response_class=HTMLResponse)
async def admin():
    conn = sqlite3.connect(DB_PATH)
    logs = conn.execute("SELECT * FROM core_vault ORDER BY timestamp DESC LIMIT 10").fetchall()
    conn.close()
    log_rows = "".join([f"<tr><td>{l[3]}</td><td>{l[1]}</td><td><b>{l[2]} EUR</b></td></tr>" for l in logs])
    return f"""
    <html>
    <body style='background:#050505;color:#00ffcc;font-family:monospace;padding:20px;'>
        <h1 style='border-bottom:2px solid #00ffcc;'>💎 TITANIUM CORE VAULT</h1>
        <table border='1' style='width:100%; border-collapse:collapse; border-color:#00ffcc;'>
            <tr><th>Időpont</th><th>Forrás</th><th>Érték</th></tr>
            {log_rows}
        </table>
    </body>
    </html>
    """
