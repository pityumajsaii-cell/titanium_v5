import os
import requests
import stripe
from dotenv import load_dotenv

load_dotenv()

def check_system():
    print("🔍 --- TITANIUM RENDSZER ELLENŐRZÉS ---")
    
    # 1. Fájlrendszer ellenőrzés
    paths = ["app/main.py", "app/services/orchestrator.py", ".env"]
    for p in paths:
        status = "✅ OK" if os.path.exists(p) else "❌ HIÁNYZIK"
        print(f"Fájl: {p} -> {status}")

    # 2. GitHub Token ellenőrzés
    print("\n☁️ GitHub Kapcsolat tesztelése...")
    token = os.getenv("GITHUB_TOKEN")
    headers = {"Authorization": f"token {token}"}
    res = requests.get("https://api.github.com/user", headers=headers)
    if res.status_code == 200:
        print(f"✅ GitHub Token OK (Felhasználó: {res.json().get('login')})")
    else:
        print(f"❌ GitHub HIBA: {res.status_code} - {res.json().get('message')}")

    # 3. Stripe ellenőrzés
    print("\n💳 Stripe Kapcsolat tesztelése...")
    stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
    try:
        balance = stripe.Balance.retrieve()
        print("✅ Stripe API Kulcs OK")
    except Exception as e:
        print(f"❌ Stripe HIBA: {e}")

    # 4. Telegram ellenőrzés
    print("\n🤖 Telegram Bot tesztelése...")
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    url = f"https://api.telegram.org/bot{bot_token}/getMe"
    res = requests.get(url)
    if res.status_code == 200:
        print(f"✅ Telegram Bot OK (@{res.json()['result']['username']})")
    else:
        print(f"❌ Telegram HIBA: {res.status_code}")

check_system()
