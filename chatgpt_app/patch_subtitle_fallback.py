from pathlib import Path

path = Path('/MoneyPrinterTurbo/app/services/subtitle.py')
text = path.read_text(encoding='utf-8')
old = '''    except Exception as exc:\n        logger.error(f"failed to translate subtitles to {target_language}: {exc}")\n        raise\n'''
new = '''    except Exception as exc:\n        logger.warning(\n            f"LLM subtitle translation failed for {target_language}: {exc}; "\n            "falling back to GoogleTranslator"\n        )\n        try:\n            from deep_translator import GoogleTranslator\n\n            translator = GoogleTranslator(source="auto", target="en")\n            translated = translator.translate_batch(source_texts)\n            if not isinstance(translated, list) or len(translated) != len(items):\n                raise ValueError(\n                    "fallback subtitle translation returned an unexpected number of cues"\n                )\n            if not all(isinstance(text, str) and text.strip() for text in translated):\n                raise ValueError(\n                    "fallback subtitle translation returned an empty or invalid cue"\n                )\n            logger.success(\n                f"fallback subtitle translation succeeded for {len(translated)} cues"\n            )\n        except Exception as fallback_exc:\n            logger.error(\n                f"failed to translate subtitles to {target_language}; "\n                f"LLM error: {exc}; fallback error: {fallback_exc}"\n            )\n            raise fallback_exc\n'''
if old not in text:
    print('Subtitle fallback patch already applied or target block changed', flush=True)
else:
    path.write_text(text.replace(old, new, 1), encoding='utf-8')
    print('Applied subtitle translation fallback patch', flush=True)
