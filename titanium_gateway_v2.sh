#!/data/data/com.termux/files/usr/bin/bash

NODES=(
"https://pityumajsaii-cell-titanium-v5.hf.space"
)

echo "🧠 TITANIUM MULTI-NODE GATEWAY V2 START"

check_node() {
    URL=$1

    ROOT=$(curl -s -o /dev/null -w "%{http_code}" $URL/)
    DOCS=$(curl -s -o /dev/null -w "%{http_code}" $URL/docs)
    HEALTH=$(curl -s -o /dev/null -w "%{http_code}" $URL/health)

    SCORE=0

    [ "$ROOT" = "200" ] && SCORE=$((SCORE+1))
    [ "$DOCS" = "200" ] && SCORE=$((SCORE+1))
    [ "$HEALTH" = "200" ] && SCORE=$((SCORE+1))

    # DEBUG CSAK STDERR (nem keveredik a számba)
    echo "📡 $URL → root:$ROOT docs:$DOCS health:$HEALTH SCORE:$SCORE" >&2

    # CSAK TISZTA SZÁM
    printf "%s" "$SCORE"
}

echo "🔍 Scanning nodes..."

BEST_NODE=""
BEST_SCORE=0

for NODE in "${NODES[@]}"; do
    SCORE=$(check_node "$NODE")

    if [ "$SCORE" -gt "$BEST_SCORE" ]; then
        BEST_SCORE=$SCORE
        BEST_NODE=$NODE
    fi
done

if [ "$BEST_SCORE" -lt 1 ]; then
    echo "❌ NO LIVE NODE FOUND → retry later"
    exit 1
fi

echo "🟢 BEST NODE SELECTED: $BEST_NODE (score: $BEST_SCORE)"

echo "⏳ Stabilizing node..."

while true; do
    STATUS=$(curl -s -o /dev/null -w "%{http_code}" $BEST_NODE/)

    if [ "$STATUS" = "200" ]; then
        echo "🟢 NODE STABLE"
        break
    fi

    echo "⏳ waiting stability... ($STATUS)"
    sleep 3
done

echo "🎯 Starting Titanium Hunter"

pkill -f titanium_one.py 2>/dev/null
nohup python3 titanium_one.py > hunter.log 2>&1 &
HUNTER_PID=$!

echo "✅ Hunter PID: $HUNTER_PID"

echo "🛡️ Watchdog ACTIVE"

while true; do

    if ! ps -p $HUNTER_PID > /dev/null; then
        echo "⚠️ Hunter died → restart"
        nohup python3 titanium_one.py > hunter.log 2>&1 &
        HUNTER_PID=$!
    fi

    SCORE=$(check_node "$BEST_NODE")

    if [ "$SCORE" -lt 1 ]; then
        echo "❌ NODE LOST → stopping hunter"
        pkill -f titanium_one.py
        exit 1
    fi

    sleep 10
done
