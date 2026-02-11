#!/bin/bash
set -e

exec python -u -m uvicorn ae.server.api_routes:app \
    --host 0.0.0.0 \
    --port "${PORT:-8000}" \
    --loop asyncio
