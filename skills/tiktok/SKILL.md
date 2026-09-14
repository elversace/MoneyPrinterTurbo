---
name: tiktok
description: Create a TikTok-ready vertical video with MoneyPrinterTurbo when the user invokes /TikTok or asks for a short TikTok video. Arabic is always the narration/script language and English subtitles are always required.
---

# TikTok Video Skill

Use this skill when the user starts a request with `/TikTok` or clearly asks to create a TikTok video with MoneyPrinterTurbo.

## Goal

Turn a topic into a complete short-form TikTok video using MoneyPrinterTurbo with fixed defaults so the user is not repeatedly asked for routine settings.

## Required input

Only the topic is required.

Example:

`/TikTok أفضل 5 سيارات رياضية في 2026`

If the user includes a desired duration, style, audience, or other creative direction, honor it. Otherwise use the defaults below and do not ask follow-up questions for routine settings.

## Fixed defaults

- Platform: TikTok
- Aspect ratio: 9:16 portrait
- Primary language: Arabic
- Script language: Arabic
- Narration/voiceover language: Arabic
- On-screen subtitles: English
- Subtitles: enabled
- Video count: 1
- Video source: pexels unless the user supplies footage or another source is configured
- Video fit mode: cover
- Video concat mode: random
- Background music: random
- Background music volume: 0.20
- Voice volume: 1.0
- Voice rate: 1.0
- Subtitle position: bottom
- Subtitle text: white with dark stroke for readability
- Output: MP4 suitable for TikTok

## Workflow

1. Read everything after `/TikTok` as the requested topic and creative direction.
2. Create a concise Arabic script designed for short-form retention. Start with a strong hook, keep sentences short, avoid filler, and end cleanly without unnecessary outro text.
3. Keep factual claims grounded. For current or time-sensitive topics, verify facts before writing the script when web access is available.
4. Generate search terms/material prompts that match the Arabic script semantically.
5. Use MoneyPrinterTurbo with these core video parameters:
   - `video_subject`: the user's topic
   - `video_language`: Arabic (`ar` or the equivalent supported Arabic locale)
   - `video_aspect`: `9:16`
   - `video_fit_mode`: `cover`
   - `video_concat_mode`: `random`
   - `video_count`: `1`
   - `subtitle_enabled`: `true`
   - `bgm_type`: `random`
   - `bgm_volume`: `0.2`
6. Use an Arabic TTS voice available in the configured provider. Prefer a natural Modern Standard Arabic voice unless the user explicitly requests a dialect.
7. Produce English subtitle text as a faithful translation of the Arabic narration. Preserve subtitle timing boundaries from the Arabic narration; translate the text inside each timed subtitle segment rather than changing timing based on English sentence length.
8. Burn the English subtitles into the final 9:16 video. Do not replace the Arabic narration with English audio.
9. Return the final MP4 and, when available, the Arabic script and English subtitle file as companion outputs.

## MoneyPrinterTurbo runtime

When the repository is available in an execution environment, prefer the project's CLI/API rather than reimplementing its video pipeline.

Typical local project commands:

```bash
uv sync --frozen
uv run python main.py
```

The API documentation is normally available on port 8080. The WebUI is normally available on port 8501.

For direct CLI generation, start from:

```bash
uv run python cli.py --video-subject "<topic>" --video-aspect "9:16"
```

Apply the fixed defaults from this skill through supported CLI options or a validated batch manifest. If the local MoneyPrinterTurbo version does not expose translated subtitle text as a built-in option, generate the Arabic timed subtitles first, translate each cue to English while preserving timestamps, then render/burn the translated subtitle track in the final composition step.

## Quality checks

Before completing the task, verify all of the following:

- Video is portrait 9:16.
- Narration is Arabic.
- Spoken script is Arabic.
- Visible subtitles are English, not Arabic.
- Subtitle timing follows the Arabic narration.
- No subtitle text is clipped outside the TikTok safe area.
- Audio is intelligible and background music does not overpower narration.
- Final output is a playable MP4.
- Do not ask the user to choose language, aspect ratio, subtitle language, or platform; those are fixed defaults for this skill.
