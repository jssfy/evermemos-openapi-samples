# EverMemOS should've been installed (pip install evermemos -U)
# SDK version of https://docs.evermind.ai/cookbook/quickstart (Steps 1-3)
import time
from datetime import datetime, timezone

from evermemos import EverMemOS

memories = EverMemOS().v0.memories

# ── Step 1: Store a Conversation ──────────────────────────────────────────────

response = memories.add(
    group_id="demo_conversation_001",
    group_name="Demo Conversation",
    message_id="msg_001",
    create_time=datetime.now(timezone.utc).isoformat(),
    sender="user_alice",
    sender_name="Alice",
    content="I prefer working in the morning, usually from 6am to 10am. That's when I'm most productive.",
)

print(response.to_json())

# ── Step 2: Wait for Indexing ─────────────────────────────────────────────────

# Send a second message to trigger boundary detection
response = memories.add(
    group_id="demo_conversation_001",
    group_name="Demo Conversation",
    message_id="msg_002",
    create_time=datetime.now(timezone.utc).isoformat(),
    sender="user_alice",
    sender_name="Alice",
    content="Let's switch topics - what's the weather like today?",
)

# Wait for processing
print("Waiting for memory extraction...")
time.sleep(5)

# ── Step 3: Search Your Memory ────────────────────────────────────────────────

response = memories.search(
    extra_query={
        "user_id": "user_alice",
        "query": "when does alice prefer to work",
        "retrieve_method": "hybrid",
        "top_k": 5,
        "memory_types": ["episodic_memory", "profile_memory"],
    },
)

result = response.result
memory_list = result.memories if result else []

print(f"Found {len(memory_list)} relevant memories:\n")
for mem in memory_list:
    print(f"Type: {mem.memory_type}")
    print(f"Content: {getattr(mem, 'episode', None) or getattr(mem, 'summary', 'N/A')}")
    print(f"Score: {getattr(mem, 'score', 'N/A')}")
    print("-" * 40)
