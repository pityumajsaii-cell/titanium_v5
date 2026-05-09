#!/bin/bash
echo "=== TITANIUM SALES AGENT RUNNING ==="
uvicorn production_stack.backend.app:app --host 0.0.0.0 --port ${PORT:-8000}
