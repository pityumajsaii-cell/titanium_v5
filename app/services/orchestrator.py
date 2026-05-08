import requests
import os
import stripe
from dotenv import load_dotenv

load_dotenv()

def send_telegram_log(message):
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    if token and chat_id:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        requests.post(url, json={"chat_id": chat_id, "text": f"🤖 TITANIUM DEBUG:\n{message}"})

def create_github_repo(repo_name):
    token = os.getenv("GITHUB_TOKEN")
    url = "https://api.github.com/user/repos"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
        "X-GitHub-Api-Version": "2022-11-28"
    }
    payload = {"name": repo_name, "private": False}
    
    res = requests.post(url, json=payload, headers=headers)
    
    if res.status_code == 201:
        send_telegram_log(f"✅ SIKER: {repo_name} létrehozva!")
        return res.json().get("html_url")
    else:
        # PONTOS HIBAÜZENET KIÍRÁSA
        error_msg = f"Hiba {res.status_code}: {res.json().get('message')}"
        print(f"DEBUG: {error_msg}")
        send_telegram_log(f"❌ GitHub Hiba!\nKód: {res.status_code}\nÜzenet: {res.json().get('message')}")
        return None

def setup_stripe_product(name):
    stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
    try:
        product = stripe.Product.create(name=name)
        price = stripe.Price.create(product=product.id, unit_amount=5000, currency="eur", recurring={"interval": "month"})
        return price.id
    except Exception as e:
        return f"Stripe Error: {str(e)}"

def trigger_render_deploy(repo_url, name):
    # Render deploy logika...
    pass
