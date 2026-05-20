# everos should've been installed:
# pip install https://pkg.stainless.com/s/everos-trial-python/ea677a49282be2c1723740b1a7fa943cc01e0d5a/everos-0.0.1-py3-none-any.whl
#
# Migration from old v1:
#   - client.v1.memories.group.add() → client.v1.memory.add(owner_id=..., owner_type="user", session_id=...)
#   - group_id becomes session_id; group_meta no longer needed
#   - sender_id/sender_name inside message still supported via name= field
import time
from everos import EverOS

client = EverOS()
memory = client.v1.memory

now_ms = int(time.time() * 1000)

# ── Step 1: Store a Conversation ──────────────────────────────────────────────
memory.add(
    owner_id="user_alice",
    owner_type="user",
    session_id="demo_conversation_001",
    messages=[
        {
            "role": "user",
            "name": "Alice",
            "timestamp": now_ms,
            "content": "I prefer working in the morning, usually from 6am to 10am. That's when I'm most productive.",
        }
    ],
)

# ── Step 2: Send another message (triggers boundary detection) ────────────────
memory.add(
    owner_id="user_alice",
    owner_type="user",
    session_id="demo_conversation_001",
    messages=[
        {
            "role": "user",
            "name": "Alice",
            "timestamp": now_ms + 5000,
            "content": "Let's switch topics - what's the weather like today?",
        }
    ],
)

# ── Step 3: Wait for Indexing ─────────────────────────────────────────────────
print("Waiting for memory extraction...")
time.sleep(5)

# ── Step 4: Search Your Memory ────────────────────────────────────────────────
response = client.v1.memory.search(
    owner_id="user_alice",
    owner_type="user",
    query="when does alice prefer to work",
    method="hybrid",
    include_profile=True,
    top_k=5,
)

data = response.data
episodes = data.episodes if data else []

print(f"Found {len(episodes)} relevant memories:\n")
for ep in episodes:
    print(f"Content: {getattr(ep, 'episode', None) or getattr(ep, 'summary', 'N/A')}")
    print(f"Score: {getattr(ep, 'score', 'N/A')}")
    print("-" * 40)
