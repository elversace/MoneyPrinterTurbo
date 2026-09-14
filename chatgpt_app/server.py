import os
from typing import Any

import httpx
from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings

APP_NAME = "TikTok"
MPT_BASE_URL = os.getenv("MPT_BASE_URL", "http://127.0.0.1:8081").rstrip("/")
MPT_API_KEY = os.getenv("MPT_API_KEY", "").strip()
MPT_ARABIC_VOICE = os.getenv("MPT_ARABIC_VOICE", "ar-SA-HamedNeural-Male").strip()
# Local video inputs are intentionally resolved by MoneyPrinterTurbo inside
# storage/local_videos. Passing only the filename satisfies that sandbox.
MPT_LOCAL_BACKGROUND = os.getenv("MPT_LOCAL_BACKGROUND", "tiktok-background.mp4").strip()
MCP_HOST = os.getenv("MCP_HOST", "0.0.0.0")
MCP_PORT = int(os.getenv("PORT", os.getenv("MCP_PORT", "8000")))
DEFAULT_DURATION_SECONDS = 60

mcp = FastMCP(
    APP_NAME,
    instructions=(
        "Create TikTok-ready short videos with MoneyPrinterTurbo. Default behavior is fixed: "
        "Arabic script and Arabic narration, portrait 9:16, TikTok-oriented pacing, English "
        "subtitle delivery, and a target duration of 60 seconds. Generate an Arabic spoken "
        "script sized for about one minute (roughly 130-150 Arabic words) and pass it in "
        "arabic_script; do not ask the user to choose language, platform, aspect ratio, or "
        "duration unless they explicitly request a different duration."
    ),
    host=MCP_HOST,
    port=MCP_PORT,
    stateless_http=True,
    json_response=True,
    transport_security=TransportSecuritySettings(enable_dns_rebinding_protection=False),
)


def _headers() -> dict[str, str]:
    headers = {"Content-Type": "application/json"}
    if MPT_API_KEY:
        headers["Authorization"] = f"Bearer {MPT_API_KEY}"
    return headers


@mcp.tool(name="create_tiktok_video", description=(
    "Create a TikTok video. Generate a concise Arabic spoken script first, sized for about "
    "60 seconds by default (roughly 130-150 Arabic words), then pass it in arabic_script. "
    "Arabic narration, portrait 9:16, English subtitles, and a 60-second target duration "
    "are fixed defaults unless a different duration is explicitly requested. A built-in "
    "local portrait background is used by default so no stock-video API key is required."
))
async def create_tiktok_video(topic: str, arabic_script: str, duration_seconds: int = DEFAULT_DURATION_SECONDS, style: str | None = None) -> dict[str, Any]:
    topic = (topic or "").strip()
    arabic_script = (arabic_script or "").strip()
    if not topic:
        raise ValueError("topic is required")
    if not arabic_script:
        raise ValueError("arabic_script is required")
    duration_seconds = int(duration_seconds or DEFAULT_DURATION_SECONDS)
    if duration_seconds < 15 or duration_seconds > 180:
        raise ValueError("duration_seconds must be between 15 and 180 seconds")

    body = {
        "video_subject": topic,
        "video_script": arabic_script,
        "video_language": "ar",
        "video_aspect": "9:16",
        "video_fit_mode": "cover",
        "video_concat_mode": "random",
        "video_clip_duration": 5,
        "video_count": 1,
        "video_source": "local",
        "video_materials": [{"provider": "local", "url": MPT_LOCAL_BACKGROUND, "duration": max(90, duration_seconds + 15)}],
        "voice_name": MPT_ARABIC_VOICE,
        "voice_volume": 1.0,
        "voice_rate": 1.0,
        "bgm_type": "",
        "bgm_volume": 0.0,
        "subtitle_enabled": True,
        "subtitle_position": "bottom",
        "subtitle_display_mode": "sentence",
        "text_fore_color": "#FFFFFF",
        "text_background_color": "#000000",
        "rounded_subtitle_background": True,
        "font_size": 54,
        "stroke_color": "#000000",
        "stroke_width": 1.5,
        "match_materials_to_script": False,
    }
    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(f"{MPT_BASE_URL}/api/v1/videos", headers=_headers(), json=body)
        response.raise_for_status()
        result = response.json()
    return {
        "status": "started", "platform": "TikTok", "language": "Arabic",
        "subtitle_language": "English", "aspect_ratio": "9:16",
        "duration_target_seconds": duration_seconds, "style": style,
        "video_source": "local_test_background", "moneyprinterturbo": result,
        "note": "Arabic narration, portrait 9:16 and a 60-second target are enabled. Actual render length follows synthesized narration."
    }


@mcp.tool(name="tiktok_defaults", description="Return the fixed defaults used by the TikTok app.")
async def tiktok_defaults() -> dict[str, Any]:
    return {
        "platform": "TikTok", "script_language": "Arabic", "narration_language": "Arabic",
        "subtitle_language": "English", "aspect_ratio": "9:16", "duration_seconds": 60,
        "video_count": 1, "video_source": "local_test_background",
        "background_music": "disabled_in_test_mode", "external_script_llm_required": False,
        "stock_video_api_key_required": False, "subtitle_translation_provider_required": True,
    }


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
