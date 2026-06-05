#!/usr/bin/env python3
"""
quickstart_sdk_complete.py — 完整流程演示

覆盖：
  1. add 个人记忆（personal）
  2. add agent 记忆（tool_call 格式）
  3. flush session 缓冲
  4. 等待索引
  5. search（hybrid）
  6. get（episodic_memory / profile）
  7. 查询 task 状态
  8. delete 清理
"""
import os, time
from everos_cloud import EverOS, NotFoundError

API_KEY  = os.getenv("EVEROS_API_KEY",  "ddcf3ffb-df31-4c9c-9d30-fb2ee67aed26")
BASE_URL = os.getenv("EVER_OS_BASE_URL", "https://dev-gateway.aws.evermind.ai")

client   = EverOS(api_key=API_KEY, base_url=BASE_URL)
memories = client.v1.memories

USER_ID    = f"cookbook-complete-{int(time.time())}"
SESSION_ID = f"session-{int(time.time())}"
now_ms     = int(time.time() * 1000)

# ── 1. add 个人记忆 ───────────────────────────────────────────
print("1. Adding personal memories...")
add_resp = memories.add(
    user_id=USER_ID,
    session_id=SESSION_ID,
    messages=[
        {
            "role": "user",
            "timestamp": now_ms,
            "content": [{"type": "text", "text": "I love hiking on weekends. Last Saturday I climbed Mt. Tai and it was breathtaking."}],
        },
        {
            "role": "assistant",
            "timestamp": now_ms + 1000,
            "content": [{"type": "text", "text": "That sounds incredible! Mt. Tai is one of China's Five Great Mountains."}],
        },
        {
            "role": "user",
            "timestamp": now_ms + 2000,
            "content": [{"type": "text", "text": "Yes! I also enjoy cycling. I ride about 30km every Sunday morning."}],
        },
    ],
)
task_id = add_resp.data.task_id
print(f"   task_id={task_id}  status={add_resp.data.status}")

# ── 2. add agent 记忆 ─────────────────────────────────────────
print("\n2. Adding agent memories (tool_call)...")
agent_session = f"agent-{SESSION_ID}"
memories.agent.add(
    user_id=USER_ID,
    session_id=agent_session,
    messages=[
        {"role": "user",      "timestamp": now_ms + 3000, "content": "查询明天北京的天气"},
        {
            "role": "assistant", "timestamp": now_ms + 4000, "content": None,
            "tool_calls": [{"id": "tc_001", "type": "function",
                            "function": {"name": "get_weather", "arguments": '{"city":"北京","date":"tomorrow"}'}}],
        },
    ],
)
print("   done")

# ── 3. flush ──────────────────────────────────────────────────
print("\n3. Flushing sessions...")
memories.flush(user_id=USER_ID, session_id=SESSION_ID)
memories.agent.flush(user_id=USER_ID, session_id=agent_session)
print("   done")

# ── 4. 等待索引 ───────────────────────────────────────────────
print("\n4. Waiting for memory extraction (6s)...")
time.sleep(6)

# ── 5. search ─────────────────────────────────────────────────
print("\n5. Searching memories...")
search_resp = memories.search(
    filters={"user_id": USER_ID},
    query="outdoor activities and hobbies",
    method="hybrid",
    top_k=5,
)
episodes = search_resp.data.episodes or []
profiles = search_resp.data.profiles or []
print(f"   episodes={len(episodes)}  profiles={len(profiles)}")
for ep in episodes[:3]:
    txt = getattr(ep, "episode", None) or getattr(ep, "summary", "N/A")
    score = getattr(ep, "score", "N/A")
    print(f"   · [{score:.3f}] {txt[:80]}" if isinstance(score, float) else f"   · {txt[:80]}")

# ── 6. get ────────────────────────────────────────────────────
print("\n6. Getting memories by type...")
for mtype in ("episodic_memory", "profile"):
    resp = memories.get(
        filters={"user_id": USER_ID},
        memory_type=mtype,
        page_size=3,
        rank_order="desc",
    )
    count = resp.data.total_count
    print(f"   {mtype}: total_count={count}")

# ── 7. 查询 task 状态 ─────────────────────────────────────────
print("\n7. Checking task status...")
try:
    task_resp = client.v1.tasks.retrieve(task_id=task_id)
    print(f"   status={task_resp.data.status}")
except NotFoundError:
    print("   task already completed (expired from query window)")

# ── 8. delete 清理 ────────────────────────────────────────────
print("\n8. Cleanup...")
memories.delete(user_id=USER_ID)
print("   deleted all memories for this user")
print("\n✅ Complete quickstart finished.")
