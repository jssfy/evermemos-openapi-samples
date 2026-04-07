from everos import EverOS

memory = EverOS(api_key="everos_api_key").v1.memories

# v1: filters DSL replaces extra_query; response.data.episodes replaces response.result.memories
response = memory.get(
    filters={"user_id": "user_demo_001"},
    memory_type="episodic_memory",
)

episodes = response.data.episodes if response.data else []
print(f"Fetched {len(episodes) if episodes else 0} memories")
