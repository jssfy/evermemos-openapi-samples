#!/usr/bin/env python3
"""
quickstart_sdk_sync.py — 同步快速入门

流程：add 对话 → 等待索引 → search

Install:
  pip install "https://pkg.stainless.com/s/everos-trial-python/\
37f86dedd9c88bd79496a8b064e7c332747fbf37/everos_cloud-0.0.1-py3-none-any.whl"
"""
import os, time
from everos_cloud import EverOS

API_KEY  = os.getenv("EVEROS_API_KEY",  "ddcf3ffb-df31-4c9c-9d30-fb2ee67aed26")
BASE_URL = os.getenv("EVER_OS_BASE_URL", "https://dev-gateway.aws.evermind.ai")

client = EverOS(api_key=API_KEY, base_url=BASE_URL)
memories = client.v1.memories

USER_ID    = "cookbook-alice"
SESSION_ID = "demo-sync-001"
now_ms = int(time.time() * 1000)

# ── Step 1: 存储对话 ──────────────────────────────────────────
print("1. Storing conversation...")

memories.add(
    user_id=USER_ID,
    session_id=SESSION_ID,
    messages=[
        {
            "role": "user",
            "timestamp": now_ms,
            "content": [{"type": "text", "text": "I prefer working in the morning, usually from 6am to 10am. That's when I'm most productive."}],
        },
        {
            "role": "assistant",
            "timestamp": now_ms + 2000,
            "content": [{"type": "text", "text": "That's a great habit! Morning hours are often ideal for deep focus work."}],
        },
    ],
)

memories.add(
    user_id=USER_ID,
    session_id=SESSION_ID,
    messages=[
        {
            "role": "user",
            "timestamp": now_ms + 10000,
            "content": [{"type": "text", "text": "Let's switch topics - what's the weather like today?"}],
        },
    ],
)

# ── Step 2: 等待索引 ──────────────────────────────────────────
print("2. Waiting for memory extraction (5s)...")
time.sleep(5)

# ── Step 3: 搜索记忆 ──────────────────────────────────────────
print("3. Searching memories...")

response = memories.search(
    filters={"user_id": USER_ID},
    query="when does alice prefer to work",
    method="hybrid",
    top_k=5,
)

data = response.data
episodes = data.episodes or []
profiles = data.profiles or []

print(f"\nFound {len(episodes)} episodes, {len(profiles)} profiles:\n")
for ep in episodes:
    print(f"  episode: {getattr(ep, 'episode', None) or getattr(ep, 'summary', 'N/A')}")
    print(f"  score:   {getattr(ep, 'score', 'N/A')}")
    print("  " + "-" * 36)
