# everos should've been installed (pip install everos -U)
# SDK version of https://docs.evermind.ai/cookbook/quickstart (Steps 1-3)
# Migration notes from v0:
#   - Group conversations → client.v1.memories.group.add()
#   - group_name + description → group_meta={"name": ..., "description": ...}
#   - sender + sender_name → sender_id + sender_name inside each message
#   - create_time (ISO) → timestamp (unix ms)
#   - response.result.memories → response.data.episodes
import time
from everos import EverOS

client = EverOS()
group_mem = client.v1.memories.group

now_ms = int(time.time() * 1000)

# ── Step 1: Store a Conversation ──────────────────────────────────────────────

group_mem.add(
    group_id="demo_conversation_001",
    group_meta={"name": "Demo Conversation"},
    messages=[
        {
            "role": "user",
            "sender_id": "user_alice",
            "sender_name": "Alice",
            "timestamp": now_ms,
            "content": "I prefer working in the morning, usually from 6am to 10am. That's when I'm most productive.",
        }
    ],
)

# ── Step 2: Wait for Indexing ─────────────────────────────────────────────────

# Send a second message to trigger boundary detection
group_mem.add(
    group_id="demo_conversation_001",
    group_meta={"name": "Demo Conversation"},
    messages=[
        {
            "role": "user",
            "sender_id": "user_alice",
            "sender_name": "Alice",
            "timestamp": now_ms + 5000,
            "content": "Let's switch topics - what's the weather like today?",
        }
    ],
)

# Wait for processing
print("Waiting for memory extraction...")
time.sleep(5)

# ── Step 3: Search Your Memory ────────────────────────────────────────────────

response = client.v1.memories.search(
    filters={"user_id": "user_alice"},
    query="when does alice prefer to work",
    method="hybrid",
    top_k=5,
    memory_types=["episodic_memory", "profile"],
)

data = response.data
episodes = data.episodes if data else []

print(f"Found {len(episodes)} relevant memories:\n")
for ep in episodes:
    print(f"Type: {getattr(ep, 'memory_type', 'N/A')}")
    print(f"Content: {getattr(ep, 'episode', None) or getattr(ep, 'summary', 'N/A')}")
    print(f"Score: {getattr(ep, 'score', 'N/A')}")
    print("-" * 40)
