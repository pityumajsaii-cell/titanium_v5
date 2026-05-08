from fastapi import FastAPI, Request, BackgroundTasks
from fastapi.responses import HTMLResponse
import stripe, json, uuid, os, time
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Titanium Money Flow V1")

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
DB = "db.json"

# ---------------- DB ----------------
def load():
    try:
        return json.load(open(DB))
    except:
        return {}

def save(data):
    json.dump(data, open(DB, "w"), indent=2)

# ---------------- LEAD CAPTURE ----------------
@app.post("/lead")
def lead(name: str, email: str, interest: str):
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
        "landing": f"/landing/{lid}"
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
            <h1>Hi {lead['name']}</h1>
            <p>Interest detected: <b>{lead['interest']}</b></p>

            <form action="/checkout/{lead_id}" method="post">
                <button style="padding:20px;background:green;color:white;">
                    Buy Now
                </button>
            </form>
        </body>
    </html>
    """

# ---------------- STRIPE CHECKOUT ----------------
@app.post("/checkout/{lead_id}")
def checkout(lead_id: str):
    db = load()
    lead = db.get(lead_id)

    if not lead:
        return {"error": "lead not found"}

    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        mode="payment",
        line_items=[{
            "price_data": {
                "currency": "eur",
                "product_data": {
                    "name": lead["interest"]
                },
                "unit_amount": 4900
            },
            "quantity": 1
        }],
        success_url="http://localhost:8000/success",
        cancel_url="http://localhost:8000/cancel",
        metadata={"lead_id": lead_id}
    )

    return {"checkout_url": session.url}

# ---------------- WEBHOOK ----------------
@app.post("/webhook/stripe")
async def webhook(request: Request):
    payload = await request.body()

    # (simplified — productionban signature check kell)
    event = json.loads(payload)

    db = load()

    if "data" in event:
        try:
            lead_id = event["data"]["object"]["metadata"]["lead_id"]
            if lead_id in db:
                db[lead_id]["status"] = "paid"
                save(db)
        except:
            pass

    return {"ok": True}

# ---------------- AUTOMATION ----------------
@app.get("/automation/run")
def automation():
    db = load()

    updated = 0
    for lid, lead in db.items():
        if lead["status"] == "new":
            lead["status"] = "contacted"
            updated += 1

    save(db)

    return {
        "message": "automation executed",
        "updated": updated
    }

# ---------------- PIPELINE ----------------
@app.get("/pipeline")
def pipeline():
    db = load()

    return {
        "total": len(db),
        "new": len([x for x in db.values() if x["status"] == "new"]),
        "contacted": len([x for x in db.values() if x["status"] == "contacted"]),
        "paid": len([x for x in db.values() if x["status"] == "paid"])
    }

# ---------------- HEALTH ----------------
@app.get("/health")
def health():
    return {"status": "LIVE", "system": "Titanium Money Flow V1"}
