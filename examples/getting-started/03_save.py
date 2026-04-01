# pip install evermemos
# Getting Started — 写入记忆（v1 SDK）
# 对应 v0: getting-started/03-save.py

import time
from evermemos import EverMemOS

client = EverMemOS()  # 自动读取 EVERMEMOS_API_KEY 环境变量
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
            "timestamp": now_ms + 60_000,
            "content": "Today I want to discuss the project progress.",
        },
    ],
)
print(f"status={response.data.status}  task_id={response.data.task_id}")

# 可选：显式触发会话边界（等价于 v0 的 flush=True）
memories.flush(user_id="user_demo_001", session_id="session_gs_001")
print("flush done")
