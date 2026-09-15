from pathlib import Path

path = Path('/MoneyPrinterTurbo/chatgpt_app/server.py')
text = path.read_text(encoding='utf-8')

old = '''        data = r.json()\n        text = str(data).lower()\n        if any(x in text for x in ["failed", "error"]):\n            return JSONResponse({"status": "failed", "message": str(data)})\n        state = "processing"\n        if isinstance(data, dict):\n            raw = data.get("data", data)\n            if isinstance(raw, dict):\n                state = str(raw.get("state") or raw.get("status") or "processing")\n        return JSONResponse({"status": "processing", "state": state})\n'''
new = '''        data = r.json()\n        state = "processing"\n        progress = None\n        if isinstance(data, dict):\n            raw = data.get("data", data)\n            if isinstance(raw, dict):\n                actual_error = raw.get("error")\n                failed_stage = raw.get("failed_stage")\n                status_value = str(raw.get("status") or "").strip().lower()\n                state_value = raw.get("state")\n                state_text = str(state_value or "").strip().lower()\n                if actual_error or failed_stage or status_value in {"failed", "error"} or state_text in {"failed", "error"}:\n                    return JSONResponse({"status": "failed", "message": str(actual_error or failed_stage or data)})\n                progress = raw.get("progress")\n                state = str(state_value if state_value is not None else raw.get("status") or "processing")\n        return JSONResponse({"status": "processing", "state": state, "progress": progress})\n'''
if old in text:
    text = text.replace(old, new, 1)

old_finals = '        finals = sorted(task_dir.glob("final-*.mp4"))\n'
new_finals = '        finals = sorted(p for p in task_dir.glob("final-*.mp4") if re.fullmatch(r"final-[0-9]+\\.mp4", p.name))\n'
if old_finals in text:
    text = text.replace(old_finals, new_finals, 1)

path.write_text(text, encoding='utf-8')
print('Applied web task status patch and final-video temp-file filter', flush=True)
