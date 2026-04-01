# pip install evermemos
# 搜索记忆（多种 method）—— 对应旧版 search_async.py
#
# 前置条件：搜索结果依赖已存在的记忆数据。
#   - 个人记忆搜索（user_id）：先运行 01_add_sync.py 写入数据，等待 ~10s 异步提取完成后再搜索
#   - 群组记忆搜索（group_id）：先运行 08_group_memories.py 写入数据，等待 ~10s 后再搜索
#   - 若搜索返回空列表，通常是数据未写入或提取尚未完成
#
# NOTE: 服务端实际支持的 method: agentic, hybrid, keyword, vector
from pprint import pprint
from evermemos import EverMemOS

client = EverMemOS()
memories = client.v1.memories

USER_ID = "user_010"

# --- 1. vector 搜索（推荐）---
print("=== vector search ===")
resp = memories.search(
    filters={"user_id": USER_ID},
    query="outdoor activities the user enjoys",
    method="vector",
    memory_types=["episodic_memory", "profile"],
    top_k=5,
)
pprint(resp)

# --- 2. vector 搜索 + 相似度阈值 ---
print("\n=== vector search (radius=0.3) ===")
resp = memories.search(
    filters={"user_id": USER_ID},
    query="fear or anxiety experiences",
    method="vector",
    radius=0.3,
    top_k=5,
)
pprint(resp)

# --- 3. keyword 搜索 ---
print("\n=== keyword search ===")
resp = memories.search(
    filters={"user_id": USER_ID},
    query="dentist",
    method="keyword",
    top_k=10,
)
pprint(resp)

# --- 4. 按 group_id 搜索（episodic_memory 支持）---
print("\n=== group search (vector) ===")
resp = memories.search(
    filters={"group_id": "group_demo_001"},
    query="project discussion",
    method="vector",
    memory_types=["episodic_memory"],
    top_k=5,
)
pprint(resp)

# --- 5. agentic 搜索 ---
print("\n=== agentic search ===")
resp = memories.search(
    filters={"user_id": USER_ID},
    query="mountain hiking",
    method="agentic",
    top_k=3,
)
pprint(resp)
