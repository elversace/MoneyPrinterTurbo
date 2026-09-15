import asyncio
import json
import os

import httpx


MCP_URL = os.getenv("MCP_SELF_TEST_URL", "http://127.0.0.1:8000/mcp")


async def main() -> None:
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream",
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        async def send(payload: dict):
            response = await client.post(MCP_URL, headers=headers, json=payload)
            session_id = response.headers.get("mcp-session-id")
            if session_id:
                headers["mcp-session-id"] = session_id
            print(
                "MCP_SELF_TEST_RESPONSE",
                json.dumps(
                    {
                        "status": response.status_code,
                        "session_id": session_id,
                        "body": response.text,
                    },
                    ensure_ascii=False,
                ),
                flush=True,
            )
            response.raise_for_status()
            return response

        await send(
            {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2025-03-26",
                    "capabilities": {},
                    "clientInfo": {"name": "railway-local-self-test", "version": "1.0"},
                },
            }
        )

        await send(
            {
                "jsonrpc": "2.0",
                "method": "notifications/initialized",
                "params": {},
            }
        )

        await send({"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}})

        # Deliberately written in formal Modern Standard Arabic (الفصحى), with
        # no dialectal wording, and shortened to target roughly one minute.
        arabic_fusha_script = (
            "إليك خمس سيارات رياضية تستحق المتابعة في عام 2026. "
            "في المركز الخامس، أستون مارتن فانتج، بتصميم أنيق ومحرك قوي يمنحها حضوراً مميزاً على الطريق. "
            "في المركز الرابع، شيفروليه كورفيت زد صفر ستة، التي تجمع بين الأداء الأمريكي الحاد والتوازن المذهل في المنعطفات. "
            "ثالثاً، بورشه تسعمئة وإحدى عشرة جي تي ثري، سيارة دقيقة صُممت لعشاق القيادة الخالصة. "
            "في المركز الثاني، فيراري مئتان وستة وتسعون سبيشيالي، بقوة هجينة واستجابة سريعة وديناميكا هوائية متقدمة. "
            "وفي المركز الأول، لامبورغيني ريفويلتو، التي تمزج محرك اثنتي عشرة أسطوانة مع التقنية الهجينة لتقدم تجربة خارقة. "
            "هذه السيارات تمثل تنوع الأداء الرياضي الحديث، من الدقة الألمانية إلى الجرأة الإيطالية والقوة الأمريكية."
        )

        await send(
            {
                "jsonrpc": "2.0",
                "id": 3,
                "method": "tools/call",
                "params": {
                    "name": "create_tiktok_video",
                    "arguments": {
                        "topic": "أفضل 5 سيارات رياضية في 2026",
                        "arabic_script": arabic_fusha_script,
                        "duration_seconds": 60,
                        "style": "modern-cinematic",
                    },
                },
            }
        )


if __name__ == "__main__":
    asyncio.run(main())
