# pip install evermemos
# 群组记忆：写入 + flush（每条消息必须带 sender_id）
import time
from pprint import pprint
from evermemos import EverMemOS

client = EverMemOS()
group_mem = client.v1.memories.group

GROUP_ID = "group_demo_001"
now_ms = int(time.time() * 1000)

# --- 1. 写入群组对话 ---
print("=== group add ===")
resp = group_mem.add(
    group_id=GROUP_ID,
    group_meta={"name": "Cookbook Demo", "description": "Multi-participant demo"},
    messages=[
        {
            "role": "user",
            "sender_id": "user_alice",
            "sender_name": "Alice",
            "timestamp": now_ms,
            "content": "Hey team, what's our plan for the weekend trip?",
            "message_id": "msg_001",
        },
        {
            "role": "user",
            "sender_id": "user_bob",
            "sender_name": "Bob",
            "timestamp": now_ms + 5000,
            "content": "I'd love to go hiking in the mountains again.",
            "message_id": "msg_002",
        },
        {
            "role": "user",
            "sender_id": "user_alice",
            "sender_name": "Alice",
            "timestamp": now_ms + 10000,
            "content": "Sounds great! Let's decide on a trail.",
            "message_id": "msg_003",
        },
    ],
)
pprint(resp)

# --- 2. 异步写入（async_mode=True）---
print("\n=== group add (async) ===")
resp = group_mem.add(
    group_id=GROUP_ID,
    async_mode=True,
    messages=[
        {
            "role": "user",
            "sender_id": "user_carol",
            "sender_name": "Carol",
            "timestamp": now_ms + 20000,
            "content": "I prefer the lakeside trail, it's more scenic.",
        },
    ],
)
pprint(resp)
# 如需轮询 task_id，参考 02_add_async.py

# --- 3. flush（触发群组会话边界提取）---
print("\n=== group flush ===")
resp = group_mem.flush(group_id=GROUP_ID)
pprint(resp)
