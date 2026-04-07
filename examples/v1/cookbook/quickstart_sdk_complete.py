# everos should've been installed (pip install everos -U)
# SDK version of https://docs.evermind.ai/cookbook/quickstart "Complete Working Script"
# Migration notes from v0:
#   - Group conversations → client.v1.memories.group.add()
#   - response.result.memories → response.data.episodes
import time
from everos import EverOS

client = EverOS()
group_mem = client.v1.memories.group

now_ms = int(time.time() * 1000)

# 1. Storing conversation...
print("1. Storing conversation...")

group_mem.add(
    group_id="demo_001",
    group_meta={"name": "Cookbook Demo"},
    messages=[
        {
            "role": "user",
            "sender_id": "user_bob",
            "sender_name": "Bob",
            "timestamp": now_ms,
            "content": "I love hiking on weekends, especially in the mountains.",
        }
    ],
)

group_mem.add(
    group_id="demo_001",
    group_meta={"name": "Cookbook Demo"},
    messages=[
        {
            "role": "user",
            "sender_id": "user_bob",
            "sender_name": "Bob",
            "timestamp": now_ms + 5000,
            "content": "Anyway, let's talk about something else now.",
        }
    ],
)

# 2. Waiting for indexing...
print("2. Waiting for indexing...")
time.sleep(5)

# 3. Searching memories...
print("3. Searching memories...")

response = client.v1.memories.search(
    filters={"user_id": "user_bob"},
    query="outdoor activities bob enjoys",
    method="hybrid",
    top_k=5,
    memory_types=["episodic_memory", "profile"],
)

data = response.data
episodes = data.episodes if data else []

print(f"\nFound {len(episodes)} memories:")
for ep in episodes:
    print(f"Type: {getattr(ep, 'memory_type', 'N/A')}")
    print(f"Content: {getattr(ep, 'episode', None) or getattr(ep, 'summary', 'N/A')}")
    print(f"Score: {getattr(ep, 'score', 'N/A')}")
    print("-" * 40)
