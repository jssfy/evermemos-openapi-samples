from evermemos import EverMemOS

memory = EverMemOS(api_key="evermemos_api_key").v0.memories

response = memory.search(
    extra_query={
        "user_id": "user_demo_001",
        "query": "coffee preference"
    }
)

total = response.result.total_count
print(f"Found {total} memories")