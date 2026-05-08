from fastapi import FastAPI, BackgroundTasks
from fastapi.responses import HTMLResponse
import json, uuid, os, stripe
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Titanium Growth V5")
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
DB_FILE = "crm_leads.json"

# --- HELPER FUNKCIÓK ---
def get_db():
    try: return json.load(open(DB_FILE))
    except: return {}

def save_db(data):
    json.dump(data, open(DB_FILE, "w"), indent=4)

# --- AI SALES COPY ENGINE (V5) ---
def generate_ai_copy(name, interest):
    return {
        "headline": f"Specialized AI Upgrade for {name}",
        "body": f"We noticed your interest in {interest}. Our Titanium V5 engine can automate this 100%.",
        "cta": f"Get started with {interest} Automation"
    }

# --- AUTOMATIZÁLT ÜGYNÖK LOGIKA ---
def process_outreach(lead_id: str):
    db = get_db()
    if lead_id in db:
        # Itt lehetne: send_email(db[lead_id]['email'])
        db[lead_id]["status"] = "contacted"
        db[lead_id]["last_action"] = "AI_Outreach_Sent"
        save_db(db)

# --- ENDPOINTS ---

@app.post("/capture")
def capture_lead(name: str, email: str, interest: str, background_tasks: BackgroundTasks):
    db = get_db()
    lid = str(uuid.uuid4())
    db[lid] = {"name": name, "email": email, "interest": interest, "status": "new"}
    save_db(db)
    
    # Automatikus outreach indítása a háttérben
    background_tasks.add_task(process_outreach, lid)
    return {"status": "captured", "lead_id": lid, "action": "outreach_started"}

@app.get("/landing/{lead_id}", response_class=HTMLResponse)
def landing_page(lead_id: str):
    db = get_db()
    lead = db.get(lead_id)
    if not lead: return "<h1>Lead Not Found</h1>"
    
    copy = generate_ai_copy(lead['name'], lead['interest'])
    
    return f"""
    <html>
        <body style='font-family:sans-serif; text-align:center; padding:50px;'>
            <h1>{copy['headline']}</h1>
            <p>{copy['body']}</p>
            <form action='/buy' method='post'>
                <input type='hidden' name='product' value='{lead['interest']}'>
                <button style='padding:20px; background:green; color:white;'>{copy['cta']}</button>
            </form>
        </body>
    </html>
    """

@app.get("/pipeline")
def get_pipeline():
    db = get_db()
    return {
        "stats": {
            "total": len(db),
            "new": len([l for l in db.values() if l['status'] == 'new']),
            "active": len([l for l in db.values() if l['status'] == 'contacted'])
        },
        "leads": db
    }

@app.get("/health")
def health():
    return {"engine": "Titanium-V5-Growth", "status": "online"}

