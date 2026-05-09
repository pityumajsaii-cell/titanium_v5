#!/data/data/com.termux/files/usr/bin/bash

echo "🧠 TITANIUM SAFE ORCHESTRATOR (FIXED LOOP)"

SPACES=(
  "https://pityumajsaii-cell-titanium-v5.hf.space"
)

ACTIVE_SPACE=""
BEST_SCORE=0
FAIL_COUNT=0
MAX_FAILS=12

check_space() {
    curl -s -o /dev/null -w "%{http_code}" "$1/"
}

select_best() {
    BEST_SPACE=""
    BEST_SCORE=0

    for S in "${SPACES[@]}"; do
        SCORE=$(check_space "$S")

        echo "📡 $S → $SCORE"

        # ❌ INVALID NODE FILTER
        if [ "$SCORE" != "200" ]; then
            continue
        fi

        BEST_SPACE=$S
        BEST_SCORE=1
    done
}

start_hunter() {
    pkill -f titanium_one.py 2>/dev/null

    if [ "$BEST_SCORE" -eq 0 ] || [ -z "$ACTIVE_SPACE" ]; then
        echo "⛔ HUNTER BLOCKED (NO VALID NODE)"
        return
    fi

    export ACTIVE_SPACE
    nohup python3 titanium_one.py > hunter.log 2>&1 &
    echo "✅ HUNTER STARTED"
}

while true; do

    select_best

    if [ -z "$BEST_SPACE" ]; then
        FAIL_COUNT=$((FAIL_COUNT+1))

        echo "❌ NO HF READY NODE (fail $FAIL_COUNT/$MAX_FAILS)"

        # BACKOFF
        sleep $((FAIL_COUNT < 10 ? FAIL_COUNT*5 : 60))

        # HARD STOP SAFETY
        if [ "$FAIL_COUNT" -ge "$MAX_FAILS" ]; then
            echo "⛔ HF NOT RECOVERING → STOPPING ORCHESTRATOR"
            exit 1
        fi

        continue
    fi

    FAIL_COUNT=0
    ACTIVE_SPACE=$BEST_SPACE

    echo "🟢 ACTIVE NODE: $ACTIVE_SPACE"

    start_hunter

    while true; do
        STATUS=$(check_space "$ACTIVE_SPACE")

        if [ "$STATUS" != "200" ]; then
            echo "❌ NODE LOST → RESELECT"
            pkill -f titanium_one.py
            break
        fi

        if ! pgrep -f titanium_one.py > /dev/null; then
            echo "⚠️ HUNTER CRASH → RESTART"
            start_hunter
        fi

        sleep 10
    done

done
