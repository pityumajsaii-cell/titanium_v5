#!/data/data/com.termux/files/usr/bin/bash

echo "💎 TITANIUM CLUSTER AI STARTING..."

# -----------------------------
# NODES (később bővíthető)
# -----------------------------
NODES=(
"https://pityumajsaii-cell-titanium-v5.hf.space"
)

# -----------------------------
# HEALTH SCORING
# -----------------------------
check_node() {
    URL=$1

    ROOT=$(curl -s -o /dev/null -w "%{http_code}" $URL/)
    DOCS=$(curl -s -o /dev/null -w "%{http_code}" $URL/docs)
    HEALTH=$(curl -s -o /dev/null -w "%{http_code}" $URL/health)

    SCORE=0
    [ "$ROOT" = "200" ] && SCORE=$((SCORE+1))
    [ "$DOCS" = "200" ] && SCORE=$((SCORE+1))
    [ "$HEALTH" = "200" ] && SCORE=$((SCORE+1))

    echo $SCORE
}

# -----------------------------
# SELECT BEST NODE
# -----------------------------
BEST_NODE=""
BEST_SCORE=0

for NODE in "${NODES[@]}"; do
    SCORE=$(check_node "$NODE")

    echo "📡 $NODE → SCORE $SCORE"

    if [ "$SCORE" -gt "$BEST_SCORE" ]; then
        BEST_SCORE=$SCORE
        BEST_NODE=$NODE
    fi
done

if [ "$BEST_SCORE" -lt 1 ]; then
    echo "❌ NO HEALTHY NODE → EXIT"
    exit 1
fi

echo "🟢 ACTIVE NODE: $BEST_NODE"

# -----------------------------
# WAIT FOR STABILITY
# -----------------------------
while true; do
    STATUS=$(curl -s -o /dev/null -w "%{http_code}" $BEST_NODE/)

    if [ "$STATUS" = "200" ]; then
        echo "🟢 NODE STABLE"
        break
    fi

    echo "⏳ waiting stability ($STATUS)"
    sleep 3
done

# -----------------------------
# START HUNTER
# -----------------------------
echo "🎯 STARTING HUNTER"

pkill -f titanium_one.py 2>/dev/null

nohup python3 titanium_one.py > hunter.log 2>&1 &
HUNTER_PID=$!

echo "✅ HUNTER PID: $HUNTER_PID"

# -----------------------------
# CLUSTER WATCHDOG
# -----------------------------
echo "🛡️ CLUSTER WATCHDOG ACTIVE"

while true; do

    # hunter health
    if ! ps -p $HUNTER_PID > /dev/null; then
        echo "⚠️ HUNTER DEAD → RESTART"
        nohup python3 titanium_one.py > hunter.log 2>&1 &
        HUNTER_PID=$!
    fi

    # node health recheck
    SCORE=$(check_node "$BEST_NODE")

    if [ "$SCORE" -lt 1 ]; then
        echo "❌ NODE LOST → FAILOVER TRIGGER"

        # reselect node
        BEST_NODE=""
        BEST_SCORE=0

        for NODE in "${NODES[@]}"; do
            S=$(check_node "$NODE")
            if [ "$S" -gt "$BEST_SCORE" ]; then
                BEST_SCORE=$S
                BEST_NODE=$NODE
            fi
        done

        echo "🔄 SWITCHED NODE: $BEST_NODE"

        pkill -f titanium_one.py
        sleep 5
    fi

    sleep 10
done

