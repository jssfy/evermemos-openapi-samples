"""
Cookbook: Your First Memory in 5 Minutes
Tests: store conversation → wait for indexing → search memory
API: https://api.evermind.ai
"""
import os
import time
from everos import EverOS

client  = EverOS()
memories = client.v1.memories

USER_ID = "cookbook_qs_user"


def _ep_text(ep) -> str:
    return getattr(ep, "episode", None) or getattr(ep, "summary", "") or ""


# ── Case 1: Step 1 – Store a conversation ──────────────────────────────────
def test_step1_store_conversation():
    print("\n=== Case 1: Store a conversation ===")
    resp = memories.add(
        user_id=USER_ID,
        session_id="qs_session",
        messages=[{
            "role": "user",
            "timestamp": int(time.time() * 1000),
            "content": "I prefer working in the morning, usually from 6am to 10am. That's when I'm most productive.",
        }],
    )
    print("response:", resp)
    assert resp.data is not None
    print("PASS")


# ── Case 2: Step 2 – Trigger boundary detection ────────────────────────────
def test_step2_trigger_boundary():
    print("\n=== Case 2: Trigger boundary detection ===")
    resp = memories.add(
        user_id=USER_ID,
        session_id="qs_session",
        messages=[{
            "role": "user",
            "timestamp": int(time.time() * 1000),
            "content": "Let's switch topics - what's the weather like today?",
        }],
    )
    print("response:", resp)
    assert resp.data is not None
    print("Waiting 5s for indexing…")
    time.sleep(5)
    print("PASS")


# ── Case 3: Step 3 – Search memory ────────────────────────────────────────
def test_step3_search_memory():
    print("\n=== Case 3: Search memory ===")
    resp = memories.search(
        filters={"user_id": USER_ID},
        query="when does alice prefer to work",
        method="hybrid",
        top_k=5,
    )
    episodes = resp.data.episodes if resp.data else []
    print(f"Found {len(episodes)} episodes")
    for ep in episodes:
        print(f"  score={getattr(ep, 'score', '?')}  summary={_ep_text(ep)[:80]}")
    print("PASS")


# ── Case 4: Complete working script (Bob's hiking preference) ──────────────
def test_complete_script():
    print("\n=== Case 4: Complete working script ===")
    now_ms = int(time.time() * 1000)

    print("1. Storing conversation…")
    memories.add(
        user_id=USER_ID,
        session_id="qs_complete",
        messages=[{"role": "user", "timestamp": now_ms,
                   "content": "I love hiking on weekends, especially in the mountains."}],
    )
    memories.add(
        user_id=USER_ID,
        session_id="qs_complete",
        messages=[{"role": "user", "timestamp": now_ms + 5000,
                   "content": "Anyway, let's talk about something else now."}],
    )

    print("2. Waiting for indexing…")
    time.sleep(5)

    print("3. Searching memories…")
    resp = memories.search(
        filters={"user_id": USER_ID},
        query="outdoor activities bob enjoys",
        method="hybrid",
        top_k=5,
    )
    episodes = resp.data.episodes if resp.data else []
    print(f"Found {len(episodes)} memories:")
    for ep in episodes:
        print(f"  score={getattr(ep, 'score', '?')}  content={_ep_text(ep)[:80]}")
    print("PASS")


if __name__ == "__main__":
    test_step1_store_conversation()
    test_step2_trigger_boundary()
    test_step3_search_memory()
    test_complete_script()
    print("\n✅ All quickstart cases passed")
