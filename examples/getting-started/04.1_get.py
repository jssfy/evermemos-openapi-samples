# pip install evermemos
# Getting Started — 查询记忆（v1 SDK）
# 对应 v0: getting-started/04.1-get.py
#
# 前置条件：先运行 03-save.py 写入数据，等待 ~10s 提取完成后再查询。

from evermemos import EverMemOS

client = EverMemOS()
memories = client.v1.memories

response = memories.get(
    filters={"user_id": "user_demo_001"},
    memory_type="episodic_memory",
)

items = response.data.episodes if response.data else []
print(f"Fetched {len(items)} memories")
for mem in items:
    print(f"  {mem.episode}")
