from evermemos import EverMemOS

memory = EverMemOS(api_key="evermemos_api_key").v0.memories

response = memory.get(
    extra_query={"user_id": "user_demo_001"}
)

memories = response.result.memories
print(f"Fetched {len(memories) if memories else 0} memories")