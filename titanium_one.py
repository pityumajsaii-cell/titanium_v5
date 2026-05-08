import requests, time, random

# CSERÉLD KI az URL-t a te aktuális éles címedre!
TARGET_URL = "https://A-TE-KOYEB-URL-ED.koyeb.app/api/bridge" 

def start_hunting():
    print("🎯 Titanium One Vadászat elindítva...")
    while True:
        # Itt szimulálunk egy sikeres piaci találatot (pl. SEO hiba vagy eladó domain)
        market_find = {
            "source": "Titanium-One-v6",
            "type": "MARKET_LEAD",
            "value": random.uniform(50.0, 300.0),
            "details": "High-value business opportunity detected."
        }
        try:
            r = requests.post(TARGET_URL, json=market_find, timeout=10)
            if r.status_code == 202:
                print(f"💰 Találat jelentve! Érték: {market_find['value']:.2f} EUR")
            else:
                print(f"❌ Szerver hiba: {r.status_code}")
        except:
            print("🌐 Kapcsolati hiba, újrapróbálkozás...")
        
        time.sleep(30) # 30 másodpercenkénti adatküldés

if __name__ == "__main__":
    start_hunting()
