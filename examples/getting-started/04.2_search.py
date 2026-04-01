# pip install evermemos
# Getting Started — 搜索记忆（v1 SDK）
# 对应 v0: getting-started/04.2-search.py
#
# 前置条件：先运行 03-save.py 写入数据，等待 ~10s 提取完成后再搜索。

from evermemos import EverMemOS

client = EverMemOS()
memories = client.v1.memories

response = memories.search(
    filters={"user_id": "user_demo_001"},
    query="coffee preference",
    method="vector",
    top_k=5,
)

episodes = response.data.episodes if response.data else []
print(f"Found {len(episodes)} memories")
for ep in episodes:
    print(f"  score={ep.score:.3f}  {ep.episode}")
