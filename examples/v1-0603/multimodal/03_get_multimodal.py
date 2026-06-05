#!/usr/bin/env python3
"""
03_get_multimodal.py — 多模态记忆的 get

自包含流程：add（图片+文本）→ 等 enrichment → flush → 等索引 → get（按类型分页拉取）。
get 接口与普通记忆一致。
"""
import time

from everos_cloud import EverOS

from _common import API_KEY, BASE_URL, now_ms, SAMPLE_IMAGE_URL

client = EverOS(api_key=API_KEY, base_url=BASE_URL)

USER_ID = f"mm-get-{int(time.time())}"
SESSION_ID = f"mm-get-s-{int(time.time())}"  # 每次唯一
ms = now_ms()

# 1. add 多模态记忆（文本+图片混排）
print("1. add multimodal memory (image)...")
client.v1.memories.add(
    user_id=USER_ID,
    session_id=SESSION_ID,
    messages=[
        {
            "role": "user",
            "timestamp": ms,
            "content": [
                {"type": "text", "text": "Here's a photo of my home office. I'm a software engineer and I prefer concise weekly updates."},
                {"type": "image", "uri": SAMPLE_IMAGE_URL},
            ],
        },
        {
            "role": "assistant",
            "timestamp": ms + 1000,
            "content": [{"type": "text", "text": "Got it. I'll keep updates concise and weekly."}],
        },
    ],
)

# 2. 等 Kafka + 多模态 enrichment 后 flush（顺序关键：sleep 必须在 flush 之前）
print("2. wait for enrichment (15s) + flush...")
time.sleep(15)
client.v1.memories.flush(user_id=USER_ID, session_id=SESSION_ID)

# 3. 等待提取索引完成
print("3. wait for extraction (10s)...")
time.sleep(10)

# 4. get（按记忆类型拉取）
print("4. get by type...")
for mtype in ("episodic_memory", "profile"):
    resp = client.v1.memories.get(
        filters={"user_id": USER_ID},
        memory_type=mtype,
        page_size=5,
        rank_order="desc",
    )
    print(f"   {mtype}: total_count={resp.data.total_count}")

# 清理
client.v1.memories.delete(user_id=USER_ID)
print("\n✅ done (cleaned up)")
