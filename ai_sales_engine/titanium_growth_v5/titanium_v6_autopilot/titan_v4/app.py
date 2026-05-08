from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import json, uuid, time, os

app = FastAPI(title="Titanium Acquisition Engine V4")

DB = "leads.json"
start = time.time()

def load():
    try:
        return json.load(open(DB))
    except:
        return {}

def save(data):
    json.dump(data, open(DB, "w"), indent=2)

@app.get("/")
def root():
    return {
        "status": "LIVE",
        "system": "Titanium V4 Acquisition Engine",
        "uptime_sec": int(time.time() - start)
    }

@app.get("/health")
def health():
    return {"status": "ok"}

# ---------------- LEAD CAPTURE ----------------
@app.post("/capture")
def capture(name: str, email: str, interest: str):
    db = load()
    lid = str(uuid.uuid4())

    db[lid] = {
        "name": name,
        "email": email,
        "interest": interest,
        "status": "new",
        "created": time.time()
    }

    save(db)

    return {
        "lead_id": lid,
        "status": "captured",
        "next": f"/landing/{lid}"
    }

# ---------------- LANDING PAGE ----------------
@app.get("/landing/{lead_id}", response_class=HTMLResponse)
def landing(lead_id: str):
    db = load()
    lead = db.get(lead_id)

    if not lead:
        return "<h1>Lead not found</h1>"

    return f"""
    <html>
      <body style="font-family:Arial;text-align:center;padding:40px">
        <h1>Hi {lead["name"]}</h1>
        <p>AI system detected interest in: <b>{lead["interest"]}</b></p>

        <h3>Automated Offer Ready</h3>

        <form action="/buy" method="post">
            <input name="product" value="{lead[interest]}" />
            <button type="submit">Activate System</button>
        </form>
      </body>
    </html>
    """

# ---------------- PIPELINE ----------------
@app.get("/pipeline")
def pipeline():
    db = load()

    return {
        "total": len(db),
        "new": len([x for x in db.values() if x["status"] == "new"]),
        "leads": db
    }

# ---------------- STRIPE PLACEHOLDER ----------------
@app.post("/buy")
def buy(product: str):
    return {
        "status": "stripe_not_connected",
        "product": product,
        "note": "Add STRIPE_SECRET_KEY in .env for activation"
    }
