#!/usr/bin/env sh
set -eu

export MPT_BASE_URL="${MPT_BASE_URL:-http://127.0.0.1:8081}"
export MPT_SUBTITLE_TARGET_LANGUAGE="${MPT_SUBTITLE_TARGET_LANGUAGE-English}"
export MCP_HOST="${MCP_HOST:-0.0.0.0}"
export PORT="${PORT:-8000}"
export MPT_LISTEN_HOST="${MPT_LISTEN_HOST:-127.0.0.1}"
export MPT_LISTEN_PORT="${MPT_LISTEN_PORT:-8081}"

python /MoneyPrinterTurbo/chatgpt_app/patch_subtitle_fallback.py

# Low-memory validation profile. Keeps 9:16 while preventing Railway's 1 GB
# container from killing FFmpeg/MoviePy during the test render.
python - <<'PY'
from pathlib import Path
p = Path('/MoneyPrinterTurbo/app/models/schema.py')
s = p.read_text(encoding='utf-8')
s = s.replace('return 1080, 1920', 'return 360, 640', 1)
s = s.replace('n_threads: Optional[int] = 2', 'n_threads: Optional[int] = 1', 1)
p.write_text(s, encoding='utf-8')
print('Applied Railway low-memory 360x640 portrait profile', flush=True)
PY

if [ -n "${OPENAI_API_KEY:-}" ]; then
  if [ ! -f /MoneyPrinterTurbo/config.toml ]; then cp /MoneyPrinterTurbo/config.example.toml /MoneyPrinterTurbo/config.toml; fi
  python - <<'PY'
import os, toml
path = '/MoneyPrinterTurbo/config.toml'
cfg = toml.load(path)
app = cfg.setdefault('app', {})
app['llm_provider'] = 'openai'
app['openai_api_key'] = os.environ['OPENAI_API_KEY']
if os.getenv('OPENAI_MODEL_NAME'): app['openai_model_name'] = os.environ['OPENAI_MODEL_NAME']
if os.getenv('OPENAI_BASE_URL'): app['openai_base_url'] = os.environ['OPENAI_BASE_URL']
with open(path, 'w', encoding='utf-8') as f: toml.dump(cfg, f)
print('Configured MoneyPrinterTurbo LLM provider from OPENAI_API_KEY', flush=True)
PY
fi

BACKGROUND_DIR="/MoneyPrinterTurbo/storage/local_videos"
BACKGROUND_FILE="$BACKGROUND_DIR/tiktok-background.mp4"
mkdir -p "$BACKGROUND_DIR"
# 480px width stays above MoneyPrinterTurbo's local-material minimum while
# reducing decode memory versus 720p.
ffmpeg -hide_banner -loglevel error -y \
  -f lavfi -i "color=c=0x101820:s=480x854:r=24:d=90" \
  -vf "format=yuv420p" \
  -c:v libx264 -preset ultrafast -crf 32 -movflags +faststart \
  "$BACKGROUND_FILE"

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
