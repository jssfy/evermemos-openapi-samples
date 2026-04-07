from everos import EverOS

memory = EverOS(api_key="everos_api_key").v1.memories

# v1: filters DSL + explicit query; response.data.episodes replaces response.result.memories
# NOTE: v1 search response does not expose total_count; use len(episodes) instead.
response = memory.search(
    filters={"user_id": "user_demo_001"},
    query="coffee preference",
)

episodes = response.data.episodes if response.data else []
print(f"Found {len(episodes) if episodes else 0} memories")
