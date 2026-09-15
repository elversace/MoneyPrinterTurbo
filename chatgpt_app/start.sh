#!/usr/bin/env sh
set -eu

export MPT_BASE_URL="${MPT_BASE_URL:-http://127.0.0.1:8081}"
export MPT_SUBTITLE_TARGET_LANGUAGE="${MPT_SUBTITLE_TARGET_LANGUAGE-English}"
export MCP_HOST="${MCP_HOST:-0.0.0.0}"
export PORT="${PORT:-8000}"
export MPT_LISTEN_HOST="${MPT_LISTEN_HOST:-127.0.0.1}"
export MPT_LISTEN_PORT="${MPT_LISTEN_PORT:-8081}"

python /MoneyPrinterTurbo/chatgpt_app/patch_subtitle_fallback.py
python /MoneyPrinterTurbo/chatgpt_app/patch_web_task.py
python /MoneyPrinterTurbo/chatgpt_app/patch_tripoli_quality.py

if [ -f /usr/share/fonts/truetype/dejavu/DejaVuSans.ttf ]; then
  cp -f /usr/share/fonts/truetype/dejavu/DejaVuSans.ttf /MoneyPrinterTurbo/resource/fonts/DejaVuSans.ttf
  echo "Installed DejaVuSans subtitle font" >&2
fi

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
IMG_DIR="$BACKGROUND_DIR/tripoli_images"
BACKGROUND_FILE="$BACKGROUND_DIR/tiktok-background.mp4"
mkdir -p "$IMG_DIR"

fetch_image() {
  out="$1"
  url="$2"
  echo "Downloading Tripoli visual: $out" >&2
  curl -fL --retry 3 --connect-timeout 15 -A "MoneyPrinterTurbo-TikTok/1.0" "$url" -o "$IMG_DIR/$out"
}

fetch_image "01-old-city.jpg" "https://commons.wikimedia.org/wiki/Special:Redirect/file/Tripoli%20old%20mad%C4%ABna%201920s.jpg?width=1280"
fetch_image "02-marcus-arch.jpg" "https://commons.wikimedia.org/wiki/Special:Redirect/file/The%20Arch%20of%20Marcus%20Aurelius%20tripoli.jpg?width=1280"
fetch_image "03-martyrs-square.jpg" "https://commons.wikimedia.org/wiki/Special:Redirect/file/Martyr%27s%20Square%20in%20Libya.jpg?width=1280"
fetch_image "04-red-castle.jpg" "https://commons.wikimedia.org/wiki/Special:Redirect/file/Red%20Castle%20of%20Tripoli.jpg?width=1280"
fetch_image "05-gurgi-mosque.jpg" "https://commons.wikimedia.org/wiki/Special:Redirect/file/Fonds%20Andr%C3%A9%20Raymond%20%281925-2011%29%20-%20Libye%20-%20Tripoli%20-%20Mosqu%C3%A9e%20Gorgi%20%28M%C3%A9diHAL%204234484%29.jpg?width=1280"
fetch_image "06-karamanli.jpg" "https://commons.wikimedia.org/wiki/Special:Redirect/file/Karamanli%20House%20IMG%201485%20%283481574806%29.jpg?width=1280"
fetch_image "07-skyline.jpg" "https://commons.wikimedia.org/wiki/Special:Redirect/file/Tripoli%20Skyline%20edit.jpg?width=1280"
fetch_image "08-sea.jpg" "https://commons.wikimedia.org/wiki/Special:Redirect/file/Tripoli%20from%20the%20sea.jpg?width=1280"

: > "$BACKGROUND_DIR/concat.txt"
for img in 01-old-city.jpg 02-marcus-arch.jpg 03-martyrs-square.jpg 04-red-castle.jpg 05-gurgi-mosque.jpg 06-karamanli.jpg 07-skyline.jpg 08-sea.jpg; do
  clip="$BACKGROUND_DIR/${img%.jpg}.mp4"
  ffmpeg -hide_banner -loglevel error -y -loop 1 -i "$IMG_DIR/$img" -t 7.5 \
    -vf "scale=520:900:force_original_aspect_ratio=increase,crop=480:854,zoompan=z='min(zoom+0.00055,1.08)':d=180:s=480x854:fps=24,format=yuv420p" \
    -an -c:v libx264 -preset ultrafast -crf 29 -movflags +faststart "$clip"
  printf "file '%s'\n" "$clip" >> "$BACKGROUND_DIR/concat.txt"
done
ffmpeg -hide_banner -loglevel error -y -f concat -safe 0 -i "$BACKGROUND_DIR/concat.txt" \
  -c copy -movflags +faststart "$BACKGROUND_FILE"
echo "Built ordered Tripoli 60-second portrait tour reel: $BACKGROUND_FILE" >&2

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
