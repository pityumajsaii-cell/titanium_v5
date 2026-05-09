#!/data/data/com.termux/files/usr/bin/bash

HF="https://pityumajsaii-cell-titanium-v5.hf.space"

STATE="INIT"

echo "🧠 TITANIUM STATE MACHINE START"

check_hf() {
    curl -s -o /dev/null -w "%{http_code}" $HF/
}

start_hunter() {
    pkill -f titanium_one.py 2>/dev/null
    nohup python3 titanium_one.py > hunter.log 2>&1 &
    echo $!
}

stop_hunter() {
    pkill -f titanium_one.py 2>/dev/null
}

while true; do

    STATUS=$(check_hf)

    # -------------------------
    # STATE LOGIC
    # -------------------------

    if [ "$STATUS" = "200" ]; then

        if [ "$STATE" != "RUN" ]; then
            echo "🟢 STATE → RUN"
            HUNTER_PID=$(start_hunter)
            STATE="RUN"
        fi

    else

        if [ "$STATE" != "WAIT" ]; then
            echo "⏳ STATE → WAIT (HF=$STATUS)"
            stop_hunter
            STATE="WAIT"
        fi
    fi

    sleep 10
done
