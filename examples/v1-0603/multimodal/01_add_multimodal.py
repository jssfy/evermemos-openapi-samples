#!/usr/bin/env python3
"""
01_add_multimodal.py — 多模态 add（图片 + 文本混排）

演示：content 里混排 text + image，image 的 uri 指向公网图片 URL，
SDK 自动下载→签名上传→替换为 object_key，再提交 add。
"""
import time

from everos_cloud import EverOS

from _common import API_KEY, BASE_URL, now_ms, SAMPLE_IMAGE_URL

client = EverOS(api_key=API_KEY, base_url=BASE_URL)

USER_ID = f"mm-add-{int(time.time())}"
SESSION_ID = f"mm-add-s-{int(time.time())}"  # 每次唯一，避免旧消息干扰 exclude 计数
ms = now_ms()

print(f"add type: {type(client.v1.memories).__name__}")  # MemoriesResourceWithMultimodal
print(f"image url: {SAMPLE_IMAGE_URL}")

# 1. add（多模态，缓冲到 session）
resp = client.v1.memories.add(
    user_id=USER_ID,
    session_id=SESSION_ID,
    messages=[
        {
            "role": "user",
            "timestamp": ms,
            "content": [
                {"type": "text", "text": "This is a photo of my study room where I work."},
                {"type": "image", "uri": SAMPLE_IMAGE_URL},  # ← http(s) URL，SDK 自动下载+上传
            ],
        },
        {
            "role": "assistant",
            "timestamp": ms + 1000,
            "content": [{"type": "text", "text": "Nice setup! Looks like a cozy place to code."}],
        },
    ],
)
print(f"\nadd response: status={resp.data.status} task_id={resp.data.task_id}")

# 2. 等待 Kafka consumer 完成多模态 enrichment（图片 OCR/VLM）后再 flush
# add 返回 202 即 queued，但 enrichment 完成、消息落 conversation DB 才能被 flush 提取；
# flush 过早会拿到 count=0 → no_extraction。
print("\nwaiting for Kafka + multimodal enrichment (15s)...")
time.sleep(15)

# 3. flush（提交 session 缓冲，触发记忆提取）
flush_resp = client.v1.memories.flush(user_id=USER_ID, session_id=SESSION_ID)
print(f"flush response: status={flush_resp.data.status} request_id={flush_resp.data.request_id}")
print(f"user_id: {USER_ID}")

# ── 备选：用本地图片文件（SDK 自动签名上传）──────────────────────
# from _common import make_test_image
# client.v1.memories.add(
#     user_id=USER_ID,
#     messages=[{"role": "user", "timestamp": now_ms(), "content": [
#         {"type": "text", "text": "Here's a local image."},
#         {"type": "image", "uri": make_test_image()},  # 本地路径，自动上传
#     ]}],
# )
