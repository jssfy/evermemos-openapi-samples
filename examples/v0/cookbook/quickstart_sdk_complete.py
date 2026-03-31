# EverMemOS should've been installed (pip install evermemos -U)
# SDK version of https://docs.evermind.ai/cookbook/quickstart "Complete Working Script"
import time
from datetime import datetime, timezone

from evermemos import EverMemOS

memories = EverMemOS().v0.memories

# 1. Storing conversation...
print("1. Storing conversation...")

memories.add(
    group_id="demo_001",
    group_name="Cookbook Demo",
    message_id="msg_1",
    create_time=datetime.now(timezone.utc).isoformat(),
    sender="user_bob",
    sender_name="Bob",
    content="I love hiking on weekends, especially in the mountains.",
)

memories.add(
    group_id="demo_001",
    group_name="Cookbook Demo",
    message_id="msg_2",
    create_time=datetime.now(timezone.utc).isoformat(),
    sender="user_bob",
    sender_name="Bob",
    content="Anyway, let's talk about something else now.",
)

# 2. Waiting for indexing...
print("2. Waiting for indexing...")
time.sleep(5)

# 3. Searching memories...
print("3. Searching memories...")

response = memories.search(
    extra_query={
        "user_id": "user_bob",
        "query": "outdoor activities bob enjoys",
        "retrieve_method": "hybrid",
        "top_k": 5,
        "memory_types": ["episodic_memory", "profile_memory"],
    },
)

result = response.result
memory_list = result.memories if result else []

print(f"\nFound {len(memory_list)} memories:")
for mem in memory_list:
    print(f"Type: {mem.memory_type}")
    print(f"Content: {getattr(mem, 'episode', None) or getattr(mem, 'summary', 'N/A')}")
    print(f"Score: {getattr(mem, 'score', 'N/A')}")
    print("-" * 40)
