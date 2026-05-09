#!/data/data/com.termux/files/usr/bin/bash

HF_URL="https://pityumajsaii-cell-titanium-v5.hf.space"

echo "🧠 TITANIUM SMART GATEWAY START"

# -----------------------------
# FUNCTION: CHECK HF ALIVE
# -----------------------------
check_hf() {
    # 1. root check
    ROOT=$(curl -s -o /dev/null -w "%{http_code}" $HF_URL/)

    # 2. docs check
    DOCS=$(curl -s -o /dev/null -w "%{http_code}" $HF_URL/docs)

    # 3. health check (optional fallback)
    HEALTH=$(curl -s -o /dev/null -w "%{http_code}" $HF_URL/health)

    echo "📡 STATUS → root:$ROOT docs:$DOCS health:$HEALTH"

    # HF considered alive if ANY of these works
    if [ "$ROOT" = "200" ] || [ "$DOCS" = "200" ] || [ "$HEALTH" = "200" ]; then
        return 0
    else
        return 1
    fi
}

# -----------------------------
# WAIT FOR STABLE STATE
# -----------------------------
echo "⏳ Waiting for HF to become stable..."

ATTEMPT=0

while true; do
    ATTEMPT=$((ATTEMPT+1))

    if check_hf; then
        echo "🟢 HF IS READY"
        break
    fi

    echo "⏳ Attempt $ATTEMPT - not ready yet..."
    
    # exponential backoff (1s → 2s → 4s → 8s max)
    SLEEP_TIME=$((ATTEMPT < 4 ? ATTEMPT*2 : 8))
    sleep $SLEEP_TIME
done

# -----------------------------
# SAFE HUNTER START
# -----------------------------
echo "🎯 Starting Titanium One (SAFE MODE)"

pkill -f titanium_one.py 2>/dev/null

nohup python3 titanium_one.py > hunter.log 2>&1 &
HUNTER_PID=$!

echo "✅ Hunter PID: $HUNTER_PID"

# -----------------------------
# WATCHDOG
# -----------------------------
echo "🛡️ Watchdog active..."

while true; do

    # hunter check
    if ! ps -p $HUNTER_PID > /dev/null; then
        echo "⚠️ Hunter crashed → restarting"
        nohup python3 titanium_one.py > hunter.log 2>&1 &
        HUNTER_PID=$!
    fi

    # HF check
    if ! check_hf; then
        echo "❌ HF DOWN → stopping hunter"
        pkill -f titanium_one.py
        sleep 10
        continue
    fi

    sleep 10
done

