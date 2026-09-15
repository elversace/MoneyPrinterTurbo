import os
import re
from pathlib import Path
from typing import Any

import httpx
from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings
from starlette.requests import Request
from starlette.responses import FileResponse, HTMLResponse, JSONResponse

APP_NAME = "TikTok"
MPT_BASE_URL = os.getenv("MPT_BASE_URL", "http://127.0.0.1:8081").rstrip("/")
MPT_API_KEY = os.getenv("MPT_API_KEY", "").strip()
MPT_ARABIC_VOICE = os.getenv("MPT_ARABIC_VOICE", "ar-SA-HamedNeural-Male").strip()
MPT_LOCAL_BACKGROUND = os.getenv("MPT_LOCAL_BACKGROUND", "tiktok-background.mp4").strip()
MCP_HOST = os.getenv("MCP_HOST", "0.0.0.0")
MCP_PORT = int(os.getenv("PORT", os.getenv("MCP_PORT", "8000")))
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()
OPENAI_MODEL_NAME = os.getenv("OPENAI_MODEL_NAME", "gpt-4.1-mini").strip()
DEFAULT_DURATION_SECONDS = 60
TASKS_ROOT = Path("/MoneyPrinterTurbo/storage/tasks")

mcp = FastMCP(
    APP_NAME,
    instructions=(
        "Create TikTok-ready short videos with MoneyPrinterTurbo. Default behavior is fixed: "
        "Arabic script and Arabic narration, portrait 9:16, TikTok-oriented pacing, English "
        "subtitle delivery, and a target duration of 60 seconds. Generate an Arabic spoken "
        "script sized for about one minute and pass it in arabic_script."
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


async def _generate_arabic_script(topic: str) -> str:
    if not OPENAI_API_KEY:
        return (
            f"اليوم نأخذكم في جولة سريعة وممتعة حول {topic}. "
            "سنكتشف أهم النقاط التي تستحق الزيارة، وما الذي يجعل كل مكان مميزاً، "
            "مع نصائح بسيطة تساعد الزائر على الاستمتاع بالتجربة. "
            "إذا كنت تزور المكان لأول مرة، احفظ هذا الفيديو وشاركه مع من يخطط للسفر."
        )
    prompt = (
        "اكتب نص تعليق صوتي عربي فصيح طبيعي لفيديو TikTok مدته نحو 60 ثانية. "
        "الجمهور أجانب مهتمون بالسفر والثقافة. اجعل النص جذاباً، سريع الإيقاع، "
        "واضحاً، ومن دون عناوين أو تعداد أو رموز. الموضوع: " + topic
    )
    body = {
        "model": OPENAI_MODEL_NAME,
        "messages": [
            {"role": "system", "content": "أنت كاتب محترف لنصوص فيديوهات السفر القصيرة."},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.7,
    }
    async with httpx.AsyncClient(timeout=45.0) as client:
        r = await client.post(
            "https://api.openai.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {OPENAI_API_KEY}", "Content-Type": "application/json"},
            json=body,
        )
        r.raise_for_status()
        data = r.json()
    return data["choices"][0]["message"]["content"].strip()


async def _start_video(topic: str, arabic_script: str, duration_seconds: int = DEFAULT_DURATION_SECONDS) -> dict[str, Any]:
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
        return response.json()


def _extract_task_id(data: Any) -> str | None:
    if isinstance(data, dict):
        task_id = data.get("task_id")
        if isinstance(task_id, str):
            return task_id
        for value in data.values():
            found = _extract_task_id(value)
            if found:
                return found
    elif isinstance(data, list):
        for value in data:
            found = _extract_task_id(value)
            if found:
                return found
    return None


WEB_HTML = r'''<!doctype html>
<html lang="ar" dir="rtl"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>TikTok Video Maker</title>
<style>
*{box-sizing:border-box}body{margin:0;background:#0b0b0f;color:#fff;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Tahoma,sans-serif;min-height:100vh;display:flex;align-items:center;justify-content:center;padding:22px}.card{width:min(560px,100%);background:#15151b;border:1px solid #2b2b34;border-radius:24px;padding:22px;box-shadow:0 18px 60px #0008}.badge{display:inline-block;background:#ff2d55;color:#fff;padding:7px 11px;border-radius:999px;font-size:13px;font-weight:700}.title{font-size:30px;margin:14px 0 6px}.sub{color:#aaa;margin:0 0 18px;line-height:1.7}textarea{width:100%;min-height:150px;border-radius:18px;border:1px solid #34343f;background:#0f0f14;color:#fff;padding:16px;font-size:18px;resize:vertical;outline:none}button{width:100%;margin-top:14px;border:0;border-radius:16px;padding:16px;font-size:18px;font-weight:800;background:#fff;color:#111;cursor:pointer}button:disabled{opacity:.5}.status{margin-top:16px;padding:14px;border-radius:14px;background:#0f0f14;color:#c9c9d0;line-height:1.6;display:none}video{width:100%;border-radius:16px;margin-top:16px;display:none;background:#000}.hint{font-size:13px;color:#777;margin-top:12px;text-align:center}
</style></head><body><div class="card"><span class="badge">/TikTok</span><div class="title">صانع فيديو TikTok</div><p class="sub">اكتب الموضوع فقط. الإعدادات ثابتة: 9:16، تعليق عربي، ترجمة إنجليزية، مدة تقارب 60 ثانية.</p><textarea id="topic">أفضل الأماكن المشهورة في طرابلس للأجانب</textarea><button id="go">إنشاء الفيديو</button><div id="status" class="status"></div><video id="video" controls playsinline></video><div class="hint">يتم إنشاء الفيديو على خادم MoneyPrinterTurbo الخاص بك.</div></div>
<script>
const go=document.getElementById('go'),status=document.getElementById('status'),video=document.getElementById('video'),topic=document.getElementById('topic');
function show(t){status.style.display='block';status.textContent=t}
async function poll(id){for(;;){await new Promise(r=>setTimeout(r,5000));const r=await fetch('/web/tasks/'+id);const j=await r.json();if(j.status==='ready'){show('تم إنشاء الفيديو ✅');video.src=j.video_url;video.style.display='block';go.disabled=false;return}if(j.status==='failed'){show('تعذر إنشاء الفيديو: '+(j.message||'خطأ غير معروف'));go.disabled=false;return}show('جاري إنشاء الفيديو… '+(j.state||''))}}
go.onclick=async()=>{const t=topic.value.trim();if(!t)return show('اكتب موضوع الفيديو أولاً.');go.disabled=true;video.style.display='none';show('جاري تجهيز النص وبدء الإنشاء…');try{const r=await fetch('/web/create',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({topic:t})});const j=await r.json();if(!r.ok)throw new Error(j.error||'فشل بدء الإنشاء');show('بدأ إنشاء الفيديو. رقم المهمة: '+j.task_id);poll(j.task_id)}catch(e){show(e.message);go.disabled=false}}
</script></body></html>'''


@mcp.custom_route("/", methods=["GET"])
async def web_home(request: Request):
    return HTMLResponse(WEB_HTML)


@mcp.custom_route("/web/create", methods=["POST"])
async def web_create(request: Request):
    try:
        payload = await request.json()
        topic = str(payload.get("topic", "")).strip()
        if not topic:
            return JSONResponse({"error": "topic is required"}, status_code=400)
        script = await _generate_arabic_script(topic)
        result = await _start_video(topic, script)
        task_id = _extract_task_id(result)
        if not task_id:
            return JSONResponse({"error": "video engine did not return a task id", "details": result}, status_code=502)
        return JSONResponse({"status": "started", "task_id": task_id, "script": script})
    except Exception as exc:
        return JSONResponse({"error": str(exc)}, status_code=500)


@mcp.custom_route("/web/tasks/{task_id}", methods=["GET"])
async def web_task(request: Request):
    task_id = request.path_params.get("task_id", "")
    if not re.fullmatch(r"[0-9a-fA-F-]{36}", task_id):
        return JSONResponse({"status": "failed", "message": "invalid task id"}, status_code=400)
    task_dir = TASKS_ROOT / task_id
    if task_dir.is_dir():
        finals = sorted(task_dir.glob("final-*.mp4"))
        if finals:
            return JSONResponse({"status": "ready", "video_url": f"/videos/{task_id}/{finals[-1].name}"})
    try:
        async with httpx.AsyncClient(timeout=20.0) as client:
            r = await client.get(f"{MPT_BASE_URL}/api/v1/tasks/{task_id}", headers=_headers())
        data = r.json()
        text = str(data).lower()
        if any(x in text for x in ["failed", "error"]):
            return JSONResponse({"status": "failed", "message": str(data)})
        state = "processing"
        if isinstance(data, dict):
            raw = data.get("data", data)
            if isinstance(raw, dict):
                state = str(raw.get("state") or raw.get("status") or "processing")
        return JSONResponse({"status": "processing", "state": state})
    except Exception as exc:
        return JSONResponse({"status": "processing", "state": str(exc)})


@mcp.custom_route("/videos/{task_id}/{filename}", methods=["GET"])
async def generated_video(request: Request):
    task_id = request.path_params.get("task_id", "")
    filename = request.path_params.get("filename", "")
    if not re.fullmatch(r"[0-9a-fA-F-]{36}", task_id) or not re.fullmatch(r"final-[0-9]+\.mp4", filename):
        return JSONResponse({"error": "invalid video path"}, status_code=400)
    task_dir = (TASKS_ROOT / task_id).resolve()
    file_path = (task_dir / filename).resolve()
    if TASKS_ROOT.resolve() not in file_path.parents or not file_path.is_file():
        return JSONResponse({"error": "video not found"}, status_code=404)
    return FileResponse(file_path, media_type="video/mp4", filename=filename)


@mcp.tool(name="create_tiktok_video", description=(
    "Create a TikTok video with Arabic narration, portrait 9:16 and a 60-second target."
))
async def create_tiktok_video(topic: str, arabic_script: str, duration_seconds: int = DEFAULT_DURATION_SECONDS, style: str | None = None) -> dict[str, Any]:
    topic = (topic or "").strip()
    arabic_script = (arabic_script or "").strip()
    if not topic:
        raise ValueError("topic is required")
    if not arabic_script:
        raise ValueError("arabic_script is required")
    duration_seconds = int(duration_seconds or DEFAULT_DURATION_SECONDS)
    result = await _start_video(topic, arabic_script, duration_seconds)
    return {"status": "started", "platform": "TikTok", "language": "Arabic", "subtitle_language": "English", "aspect_ratio": "9:16", "duration_target_seconds": duration_seconds, "style": style, "moneyprinterturbo": result}


@mcp.tool(name="tiktok_defaults", description="Return the fixed defaults used by the TikTok app.")
async def tiktok_defaults() -> dict[str, Any]:
    return {"platform": "TikTok", "script_language": "Arabic", "narration_language": "Arabic", "subtitle_language": "English", "aspect_ratio": "9:16", "duration_seconds": 60, "video_count": 1, "video_source": "local_test_background"}


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
