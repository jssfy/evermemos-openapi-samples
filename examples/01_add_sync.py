# pip install everos (from EverOS-python SDK)
# 同步写入个人记忆 —— 对应旧版 add_sync.py
import time
from everos import EverOS

client = EverOS()
memories = client.v1.memories

# --- 单次写入（同步，立即提取）---
response = memories.add(
    user_id="user_010",
    messages=[
        {
            "role": "user",
            "timestamp": int(time.time() * 1000),
            "content": "I went to the dentist today. I was scared of the dentist.",
        }
    ],
)
print(response)

response = memories.add(
    user_id="user_010",
    messages=[
        {
            "role": "user",
            "timestamp": int(time.time() * 1000),
            "content": "I admire the beauty of the sea.",
        }
    ],
)
print(response)
