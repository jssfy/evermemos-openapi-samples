#!/usr/bin/env python3
"""
01_add_sync.py — 同步 add 记忆

包：everos_cloud（pip install everos-cloud）
环境：dev  https://dev-gateway.aws.evermind.ai

EVEROS_API_KEY 读取 ~/.env 或直接传入 client。
"""
import os, time
from everos_cloud import EverOS

API_KEY  = os.getenv("EVEROS_API_KEY", "ddcf3ffb-df31-4c9c-9d30-fb2ee67aed26")
BASE_URL = os.getenv("EVER_OS_BASE_URL", "https://dev-gateway.aws.evermind.ai")
USER_ID  = "everos-cloud-example-001"

client = EverOS(api_key=API_KEY, base_url=BASE_URL)

now_ms = int(time.time() * 1000)
resp = client.v1.memories.add(
    user_id=USER_ID,
    session_id=f"session-{int(time.time())}",
    messages=[
        {
            "role": "user",
            "timestamp": now_ms,
            "content": [{"type": "text", "text": "我最近在读《思考，快与慢》，双过程理论让我重新理解了决策过程。"}],
        },
        {
            "role": "assistant",
            "timestamp": now_ms + 1000,
            "content": [{"type": "text", "text": "卡尼曼的这本书确实经典，系统一的自动化反应和系统二的慢速推理对理解认知偏见很有帮助。"}],
        },
    ],
)

print("add response:", resp)
print("task_id:", resp.data.task_id)
print("status: ", resp.data.status)
