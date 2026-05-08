import requests
import time
import json
import random

# --- KONFIGURÁCIÓ (A Te Agyad címe) ---
NEXUS_URL = "https://titanium-render-publi-yht5.onrender.com/api/bridge" # Vagy az új Railway/Fly URL-ed
ADMIN_TOKEN = "dev"

def hunt_and_report():
    print("🚀 Titanium One: Vadászat elindítva...")
    
    # SZIMULÁLT ADATGYŰJTÉS (Ezt váltjuk majd valódi crawlerre)
    # Példa: Magas értékű üzleti lehetőségek keresése
    sample_data = {
        "source": "Titanium-One-Unit-01",
        "payload": {
            "lead": "Potential Enterprise Client",
            "info": "Looking for AI automation solutions",
            "value_estimate": random.randint(100, 500)
        },
        "value": random.randint(100, 500)
    }

    try:
        response = requests.post(
            NEXUS_URL,
            json=sample_data,
            headers={"Authorization": f"Bearer {ADMIN_TOKEN}"},
            timeout=10
        )
        if response.status_code == 202:
            print(f"✅ Adat sikeresen beküldve az Agyba! Döntés: {response.json().get('brain_decision')}")
        else:
            print(f"⚠️ Hiba a beküldésnél: {response.status_code}")
    except Exception as e:
        print(f"❌ Kapcsolati hiba: {e}")

if __name__ == "__main__":
    while True:
        hunt_and_report()
        time.sleep(60) # Percenként egy jelentés
