#!/usr/bin/env python3
"""
02_search_multimodal.py — 多模态记忆的 search

自包含流程：add（图片+文本）→ 等 enrichment → flush → 等索引 → search。
search 接口本身与普通记忆一致（多模态内容已在 add 时上传并由 OCR/VLM 解析入库）。
"""
import time

from everos_cloud import EverOS

from _common import API_KEY, BASE_URL, now_ms, SAMPLE_IMAGE_URL

client = EverOS(api_key=API_KEY, base_url=BASE_URL)

USER_ID = f"mm-search-{int(time.time())}"
SESSION_ID = f"mm-search-s-{int(time.time())}"  # 每次唯一
ms = now_ms()

# 1. add 多模态记忆（文本+图片混排，文本含可提取的偏好信息）
print("1. add multimodal memory (image)...")
client.v1.memories.add(
    user_id=USER_ID,
    session_id=SESSION_ID,
    messages=[
        {
            "role": "user",
            "timestamp": ms,
            "content": [
                {"type": "text", "text": "This is my study room. I love coding here on weekends with a cup of pudding."},
                {"type": "image", "uri": SAMPLE_IMAGE_URL},
            ],
        },
        {
            "role": "assistant",
            "timestamp": ms + 1000,
            "content": [{"type": "text", "text": "Great workspace! The dual setup with bookshelves looks productive."}],
        },
        {
            "role": "user",
            "timestamp": ms + 2000,
            "content": [{"type": "text", "text": "Yes! I usually wear my yellow-tinted glasses while working."}],
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

# 4. search
print("4. search...")
resp = client.v1.memories.search(
    filters={"user_id": USER_ID},
    query="study room coding workspace",
    method="hybrid",
    top_k=5,
)
episodes = resp.data.episodes or []
profiles = resp.data.profiles or []
print(f"\nepisodes={len(episodes)}  profiles={len(profiles)}")
for ep in episodes[:3]:
    txt = getattr(ep, "episode", None) or getattr(ep, "summary", "N/A")
    print(f"  · {txt[:90]}")

# 清理
client.v1.memories.delete(user_id=USER_ID)
print("\n✅ done (cleaned up)")
