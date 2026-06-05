#!/usr/bin/env python3
"""
SDK 功能测试脚本：验证 memory add(sync/async) / get / search

环境变量（SDK 自动读取）：
  EVEROS_API_KEY      API Key
  EVER_OS_BASE_URL    接入点，默认 https://api.evermind.ai
"""

import sys
import os
import time
import asyncio
from datetime import datetime

# 从本地 SDK 源码导入（无需 pip install）
sdk_path = os.path.join(os.path.dirname(__file__), "../../sdks/EverOS-python/src")
sys.path.insert(0, os.path.abspath(sdk_path))

from everos import EverOS, AsyncEverOS

OWNER_ID = "test_user_001"
OWNER_TYPE = "user"
SESSION_ID = f"test_session_{datetime.now().isoformat()}"


def with_timestamps(messages):
    """Inject current timestamp (ms) into messages that lack one."""
    now_ms = int(time.time() * 1000)
    return [{**msg, "timestamp": msg.get("timestamp", now_ms)} for msg in messages]

# 三段不同主题的对话，分别用于三种 add 测试
CONV_1 = [
    {
        "sender_id": OWNER_ID,
        "role": "user",
        "content": [{"type": "text", "text": "I just finished reading 'Thinking, Fast and Slow' by Daniel Kahneman. The dual-process theory really changed how I view decision making."}],
    },
    {
        "sender_id": "assistant",
        "role": "assistant",
        "content": [{"type": "text", "text": "That's a landmark book. System 1 vs System 2 thinking is incredibly useful for understanding cognitive biases. Did any particular bias resonate with you?"}],
    },
    {
        "sender_id": OWNER_ID,
        "role": "user",
        "content": [{"type": "text", "text": "The anchoring effect surprised me most. I never realized how much initial numbers influence my judgment in negotiations."}],
    },
]

CONV_2 = [
    {
        "sender_id": OWNER_ID,
        "role": "user",
        "content": [{"type": "text", "text": "我在学习 Rust，但所有权机制让我很困惑。借用检查器总是报错，不知道该怎么理解生命周期。"}],
    },
    {
        "sender_id": "assistant",
        "role": "assistant",
        "content": [{"type": "text", "text": "生命周期是 Rust 最陡峭的学习曲线。核心规则是：引用不能比它指向的数据活得更长。可以先从函数签名上的 `'a` 标注入手，理解编译器在帮你做什么。"}],
    },
    {
        "sender_id": OWNER_ID,
        "role": "user",
        "content": [{"type": "text", "text": "好的，我先专注于理解所有权转移和 clone 的区别，再去碰生命周期标注。"}],
    },
]

CONV_3 = [
    {
        "sender_id": OWNER_ID,
        "role": "user",
        "content": [{"type": "text", "text": "We need to plan the Q3 roadmap. Top priorities are: 1) ship the new memory search API, 2) reduce p99 latency below 200ms, 3) onboard three enterprise pilots."}],
    },
    {
        "sender_id": "assistant",
        "role": "assistant",
        "content": [{"type": "text", "text": "Got it. For latency, the biggest win is likely caching the embedding lookups. For the enterprise pilots, do you have the three companies identified yet?"}],
    },
    {
        "sender_id": OWNER_ID,
        "role": "user",
        "content": [{"type": "text", "text": "Yes: FinCo, MedAI, and LegalTech. FinCo is the most urgent, they want a POC by end of July."}],
    },
]


def make_client():
    return EverOS()  # 读取 EVEROS_API_KEY 和 EVER_OS_BASE_URL


def make_async_client():
    return AsyncEverOS()


def test_add_sync():
    """同步 add：async_mode=False，直接返回提取结果（对话主题：读书笔记·锚定效应）"""
    print("\n=== 测试 add_memories（sync，async_mode=False）===")
    print("    对话主题：读书笔记 - 《思考，快与慢》")
    try:
        response = make_client().memory.add(
            owner_id=OWNER_ID,
            owner_type=OWNER_TYPE,
            session_id=f"{SESSION_ID}_sync",
            messages=with_timestamps(CONV_1),
            async_mode=False,
        )
        print(f"✅ add sync 成功")
        print(f"   request_id: {response.request_id}")
        print(f"   status: {response.data.status}")
        print(f"   message_count: {response.data.message_count}")
        return True
    except Exception as e:
        print(f"❌ add sync 失败: {e}")
        return False


def test_add_async_mode():
    """异步 add：async_mode=True，后台处理，通过 tasks.retrieve 轮询状态（对话主题：Rust 学习）"""
    print("\n=== 测试 add_memories（async_mode=True）+ tasks.retrieve 轮询 ===")
    print("    对话主题：Rust 所有权与生命周期学习")
    try:
        client = make_client()
        response = client.memory.add(
            owner_id=OWNER_ID,
            owner_type=OWNER_TYPE,
            session_id=f"{SESSION_ID}_async",
            messages=with_timestamps(CONV_2),
            async_mode=True,
        )
        print(f"✅ add async 提交成功")
        print(f"   request_id: {response.request_id}")
        print(f"   status: {response.data.status}")  # 预期 "processing"

        # 用 request_id 作为 task_id 轮询
        task_id = response.request_id
        task = client.tasks.retrieve(task_id=task_id)
        print(f"   task status: {task.status}")
        return True
    except Exception as e:
        print(f"❌ add async 失败: {e}")
        return False


