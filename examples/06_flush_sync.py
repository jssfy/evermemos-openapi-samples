# pip install evermemos
# 手动触发会话边界（boundary detection）—— 对应旧版 flush=True 参数
from evermemos import EverMemOS

client = EverMemOS()
memories = client.v1.memories

# --- 1. 全局 flush（user 级别）---
print("=== flush user ===")
resp = memories.flush(user_id="user_010")
print(resp)

# --- 2. 按 session 精确 flush ---
print("=== flush user + session ===")
resp = memories.flush(
    user_id="user_010",
    session_id="session_xyz",
)
print(resp)

# --- 典型用法：写入若干消息后手动 flush ---
import time

now_ms = int(time.time() * 1000)

memories.add(
    user_id="user_010",
    session_id="session_abc",
    messages=[
        {"role": "user", "timestamp": now_ms, "content": "Hello, let's talk about travel."},
        {"role": "assistant", "timestamp": now_ms + 500, "content": "Sure! Where have you been?"},
        {"role": "user", "timestamp": now_ms + 1000, "content": "I visited Japan last month."},
    ],
)

# 明确告知系统本次会话已结束，立即提取记忆
resp = memories.flush(user_id="user_010", session_id="session_abc")
print("flush response:", resp)
