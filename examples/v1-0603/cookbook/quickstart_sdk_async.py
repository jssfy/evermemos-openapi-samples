#!/usr/bin/env python3
"""
quickstart_sdk_async.py — 异步快速入门

AsyncEverOS 适用于 FastAPI / asyncio 应用。
流程：async add（并发两段对话）→ 等待 → async search
"""
import asyncio, os, time
from everos_cloud import AsyncEverOS

API_KEY  = os.getenv("EVEROS_API_KEY",  "ddcf3ffb-df31-4c9c-9d30-fb2ee67aed26")
BASE_URL = os.getenv("EVER_OS_BASE_URL", "https://dev-gateway.aws.evermind.ai")

client  = AsyncEverOS(api_key=API_KEY, base_url=BASE_URL)
memories = client.v1.memories

USER_ID = "cookbook-async-bob"
now_ms  = int(time.time() * 1000)


async def main() -> None:
    # ── Step 1: 并发存储两段对话 ──────────────────────────────
    print("1. Storing conversations (concurrent)...")

    await asyncio.gather(
        memories.add(
            user_id=USER_ID,
            session_id="async-s1",
            messages=[
                {"role": "user",      "timestamp": now_ms,      "content": [{"type": "text", "text": "I love hiking on weekends, especially in the mountains."}]},
                {"role": "assistant", "timestamp": now_ms + 500, "content": [{"type": "text", "text": "That sounds amazing! Do you prefer trails or open terrain?"}]},
            ],
        ),
        memories.add(
            user_id=USER_ID,
            session_id="async-s2",
            messages=[
                {"role": "user", "timestamp": now_ms + 1000, "content": [{"type": "text", "text": "我喜欢在早上跑步，每次大约5公里。"}]},
            ],
        ),
    )

    # ── Step 2: 等待索引 ──────────────────────────────────────
    print("2. Waiting for memory extraction (5s)...")
    await asyncio.sleep(5)

    # ── Step 3: 搜索 ──────────────────────────────────────────
    print("3. Searching memories...")

    response = await memories.search(
        filters={"user_id": USER_ID},
        query="outdoor activities and exercise habits",
        method="hybrid",
        top_k=5,
    )

    episodes = response.data.episodes or []
    print(f"\nFound {len(episodes)} relevant memories:\n")
    for ep in episodes:
        print(f"  episode: {getattr(ep, 'episode', None) or getattr(ep, 'summary', 'N/A')}")
        print(f"  score:   {getattr(ep, 'score', 'N/A')}")
        print("  " + "-" * 36)

    # ── Step 4: 清理 ──────────────────────────────────────────
    print("\n4. Cleanup...")
    await memories.delete(user_id=USER_ID)
    print("Done.")


if __name__ == "__main__":
    asyncio.run(main())
