# Install the everos python sdk
# bash command: pip install everos

from everos import EverOS

memory = EverOS(api_key="everos_api_key").v1.memories

# v1 add() accepts a batch of messages in one call.
# create_time (ISO string) → timestamp (unix milliseconds)
# sender → user_id (top-level) + role inside each message
# flush=True param is removed; memory extraction is automatic.
response = memory.add(
    user_id="user_demo_001",
    messages=[
        {
            "role": "user",
            "timestamp": 1736935200000,  # 2025-01-15T10:00:00Z
            "content": "I like black Americano, no sugar, the stronger the better!",
        },
        {
            "role": "user",
            "timestamp": 1737021660000,  # 2025-01-16T10:01:00Z
            "content": "Today I want to discuss the project progress.",
        },
    ],
)
print(f"Status: {response.data.status}, Task ID: {response.data.task_id}")
