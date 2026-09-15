#!/usr/bin/env sh
set -eu

export MPT_BASE_URL="${MPT_BASE_URL:-http://127.0.0.1:8081}"
export MPT_SUBTITLE_TARGET_LANGUAGE="${MPT_SUBTITLE_TARGET_LANGUAGE-English}"
export MCP_HOST="${MCP_HOST:-0.0.0.0}"
export PORT="${PORT:-8000}"
export MPT_LISTEN_HOST="${MPT_LISTEN_HOST:-127.0.0.1}"
export MPT_LISTEN_PORT="${MPT_LISTEN_PORT:-8081}"

python /MoneyPrinterTurbo/chatgpt_app/patch_subtitle_fallback.py

# Low-memory Railway profile: portrait 9:16 while staying below the 1 GB limit.
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

# Build a real 60-second portrait visual reel from CC0 Wikimedia Commons photos.
# The five subjects match the Arabic Fusha validation script.
BACKGROUND_DIR="/MoneyPrinterTurbo/storage/local_videos"
IMG_DIR="$BACKGROUND_DIR/car_images"
BACKGROUND_FILE="$BACKGROUND_DIR/tiktok-background.mp4"
mkdir -p "$IMG_DIR"

fetch_image() {
  out="$1"
  url="$2"
  echo "Downloading real visual: $out" >&2
  curl -fL --retry 3 --connect-timeout 15 -A "MoneyPrinterTurbo-TikTok/1.0" "$url" -o "$IMG_DIR/$out"
}

fetch_image "01-aston.jpg" "https://commons.wikimedia.org/wiki/Special:Redirect/file/Aston%20Martin%20Vantage%20Coup%C3%A9%20%282025%29%20%2854801016671%29.jpg?width=1280"
fetch_image "02-corvette.jpg" "https://commons.wikimedia.org/wiki/Special:Redirect/file/Chevrolet%20Corvette%20Z06%20Coup%C3%A9%20%28C8%2C%202023%29%20%2854802404220%29.jpg?width=1280"
fetch_image "03-porsche.jpg" "https://commons.wikimedia.org/wiki/Special:Redirect/file/Porsche%20911%20GT3%20Touring%20%28992.2%29%20001.jpg?width=1280"
fetch_image "04-ferrari.jpg" "https://commons.wikimedia.org/wiki/Special:Redirect/file/Ferrari%20296%20Speciale%20%282026%29%20%2855080072923%29.jpg?width=1280"
fetch_image "05-lamborghini.jpg" "https://commons.wikimedia.org/wiki/Special:Redirect/file/Lamborghini%20Revuelto%20%282026%29%20%2855082446885%29.jpg?width=1280"

: > "$BACKGROUND_DIR/concat.txt"
for img in 01-aston.jpg 02-corvette.jpg 03-porsche.jpg 04-ferrari.jpg 05-lamborghini.jpg; do
  clip="$BACKGROUND_DIR/${img%.jpg}.mp4"
  ffmpeg -hide_banner -loglevel error -y -loop 1 -i "$IMG_DIR/$img" -t 12 \
    -vf "scale=520:900:force_original_aspect_ratio=increase,crop=480:854,zoompan=z='min(zoom+0.00035,1.06)':d=288:s=480x854:fps=24,format=yuv420p" \
    -an -c:v libx264 -preset ultrafast -crf 30 -movflags +faststart "$clip"
  printf "file '%s'\n" "$clip" >> "$BACKGROUND_DIR/concat.txt"
done
ffmpeg -hide_banner -loglevel error -y -f concat -safe 0 -i "$BACKGROUND_DIR/concat.txt" \
  -c copy -movflags +faststart "$BACKGROUND_FILE"
echo "Built real-car 60-second portrait visual reel: $BACKGROUND_FILE" >&2

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
