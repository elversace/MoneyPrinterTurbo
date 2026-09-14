# /TikTok Skill for MoneyPrinterTurbo

This folder defines the custom `/TikTok` workflow for this fork of MoneyPrinterTurbo.

## Usage

```text
/TikTok أفضل 5 سيارات رياضية في 2026
```

Only the topic is required. Routine settings are fixed automatically.

## Defaults

- Arabic script and narration
- English subtitles
- TikTok platform
- 9:16 portrait video
- Subtitles enabled
- One final MP4
- Pexels footage by default when available
- Random background music at low volume

## Important

The `SKILL.md` file defines the behavior for a skill-capable ChatGPT/Codex environment. The GitHub repository itself does not automatically register a native ChatGPT slash command. The skill must be installed or loaded by a compatible skills/plugin runtime.

MoneyPrinterTurbo remains the video-generation engine. The skill instructs the runtime to use the existing CLI/API and preserve Arabic narration while rendering English subtitles.
