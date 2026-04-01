# pip install evermemos
# Getting Started — Save memories (v1 SDK)

import time
from evermemos import EverMemOS

client = EverMemOS(api_key="evermemos_api_key")
memories = client.v1.memories

now_ms = int(time.time() * 1000)

response = memories.add(
    user_id="user_demo_001",
    session_id="session_gs_001",
    messages=[
        {
            "role": "user",
            "timestamp": now_ms,
            "content": "I like black Americano, no sugar, the stronger the better!",
        },
        {
            "role": "user",
            "timestamp": now_ms + 86_400_000,  # 1 day later
            "content": "Today I want to discuss the project progress.",
        },
    ],
)
print(f"status={response.data.status}  task_id={response.data.task_id}")
