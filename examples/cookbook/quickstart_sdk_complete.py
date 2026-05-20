# pip install everos -U
# SDK version of https://docs.evermind.ai/cookbook/quickstart "Complete Working Script", v1
import time

from everos import EverOS

client = EverOS()
memories = client.v1.memories

now_ms = int(time.time() * 1000)

# 1. Storing conversation...
print("1. Storing conversation...")

memories.add(
    user_id="user_bob",
    session_id="demo_001",
    messages=[
        {
            "role": "user",
            "timestamp": now_ms,
            "content": "I love hiking on weekends, especially in the mountains.",
        },
        {
            "role": "assistant",
            "timestamp": now_ms + 500,
            "content": "That sounds amazing! Do you have a favorite trail?",
        },
        {
            "role": "user",
            "timestamp": now_ms + 1000,
            "content": "Yes, the mountain trails near the lake are my favorite.",
        },
    ],
)

# 2. Triggering memory extraction...
print("2. Triggering memory extraction...")
memories.flush(user_id="user_bob", session_id="demo_001")
time.sleep(5)

# 3. Searching memories...
print("3. Searching memories...")

response = memories.search(
    filters={"user_id": "user_bob"},
    query="outdoor activities bob enjoys",
    method="hybrid",
    top_k=5,
    memory_types=["episodic_memory", "profile"],
)

data = response.data
episodes = data.episodes or [] if data else []
profiles = data.profiles or [] if data else []

print(f"\nFound {len(episodes)} episodic memories and {len(profiles)} profiles:")
for ep in episodes:
    print(f"Type: episodic_memory")
    print(f"Content: {ep.episode or ep.summary or 'N/A'}")
    print(f"Score: {ep.score}")
    print("-" * 40)
for prof in profiles:
    print(f"Type: profile")
    print(f"Score: {prof.score}")
    print("-" * 40)
