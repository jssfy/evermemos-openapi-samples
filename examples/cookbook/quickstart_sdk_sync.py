# pip install everos -U
# SDK version of https://docs.evermind.ai/cookbook/quickstart (Steps 1-3), v1 sync
import time

from everos import EverOS

client = EverOS()
memories = client.v1.memories

# ── Step 1: Store a Conversation ──────────────────────────────────────────────

now_ms = int(time.time() * 1000)

response = memories.add(
    user_id="user_alice",
    session_id="demo_conversation_001",
    messages=[
        {
            "role": "user",
            "timestamp": now_ms,
            "content": "I prefer working in the morning, usually from 6am to 10am. That's when I'm most productive.",
        }
    ],
)

print(response)

# ── Step 2: Trigger Memory Extraction ────────────────────────────────────────

# Flush the session to immediately trigger boundary detection and memory extraction
print("Flushing session to trigger memory extraction...")
memories.flush(user_id="user_alice", session_id="demo_conversation_001")

# Wait briefly for extraction to complete
time.sleep(5)

# ── Step 3: Search Your Memory ────────────────────────────────────────────────

response = memories.search(
    filters={"user_id": "user_alice"},
    query="when does alice prefer to work",
    method="hybrid",
    top_k=5,
    memory_types=["episodic_memory", "profile"],
)

data = response.data
episodes = data.episodes or [] if data else []
profiles = data.profiles or [] if data else []

print(f"Found {len(episodes)} episodic memories and {len(profiles)} profiles:\n")
for ep in episodes:
    print(f"Type: episodic_memory")
    print(f"Content: {ep.episode or ep.summary or 'N/A'}")
    print(f"Score: {ep.score}")
    print("-" * 40)
for prof in profiles:
    print(f"Type: profile")
    print(f"Score: {prof.score}")
    print("-" * 40)
