from pathlib import Path

path = Path('/MoneyPrinterTurbo/chatgpt_app/server.py')
text = path.read_text(encoding='utf-8')
old = '''        data = r.json()\n        text = str(data).lower()\n        if any(x in text for x in ["failed", "error"]):\n            return JSONResponse({"status": "failed", "message": str(data)})\n        state = "processing"\n        if isinstance(data, dict):\n            raw = data.get("data", data)\n            if isinstance(raw, dict):\n                state = str(raw.get("state") or raw.get("status") or "processing")\n        return JSONResponse({"status": "processing", "state": state})\n'''
new = '''        data = r.json()\n        state = "processing"\n        progress = None\n        if isinstance(data, dict):\n            raw = data.get("data", data)\n            if isinstance(raw, dict):\n                actual_error = raw.get("error")\n                failed_stage = raw.get("failed_stage")\n                status_value = str(raw.get("status") or "").strip().lower()\n                state_value = raw.get("state")\n                state_text = str(state_value or "").strip().lower()\n                if actual_error or failed_stage or status_value in {"failed", "error"} or state_text in {"failed", "error"}:\n                    return JSONResponse({"status": "failed", "message": str(actual_error or failed_stage or data)})\n                progress = raw.get("progress")\n                state = str(state_value if state_value is not None else raw.get("status") or "processing")\n        return JSONResponse({"status": "processing", "state": state, "progress": progress})\n'''
if old not in text:
    raise SystemExit('web_task block not found; patch not applied')
path.write_text(text.replace(old, new, 1), encoding='utf-8')
print('Applied web task status patch', flush=True)
