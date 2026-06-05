#!/usr/bin/env python3
"""
07_search_async.py — 异步 search，覆盖四种检索方式

method: keyword | vector | hybrid | agentic
"""
import asyncio, os
from everos_cloud import AsyncEverOS
from pprint import pprint

API_KEY  = os.getenv("EVEROS_API_KEY",  "ddcf3ffb-df31-4c9c-9d30-fb2ee67aed26")
BASE_URL = os.getenv("EVER_OS_BASE_URL", "https://dev-gateway.aws.evermind.ai")
USER_ID  = "everos-cloud-async-001"   # 先运行 06_add_async.py 写入数据

client = AsyncEverOS(api_key=API_KEY, base_url=BASE_URL)


async def main() -> None:
    query = "basketball outdoor activities"

    for method in ("hybrid", "vector", "keyword"):
        print(f"\n=== search method={method} ===")
        resp = await client.v1.memories.search(
            filters={"user_id": USER_ID},
            query=query,
            method=method,
            top_k=3,
        )
        print(f"episodes: {len(resp.data.episodes or [])}")
        print(f"profiles: {len(resp.data.profiles or [])}")
        for ep in (resp.data.episodes or [])[:2]:
            pprint(ep)


if __name__ == "__main__":
    asyncio.run(main())
