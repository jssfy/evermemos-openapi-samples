#!/usr/bin/env python3
"""
08_get_async.py — 异步 get，覆盖所有 memory_type

memory_type: episodic_memory | profile | agent_case | agent_skill
"""
import asyncio, os
from everos_cloud import AsyncEverOS
from pprint import pprint

API_KEY  = os.getenv("EVEROS_API_KEY",  "ddcf3ffb-df31-4c9c-9d30-fb2ee67aed26")
BASE_URL = os.getenv("EVER_OS_BASE_URL", "https://dev-gateway.aws.evermind.ai")
USER_ID  = "everos-cloud-async-001"

client = AsyncEverOS(api_key=API_KEY, base_url=BASE_URL)


async def main() -> None:
    for mtype in ("episodic_memory", "profile", "agent_case", "agent_skill"):
        print(f"\n=== get memory_type={mtype} ===")
        resp = await client.v1.memories.get(
            filters={"user_id": USER_ID},
            memory_type=mtype,
            page=1,
            page_size=5,
            rank_by="created_at",
            rank_order="desc",
        )
        print(f"total_count: {resp.data.total_count}")
        items = (
            resp.data.episodes    if mtype == "episodic_memory" else
            resp.data.profiles    if mtype == "profile"         else
            resp.data.agent_cases if mtype == "agent_case"      else
            resp.data.agent_skills
        )
        for item in (items or [])[:2]:
            pprint(item)


if __name__ == "__main__":
    asyncio.run(main())
