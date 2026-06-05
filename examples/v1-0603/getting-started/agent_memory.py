#!/usr/bin/env python3
# pip install everos-cloud
# Getting Started — Agent Memory (everos-cloud SDK)
#
# content format: plain string
# access path:    client.v1.memories.agent (add) / client.v1.memories (get, search)

import os, time
from everos_cloud import EverOS

API_KEY  = os.getenv("EVEROS_API_KEY", "your_api_key_here")
BASE_URL = os.getenv("EVER_OS_BASE_URL", "https://api.evermind.ai")

client   = EverOS(api_key=API_KEY, base_url=BASE_URL)
agent    = client.v1.memories.agent
memories = client.v1.memories

# ── Add ──────────────────────────────────────────────────────────────────────
now_ms = int(time.time() * 1000)

response = agent.add(
    user_id="user_demo_001",
    session_id="session_gs_agent_001",
    messages=[
        {
            "role": "user",
            "timestamp": now_ms,
            "content": "I like black Americano, no sugar, the stronger the better!",
        },
        {
            "role": "assistant",
            "timestamp": now_ms + 1000,
            "content": "Got it, I'll remember your coffee preference.",
        },
    ],
)
print(response)

# ── Flush ─────────────────────────────────────────────────────────────────────
# Agent add only queues messages. flush triggers boundary detection and
# extracts agent_case / agent_skill memories from the buffered trajectory.
agent.flush(user_id="user_demo_001", session_id="session_gs_agent_001")

# ── Get ───────────────────────────────────────────────────────────────────────
print("\nWaiting 3s for indexing...")
time.sleep(3)

response = memories.get(
    filters={"user_id": "user_demo_001"},
    memory_type="agent_case",
    page=1,
    page_size=10,
)
print(response)

# ── Search ────────────────────────────────────────────────────────────────────
response = memories.search(
    filters={"user_id": "user_demo_001"},
    query="coffee preference",
    method="hybrid",
    top_k=5,
)
print(response)
