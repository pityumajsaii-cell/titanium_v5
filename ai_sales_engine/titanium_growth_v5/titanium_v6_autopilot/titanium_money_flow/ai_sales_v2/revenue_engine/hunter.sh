#!/bin/bash

# --- TITANIUM V9: YOUTUBE & GOOGLE HYBRID ENGINE ---
GEMINI_KEY="sk-proj-cJ70JWYLWn-EkNz1dv1sPD0AG-ZzFl-0"
TG_TOKEN="8425805311:AAFG_Y4vLl2r6SlJeuBsRFTa_bHDXTI54r4"
TG_CHAT="8450519491"
STRIPE_LINK="https://buy.stripe.com/28EeVfeqwfKA0Y33Gv9IQ03"

# Keresési pool: Üzleti Google keresések + YouTube specifikus kulcsszavak
SEARCH_POOL=(
  "site:youtube.com 'business email' real+estate+switzerland"
  "site:youtube.com 'contact' dental+clinic+usa"
  "software+agency+zürich+email"
  "youtube+channel+about+contact+email+austin"
)

echo "[V9 ENGINE] Hybrid YouTube-Google vadászat indul..."

while true; do
    QUERY=${SEARCH_POOL[$RANDOM % ${#SEARCH_POOL[@]}]}
    
    # Keresés és email bányászat
    RAW_DATA=$(curl -s -A "Mozilla/5.0" "https://www.google.com/search?q=$QUERY")
    EMAILS=$(echo "$RAW_DATA" | grep -Eio '[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,4}' | sort -u | grep -v "google")

    if [ -n "$EMAILS" ]; then
        for EMAIL in $EMAILS; do
            # AI AJÁNLAT: Most már megemlítjük a YouTube-ot és a videós jelenlétet
            PROMPT="Write a sales email to $EMAIL. They are active on YouTube/Online. Offer AI automation to turn their viewers into paying customers and automate their lead follow-up. High-end tone. Link: $STRIPE_LINK."
            
            AI_RESPONSE=$(curl -s -X POST "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=$GEMINI_KEY" \
                -H "Content-Type: application/json" \
                -d "{ \"contents\": [{\"parts\":[{\"text\": \"$PROMPT\"}]}] }")

            AI_MESSAGE=$(echo "$AI_RESPONSE" | jq -r '.candidates[0].content.parts[0].text // "null"')

            if [ "$AI_MESSAGE" != "null" ]; then
                ENCODED_MESSAGE=$(echo "$AI_MESSAGE" | jq -sRr @uri)
                REPORT="📺 *YOUTUBE/ÜZLETI LEAD TALÁLVA*%0A📧 *Email:* $EMAIL%0A📝 *Ajánlat:* $ENCODED_MESSAGE"
                
                curl -s -X POST "https://api.telegram.org/bot$TG_TOKEN/sendMessage" \
                    -d "chat_id=$TG_CHAT&text=$REPORT&parse_mode=Markdown" > /dev/null
            fi
            sleep 300
        done
    fi
    sleep 1800
done
