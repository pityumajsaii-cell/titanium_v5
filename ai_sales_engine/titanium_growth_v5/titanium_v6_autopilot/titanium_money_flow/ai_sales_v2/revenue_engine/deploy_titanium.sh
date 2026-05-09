#!/bin/bash
echo -e "\e[1;34m[DEPLOY]\e[0m Render & GitHub fájlok generálása..."

# 1. A V8 MOTOR (hunter.sh)
cat << 'HUNTER' > hunter.sh
#!/bin/bash
GEMINI_KEY="sk-proj-cJ70JWYLWn-EkNz1dv1sPD0AG-ZzFl-0"
TG_TOKEN="8425805311:AAFG_Y4vLl2r6SlJeuBsRFTa_bHDXTI54r4"
TG_CHAT="8450519491"
STRIPE_LINK="https://buy.stripe.com/28EeVfeqwfKA0Y33Gv9IQ03"

SEARCH_POOL=("dentist+zurich+contact" "real+estate+sydney+contact" "software+austin+contact" "law+firm+geneva+contact")

while true; do
    QUERY=${SEARCH_POOL[$RANDOM % ${#SEARCH_POOL[@]}]}
    RAW_DATA=$(curl -s -A "Mozilla/5.0" "https://www.google.com/search?q=$QUERY")
    EMAILS=$(echo "$RAW_DATA" | grep -Eio '[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,4}' | sort -u | grep -v "google")

    if [ -n "$EMAILS" ]; then
        for EMAIL in $EMAILS; do
            PROMPT="Write a high-end corporate sales email to $EMAIL for AI automation services. Include: $STRIPE_LINK."
            AI_MESSAGE=$(curl -s -X POST "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=$GEMINI_KEY" \
                -H "Content-Type: application/json" \
                -d "{ \"contents\": [{\"parts\":[{\"text\": \"$PROMPT\"}]}] }" | jq -r '.candidates[0].content.parts[0].text')

            ENCODED_MESSAGE=$(echo "$AI_MESSAGE" | jq -sRr @uri)
            curl -s -X POST "https://api.telegram.org/bot$TG_TOKEN/sendMessage" -d "chat_id=$TG_CHAT&text=💎 *CLOUDBOT V8 LEAD*%0A📧 $EMAIL%0A📝 $ENCODED_MESSAGE&parse_mode=Markdown"
            sleep 300
        done
    fi
    sleep 1800
done
HUNTER

# 2. DOCKERFILE (A Rendernek)
cat << 'DOCKER' > Dockerfile
FROM alpine:latest
RUN apk add --no-cache bash curl jq
COPY hunter.sh /app/hunter.sh
WORKDIR /app
RUN chmod +x hunter.sh
CMD ["./hunter.sh"]
DOCKER

# 3. RENDER CONFIG
cat << 'RENDER' > render.yaml
services:
  - type: worker
    name: titanium-v8-cloud
    env: docker
    plan: free
RENDER

chmod +x hunter.sh
echo -e "\e[1;32m[KÉSZ]\e[0m Minden fájl készen áll: hunter.sh, Dockerfile, render.yaml."
echo -e "\e[1;33m[TEENDŐ]\e[0m Töltsd fel ezeket a GitHubodra, és a Render automatikusan elindítja a globális vadászatot!"
