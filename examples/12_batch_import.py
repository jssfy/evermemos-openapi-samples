# pip install evermemos httpx
# 批量离线导入历史消息 —— POST /api/v1/memories/import
#
# 适用场景：将历史对话（如从其他系统迁移的数据）批量写入 EverMemOS，
#          与逐条 add() 相比，import 将 conversation_meta + messages 合并为单次请求。
#
# 注意：v1 SDK (0.3.6) 尚未内置 import 资源，通过 httpx 直接调用。

import os
import time
from datetime import datetime, timezone
from pprint import pprint

import httpx

BASE_URL = os.environ.get("EVER_MEM_OS_BASE_URL", "https://api.evermind.ai")
API_KEY = os.environ["EVERMEMOS_API_KEY"]

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
}

# ======================== 1. 基础导入（个人助手场景）========================

print("=== batch import: personal assistant history ===")

now_iso = datetime.now(timezone.utc).isoformat()
base_ts = int(time.time()) - 3600  # 1 小时前

resp = httpx.post(
    f"{BASE_URL}/api/v1/memories/import",
    headers=headers,
    json={
        "version": "1.0.0",
        "conversation_meta": {
            "group_id": "group_import_personal_001",
            "scene": "assistant",
            "name": "Imported Personal Chat",
            "description": "Migrated from legacy chat system",
            "created_at": "2025-01-01T00:00:00Z",
            "default_timezone": "UTC",
            "user_details": {
                "user_001": {"role": "user", "full_name": "Alice"},
                "bot_001": {"role": "assistant", "full_name": "AI Assistant", "extra": {"type": "ai"}},
            },
            "tags": ["imported", "personal"],
        },
        "conversation_list": [
            {
                "message_id": "msg_001",
                "create_time": f"{datetime.fromtimestamp(base_ts, tz=timezone.utc).isoformat()}",
                "sender": "user_001",
                "sender_name": "Alice",
                "role": "user",
                "type": "text",
                "content": "I prefer reading science fiction novels, especially those about space exploration.",
            },
            {
                "message_id": "msg_002",
                "create_time": f"{datetime.fromtimestamp(base_ts + 30, tz=timezone.utc).isoformat()}",
                "sender": "bot_001",
                "sender_name": "AI Assistant",
                "role": "assistant",
                "type": "text",
                "content": "That's great! Do you have a favorite author or series?",
            },
            {
                "message_id": "msg_003",
                "create_time": f"{datetime.fromtimestamp(base_ts + 60, tz=timezone.utc).isoformat()}",
                "sender": "user_001",
                "sender_name": "Alice",
                "role": "user",
                "type": "text",
                "content": "I love The Expanse series by James S.A. Corey. I also enjoy hiking on weekends.",
            },
        ],
    },
    timeout=30,
)
print(f"status_code={resp.status_code}")
data = resp.json()
pprint(data)

# 导入为异步队列处理，可通过 task_id 追踪（若响应包含 request_id）
if isinstance(data, dict) and data.get("request_id"):
    print(f"\nrequest_id: {data['request_id']} (可通过 /api/v1/stats/request 查询处理状态)")

# ======================== 2. 群组历史对话导入 ========================

print("\n=== batch import: group chat history ===")

resp = httpx.post(
    f"{BASE_URL}/api/v1/memories/import",
    headers=headers,
    json={
        "version": "1.0.0",
        "conversation_meta": {
            "group_id": "group_import_team_001",
            "scene": "group_chat",
            "name": "Team Sprint Planning",
            "created_at": "2025-03-01T09:00:00Z",
            "default_timezone": "Asia/Shanghai",
            "user_details": {
                "alice": {"role": "user", "full_name": "Alice", "custom_role": "Product Manager"},
                "bob":   {"role": "user", "full_name": "Bob",   "custom_role": "Engineer"},
                "carol": {"role": "user", "full_name": "Carol", "custom_role": "Designer"},
            },
            "tags": ["sprint", "planning", "team"],
        },
        "conversation_list": [
            {
                "message_id": "sprint_msg_001",
                "create_time": "2025-03-01T09:00:00Z",
                "sender": "alice",
                "sender_name": "Alice",
                "role": "user",
                "type": "text",
                "content": "Let's review sprint goals for Q2. We need to ship the new dashboard by April 15.",
            },
            {
                "message_id": "sprint_msg_002",
                "create_time": "2025-03-01T09:01:30Z",
                "sender": "bob",
                "sender_name": "Bob",
                "role": "user",
                "type": "text",
                "content": "I can take the backend API work. The authentication refactor will be ready by end of March.",
            },
            {
                "message_id": "sprint_msg_003",
                "create_time": "2025-03-01T09:02:45Z",
                "sender": "carol",
                "sender_name": "Carol",
                "role": "user",
                "type": "text",
                "content": "Design mockups for the dashboard are done. I'll share them in Figma today.",
            },
        ],
    },
    timeout=30,
)
print(f"status_code={resp.status_code}")
pprint(resp.json())

# ======================== 3. 仅导入 conversation_meta（不含消息）========================

print("\n=== batch import: meta only (no messages) ===")

resp = httpx.post(
    f"{BASE_URL}/api/v1/memories/import",
    headers=headers,
    json={
        "version": "1.0.0",
        "conversation_meta": {
            "group_id": "group_import_meta_only_001",
            "scene": "assistant",
            "name": "Pre-registered Session",
            "created_at": "2025-06-01T00:00:00Z",
            "default_timezone": "UTC",
        },
        # conversation_list 可省略，仅注册 meta
    },
    timeout=30,
)
print(f"status_code={resp.status_code}")
pprint(resp.json())

# ======================== 4. 错误处理：缺少必填字段 ========================

print("\n=== error: missing conversation_meta.group_id ===")

resp = httpx.post(
    f"{BASE_URL}/api/v1/memories/import",
    headers=headers,
    json={
        "version": "1.0.0",
        "conversation_meta": {
            # group_id is required but omitted
            "scene": "assistant",
            "name": "Invalid Import",
            "created_at": "2025-01-01T00:00:00Z",
        },
        "conversation_list": [],
    },
    timeout=30,
)
print(f"status_code={resp.status_code}")
pprint(resp.json())
