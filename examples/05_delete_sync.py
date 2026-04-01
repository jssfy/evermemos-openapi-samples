# pip install everos
# 删除记忆（单条 / 批量）—— 对应旧版 delete_async.py
from everos import EverOS, InternalServerError, NotFoundError

client = EverOS()
memories = client.v1.memories

# --- 1. 按 memory_id 删除单条 ---
# SERVER BUG: 不存在的 memory_id 返回 500 而非 404，已知问题
print("=== delete by memory_id ===")
try:
    memories.delete(memory_id="mem_abc123")
    print("  done")
except (NotFoundError, InternalServerError) as e:
    print(f"  expected error (id not found): {e.status_code}")

# --- 2. 按 user_id 批量清空 ---
print("=== delete all by user_id ===")
memories.delete(user_id="user_010")
print("  done")

# --- 3. 按 user_id + session_id 精确批量删除 ---
print("=== delete by user_id + session_id ===")
memories.delete(
    user_id="user_010",
    session_id="session_xyz",
)
print("  done")

# --- 4. 按 group_id 删除群组记忆 ---
print("=== delete by group_id ===")
memories.delete(group_id="group_demo_001")
print("  done")

# --- 5. 按 user_id + sender_id 过滤删除 ---
print("=== delete by user_id + sender_id ===")
memories.delete(
    user_id="user_010",
    sender_id="sender_alice",
)
print("  done")
