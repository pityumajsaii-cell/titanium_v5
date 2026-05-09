#!/bin/bash
echo "=== TITANIUM V8 RUNNING AUTONOMOUS REVENUE ENGINE ==="
uvicorn production_stack.backend.app:app --host 0.0.0.0 --port ${PORT:-8000}
