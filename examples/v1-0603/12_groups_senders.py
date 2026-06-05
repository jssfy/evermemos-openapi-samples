#!/usr/bin/env python3
"""
12_groups_senders.py — group / sender 管理

Groups：多用户共享记忆的命名空间
Senders：消息发送者身份注册

流程：create group → create sender → add group memory → get group memory
"""
import os, time
from everos_cloud import EverOS

API_KEY  = os.getenv("EVEROS_API_KEY",  "ddcf3ffb-df31-4c9c-9d30-fb2ee67aed26")
BASE_URL = os.getenv("EVER_OS_BASE_URL", "https://dev-gateway.aws.evermind.ai")

client = EverOS(api_key=API_KEY, base_url=BASE_URL)
ts = int(time.time())
GROUP_ID  = f"group-demo-{ts}"
SENDER_ID = f"sender-demo-{ts}"
USER_ID   = f"user-group-{ts}"

# ── 1. 创建 group ──────────────────────────────────────────────
print("=== create group ===")
g = client.v1.groups.create(group_id=GROUP_ID, name="Demo Group", description="SDK example group")
print(g)

# ── 2. 查询 group ──────────────────────────────────────────────
print("\n=== retrieve group ===")
g = client.v1.groups.retrieve(GROUP_ID)
print(g)

# ── 3. 创建 sender ─────────────────────────────────────────────
print("\n=== create sender ===")
s = client.v1.senders.create(sender_id=SENDER_ID, name="Alice")
print(s)

# ── 4. group memories: add ────────────────────────────────────
# GroupMessageItemParam 必填：role / sender_id / timestamp / content
print("\n=== group memories add ===")
now_ms = int(time.time() * 1000)
resp = client.v1.memories.group.add(
    group_id=GROUP_ID,
    messages=[
        {"role": "user",      "sender_id": SENDER_ID, "timestamp": now_ms,
         "content": [{"type": "text", "text": "大家好，今天我们讨论一下项目的技术选型。"}]},
        {"role": "assistant", "sender_id": "bot",      "timestamp": now_ms + 500,
         "content": [{"type": "text", "text": "好的，可以从性能、社区活跃度和学习成本三个维度来评估。"}]},
    ],
)
print(resp)

# ── 5. group memories: flush ──────────────────────────────────
print("\n=== group memories flush ===")
flush = client.v1.memories.group.flush(group_id=GROUP_ID)
print(flush)
