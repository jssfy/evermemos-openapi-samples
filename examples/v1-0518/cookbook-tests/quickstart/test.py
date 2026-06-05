"""
Cookbook: Your First Memory in 5 Minutes
SDK: everos (new v1 SDK)
ENV: EVEROS_API_KEY_DEV + dev-gateway
"""
import os
import time
from everos import EverOS

BASE_URL = os.environ.get("EVEROS_BASE_URL", "https://dev-gateway.aws.evermind.ai")
API_KEY  = os.environ.get("EVEROS_API_KEY", "")

client  = EverOS(api_key=API_KEY, base_url=BASE_URL)
memory  = client.memory

OWNER_ID   = "cookbook_qs_user"
OWNER_TYPE = "user"


def _ep_text(ep) -> str:
    return getattr(ep, "episode", None) or getattr(ep, "summary", "") or ""


# ── Case 1: Store a conversation ──────────────────────────────────────────
def test_step1_store_conversation():
    print("\n=== Case 1: Store a conversation ===")
    resp = memory.add(
        owner_id=OWNER_ID, owner_type=OWNER_TYPE,
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


# ── Case 2: Trigger boundary detection ────────────────────────────────────
def test_step2_trigger_boundary():
    print("\n=== Case 2: Trigger boundary detection ===")
    resp = memory.add(
        owner_id=OWNER_ID, owner_type=OWNER_TYPE,
        session_id="qs_session",
        messages=[{
            "role": "user",
            "timestamp": int(time.time() * 1000),
            "content": "Let's switch topics - what's the weather like today?",
        }],
    )
    assert resp.data is not None
    print("Waiting 5s for indexing…")
    time.sleep(5)
    print("PASS")


# ── Case 3: Search memory ─────────────────────────────────────────────────
def test_step3_search_memory():
    print("\n=== Case 3: Search memory ===")
    resp = memory.search(
        owner_id=OWNER_ID, owner_type=OWNER_TYPE,
        query="when does alice prefer to work",
        method="hybrid", top_k=5,
    )
    episodes = resp.data.episodes or [] if resp.data else []
    print(f"Found {len(episodes)} episodes")
    for ep in episodes:
        print(f"  score={getattr(ep, 'score', '?')}  {_ep_text(ep)[:80]}")
    print("PASS")


# ── Case 4: Complete working script ───────────────────────────────────────
def test_complete_script():
    print("\n=== Case 4: Complete working script ===")
    now_ms = int(time.time() * 1000)
    memory.add(
        owner_id=OWNER_ID, owner_type=OWNER_TYPE, session_id="qs_complete",
        messages=[{"role": "user", "timestamp": now_ms,
                   "content": "I love hiking on weekends, especially in the mountains."}],
    )
    memory.add(
        owner_id=OWNER_ID, owner_type=OWNER_TYPE, session_id="qs_complete",
        messages=[{"role": "user", "timestamp": now_ms + 5000,
                   "content": "Anyway, let's talk about something else now."}],
    )
    print("Waiting 5s…")
    time.sleep(5)
    resp = memory.search(
        owner_id=OWNER_ID, owner_type=OWNER_TYPE,
        query="outdoor activities", method="hybrid", top_k=5,
    )
    episodes = resp.data.episodes or [] if resp.data else []
    print(f"Found {len(episodes)} memories")
    for ep in episodes:
        print(f"  {_ep_text(ep)[:80]}")
    print("PASS")


if __name__ == "__main__":
    assert API_KEY, "Set EVEROS_API_KEY env var"
    test_step1_store_conversation()
    test_step2_trigger_boundary()
    test_step3_search_memory()
    test_complete_script()
    print("\n✅ All quickstart cases passed")
