from pathlib import Path

path = Path('/MoneyPrinterTurbo/app/services/subtitle.py')
text = path.read_text(encoding='utf-8')
old = '''    except Exception as exc:\n        logger.error(f"failed to translate subtitles to {target_language}: {exc}")\n        raise\n'''
new = '''    except Exception as exc:\n        logger.warning(\n            f"subtitle translation to {target_language} failed: {exc}; "\n            "continuing with original subtitle cues so video rendering is not blocked"\n        )\n        # Fail open: keep the original timed cues. This guarantees that subtitle\n        # translation problems never abort the entire video pipeline.\n        return items\n'''
if old not in text:
    # Also replace the older GoogleTranslator fallback block if it was already patched.
    marker_start = '    except Exception as exc:\n        logger.warning(\n            f"LLM subtitle translation failed for {target_language}: {exc}; "'
    marker_end = '            raise fallback_exc\n'
    start = text.find(marker_start)
    if start != -1:
        end = text.find(marker_end, start)
        if end != -1:
            end += len(marker_end)
            text = text[:start] + new + text[end:]
            path.write_text(text, encoding='utf-8')
            print('Replaced Google subtitle fallback with fail-open behavior', flush=True)
        else:
            print('Subtitle fallback end marker not found', flush=True)
    else:
        print('Subtitle translation patch already applied or target block changed', flush=True)
else:
    path.write_text(text.replace(old, new, 1), encoding='utf-8')
    print('Applied fail-open subtitle translation patch', flush=True)
