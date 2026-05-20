# Install the everos python sdk:
# pip install https://pkg.stainless.com/s/everos-trial-python/ea677a49282be2c1723740b1a7fa943cc01e0d5a/everos-0.0.1-py3-none-any.whl
#
# Migration from old v1:
#   - EverOS().v1.memories  → EverOS().v1.memory
#   - add(user_id=...)      → add(owner_id=..., owner_type="user", session_id=...)
#   - response.data.task_id removed; use response.data.status / message_count

from everos import EverOS

memory = EverOS().v1.memory  # reads EVEROS_API_KEY + EVER_OS_BASE_URL from env

response = memory.add(
    owner_id="user_demo_001",
    owner_type="user",
    session_id="session_getting_started",
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
print(f"Status: {response.data.status}, Message count: {response.data.message_count}")
