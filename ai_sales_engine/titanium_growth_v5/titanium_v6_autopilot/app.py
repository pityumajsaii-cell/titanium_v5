from fastapi import FastAPI, BackgroundTasks, Request
import json, uuid, os, stripe, time
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Titanium V6 Autopilot")
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
DB_FILE = "v6_growth_db.json"

# --- ADATBÁZIS KEZELÉS ---
def get_db():
    try: return json.load(open(DB_FILE))
    except: return {}

def save_db(data):
    json.dump(data, open(DB_FILE, "w"), indent=4)

# --- AI SALES AGENT CORE ---
def ai_agent_sequence(lead_id, step):
    db = get_db()
    lead = db.get(lead_id)
    if not lead: return
    
    # Különböző üzenetek a tölcsér különböző fázisaiban
    sequences = {
        1: f"Szia {lead['name']}! Láttuk, hogy érdekel a {lead['interest']}. Itt egy exkluzív ajánlat.",
        2: f"Még mindig bizonytalan vagy a {lead['interest']} kapcsán? Az AI motorunk készen áll.",
        3: "Utolsó esély! 20% kedvezmény a Titanium V6 hozzáféréshez."
    }
    return sequences.get(step, "Ajánlat vége.")

# --- ESEMÉNYVEZÉRELT LOGIKA ---
@app.post("/webhook/stripe")
async def stripe_webhook(request: Request):
    payload = await request.body()
    # Itt a Stripe eseményeket dolgozzuk fel (Sikeres fizetés esetén CRM frissítés)
    # Titanium: Ide jön majd a Stripe szignatúra ellenőrzés
    return {"status": "event_received"}

@app.post("/inbound/lead")
def inbound_lead(name: str, email: str, interest: str, background_tasks: BackgroundTasks):
    db = get_db()
    lid = str(uuid.uuid4())
    db[lid] = {
        "id": lid, "name": name, "email": email, 
        "interest": interest, "status": "lead_captured", 
        "score": 50, "created_at": time.time()
    }
    save_db(db)
    
    # Első AI outreach ütemezése
    background_tasks.add_task(print, f"🔵 AI AGENT: Outreach sequence 1 sent to {email}")
    return {"status": "growth_sequence_initiated", "lead_id": lid}

@app.get("/dashboard")
def dashboard():
    db = get_db()
    return {
        "funnel_stats": {
            "total_leads": len(db),
            "converted": len([l for l in db.values() if l['status'] == 'paid']),
            "warm_leads": len([l for l in db.values() if l['score'] > 70])
        },
        "recent_activity": list(db.values())[-5:]
    }

@app.get("/health")
def health():
    return {"system": "Titanium V6", "engine": "Event-Driven", "status": "online"}
