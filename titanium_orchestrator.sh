#!/data/data/com.termux/files/usr/bin/bash
HF_URL="https://pityumajsaii-cell-titanium-v5.hf.space"

echo "🧠 TITANIUM SMART GATEWAY V2.0 AKTIVÁLVA"
echo "📡 Célpont: $HF_URL"

# ------------------------------------------------
# 1. SMART READINESS FINGERPRINT (Intelligens várakozás)
# ------------------------------------------------
echo "⏳ Checking infrastructure readiness..."

while true; do
    # Itt a ROOT-ot nézzük, ami a legbiztosabb indikátor
    STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$HF_URL/")
    
    if [ "$STATUS" = "200" ]; then
        echo "🟢 [GATEWAY] HF ROOT ELÉRHETŐ (200 OK)"
        # Egy gyors extra ellenőrzés a JSON válaszra (fingerprint)
        if curl -s "$HF_URL/" | grep -q "Titanium Core"; then
            echo "✅ [FINGERPRINT] Titanium Nexus azonosítva. Rendszer éles!"
            break
        fi
        echo "⚠️ [WARN] Port nyitva, de a Titanium Core még nem válaszol..."
    elif [ "$STATUS" = "503" ] || [ "$STATUS" = "404" ]; then
        echo "⏳ [WAIT] HF Space még épül vagy alvó módban van ($STATUS)..."
    else
        echo "📡 [RETRY] Szerver válaszra várva: $STATUS"
    fi
    sleep 7
done

# ------------------------------------------------
# 2. ZERO-FALSE-START HUNTER (Biztonsági indítás)
# ------------------------------------------------
echo "🎯 [DEPLOY] Vadász indítása optimalizált környezetben..."
pkill -f titanium_one.py 2>/dev/null
nohup python3 titanium_one.py > hunter.log 2>&1 &
HUNTER_PID=$!

echo "🛡️ [WATCHDOG] Öngyógyító hurok aktív. PID: $HUNTER_PID"

# ------------------------------------------------
# 3. SELF-HEALING LOOP (Vigvigyázó)
# ------------------------------------------------
while true; do
    # Ellenőrizzük, él-e a Vadász folyamat
    if ! ps -p $HUNTER_PID > /dev/null; then
        echo "⚠️ [CRASH] Vadász leállt! Újraindítás..."
        nohup python3 titanium_one.py > hunter.log 2>&1 &
        HUNTER_PID=$!
    fi

    # Ellenőrizzük, él-e a kapcsolat a szerverrel
    STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$HF_URL/")
    if [ "$STATUS" != "200" ]; then
        echo "❌ [CON-LOST] Kapcsolat megszakadt ($STATUS). Vadász felfüggesztve."
        pkill -f titanium_one.py
        # Visszaugrik a várakozásra
        exec "$0"
    fi
    sleep 15
done
