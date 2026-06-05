#!/usr/bin/env python3
"""
05_agent_memories.py — Agent 记忆 add / flush

agent add 接受 tool_call 格式消息，适合 AI agent 场景。
"""
import os, time
from everos_cloud import EverOS

API_KEY  = os.getenv("EVEROS_API_KEY", "ddcf3ffb-df31-4c9c-9d30-fb2ee67aed26")
BASE_URL = os.getenv("EVER_OS_BASE_URL", "https://dev-gateway.aws.evermind.ai")
USER_ID  = "everos-cloud-agent-001"
SESSION  = f"agent-session-{int(time.time())}"

client = EverOS(api_key=API_KEY, base_url=BASE_URL)

# agent add
now_ms = int(time.time() * 1000)
resp = client.v1.memories.agent.add(
    user_id=USER_ID,
    session_id=SESSION,
    messages=[
        {
            "role": "user",
            "timestamp": now_ms,
            "content": "帮我查一下明天上海的天气",
        },
        {
            "role": "assistant",
            "timestamp": now_ms + 1000,
            "content": None,
            "tool_calls": [
                {
                    "id": "call_001",
                    "type": "function",
                    "function": {"name": "get_weather", "arguments": '{"city":"上海","date":"tomorrow"}'},
                }
            ],
        },
    ],
)
print("agent add:", resp)

# agent flush
flush_resp = client.v1.memories.agent.flush(user_id=USER_ID, session_id=SESSION)
print("agent flush:", flush_resp)
