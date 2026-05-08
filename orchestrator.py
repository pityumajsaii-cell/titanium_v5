import time
import requests
import os
import subprocess

# --- CONFIG ---
TARGET_BASE = "https://pityumajsaii-cell-titanium-v5.hf.space"
HEALTH_URL = f"{TARGET_BASE}/health"
HUNTER_SCRIPT = "titanium_one.py"

def check_hf_status():
    print(f"📡 [ORCHESTRATOR] Célpont ellenőrzése: {HEALTH_URL}")
    try:
        r = requests.get(HEALTH_URL, timeout=10)
        if r.status_code == 200:
            print("🟢 [SUCCESS] Hugging Face Space ONLINE és READY!")
            return True
        else:
            print(f"⏳ [WAIT] Space válaszol, de státusza: {r.status_code}")
    except Exception:
        print("🔴 [OFFLINE] A szerver még nem elérhető (Building vagy 404)...")
    return False

def start_hunter():
    print(f"🚀 [START] Titanium Vadász indítása: {HUNTER_SCRIPT}")
    # Leállítjuk a régit, ha futna
    subprocess.run(["pkill", "-f", HUNTER_SCRIPT])
    # Elindítjuk az újat a háttérben
    subprocess.Popen(["python3", HUNTER_SCRIPT])
    print("💎 [ACTIVE] A rendszer élesítve, a 404-es korszak véget ért.")

if __name__ == "__main__":
    print("🛡️ TITANIUM ORCHESTRATOR V1.0 AKTIVÁLVA")
    while True:
        if check_hf_status():
            start_hunter()
            break
        time.sleep(10) # 10 másodpercenként csekkol, nem terhel
