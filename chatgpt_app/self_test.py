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

        # Notification responses may legitimately have no JSON body.
        await send(
            {
                "jsonrpc": "2.0",
                "method": "notifications/initialized",
                "params": {},
            }
        )

        await send({"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}})

        await send(
            {
                "jsonrpc": "2.0",
                "id": 3,
                "method": "tools/call",
                "params": {
                    "name": "create_tiktok_video",
                    "arguments": {
                        "topic": "أفضل 5 سيارات رياضية في 2026",
                        "arabic_script": (
                            "في عام 2026 تستمر السيارات الرياضية في دفع حدود الأداء والتقنية إلى مستويات جديدة. "
                            "في هذا الفيديو نستعرض خمس سيارات لافتة تجمع بين السرعة والتصميم والهندسة المتقدمة. "
                            "نبدأ مع طرازات أوروبية تقدم تسارعاً مذهلاً وأنظمة هجينة أكثر ذكاءً، ثم ننتقل إلى سيارات "
                            "تركز على خفة الوزن ودقة التحكم داخل المنعطفات. بعض هذه السيارات يضع الراحة اليومية إلى جانب "
                            "القوة، بينما يختار البعض الآخر تجربة قيادة شرسة موجهة للحلبات. الفكرة ليست فقط في رقم القوة "
                            "الحصانية، بل في كيفية توصيل هذه القوة للطريق، وثبات السيارة عند السرعات العالية، وكفاءة المكابح "
                            "والديناميكا الهوائية. ومع تطور البطاريات والمحركات الكهربائية أصبحت الاستجابة أسرع من أي وقت مضى. "
                            "هذه هي الفئة التي ستحدد شكل السيارة الرياضية الحديثة في 2026، بين الصوت التقليدي والأداء الكهربائي "
                            "الفوري والتقنيات الذكية التي تساعد السائق على استخراج أقصى أداء ممكن."
                        ),
                        "duration_seconds": 60,
                        "style": "default",
                    },
                },
            }
        )


if __name__ == "__main__":
    asyncio.run(main())
