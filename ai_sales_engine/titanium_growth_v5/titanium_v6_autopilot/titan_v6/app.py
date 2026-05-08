from fastapi import FastAPI, BackgroundTasks, Request
import json, uuid, time, threading, os

app = FastAPI(title="Titanium V6.1 Autopilot Engine")

DB = "db.json"
start = time.time()

def load():
    try: return json.load(open(DB))
    except: return {}

def save(d):
    json.dump(d, open(DB,"w"), indent=2)

# ---------------- AI ENGINE (simple but effective) ----------------
def ai_message(name, interest, stage):
    if stage == "new":
        return f"Szia {name}, láttuk hogy érdekel: {interest}. Mutatok egy gyors megoldást."
    if stage == "warm":
        return f"Még mindig gondolkozol a {interest}-en? Van egy gyors setup rendszerünk."
    if stage == "hot":
        return f"Utolsó lehetőség {interest} automatizálásra kedvezménnyel."
    return "OK"

# ---------------- BACKGROUND WORKER ----------------
def follow_up_worker():
    while True:
        db = load()
        changed = False

        for lid, lead in db.items():
            if lead["status"] == "new":
                if time.time() - lead["created"] > 30:
                    lead["status"] = "warm"
                    lead["msg"] = ai_message(lead["name"], lead["interest"], "warm")
                    changed = True

            if lead["status"] == "warm":
                if time.time() - lead["created"] > 60:
                    lead["status"] = "hot"
                    lead["msg"] = ai_message(lead["name"], lead["interest"], "hot")
                    changed = True

        if changed:
            save(db)

        time.sleep(10)

threading.Thread(target=follow_up_worker, daemon=True).start()

# ---------------- API ----------------

@app.get("/")
def root():
    return {
        "status": "LIVE",
        "system": "Titanium V6.1 Autopilot",
        "uptime": int(time.time() - start)
    }

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
        "status": "captured",
        "next": "/pipeline"
    }

@app.post("/webhook/stripe")
async def stripe_webhook(req: Request):
    data = await req.body()

    db = load()
    # demo: minden fizetés = first lead paid
    for k in db:
        db[k]["status"] = "paid"
        break

    save(db)

    return {"status": "payment_processed"}

@app.get("/pipeline")
def pipeline():
    db = load()

    return {
        "total": len(db),
        "new": len([x for x in db.values() if x["status"]=="new"]),
        "warm": len([x for x in db.values() if x["status"]=="warm"]),
        "hot": len([x for x in db.values() if x["status"]=="hot"]),
        "paid": len([x for x in db.values() if x["status"]=="paid"]),
        "data": db
    }

@app.get("/health")
def health():
    return {"status": "ok", "engine": "V6.1 running"}
