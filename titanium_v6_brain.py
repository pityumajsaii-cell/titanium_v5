import os
import time
import requests
import subprocess
from datetime import datetime

# --- CONFIG ---
HF_URL = "https://pityumajsaii-cell-titanium-v5.hf.space"
HUNTER_SCRIPT = "titanium_one.py"

class TitaniumBrain:
    def __init__(self):
        self.state = "INIT"
        self.hunter_proc = None
        print(f"🧠 [V6 BRAIN] Rendszer inicializálva: {datetime.now()}")

    def log_event(self, message):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"💎 [{timestamp}] {message}")

    def get_hf_status(self):
        try:
            r = requests.get(f"{HF_URL}/", timeout=5)
            return r.status_code
        except:
            return 0

    def start_hunter(self):
        self.stop_hunter()
        self.log_event("🚀 Vadász indítása...")
        self.hunter_proc = subprocess.Popen(["python3", HUNTER_SCRIPT], 
                                          stdout=open("hunter.log", "a"), 
                                          stderr=subprocess.STDOUT)

    def stop_hunter(self):
        if self.hunter_proc:
            self.hunter_proc.terminate()
            self.hunter_proc = None
        subprocess.run(["pkill", "-f", HUNTER_SCRIPT], stderr=subprocess.DEVNULL)

    def run(self):
        while True:
            status = self.get_hf_status()
            
            # --- STATE MACHINE LOGIC ---
            if status == 200:
                if self.state != "RUN":
                    self.log_event("🟢 Állapot -> RUN (Szerver online)")
                    self.start_hunter()
                    self.state = "RUN"
            else:
                if self.state != "WAIT":
                    self.log_event(f"⏳ Állapot -> WAIT (Szerver kód: {status})")
                    self.stop_hunter()
                    self.state = "WAIT"
            
            # Watchdog: Ha RUN állapotban leállna a folyamat
            if self.state == "RUN" and (not self.hunter_proc or self.hunter_proc.poll() is not None):
                self.log_event("⚠️ Vadász váratlanul leállt! Újraindítás...")
                self.start_hunter()

            time.sleep(15)

if __name__ == "__main__":
    brain = TitaniumBrain()
    brain.run()
