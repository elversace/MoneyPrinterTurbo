#!/usr/bin/env sh
set -eu

export MPT_INTERNAL_PORT="${MPT_INTERNAL_PORT:-8081}"
export MPT_BASE_URL="${MPT_BASE_URL:-http://127.0.0.1:${MPT_INTERNAL_PORT}}"
export MPT_SUBTITLE_TARGET_LANGUAGE="${MPT_SUBTITLE_TARGET_LANGUAGE:-English}"
export MCP_HOST="${MCP_HOST:-0.0.0.0}"
export PORT="${PORT:-8000}"

# Run the MoneyPrinterTurbo API on a private loopback port so it cannot
# conflict with Railway's public PORT used by the MCP server.
python -m uvicorn app.asgi:app \
  --host 127.0.0.1 \
  --port "${MPT_INTERNAL_PORT}" \
  --log-level warning &
MPT_PID=$!

cleanup() {
  kill "$MPT_PID" 2>/dev/null || true
}
trap cleanup EXIT INT TERM

# Give the internal API a brief startup window before exposing MCP.
sleep "${MPT_STARTUP_DELAY:-5}"

# Expose only the MCP HTTP server on the platform-provided public port.
exec python chatgpt_app/server.py
