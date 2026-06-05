#!/usr/bin/env python3
"""
06_add_async.py — 异步 add 记忆

AsyncEverOS 与 EverOS 接口相同，适合在 FastAPI / asyncio 应用中使用。
"""
import asyncio, os, time
from everos_cloud import AsyncEverOS

API_KEY  = os.getenv("EVEROS_API_KEY",  "ddcf3ffb-df31-4c9c-9d30-fb2ee67aed26")
BASE_URL = os.getenv("EVER_OS_BASE_URL", "https://dev-gateway.aws.evermind.ai")
USER_ID  = "everos-cloud-async-001"

client = AsyncEverOS(api_key=API_KEY, base_url=BASE_URL)


async def main() -> None:
    now_ms = int(time.time() * 1000)

    # 并发写入两段对话
    r1, r2 = await asyncio.gather(
        client.v1.memories.add(
            user_id=USER_ID,
            session_id="async-session-001",
            messages=[
                {"role": "user",      "timestamp": now_ms,      "content": [{"type": "text", "text": "I love basketball and hiking."}]},
                {"role": "assistant", "timestamp": now_ms + 500, "content": [{"type": "text", "text": "Great! Both are excellent for staying fit."}]},
            ],
        ),
        client.v1.memories.add(
            user_id=USER_ID,
            session_id="async-session-002",
            messages=[
                {"role": "user", "timestamp": now_ms + 1000, "content": [{"type": "text", "text": "我今天读完了《人类简史》，收获很大。"}]},
            ],
        ),
    )
    print("add 1:", r1.data.task_id, r1.data.status)
    print("add 2:", r2.data.task_id, r2.data.status)


if __name__ == "__main__":
    asyncio.run(main())
