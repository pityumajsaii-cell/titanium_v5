import os, json, uuid, requests, smtplib, time
from fastapi import FastAPI, BackgroundTasks
from email.mime.text import MIMEText
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Titanium V3 Autonomous Agent")
DB_FILE = "v3_leads.json"

def get_db():
    try: return json.load(open(DB_FILE))
    except: return {}

def save_db(data):
    json.dump(data, open(DB_FILE, "w"), indent=2)

# --- 🧠 VALÓDI AI GENERÁLÁS (GEMINI) ---
def ai_generate_sales_pitch(name, interest):
    api_key = os.getenv("GEMINI_API_KEY")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    prompt = f"Írj egy rövid, meggyőző magyar nyelvű sales emailt {name} részére, akit érdekel a {interest}. Max 3 mondat, legyen benne sürgetés és CTA."
    
    try:
        res = requests.post(url, json={"contents": [{"parts": [{"text": prompt}]}]})
        return res.json()['candidates'][0]['content']['parts'][0]['text']
    except:
        return f"Szia {name}! Láttuk, hogy érdekel a {interest}. Az AI rendszerünk készen áll a skálázásra!"

# --- 📩 VALÓDI OUTREACH (SMTP + TELEGRAM) ---
def perform_outreach(lead_id, name, email, interest):
    # 1. AI szöveg generálása
    pitch = ai_generate_sales_pitch(name, interest)
    
    # 2. Email küldés (Aktív!)
    user = os.getenv("SMTP_USER")
    pw = os.getenv("SMTP_PASS")
    msg = MIMEText(pitch)
    msg['Subject'] = f"Exkluzív lehetőség: {interest}"
    msg['From'] = user
    msg['To'] = email
    
    email_status = "FAILED"
    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(user, pw)
            server.send_message(msg)
        email_status = "SUCCESS"
    except Exception as e:
        print(f"SMTP Error: {e}")

    # 3. Jelentés Telegramon neked
    report = f"🤖 [V3 AGENT ACTION]\n👤 Név: {name}\n📧 Email: {email_status}\n🔥 Lead: {interest}\n📝 AI Pitch: {pitch[:100]}..."
    tg_token = os.getenv("TELEGRAM_BOT_TOKEN")
    tg_chat = os.getenv("TELEGRAM_CHAT_ID")
    requests.post(f"https://api.telegram.org/bot{tg_token}/sendMessage", json={"chat_id": tg_chat, "text": report})

    # 4. CRM frissítés
    db = get_db()
    if lead_id in db:
        db[lead_id].update({"status": "contacted", "ai_pitch": pitch, "outreach_time": time.time()})
        save_db(db)

@app.post("/lead")
def new_lead(name: str, email: str, interest: str, bg: BackgroundTasks):
    db = get_db()
    lid = str(uuid.uuid4())
    db[lid] = {"name": name, "email": email, "interest": interest, "status": "new", "created": time.time()}
    save_db(db)
    
    # Az autonóm ügynök azonnali indítása a háttérben
    bg.add_task(perform_outreach, lid, name, email, interest)
    return {"status": "Agent Deployed", "lead_id": lid}

@app.get("/pipeline")
def pipeline():
    return get_db()

