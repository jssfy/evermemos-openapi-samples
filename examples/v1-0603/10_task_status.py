#!/usr/bin/env python3
"""
10_task_status.py — 查询异步任务状态

add() 返回 task_id，可用 tasks.retrieve() 轮询直到 status != "processing"。
"""
import os, time
from everos_cloud import EverOS

API_KEY  = os.getenv("EVEROS_API_KEY",  "ddcf3ffb-df31-4c9c-9d30-fb2ee67aed26")
BASE_URL = os.getenv("EVER_OS_BASE_URL", "https://dev-gateway.aws.evermind.ai")
USER_ID  = f"everos-cloud-task-{int(time.time())}"

client = EverOS(api_key=API_KEY, base_url=BASE_URL)

# 1. add → 拿到 task_id
now_ms = int(time.time() * 1000)
add_resp = client.v1.memories.add(
    user_id=USER_ID,
    messages=[{"role": "user", "timestamp": now_ms, "content": [{"type": "text", "text": "task status polling test"}]}],
)
task_id = add_resp.data.task_id
print(f"task_id: {task_id}")
print(f"initial status: {add_resp.data.status}")

# 2. 轮询直到完成（最多 30s）
# 注：task 在短时间内（约数秒）可查询，处理完成后会过期返回 404
from everos_cloud import NotFoundError

deadline = time.time() + 30
resp = None
while time.time() < deadline:
    try:
        resp = client.v1.tasks.retrieve(task_id=task_id)
        print(f"  [{time.strftime('%H:%M:%S')}] status={resp.data.status}")
        if resp.data.status not in ("queued", "processing", "pending"):
            break
    except NotFoundError:
        print(f"  [{time.strftime('%H:%M:%S')}] task expired / not found (已处理完成)")
        break
    time.sleep(2)

if resp:
    print(f"\nfinal status: {resp.data.status}")
