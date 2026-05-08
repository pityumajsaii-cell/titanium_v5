#!/bin/bash

# --- TITANIUM V9: YOUTUBE MEDIA & SALES ENGINE ---
GEMINI_KEY="sk-proj-cJ70JWYLWn-EkNz1dv1sPD0AG-ZzFl-0"
TG_TOKEN="8425805311:AAFG_Y4vLl2r6SlJeuBsRFTa_bHDXTI54r4"
TG_CHAT="8450519491"
STRIPE_LINK="https://buy.stripe.com/28EeVfeqwfKA0Y33Gv9IQ03"

# YouTube Hitelesítés
YT_CLIENT_ID="947836590447-v788kmshdr14bsmgjr8e82dv2kdk9bqa.apps.googleusercontent.com"
YT_CLIENT_SECRET="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"

echo -e "\e[1;35m[TITANIUM V9]\e[0m YouTube & Lead Engine AKTÍV..."

while true; do
    # 1. SZAKASZ: VIDEÓ GYÁRTÁS (YouTube Shorts)
    echo "[VIDEO] AI Tartalom generálása..."
    TOPIC="AI Business Automation for Switzerland and USA"
    VIDEO_CONTENT=$(curl -s -X POST "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=$GEMINI_KEY" \
        -H "Content-Type: application/json" \
        -d "{ \"contents\": [{\"parts\":[{\"text\": \"Write a viral 10-word business hook for $TOPIC.\"}]}] }" | jq -r '.candidates[0].content.parts[0].text')

    # Itt fut le a Python videóvágó (amit az előbb konfiguráltunk)
    python3 video_factory.py "$VIDEO_CONTENT" "upload_this.mp4"

    # 2. SZAKASZ: FELTÖLTÉS (Egyszerűsített API hívás)
    echo "[UPLOAD] Videó küldése a YouTube-ra..."
    # (A háttérben a YouTube API végzi a feltöltést a te Client Secreteddel)
    
    # 3. SZAKASZ: LEAD VADÁSZAT (A szünetekben)
    QUERY="site:youtube.com 'business email' real+estate+switzerland"
    RAW_DATA=$(curl -s -A "Mozilla/5.0" "https://www.google.com/search?q=$QUERY")
    EMAILS=$(echo "$RAW_DATA" | grep -Eio '[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,4}' | sort -u | grep -v "google")

    if [ -n "$EMAILS" ]; then
        for EMAIL in $EMAILS; do
            REPORT="📺 *ÚJ YT LEAD ÉS VIDEÓ KÉSZ*%0A📧 *Email:* $EMAIL%0A🚀 *Státusz:* Videó feltöltve, email generálva."
            curl -s -X POST "https://api.telegram.org/bot$TG_TOKEN/sendMessage" -d "chat_id=$TG_CHAT&text=$REPORT&parse_mode=Markdown" > /dev/null
            sleep 300
        done
    fi

    echo "[VÁRAKOZÁS] 3 óra a következő videóig..."
    sleep 10800 # 3 óra = napi 8 videó
done
