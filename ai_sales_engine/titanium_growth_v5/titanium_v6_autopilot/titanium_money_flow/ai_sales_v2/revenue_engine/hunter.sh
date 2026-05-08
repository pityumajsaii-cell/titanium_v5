#!/bin/bash

# --- TITANIUM V9: YOUTUBE & GOOGLE HYBRID ENGINE ---
GEMINI_KEY="sk-proj-cJ70JWYLWn-EkNz1dv1sPD0AG-ZzFl-0"
TG_TOKEN="8425805311:AAFG_Y4vLl2r6SlJeuBsRFTa_bHDXTI54r4"
TG_CHAT="8450519491"
STRIPE_LINK="https://buy.stripe.com/28EeVfeqwfKA0Y33Gv9IQ03"

# Bővített keresési pool: YouTube üzleti adatok + Svájci/USA prémium szektorok
SEARCH_POOL=(
  "site:youtube.com 'business email' real+estate+switzerland"
  "site:youtube.com 'contact' luxury+car+rental+dubai"
  "site:youtube.com 'email' medical+clinic+usa"
  "software+agency+zürich+contact+email"
  "law+firm+geneva+youtube+channel+contact"
)

echo -e "\e[1;35m[V9 ENGINE]\e[0m Hybrid YouTube-Google vadászat indul..."

while true; do
    QUERY=${SEARCH_POOL[$RANDOM % ${#SEARCH_POOL[@]}]}
    echo -e "\e[1;34m[KERESÉS]\e[0m Célpont: $QUERY"
    
    # Keresés és email bányászat a Google indexéből
    RAW_DATA=$(curl -s -A "Mozilla/5.0" "https://www.google.com/search?q=$QUERY")
    EMAILS=$(echo "$RAW_DATA" | grep -Eio '[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,4}' | sort -u | grep -v "google")

    if [ -n "$EMAILS" ]; then
        for EMAIL in $EMAILS; do
            # AI AJÁNLAT: YouTube-fókuszú marketing szöveg
            PROMPT="Write a high-end sales email to $EMAIL. They have an online presence/YouTube channel. Offer an AI system that automatically converts their viewers into leads and handles customer service 24/7. Focus on ROI. Include link: $STRIPE_LINK."
            
            AI_RESPONSE=$(curl -s -X POST "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=$GEMINI_KEY" \
                -H "Content-Type: application/json" \
                -d "{ \"contents\": [{\"parts\":[{\"text\": \"$PROMPT\"}]}] }")

            AI_MESSAGE=$(echo "$AI_RESPONSE" | jq -r '.candidates[0].content.parts[0].text // "null"')

            if [ "$AI_MESSAGE" != "null" ]; then
                ENCODED_MESSAGE=$(echo "$AI_MESSAGE" | jq -sRr @uri)
                REPORT="📺 *YOUTUBE/PRÉMIUM LEAD*%0A📧 *Email:* $EMAIL%0A📍 *Piac:* $QUERY%0A📝 *Ajánlat:* $ENCODED_MESSAGE"
                
                curl -s -X POST "https://api.telegram.org/bot$TG_TOKEN/sendMessage" \
                    -d "chat_id=$TG_CHAT&text=$REPORT&parse_mode=Markdown" > /dev/null
                echo -e "✅ Lead küldve a Telegramra: $EMAIL"
            fi
            sleep 300 # 5 perc szünet a leadek között
        done
    fi
    echo -e "\e[1;33m[VÁRAKOZÁS]\e[0m Következő bányászati ciklus..."
    sleep 1800 # 30 perc szünet a blokkolás elkerülésére
done
