# Your First Memory in 5 Minutes (Python SDK v1)

Get EverMemOS working in under 5 minutes using the v1 Python SDK. By the end of this guide, you'll store a conversation, trigger memory extraction, and search for it.

## Prerequisites

- Python 3.9+
- `everos` SDK (`pip install everos -U`)
- Set your API key: `export EVEROS_API_KEY="your_api_key"`

## Step 1: Store a Conversation

Store a conversation using the `messages` array format. Each message has a `role`, `timestamp` (Unix milliseconds), and `content`.

```python
import time
from everos import EverOS

client = EverOS()
memories = client.v1.memories

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
```

**Expected output:**

```
data=AddMemoryResponse(status='accumulated', task_id='...') ...
```

## Step 2: Trigger Memory Extraction

EverMemOS extracts memories at session boundaries. Call `flush()` to explicitly mark a session as complete and trigger immediate extraction.

```python
# Flush the session to trigger memory extraction
print("Flushing session to trigger memory extraction...")
memories.flush(user_id="user_alice", session_id="demo_conversation_001")

# Wait briefly for async extraction to complete
import time
time.sleep(5)
```

> **Tip:** Without `flush()`, extraction happens automatically when EverMemOS detects a topic change or time gap. `flush()` gives you explicit control over when extraction runs.

## Step 3: Search Your Memory

Search for the preference you stored using semantic or keyword search.

```python
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
```

**Expected output:**

```
Found 1 episodic memories and 0 profiles:
Type: episodic_memory
Content: Alice prefers working in the morning, from 6am to 10am when she is most productive.
Score: 0.85
----------------------------------------
```

## Complete Working Script

Here's the full script you can copy and run:

```python
# pip install everos -U
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
```

**Expected output:**

```
1. Storing conversation...
2. Triggering memory extraction...
3. Searching memories...

Found 1 episodic memories and 0 profiles:
Type: episodic_memory
Content: Bob loves hiking on weekends, especially in the mountains, and the mountain trails near the lake are his favorite.
Score: 0.77
----------------------------------------
```

## Key Differences from v0

| Feature | v0 SDK | v1 SDK |
|---------|--------|--------|
| Package | `evermemos` | `everos` |
| API key env | `EVERMEMOS_API_KEY` | `EVEROS_API_KEY` |
| Client entry | `EverMemOS().v0.memories` | `EverOS().v1.memories` |
| Message format | Single flat params | `messages=[{role, timestamp, content}]` |
| Boundary trigger | Send a topic-change message | `memories.flush(user_id, session_id)` |
| Search params | `extra_query={}` dict | Typed params: `filters`, `query`, `method` |
| Search methods | `hybrid / vector / keyword / agentic` | `hybrid / vector / keyword / agentic` |
| Memory types | `episodic_memory / profile_memory` | `episodic_memory / profile` |
