# everos should've been installed:
# pip install https://pkg.stainless.com/s/everos-trial-python/ea677a49282be2c1723740b1a7fa943cc01e0d5a/everos-0.0.1-py3-none-any.whl
#
# Complete quickstart: store → wait → search → feedback
# Migration from old v1:
#   - client.v1.memories.group.add() → client.v1.memory.add(owner_id=..., owner_type=..., session_id=...)
import time
from everos import EverOS

client = EverOS()
memory = client.v1.memory

now_ms = int(time.time() * 1000)

# 1. Storing conversation...
print("1. Storing conversation...")

memory.add(
    owner_id="user_bob",
    owner_type="user",
    session_id="demo_complete_001",
    messages=[
        {
            "role": "user",
            "name": "Bob",
            "timestamp": now_ms,
            "content": "I love hiking on weekends, especially in the mountains.",
        }
    ],
)

memory.add(
    owner_id="user_bob",
    owner_type="user",
    session_id="demo_complete_001",
    messages=[
        {
            "role": "user",
            "name": "Bob",
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

response = client.v1.memory.search(
    owner_id="user_bob",
    owner_type="user",
    query="outdoor activities bob enjoys",
    method="hybrid",
    include_profile=True,
    top_k=5,
)

data = response.data
episodes = data.episodes if data else []

print(f"\nFound {len(episodes)} memories:")
for ep in episodes:
    print(f"Content: {getattr(ep, 'episode', None) or getattr(ep, 'summary', 'N/A')}")
    print(f"Score: {getattr(ep, 'score', 'N/A')}")
    print("-" * 40)

# 4. Submit feedback to correct a memory (if any episodes found)
if episodes:
    first_ep = episodes[0]
    memory_id = getattr(first_ep, 'id', None)
    if memory_id:
        print(f"\n4. Submitting feedback on memory {memory_id}...")
        fb = client.v1.memory.feedback(
            memory_id=memory_id,
            memory_type="episodic_memory",
            content="Bob also enjoys cycling, not just hiking.",
            owner_id="user_bob",
            owner_type="user",
        )
        print(f"Feedback result: record_id={fb.data.record_id if fb.data else None}")
