#!/usr/bin/env python3
"""
04_delete_flush.py — delete 指定用户记忆 / flush session 缓冲

delete：按 user_id / session_id / memory_id 精确删除
flush：把 session 缓冲中尚未处理的消息强制落库
"""
import os, time
from everos_cloud import EverOS

API_KEY  = os.getenv("EVEROS_API_KEY", "ddcf3ffb-df31-4c9c-9d30-fb2ee67aed26")
BASE_URL = os.getenv("EVER_OS_BASE_URL", "https://dev-gateway.aws.evermind.ai")
USER_ID  = "everos-cloud-example-delete-001"
SESSION  = f"session-flush-{int(time.time())}"

client = EverOS(api_key=API_KEY, base_url=BASE_URL)

# 1. 先写入一条
client.v1.memories.add(
    user_id=USER_ID,
    session_id=SESSION,
    messages=[{"role": "user", "timestamp": int(time.time() * 1000), "content": [{"type": "text", "text": "temp message for flush/delete test"}]}],
)
print("add done")

# 2. flush session 缓冲
flush_resp = client.v1.memories.flush(user_id=USER_ID, session_id=SESSION)
print("flush:", flush_resp)

# 3. delete 该用户的所有记忆
client.v1.memories.delete(user_id=USER_ID)
print("delete done (no response body)")
