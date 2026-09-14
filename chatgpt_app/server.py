import os
from typing import Any

import httpx
from mcp.server.fastmcp import FastMCP

APP_NAME = "TikTok"
MPT_BASE_URL = os.getenv("MPT_BASE_URL", "http://127.0.0.1:8080").rstrip("/")
MPT_API_KEY = os.getenv("MPT_API_KEY", "").strip()
MPT_ARABIC_VOICE = os.getenv("MPT_ARABIC_VOICE", "ar-SA-HamedNeural-Male").strip()

mcp = FastMCP(
    APP_NAME,
    instructions=(
        "Create TikTok-ready short videos with MoneyPrinterTurbo. "
        "Default behavior is fixed: Arabic script and Arabic narration, "
        "portrait 9:16, TikTok-oriented pacing, and English subtitle delivery. "
        "Do not ask the user to choose language, platform, or aspect ratio."
    ),
)


def _headers() -> dict[str, str]:
    headers = {"Content-Type": "application/json"}
    if MPT_API_KEY:
        headers["Authorization"] = f"Bearer {MPT_API_KEY}"
    return headers


@mcp.tool(
    name="create_tiktok_video",
    description=(
        "Create a TikTok video from a topic. The narration and script are Arabic, "
        "the aspect ratio is 9:16, and English subtitles are required."
    ),
)
async def create_tiktok_video(
    topic: str,
    duration_seconds: int | None = None,
    style: str | None = None,
) -> dict[str, Any]:
    """Start a TikTok video generation task in MoneyPrinterTurbo."""
    topic = (topic or "").strip()
    if not topic:
        raise ValueError("topic is required")

    creative_notes: list[str] = []
    if duration_seconds:
        creative_notes.append(f"Target duration: about {duration_seconds} seconds.")
    if style:
        creative_notes.append(f"Style: {style.strip()}.")

    prompt = (
        "Write the complete spoken script in Arabic. Use a strong opening hook, "
        "short natural sentences, fast TikTok pacing, and no filler. "
        "Do not write the narration in English. "
        "The final visible subtitle track must be translated to English while "
        "preserving the timing of the Arabic narration."
    )
    if creative_notes:
        prompt += " " + " ".join(creative_notes)

    body = {
        "video_subject": topic,
        "video_language": "ar",
        "video_aspect": "9:16",
        "video_fit_mode": "cover",
        "video_concat_mode": "random",
        "video_count": 1,
        "video_source": "pexels",
        "voice_name": MPT_ARABIC_VOICE,
        "voice_volume": 1.0,
        "voice_rate": 1.0,
        "bgm_type": "random",
        "bgm_volume": 0.2,
        "subtitle_enabled": True,
        "subtitle_position": "bottom",
        "text_fore_color": "#FFFFFF",
        "stroke_color": "#000000",
        "stroke_width": 1.5,
        "video_script_prompt": prompt,
        "custom_system_prompt": (
            "Always produce the spoken video script in Arabic. "
            "Optimize for a vertical TikTok short."
        ),
    }

    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            f"{MPT_BASE_URL}/api/v1/videos",
            headers=_headers(),
            json=body,
        )
        response.raise_for_status()
        result = response.json()

    return {
        "status": "started",
        "platform": "TikTok",
        "language": "Arabic",
        "subtitle_language": "English",
        "aspect_ratio": "9:16",
        "moneyprinterturbo": result,
        "note": (
            "MoneyPrinterTurbo has started the video task. If this fork's runtime "
            "does not yet have an English-subtitle translation post-process enabled, "
            "the generated subtitle track may still follow the Arabic narration."
        ),
    }


@mcp.tool(
    name="tiktok_defaults",
    description="Return the fixed defaults used by the TikTok app.",
)
async def tiktok_defaults() -> dict[str, Any]:
    return {
        "platform": "TikTok",
        "script_language": "Arabic",
        "narration_language": "Arabic",
        "subtitle_language": "English",
        "aspect_ratio": "9:16",
        "video_count": 1,
        "video_source": "pexels",
        "background_music": "random",
    }


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
