import requests
import time
from datetime import datetime

# Configuration
BASE_URL = "https://api.evermind.ai"
headers = {"Content-Type": "application/json"}

def store_message(group_id, message_id, sender, content):
    """Store a single message."""
    message = {
        "group_id": group_id,
        "group_name": "Cookbook Demo",
        "message_id": message_id,
        "create_time": datetime.now().isoformat() + "Z",
        "sender": sender,
        "sender_name": sender.replace("user_", "").title(),
        "content": content
    }
    response = requests.post(f"{BASE_URL}/api/v0/memories", json=message, headers=headers)
    return response.json()

def search_memories(user_id, query):
    """Search for memories."""
    search_params = {
        "user_id": user_id,
        "query": query,
        "retrieve_method": "hybrid",
        "top_k": 5,
        "memory_types": ["episodic_memory", "profile_memory"]
    }
    response = requests.get(f"{BASE_URL}/api/v0/memories/search", json=search_params, headers=headers)
    return response.json()

# Main flow
print("1. Storing conversation...")
store_message("demo_001", "msg_1", "user_bob", "I love hiking on weekends, especially in the mountains.")
store_message("demo_001", "msg_2", "user_bob", "Anyway, let's talk about something else now.")

print("2. Waiting for processing...")
time.sleep(5)

print("3. Searching memories...")
result = search_memories("user_bob", "outdoor activities bob enjoys")

memories = result.get("result", {}).get("memories", [])
print(f"\nFound {len(memories)} memories:")
for mem in memories:
    print(f"  - {mem.get('memory_content', 'N/A')[:100]}...")