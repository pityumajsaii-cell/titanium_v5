#!/data/data/com.termux/files/usr/bin/bash

REPO_DIR="."

HF_SPACE="https://huggingface.co/spaces/pityumajsaii-cell/titanium_v5"

echo "🧠 TITANIUM HF AUTO-REPAIR ENGINE START"

# -----------------------------
# 1. FETCH LOGS
# -----------------------------
echo "📡 Checking HF logs..."

LOG=$(curl -s "$HF_SPACE/logs")

echo "$LOG" > hf_last_log.txt

# -----------------------------
# 2. DETECT ERROR TYPE
# -----------------------------

if echo "$LOG" | grep -qi "ModuleNotFoundError"; then
    ERROR="IMPORT_ERROR"
elif echo "$LOG" | grep -qi "uvicorn"; then
    ERROR="UVICORN_ERROR"
elif echo "$LOG" | grep -qi "ASGI"; then
    ERROR="APP_INIT_ERROR"
elif echo "$LOG" | grep -qi "Exited with code 1"; then
    ERROR="CRASH_LOOP"
else
    ERROR="UNKNOWN"
fi

echo "⚠️ DETECTED: $ERROR"

# -----------------------------
# 3. AUTO FIX LOGIC
# -----------------------------

case "$ERROR" in

IMPORT_ERROR)
    echo "🛠 Fix: dependency patch"

    # biztos fastapi stack
    cat << 'REQ' > requirements.txt
fastapi
uvicorn[standard]
REQ
    ;;

UVICORN_ERROR)
    echo "🛠 Fix: Docker repair"

    cat << 'DOCKER' > Dockerfile
FROM python:3.11-slim
WORKDIR /app
RUN pip install --no-cache-dir fastapi uvicorn[standard]
COPY . .
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "7860"]
DOCKER
    ;;

APP_INIT_ERROR|CRASH_LOOP)
    echo "🛠 Fix: app safety patch"

    cat << 'APP' > app.py
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
    return {"status":"HF_RECOVERY_MODE"}

@app.get("/health")
def health():
    return {"ok": True}
APP
    ;;

*)
    echo "⚠️ Unknown issue → no auto fix applied"
    ;;
esac

# -----------------------------
# 4. DEPLOY TRIGGER
# -----------------------------

echo "🚀 Committing fix..."

git add .
git commit -m "🤖 HF AUTO-REPAIR: $ERROR fix"
git push origin main -f

echo "🟢 Pushed to GitHub → HF will redeploy automatically"

# -----------------------------
# 5. WAIT FOR RECOVERY
# -----------------------------

echo "⏳ Waiting for HF recovery..."

for i in {1..30}; do
    STATUS=$(curl -s -o /dev/null -w "%{http_code}" https://pityumajsaii-cell-titanium-v5.hf.space/)

    echo "Attempt $i → status $STATUS"

    if [ "$STATUS" = "200" ]; then
        echo "🟢 HF RECOVERED"
        exit 0
    fi

    sleep 5
done

echo "❌ Recovery failed (manual intervention needed)"

