# pip install everos
# 查询记忆（分类型） —— 对应旧版 get_async.py
from pprint import pprint
from everos import EverOS

client = EverOS()
memories = client.v1.memories

USER_ID = "user_010"

# --- 1. 查 episodic_memory（个人 + 群组均支持）---
print("=== episodic_memory ===")
resp = memories.get(
    filters={"user_id": USER_ID},
    memory_type="episodic_memory",
    page=1,
    page_size=10,
    rank_by="timestamp",
    rank_order="desc",
)
pprint(resp)

# --- 2. 查 profile（仅支持 user_id，group_id 会报 400）---
print("\n=== profile ===")
resp = memories.get(
    filters={"user_id": USER_ID},
    memory_type="profile",
)
pprint(resp)

# --- 3. 带时间范围过滤（timestamp DSL）---
import time
now_ms = int(time.time() * 1000)
one_day_ms = 24 * 60 * 60 * 1000

print("\n=== episodic_memory (last 24 h) ===")
resp = memories.get(
    filters={
        "user_id": USER_ID,
        "timestamp": {"gte": now_ms - one_day_ms, "lt": now_ms},
    },
    memory_type="episodic_memory",
)
pprint(resp)

# --- 4. 通过 group_id 查 episodic_memory ---
print("\n=== episodic_memory by group ===")
resp = memories.get(
    filters={"group_id": "group_demo_001"},
    memory_type="episodic_memory",
)
pprint(resp)
