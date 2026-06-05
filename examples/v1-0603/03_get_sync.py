#!/usr/bin/env python3
"""
03_get_sync.py — 同步 get 记忆列表

memory_type 可选：episodic_memory | profile | agent_case | agent_skill
"""
import os
from everos_cloud import EverOS

API_KEY  = os.getenv("EVEROS_API_KEY", "ddcf3ffb-df31-4c9c-9d30-fb2ee67aed26")
BASE_URL = os.getenv("EVER_OS_BASE_URL", "https://dev-gateway.aws.evermind.ai")
USER_ID  = "everos-cloud-example-001"

client = EverOS(api_key=API_KEY, base_url=BASE_URL)

for mtype in ("episodic_memory", "profile"):
    resp = client.v1.memories.get(
        filters={"user_id": USER_ID},
        memory_type=mtype,
        page=1,
        page_size=5,
        rank_by="created_at",
        rank_order="desc",
    )
    print(f"\n=== {mtype} (total={resp.data.total_count}) ===")
    items = resp.data.episodes if mtype == "episodic_memory" else resp.data.profiles
    for item in items:
        print(" -", item)
