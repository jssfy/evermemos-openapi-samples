#!/usr/bin/env python3
# pip install everos-cloud
# Getting Started — User Memory (everos-cloud SDK)
#
# content format: [{"type": "text", "text": "..."}]
# access path:    client.v1.memories

import os, time
from everos_cloud import EverOS

API_KEY  = os.getenv("EVEROS_API_KEY", "your_api_key_here")
BASE_URL = os.getenv("EVER_OS_BASE_URL", "https://api.evermind.ai")

client   = EverOS(api_key=API_KEY, base_url=BASE_URL)
memories = client.v1.memories

# ── Add ──────────────────────────────────────────────────────────────────────
now_ms = int(time.time() * 1000)

response = memories.add(
    user_id="user_demo_001",
    session_id="session_gs_001",
    messages=[
        {
            "role": "user",
            "timestamp": now_ms,
            "content": [{"type": "text", "text": "I like black Americano, no sugar, the stronger the better!"}],
        },
        {
            "role": "assistant",
            "timestamp": now_ms + 1000,
            "content": [{"type": "text", "text": "Got it, I'll remember your coffee preference."}],
        },
    ],
)
print(response)

# ── Get ───────────────────────────────────────────────────────────────────────
print("\nWaiting 3s for indexing...")
time.sleep(3)

response = memories.get(
    filters={"user_id": "user_demo_001"},
    memory_type="episodic_memory",
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
