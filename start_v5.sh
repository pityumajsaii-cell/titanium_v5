#!/bin/bash
echo "🛡️ TITANIUM V5.2 — FULL POWER ONLINE"
echo "Minden API (Stripe, Google, GitHub, Render, Telegram) betöltve."
pip install -q fastapi uvicorn requests python-dotenv stripe
uvicorn app.main:app --host 0.0.0.0 --port 8000
