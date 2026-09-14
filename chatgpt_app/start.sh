#!/usr/bin/env sh
set -eu

export MPT_BASE_URL="${MPT_BASE_URL:-http://127.0.0.1:8080}"
export MCP_HOST="${MCP_HOST:-0.0.0.0}"
export PORT="${PORT:-8000}"

# Start MoneyPrinterTurbo API internally.
python main.py &
MPT_PID=$!

cleanup() {
  kill "$MPT_PID" 2>/dev/null || true
}
trap cleanup EXIT INT TERM

# Give the API a brief startup window before exposing MCP.
sleep "${MPT_STARTUP_DELAY:-5}"

# Expose only the MCP HTTP server on the platform-provided public port.
exec python chatgpt_app/server.py
