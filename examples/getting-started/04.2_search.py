# pip install everos
# Getting Started — Search memories (v1 SDK)

from everos import EverOS

client = EverOS(api_key="everos_api_key")
memories = client.v1.memories

response = memories.search(
    filters={"user_id": "user_demo_001"},
    query="coffee preference",
    method="vector",
    top_k=5,
)

episodes = response.data.episodes if response.data else []
print(f"Found {len(episodes)} memories")
