from pathlib import Path

path = Path('/MoneyPrinterTurbo/app/services/subtitle.py')
text = path.read_text(encoding='utf-8')
old = '''    except Exception as exc:\n        logger.error(f"failed to translate subtitles to {target_language}: {exc}")\n        raise\n'''
new = '''    except Exception as exc:\n        logger.warning(\n            f"MoneyPrinterTurbo subtitle translation failed for {target_language}: {exc}; "\n            "trying one direct OpenAI batch translation request"\n        )\n        try:\n            import os as _os\n            import urllib.request as _urllib_request\n\n            api_key = (_os.getenv("OPENAI_API_KEY") or "").strip()\n            if not api_key:\n                raise RuntimeError("OPENAI_API_KEY is unavailable for subtitle fallback")\n            fallback_prompt = (\n                f"Translate these subtitle cues into {target_language}. "\n                "Return ONLY a JSON array of strings with exactly the same number of items "\n                "and the same order. Keep each cue concise for on-screen subtitles. Input: "\n                + json.dumps(source_texts, ensure_ascii=False)\n            )\n            payload = json.dumps({\n                "model": _os.getenv("OPENAI_MODEL_NAME", "gpt-4.1-mini"),\n                "messages": [\n                    {"role": "system", "content": "You translate subtitles accurately and concisely."},\n                    {"role": "user", "content": fallback_prompt},\n                ],\n                "temperature": 0,\n            }).encode("utf-8")\n            req = _urllib_request.Request(\n                "https://api.openai.com/v1/chat/completions",\n                data=payload,\n                headers={\n                    "Authorization": f"Bearer {api_key}",\n                    "Content-Type": "application/json",\n                },\n                method="POST",\n            )\n            with _urllib_request.urlopen(req, timeout=45) as resp:\n                response_data = json.loads(resp.read().decode("utf-8"))\n            translated_raw = response_data["choices"][0]["message"]["content"]\n            translated = json.loads(_strip_json_fence(translated_raw))\n            if not isinstance(translated, list) or len(translated) != len(items):\n                raise ValueError("direct subtitle fallback returned an unexpected cue count")\n            if not all(isinstance(t, str) and t.strip() for t in translated):\n                raise ValueError("direct subtitle fallback returned an invalid cue")\n            logger.success(f"direct OpenAI subtitle fallback translated {len(translated)} cues")\n        except Exception as fallback_exc:\n            logger.warning(\n                f"subtitle translation still failed: {fallback_exc}; "\n                "continuing with original timed cues so the video is still produced"\n            )\n            return items\n'''
if old in text:
    text = text.replace(old, new, 1)
else:
    marker_start = '    except Exception as exc:\n        logger.warning('
    marker_end = '        return items\n'
    start = text.find(marker_start, text.find('def _translate_subtitle_items'))
    if start != -1:
        end = text.find(marker_end, start)
        if end != -1:
            end += len(marker_end)
            text = text[:start] + new + text[end:]
path.write_text(text, encoding='utf-8')
print('Applied single-request OpenAI subtitle fallback; no Google translation dependency', flush=True)
