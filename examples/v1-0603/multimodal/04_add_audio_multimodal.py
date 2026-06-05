#!/usr/bin/env python3
"""
04_add_audio_multimodal.py — 多模态 add（音频文件）

演示：content 里放 audio 类型，uri 指向本地 WAV 文件，
SDK 自动签名上传并替换为 object_key，再提交 add。

自包含流程：动态生成 WAV → add（audio）→ flush → 等待索引 → search → delete。

若要测试真实语音（ASR 可提取语义），可用 macOS 生成后运行：
  say -v Mei-Jia -o /tmp/speech.aiff "我喜欢在周末爬山，上周去了泰山，风景很美"
  afconvert -f WAVE -d LEI16@16000 /tmp/speech.aiff /tmp/speech.wav
  AUDIO_PATH=/tmp/speech.wav python3 04_add_audio_multimodal.py
"""
import os
import time

from everos_cloud import EverOS

from _common import API_KEY, BASE_URL, now_ms, make_test_audio

client = EverOS(api_key=API_KEY, base_url=BASE_URL)

# 优先读环境变量指定的真实音频，否则动态生成测试 WAV
AUDIO_PATH = os.environ.get("AUDIO_PATH") or make_test_audio()

USER_ID = f"mm-audio-{int(time.time())}"
SESSION_ID = f"mm-audio-s-{int(time.time())}"  # 每次唯一，避免旧消息干扰 exclude 计数
ms = now_ms()

print(f"audio file: {AUDIO_PATH}  ({os.path.getsize(AUDIO_PATH) / 1024:.1f} KB)")

# 1. add（多模态，音频 + 文本混排）
print("\n1. add multimodal memory (audio)...")
resp = client.v1.memories.add(
    user_id=USER_ID,
    session_id=SESSION_ID,
    messages=[
        {
            "role": "user",
            "timestamp": ms,
            "content": [
                {"type": "text", "text": "Here is a voice message I recorded."},
                {
                    "type": "audio",
                    "uri": AUDIO_PATH,          # 本地文件 → SDK 自动上传
                    "name": os.path.basename(AUDIO_PATH),
                    "ext": "wav",
                },
            ],
        },
        {
            "role": "assistant",
            "timestamp": ms + 1000,
            "content": [{"type": "text", "text": "Got it, I've received your voice message."}],
        },
    ],
)
print(f"add response: status={resp.data.status} task_id={resp.data.task_id}")

# 2. 等待 Kafka consumer 完成多模态 enrichment（GeminiAudioParser 约 3s）
# add 返回 202 即 queued，但 Kafka consumer 异步做 MultimodalEnrich（调用 ASR），
# enrichment 完成后才写入 conversation DB；flush 过早会拿到 count=0 → no_extraction。
# 总耗时：Kafka 延迟(~4s) + multimodal enrichment(~3s) + 边界检测(~2s) ≈ 10s
print("\n2. waiting for Kafka + multimodal enrichment (15s)...")
time.sleep(15)

# 3. flush（提交 session 缓冲，触发记忆提取）
print("\n3. flush...")
flush_resp = client.v1.memories.flush(user_id=USER_ID, session_id=SESSION_ID)
print(f"flush response: status={flush_resp.data.status} request_id={flush_resp.data.request_id}")

# 4. 等待异步提取完成
print("\n4. waiting for extraction (15s)...")
time.sleep(15)

# 5. search
print("\n5. search...")
resp = client.v1.memories.search(
    filters={"user_id": USER_ID},
    query="爬山 户外 周末",  # 匹配 TTS 中文内容；英文音频可改为对应词
    method="hybrid",
    top_k=5,
)
episodes = resp.data.episodes or []
profiles = resp.data.profiles or []
print(f"episodes={len(episodes)}  profiles={len(profiles)}")
for ep in episodes[:3]:
    txt = getattr(ep, "episode", None) or getattr(ep, "summary", "N/A")
    print(f"  · {txt[:120]}")

# 6. 清理
print("\n6. cleanup...")
client.v1.memories.delete(user_id=USER_ID)
print(f"\n✅ done (user_id={USER_ID} cleaned up)")