async def test_add_async_client():
    """使用 AsyncEverOS 客户端的异步 add（对话主题：Q3 roadmap 规划）"""
    print("\n=== 测试 add_memories（AsyncEverOS 异步客户端）===")
    print("    对话主题：Q3 roadmap - 企业 pilot 规划")
    try:
        async with make_async_client() as client:
            response = await client.memory.add(
                owner_id=OWNER_ID,
                owner_type=OWNER_TYPE,
                session_id=f"{SESSION_ID}_asyncclient",
                messages=with_timestamps(CONV_3),
                async_mode=False,
            )
        print(f"✅ AsyncEverOS add 成功")
        print(f"   request_id: {response.request_id}")
        print(f"   status: {response.data.status}")
        print(f"   message_count: {response.data.message_count}")
        return True
    except Exception as e:
        print(f"❌ AsyncEverOS add 失败: {e}")
        return False


def test_search_memories():
    print("\n=== 测试 search_memories ===")
    try:
        response = make_client().memory.search(
            owner_id=OWNER_ID,
            owner_type=OWNER_TYPE,
            query="SDK testing",
            method="keyword",
            top_k=10,
        )
        print(f"✅ search_memories 成功")
        print(f"   request_id: {response.request_id}")
        if response.data:
            print(f"   episodes: {len(response.data.episodes) if response.data.episodes else 0}")
            print(f"   profiles: {len(response.data.profiles) if response.data.profiles else 0}")
        return True
    except Exception as e:
        print(f"❌ search_memories 失败: {e}")
        return False


def test_get_memories():
    print("\n=== 测试 get_memories ===")
    try:
        response = make_client().memory.get(
            owner_id=OWNER_ID,
            owner_type=OWNER_TYPE,
            memory_type="episodic_memory",
            page=1,
            page_size=10,
        )
        print(f"✅ get_memories 成功")
        print(f"   request_id: {response.request_id}")
        if response.data:
            print(f"   total_count: {response.data.total_count}")
            print(f"   count: {response.data.count}")
            print(f"   episodes: {len(response.data.episodes) if response.data.episodes else 0}")
        return True
    except Exception as e:
        print(f"❌ get_memories 失败: {e}")
        return False


def test_add_multimodal():
    """多模态 add：本地图片文件 → 自动 sign + upload → memory add（对话主题：图片分享）"""
    import tempfile
    print("\n=== 测试 add_memories（多模态：本地图片自动上传）===")
    print("    流程：创建本地图片 → scan_messages 检测 → batch_sign → S3 upload → memory add")
    try:
        # 创建最小 JPEG 测试文件（8×8 纯红色，50 字节左右）
        jpeg_bytes = (
            b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00"
            b"\xff\xdb\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t"
            b"\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d\x1a"
            b"\x1f\x1e\x1d\x1a\x1c\x1c $.' \",#\x1c\x1c(7),01444\x1f'9=82<.342\x1e\xfe\xd9"
        )
        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
            tmp.write(jpeg_bytes)
            tmp_path = tmp.name

        print(f"   临时图片: {tmp_path}")

        # 构造带图片 uri 的消息（uri 指向本地文件，multimodal 层会自动上传）
        msg_with_image = [
            {
                "sender_id": OWNER_ID,
                "role": "user",
                "content": [
                    {"type": "text", "text": "这是我今天拍的照片，帮我记一下。"},
                    {"type": "image", "uri": tmp_path, "name": "test_photo.jpg", "ext": "jpg"},
                ],
            }
        ]

        response = make_client().memory.add(
            owner_id=OWNER_ID,
            owner_type=OWNER_TYPE,
            session_id=f"{SESSION_ID}_multimodal",
            messages=with_timestamps(msg_with_image),
            async_mode=False,
        )
        print(f"✅ 多模态 add 成功")
        print(f"   request_id: {response.request_id}")
        print(f"   status: {response.data.status}")
        return True

    except Exception as e:
        import traceback
        print(f"❌ 多模态 add 失败: {e}")
        traceback.print_exc()
        return False
    finally:
        try:
            os.unlink(tmp_path)
        except Exception:
            pass


def main():
    base_url = os.environ.get("EVER_OS_BASE_URL", "https://api.evermind.ai")
    api_key_set = bool(os.environ.get("EVEROS_API_KEY"))

    print("=" * 60)
    print("EverOS Python SDK 功能测试")
    print("=" * 60)
    print(f"BASE_URL:  {base_url}")
    print(f"API_KEY:   {'已设置' if api_key_set else '❌ 未设置（请设置 EVEROS_API_KEY）'}")
    print(f"OWNER_ID:  {OWNER_ID}")
    print(f"SESSION:   {SESSION_ID}")

    if not api_key_set:
        print("\n❌ 缺少 EVEROS_API_KEY，退出")
        return 1

    results = {
        "add sync":          test_add_sync(),
        "add async_mode":    test_add_async_mode(),
        "add AsyncEverOS":   asyncio.run(test_add_async_client()),
        "search":            test_search_memories(),
        "get":               test_get_memories(),
        "add multimodal":    test_add_multimodal(),
    }

    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)
    for name, passed in results.items():
        print(f"{name:20} {'✅ 通过' if passed else '❌ 失败'}")

    all_passed = all(results.values())
    print("\n" + ("✅ 全部通过" if all_passed else "❌ 部分失败"))
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
