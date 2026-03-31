# Your First Memory in 5 Minutes (Python SDK)

Get EverMemOS working in under 5 minutes using the Python SDK. By the end of this guide, you'll store a conversation, wait for indexing, and search for it.

## Prerequisites

- Python 3.9+
- `evermemos` SDK (`pip install evermemos -U`)
- Set your API key: `export EVERMEMOS_API_KEY="your_api_key"`

## Step 1: Store a Conversation

Store a simple conversation message containing a user preference.

```python
from datetime import datetime, timezone
from evermemos import EverMemOS

memories = EverMemOS().v0.memories

# Store a message
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
```

**Expected output:**

```json
{
  "status": "queued",
  "message": "Message accepted and queued for processing",
  "request_id": "02177034845390800000000000000000000ffff..."
}
```

## Step 2: Wait for Indexing

EverMemOS processes messages asynchronously. Memory extraction happens when:

- A conversation boundary is detected (topic change, time gap)
- Enough context accumulates for meaningful extraction

```python
import time

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

# Wait for indexing
print("Waiting for memory extraction...")
time.sleep(5)
```

## Step 3: Search Your Memory

Now search for the preference you stored.

```python
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
```

**Expected output:**

```
Found 1 relevant memories:

Type: episodic_memory
Content: Alice prefers working in the morning, from 6am to 10am when she is most productive.
Score: 0.85
----------------------------------------
```

## Complete Working Script

Here's the full script you can copy and run:

```python
# EverMemOS should've been installed (pip install evermemos -U)
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
```

**Expected output:**

```
1. Storing conversation...
2. Waiting for indexing...
3. Searching memories...

Found 1 memories:
Type: episodic_memory
Content: Bob loves hiking on weekends, especially in the mountains.
Score: 0.82
----------------------------------------
```
