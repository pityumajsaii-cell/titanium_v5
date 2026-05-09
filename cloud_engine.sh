#!/bin/bash

echo "☁️ TITANIUM CLOUD ENGINE START"

BASE=$HOME
LOG=$BASE/cloud_log.txt
> $LOG

# ---- CONFIG ----
GITHUB_USER="pityumajsaii-cell"
GITHUB_TOKEN="PUT_YOUR_NEW_TOKEN_HERE"

PROJECTS=("titanium_v5" "titanium_v4" "titanium_v5")

deploy_project() {
  DIR=$1
  NAME=$(basename "$DIR")

  if [ ! -d "$DIR" ]; then
    echo "❌ SKIP (not found): $DIR"
    return
  fi

  cd "$DIR" || return

  echo "📦 DEPLOY: $NAME"

  git init -q
  git add .
  git commit -m "auto deploy" -q

  git branch -M main

  # GitHub remote FIX (token auth)
  REMOTE="https://${GITHUB_USER}:${GITHUB_TOKEN}@github.com/${GITHUB_USER}/${NAME}.git"

  git remote remove origin 2>/dev/null
  git remote add origin "$REMOTE"

  if git push -f origin main 2>/dev/null; then
     echo "✔ OK: $NAME" | tee -a $LOG
  else
     echo "❌ FAIL: $NAME" | tee -a $LOG
  fi
}

echo "🔍 scanning projects..."

for p in "${PROJECTS[@]}"; do
  deploy_project "$p"
done

echo ""
echo "☁️ DONE"
echo "LOG: $LOG"
