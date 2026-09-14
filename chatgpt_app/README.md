# TikTok ChatGPT App for MoneyPrinterTurbo

This folder exposes the MoneyPrinterTurbo fork as an MCP app for ChatGPT.

## Fixed behavior

The `create_tiktok_video` tool uses these defaults automatically:

- Platform: TikTok
- Script: Arabic
- Narration: Arabic
- Subtitles: English target
- Aspect ratio: 9:16 portrait
- Source: Pexels by default
- Background music: random
- Video count: 1

Users should only need to provide a topic, for example:

```text
/TikTok أفضل 5 سيارات رياضية في 2026
```

When installed as a ChatGPT app, the app can also be invoked by its app name (for example `@TikTok`) depending on the ChatGPT client.

## 1. Start MoneyPrinterTurbo

From the repository root:

```bash
uv sync --frozen
uv run python main.py
```

The MoneyPrinterTurbo API normally listens on port 8080.

If you configured an API key in MoneyPrinterTurbo, export the same value for the MCP bridge:

```bash
export MPT_API_KEY="your-api-key"
```

If MoneyPrinterTurbo is on another host or port:

```bash
export MPT_BASE_URL="http://127.0.0.1:8080"
```

The default Arabic voice can be changed without changing the skill behavior:

```bash
export MPT_ARABIC_VOICE="ar-SA-HamedNeural-Male"
```

## 2. Start the MCP app

Create a separate virtual environment or install the small bridge requirements:

```bash
python -m venv .mcp-venv
source .mcp-venv/bin/activate
pip install -r chatgpt_app/requirements.txt
python chatgpt_app/server.py
```

On Windows PowerShell:

```powershell
python -m venv .mcp-venv
.\.mcp-venv\Scripts\Activate.ps1
pip install -r chatgpt_app\requirements.txt
python chatgpt_app\server.py
```

The server uses MCP Streamable HTTP.

## 3. Make the MCP endpoint reachable by ChatGPT

ChatGPT needs a remote MCP endpoint; it cannot directly connect to a private localhost-only endpoint. Host the MCP service on a public HTTPS deployment or use an OpenAI-supported secure MCP tunnel when available for your account/workspace.

Keep the MoneyPrinterTurbo API private if possible and expose only the MCP bridge. Set `MPT_BASE_URL` so the bridge can reach the video backend internally.

## 4. Add the app in ChatGPT Developer Mode

When Developer Mode/custom apps are available for the account or workspace:

1. Open ChatGPT settings.
2. Open Apps / Advanced settings and enable Developer Mode if available.
3. Choose Create custom app / MCP app.
4. Enter the remote MCP endpoint URL.
5. Scan tools.
6. Confirm that these tools appear:
   - `create_tiktok_video`
   - `tiktok_defaults`
7. Create/enable the app.

Then use the TikTok app in a chat and provide only the video topic.

## Important subtitle note

The bridge requests English subtitles, but upstream MoneyPrinterTurbo currently derives subtitle timing/text from the Arabic narration. To guarantee that the final burned subtitle track is English, this fork still needs a post-processing step that translates each timed Arabic subtitle cue to English while preserving timestamps before final rendering.

The MCP server reports this limitation rather than claiming the translation step has completed when it has not.
