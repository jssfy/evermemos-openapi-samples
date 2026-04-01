# pip install evermemos
# Conversation Meta：创建 / 更新 / 查询会话元数据
#
# 注意：v1 SDK (0.3.6) 尚未内置 conversation_meta 资源，
#      通过 SDK 底层 HTTP 方法直接调用 /api/v1/memories/conversation-meta。
#
# 对应端点：
#   POST   /api/v1/memories/conversation-meta  — 创建（绑定 group_id 或全局默认配置）
#   PATCH  /api/v1/memories/conversation-meta  — 局部更新
#   GET    /api/v1/memories/conversation-meta  — 查询（含 fallback 到默认配置）

import os
from datetime import datetime, timezone
from pprint import pprint

import httpx

BASE_URL = os.environ.get("EVER_MEM_OS_BASE_URL", "https://api.evermind.ai")
API_KEY = os.environ["EVERMEMOS_API_KEY"]

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
}

GROUP_ID = "group_demo_meta_001"
NOW = datetime.now(timezone.utc).isoformat()

# ======================== 1. 创建全局默认配置（不绑定 group_id）========================

print("=== create: global default config ===")
resp = httpx.post(
    f"{BASE_URL}/api/v1/memories/conversation-meta",
    headers=headers,
    json={
        "scene": "assistant",
        "scene_desc": {
            "description": "Personal AI assistant",
            "type": "personal_assistant",
        },
        "name": "Default Config",
        "created_at": NOW,
        "default_timezone": "Asia/Shanghai",
        "tags": ["default", "assistant"],
    },
)
resp.raise_for_status()
pprint(resp.json())

# ======================== 2. 创建绑定 group_id 的配置 ========================

print("\n=== create: group config ===")
resp = httpx.post(
    f"{BASE_URL}/api/v1/memories/conversation-meta",
    headers=headers,
    json={
        "scene": "group_chat",
        "scene_desc": {
            "description": "Project discussion group chat",
            "type": "project_discussion",
        },
        "name": "Project Alpha",
        "group_id": GROUP_ID,
        "created_at": NOW,
        "default_timezone": "Asia/Shanghai",
        "description": "Engineering team weekly sync",
        "tags": ["work", "engineering"],
        "user_details": {
            "user_001": {
                "full_name": "Alice",
                "role": "user",
                "custom_role": "Tech Lead",
                "extra": {"department": "Engineering"},
            },
            "bot_001": {
                "full_name": "AI Assistant",
                "role": "assistant",
                "extra": {"type": "ai"},
            },
        },
    },
)
resp.raise_for_status()
pprint(resp.json())

# ======================== 3. 局部更新（PATCH）========================

print("\n=== patch: update tags + user_details ===")
resp = httpx.patch(
    f"{BASE_URL}/api/v1/memories/conversation-meta",
    headers=headers,
    json={
        "group_id": GROUP_ID,
        "name": "Project Alpha (Updated)",
        "tags": ["work", "engineering", "q2"],
        "user_details": {
            "user_001": {
                "full_name": "Alice (Senior)",
                "role": "user",
                "custom_role": "Senior Tech Lead",
            },
            "user_002": {
                "full_name": "Bob",
                "role": "user",
                "custom_role": "Backend Engineer",
            },
        },
    },
)
resp.raise_for_status()
pprint(resp.json())

# ======================== 4. 查询 group 配置（GET）========================

print("\n=== get: by group_id ===")
resp = httpx.get(
    f"{BASE_URL}/api/v1/memories/conversation-meta",
    headers=headers,
    params={"group_id": GROUP_ID},
)
resp.raise_for_status()
pprint(resp.json())

# ======================== 5. 查询默认配置（不传 group_id）========================

print("\n=== get: default config (no group_id) ===")
resp = httpx.get(
    f"{BASE_URL}/api/v1/memories/conversation-meta",
    headers=headers,
)
resp.raise_for_status()
pprint(resp.json())

# ======================== 6. 错误处理：404 group 不存在时的 fallback 行为 ========================

print("\n=== get: nonexistent group_id → fallback to default ===")
resp = httpx.get(
    f"{BASE_URL}/api/v1/memories/conversation-meta",
    headers=headers,
    params={"group_id": "group_nonexistent_xyz"},
)
# 404 表示 group 不存在且无默认配置；200 表示已 fallback 到默认配置
print(f"status_code={resp.status_code}")
pprint(resp.json())
