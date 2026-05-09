#!/bin/bash
echo "--- TITANIUM V5.5 RENDSZER INDÍTÁSA ---"
# Itt indul a fő alkalmazásod
if [ -f "app.py" ]; then
    python3 app.py
else
    echo "❌ Hiba: app.py nem található!"
fi
