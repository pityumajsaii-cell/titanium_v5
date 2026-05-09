#!/bin/bash
echo "=== TITANIUM V9 RUNNING AUTONOM SALES CORE ==="
uvicorn production_stack.backend.app:app --host 0.0.0.0 --port ${PORT:-8000}
