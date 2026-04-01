# pip install evermemos
# Getting Started — Get memories (v1 SDK)

from evermemos import EverMemOS

client = EverMemOS(api_key="evermemos_api_key")
memories = client.v1.memories

response = memories.get(
    filters={"user_id": "user_demo_001"},
    memory_type="episodic_memory",
)

episodes = response.data.episodes if response.data else []
print(f"Fetched {len(episodes) if episodes else 0} memories")
