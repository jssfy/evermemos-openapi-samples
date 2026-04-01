# pip install everos
# Agent 记忆：写入 + flush（支持 tool_calls / tool role）
import time
from pprint import pprint
from everos import EverOS

client = EverOS()
agent = client.v1.memories.agent

USER_ID = "user_010"
SESSION_ID = "agent_session_001"
now_ms = int(time.time() * 1000)

# --- 1. 基础 agent 轨迹（user / assistant）---
print("=== agent add: basic trajectory ===")
resp = agent.add(
    user_id=USER_ID,
    session_id=SESSION_ID,
    messages=[
        {
            "role": "user",
            "timestamp": now_ms,
            "content": "Search for the latest news about AI.",
        },
        {
            "role": "assistant",
            "timestamp": now_ms + 1000,
            "content": "I'll search the web for you.",
            "tool_calls": [
                {
                    "id": "call_001",
                    "type": "function",
                    "function": {
                        "name": "web_search",
                        "arguments": '{"query": "latest AI news 2026"}',
                    },
                }
            ],
        },
        {
            "role": "tool",
            "timestamp": now_ms + 2000,
            "content": "Found 10 results about AI in 2026...",
            "tool_call_id": "call_001",
        },
        {
            "role": "assistant",
            "timestamp": now_ms + 3000,
            "content": "Here's a summary of the latest AI news...",
        },
    ],
)
pprint(resp)

# --- 2. assistant 消息有 tool_calls 时 content 处理（OpenAI 兼容）---
# SERVER BUG: spec 允许 content=null 或省略，但服务端要求 content 必须存在且非空。
# null / "" / 省略均会报 400，需提供非空占位字符串。
print("\n=== agent add: assistant with tool_calls (content='[tool call]') ===")
resp = agent.add(
    user_id=USER_ID,
    session_id="agent_session_002",
    messages=[
        {
            "role": "user",
            "timestamp": now_ms,
            "content": "Calculate 42 * 7.",
        },
        {
            "role": "assistant",
            "timestamp": now_ms + 500,
            "content": "[tool call]",  # 服务端不接受 null / "" / 省略，必须非空占位
            "tool_calls": [
                {
                    "id": "call_002",
                    "type": "function",
                    "function": {
                        "name": "calculator",
                        "arguments": '{"a": 42, "b": 7, "op": "multiply"}',
                    },
                }
            ],
        },
        {
            "role": "tool",
            "timestamp": now_ms + 1000,
            "content": "294",
            "tool_call_id": "call_002",
        },
        {
            "role": "assistant",
            "timestamp": now_ms + 1500,
            "content": "42 × 7 = 294",
        },
    ],
)
pprint(resp)

# --- 3. 手动 flush ---
print("\n=== agent flush ===")
resp = agent.flush(user_id=USER_ID, session_id=SESSION_ID)
pprint(resp)
