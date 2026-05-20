import time
import requests

# Configuration
BASE_URL = "https://api.evermind.ai"
headers = {
    "Content-Type": "application/json",
    # "Authorization": "Bearer your_api_key",  # set EVEROS_API_KEY in env or pass here
}


def store_messages(user_id, session_id, messages):
    """Store a list of messages for a user session."""
    payload = {
        "user_id": user_id,
        "session_id": session_id,
        "messages": messages,
    }
    response = requests.post(f"{BASE_URL}/api/v1/memories", json=payload, headers=headers)
    return response.json()


def flush_session(user_id, session_id):
    """Flush a session to trigger immediate memory extraction."""
    payload = {"user_id": user_id, "session_id": session_id}
    response = requests.post(f"{BASE_URL}/api/v1/memories/flush", json=payload, headers=headers)
    return response.json()


def search_memories(user_id, query, method="hybrid", top_k=5):
    """Search for memories by user."""
    payload = {
        "filters": {"user_id": user_id},
        "query": query,
        "method": method,
        "top_k": top_k,
        "memory_types": ["episodic_memory", "profile"],
    }
    response = requests.post(f"{BASE_URL}/api/v1/memories/search", json=payload, headers=headers)
    return response.json()


now_ms = int(time.time() * 1000)

# Main flow
print("1. Storing conversation...")
store_messages(
    user_id="user_bob",
    session_id="demo_001",
    messages=[
        {"role": "user", "timestamp": now_ms, "content": "I love hiking on weekends, especially in the mountains."},
        {"role": "assistant", "timestamp": now_ms + 500, "content": "That sounds amazing! Do you have a favorite trail?"},
        {"role": "user", "timestamp": now_ms + 1000, "content": "Yes, the mountain trails near the lake are my favorite."},
    ],
)

print("2. Triggering memory extraction...")
flush_session("user_bob", "demo_001")
time.sleep(5)

print("3. Searching memories...")
result = search_memories("user_bob", "outdoor activities bob enjoys")

data = result.get("data", {})
episodes = data.get("episodes", [])
profiles = data.get("profiles", [])
print(f"\nFound {len(episodes)} episodic memories and {len(profiles)} profiles:")
for ep in episodes:
    content = ep.get("episode") or ep.get("summary") or "N/A"
    print(f"  Type: episodic_memory")
    print(f"  Content: {str(content)[:100]}...")
    print(f"  Score: {ep.get('score')}")
    print("-" * 40)
