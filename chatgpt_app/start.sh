#!/usr/bin/env sh
set -eu

export MPT_BASE_URL="${MPT_BASE_URL:-http://127.0.0.1:8081}"
export MPT_SUBTITLE_TARGET_LANGUAGE="${MPT_SUBTITLE_TARGET_LANGUAGE-English}"
export MCP_HOST="${MCP_HOST:-0.0.0.0}"
export PORT="${PORT:-8000}"
export MPT_LISTEN_HOST="${MPT_LISTEN_HOST:-127.0.0.1}"
export MPT_LISTEN_PORT="${MPT_LISTEN_PORT:-8081}"

python /MoneyPrinterTurbo/chatgpt_app/patch_subtitle_fallback.py

# Railway test instances are memory constrained. Render portrait at 720x1280,
# still standard 9:16, to avoid FFmpeg broken-pipe/OOM failures during validation.
python - <<'PY'
from pathlib import Path
p = Path('/MoneyPrinterTurbo/app/models/schema.py')
s = p.read_text(encoding='utf-8')
s = s.replace('return 1080, 1920', 'return 720, 1280', 1)
p.write_text(s, encoding='utf-8')
print('Applied Railway 720p portrait render profile', flush=True)
PY

if [ -n "${OPENAI_API_KEY:-}" ]; then
  if [ ! -f /MoneyPrinterTurbo/config.toml ]; then
    cp /MoneyPrinterTurbo/config.example.toml /MoneyPrinterTurbo/config.toml
  fi
  python - <<'PY'
import os
import toml
path = "/MoneyPrinterTurbo/config.toml"
cfg = toml.load(path)
app = cfg.setdefault("app", {})
app["llm_provider"] = "openai"
app["openai_api_key"] = os.environ["OPENAI_API_KEY"]
if os.getenv("OPENAI_MODEL_NAME"):
    app["openai_model_name"] = os.environ["OPENAI_MODEL_NAME"]
if os.getenv("OPENAI_BASE_URL"):
    app["openai_base_url"] = os.environ["OPENAI_BASE_URL"]
with open(path, "w", encoding="utf-8") as f:
    toml.dump(cfg, f)
print("Configured MoneyPrinterTurbo LLM provider from OPENAI_API_KEY", flush=True)
PY
fi

BACKGROUND_DIR="/MoneyPrinterTurbo/storage/local_videos"
BACKGROUND_FILE="$BACKGROUND_DIR/tiktok-background.mp4"
mkdir -p "$BACKGROUND_DIR"
if [ ! -s "$BACKGROUND_FILE" ]; then
  ffmpeg -hide_banner -loglevel error -y \
    -f lavfi -i "color=c=0x101820:s=720x1280:r=30:d=90" \
    -vf "format=yuv420p" \
    -c:v libx264 -preset ultrafast -crf 30 -movflags +faststart \
    "$BACKGROUND_FILE"
fi

python main.py &
MPT_PID=$!
MCP_PID=""
cleanup() {
  if [ -n "$MCP_PID" ]; then kill "$MCP_PID" 2>/dev/null || true; fi
  kill "$MPT_PID" 2>/dev/null || true
}
trap cleanup EXIT INT TERM
sleep "${MPT_STARTUP_DELAY:-5}"

if [ "${MPT_RUN_SELF_TEST:-0}" = "1" ]; then
  python chatgpt_app/server.py &
  MCP_PID=$!
  sleep "${MCP_SELF_TEST_DELAY:-3}"
  python chatgpt_app/self_test.py || true
  wait "$MCP_PID"
else
  exec python chatgpt_app/server.py
fi
