#!/usr/bin/env python3
"""
test_dev.py — everos_cloud SDK v1 dev 环境全流程冒烟测试

测试范围：
  - add (sync)
  - search (hybrid)
  - get (episodic_memory / profile)
  - agent.add + agent.flush
  - delete

运行：
  /opt/miniconda3/bin/python3 test_dev.py
  或设置环境变量后运行：
  EVEROS_API_KEY=xxx EVER_OS_BASE_URL=https://dev-gateway.aws.evermind.ai python3 test_dev.py
"""
import os, sys, time

# ── 配置 ──────────────────────────────────────────────────────
API_KEY  = os.getenv("EVEROS_API_KEY",  "ddcf3ffb-df31-4c9c-9d30-fb2ee67aed26")
BASE_URL = os.getenv("EVER_OS_BASE_URL", "https://dev-gateway.aws.evermind.ai")
USER_ID  = f"everos-cloud-smoke-{int(time.time())}"
SESSION  = f"session-{int(time.time())}"

from everos_cloud import EverOS

client = EverOS(api_key=API_KEY, base_url=BASE_URL)

PASS = "✅"
FAIL = "❌"
results = []

def check(name, fn):
    try:
        fn()
        print(f"{PASS} {name}")
        results.append((name, True, None))
    except Exception as e:
        print(f"{FAIL} {name}: {e}")
        results.append((name, False, str(e)))

# ── 1. add ────────────────────────────────────────────────────
def test_add():
    now_ms = int(time.time() * 1000)
    resp = client.v1.memories.add(
        user_id=USER_ID,
        session_id=SESSION,
        messages=[
            {
                "role": "user",
                "timestamp": now_ms,
                "content": [{"type": "text", "text": "我在学习机器学习，最近在研究 Transformer 架构的注意力机制。"}],
            },
            {
                "role": "assistant",
                "timestamp": now_ms + 1000,
                "content": [{"type": "text", "text": "Transformer 的 Self-Attention 让模型可以关注序列中任意位置的关系，是 LLM 的核心基础。"}],
            },
        ],
    )
    assert resp.data.task_id, "task_id 为空"
    assert resp.data.status in ("queued", "processing", "completed"), f"意外 status: {resp.data.status}"
    test_add.task_id = resp.data.task_id

check("add (sync)", test_add)
print(f"   task_id={getattr(test_add, 'task_id', None)}")

# ── 2. flush ──────────────────────────────────────────────────
def test_flush():
    resp = client.v1.memories.flush(user_id=USER_ID, session_id=SESSION)
    assert resp is not None

check("flush", test_flush)

# ── 等待索引 ──────────────────────────────────────────────────
print("   等待 5s 让记忆索引完成...")
time.sleep(5)

# ── 3. search ─────────────────────────────────────────────────
def test_search():
    resp = client.v1.memories.search(
        filters={"user_id": USER_ID},
        query="Transformer 注意力机制",
        top_k=5,
        method="hybrid",
    )
    assert resp.data is not None

check("search (hybrid)", test_search)

# ── 4. get episodic_memory ────────────────────────────────────
def test_get_episodic():
    resp = client.v1.memories.get(
        filters={"user_id": USER_ID},
        memory_type="episodic_memory",
        page_size=5,
    )
    assert resp.data is not None

check("get (episodic_memory)", test_get_episodic)

# ── 5. get profile ────────────────────────────────────────────
def test_get_profile():
    resp = client.v1.memories.get(
        filters={"user_id": USER_ID},
        memory_type="profile",
        page_size=5,
    )
    assert resp.data is not None

check("get (profile)", test_get_profile)

# ── 6. agent add + flush ──────────────────────────────────────
def test_agent():
    agent_session = f"agent-{SESSION}"
    now_ms = int(time.time() * 1000)
    add_resp = client.v1.memories.agent.add(
        user_id=USER_ID,
        session_id=agent_session,
        messages=[
            {"role": "user", "timestamp": now_ms, "content": "查询北京明天天气"},
            {
                "role": "assistant",
                "timestamp": now_ms + 1000,
                "content": None,
                "tool_calls": [{
                    "id": "tc_001",
                    "type": "function",
                    "function": {"name": "get_weather", "arguments": '{"city":"北京"}'},
                }],
            },
        ],
    )
    assert add_resp.data.task_id
    flush_resp = client.v1.memories.agent.flush(user_id=USER_ID, session_id=agent_session)
    assert flush_resp is not None

check("agent.add + agent.flush", test_agent)

# ── 7. delete ─────────────────────────────────────────────────
def test_delete():
    client.v1.memories.delete(user_id=USER_ID)

check("delete (by user_id)", test_delete)

# ── 汇总 ──────────────────────────────────────────────────────
total  = len(results)
passed = sum(1 for _, ok, _ in results if ok)
print(f"\n{'='*40}")
print(f"结果：{passed}/{total} 通过")
print(f"SDK:  everos_cloud {__import__('everos_cloud').__version__}")
print(f"env:  {BASE_URL}")
if passed < total:
    sys.exit(1)
