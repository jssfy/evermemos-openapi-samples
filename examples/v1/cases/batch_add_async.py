#!/usr/bin/env python3
# everos should've been installed (pip install everos -U)
"""
Batch add memories to EverOS (v1)
Migration notes from v0:
  - memories.add(group_id=..., group_name=..., sender=..., sender_name=...) is REMOVED
  - Group memories → memories.group.add(group_id=..., group_meta={...}, messages=[...])
  - create_time (ISO string) → timestamp (unix milliseconds): int(time.time() * 1000)
  - message_id still supported inside each message object
  - Env vars: EVERMEMOS_* → EVEROS_*
"""

import os
import re
import sys
import asyncio
import time
from typing import Generator, Optional
from everos import AsyncEverOS

client = AsyncEverOS()
group_mem = client.v1.memories.group


def normalize_text(text: str) -> str:
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()
    return text


def is_chapter_title(text: str) -> bool:
    pattern = r'^第[一二三四五六七八九十百千万\d]+章'
    return bool(re.match(pattern, text.strip()))


def read_file_chunks(file_path: str, chunk_size: int = 1000) -> Generator[str, None, None]:
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"错误: 文件 '{file_path}' 不存在", file=sys.stderr)
        return
    except Exception as e:
        print(f"错误: 读取文件时发生异常: {e}", file=sys.stderr)
        return

    content = normalize_text(content)

    chapter_pattern = r'(第[一二三四五六七八九十百千万\d]+章)'
    marked_content = re.sub(chapter_pattern, r'|||CHAPTER_TITLE|||\1', content)
    segments = marked_content.split('|||CHAPTER_TITLE|||')

    current_chunk = ""

    for idx, segment in enumerate(segments):
        if not segment.strip():
            continue

        segment_stripped = segment.strip()

        if idx == 0:
            parts = re.split(r'([。！？])', segment)
        else:
            if is_chapter_title(segment_stripped):
                if current_chunk.strip():
                    yield current_chunk.strip()
                    current_chunk = ""
                match = re.match(r'(第[一二三四五六七八九十百千万\d]+章)', segment_stripped)
                if match:
                    chapter_title = match.group(1)
                    current_chunk = chapter_title
                    remaining = segment_stripped[len(chapter_title):].strip()
                    if remaining:
                        if not current_chunk.endswith(' '):
                            current_chunk += ' '
                        segment = remaining
                        parts = re.split(r'([。！？])', segment)
                    else:
                        continue
                else:
                    parts = re.split(r'([。！？])', segment)
            else:
                parts = re.split(r'([。！？])', segment)

        i = 0
        while i < len(parts):
            part = parts[i].strip()
            if not part:
                i += 1
                continue

            if part in ['。', '！', '？']:
                if current_chunk:
                    current_chunk += part
                    if len(current_chunk) >= chunk_size:
                        yield current_chunk.strip()
                        current_chunk = ""
                i += 1
                continue

            test_chunk = current_chunk + part if current_chunk else part

            if len(part) >= chunk_size:
                if current_chunk.strip():
                    yield current_chunk.strip()
                    current_chunk = ""
                yield part
                i += 1
                continue

            if len(test_chunk) >= chunk_size:
                if i + 1 < len(parts) and parts[i + 1] in ['。', '！', '？']:
                    test_chunk += parts[i + 1]
                    yield test_chunk.strip()
                    current_chunk = ""
                    i += 2
                else:
                    if current_chunk.strip():
                        yield current_chunk.strip()
                    current_chunk = part
                    i += 1
            else:
                current_chunk = test_chunk
                if i + 1 < len(parts) and parts[i + 1] in ['。', '！', '？']:
                    current_chunk += parts[i + 1]
                    i += 2
                else:
                    i += 1

    if current_chunk.strip():
        yield current_chunk.strip()


async def add_memory_batch(
    chunk: str,
    chunk_count: int,
    group_id: str,
    group_name: Optional[str] = None,
    sender: Optional[str] = None,
    sender_name: Optional[str] = None,
) -> bool:
    """
    Add memory to memory library using v1 group.add()

    Args:
        chunk: Text chunk content
        chunk_count: Chunk number
        group_id: Group ID
        group_name: Group name (used in group_meta)
        sender: Sender ID (sender_id in v1 message)
        sender_name: Sender name (optional)

    Returns:
        True on success, False on failure
    """
    try:
        message_id = f"chunk_{chunk_count}_{int(time.time() * 1000)}"
        timestamp = int(time.time() * 1000)
        sender_id = sender or "user_001"

        response = await group_mem.add(
            group_id=group_id,
            group_meta={"name": group_name or group_id},
            messages=[
                {
                    "role": "user",
                    "sender_id": sender_id,
                    "sender_name": sender_name,
                    "timestamp": timestamp,
                    "content": chunk,
                    "message_id": message_id,
                }
            ],
        )
        print(f"✓ 块 {chunk_count} 已成功添加到记忆库 (长度: {len(chunk)} 字符)")
        print(f"  add 参数: content_len={len(chunk)}, timestamp={timestamp}, message_id={message_id!r}, sender_id={sender_id!r}, sender_name={sender_name!r}, group_id={group_id!r}")
        return True
    except Exception as e:
        print(f"✗ 块 {chunk_count} 添加到记忆库失败: {e}", file=sys.stderr)
        return False


async def main() -> None:
    if len(sys.argv) < 2:
        print("用法: python batch_add_async.py <文件路径> [块大小] [起始块号] [最大块数]", file=sys.stderr)
        print("示例: python batch_add_async.py input.txt 1000", file=sys.stderr)
        print("示例: python batch_add_async.py input.txt 1000 5  # 从第5块开始", file=sys.stderr)
        print("示例: python batch_add_async.py input.txt 1000 1 10  # 从第1块开始，处理10个块", file=sys.stderr)
        print("\n环境变量配置（可选，已有默认值）:", file=sys.stderr)
        print("  EVEROS_API_KEY: API密钥（必需）", file=sys.stderr)
        print("  EVER_OS_BASE_URL: API地址（可选）", file=sys.stderr)
        print("  EVEROS_GROUP_ID: 群组ID（默认: group_123）", file=sys.stderr)
        print("  EVEROS_GROUP_NAME: 群组名称（默认: Project Discussion Group）", file=sys.stderr)
        print("  EVEROS_SENDER: 发送者ID（默认: user_001）", file=sys.stderr)
        print("  EVEROS_SENDER_NAME: 发送者名称（默认: User）", file=sys.stderr)
        sys.exit(1)

    file_path = sys.argv[1]
    chunk_size = int(sys.argv[2]) if len(sys.argv) > 2 else 1000
    start_from = int(sys.argv[3]) if len(sys.argv) > 3 else 1
    max_blocks = int(sys.argv[4]) if len(sys.argv) > 4 else None

    group_id = os.getenv("EVEROS_GROUP_ID", "group_123")
    group_name = os.getenv("EVEROS_GROUP_NAME", "Project Discussion Group")
    sender = os.getenv("EVEROS_SENDER", "user_001")
    sender_name = os.getenv("EVEROS_SENDER_NAME", "User")

    print(f"读取文件: {file_path}")
    print(f"块大小: {chunk_size} 字符")
    if start_from > 1:
        print(f"从第 {start_from} 块开始处理")
    if max_blocks is not None:
        print(f"最多处理 {max_blocks} 个块")
    print(f"记忆库: 已配置 (方式: SDK v1 group.add, 群组: {group_id})")
    print("-" * 50)

    chunk_count = 0
    total_chars = 0
    processed_count = 0
    success_count = 0
    failed_at_chunk = None

    for chunk in read_file_chunks(file_path, chunk_size):
        chunk_count += 1

        if chunk_count < start_from:
            continue

        if max_blocks is not None and processed_count >= max_blocks:
            break

        processed_count += 1
        chunk_length = len(chunk)
        total_chars += chunk_length

        print(f"\n[块 {chunk_count}] (长度: {chunk_length} 字符)")
        print(f"内容预览: {chunk[:100]}..." if len(chunk) > 100 else f"内容: {chunk}")
        print("-" * 50)

        success = await add_memory_batch(
            chunk=chunk,
            chunk_count=chunk_count,
            group_id=group_id,
            group_name=group_name,
            sender=sender,
            sender_name=sender_name,
        )

        if success:
            success_count += 1
        else:
            failed_at_chunk = chunk_count
            print(f"\n❌ 处理失败，已停止。成功处理 {success_count} 个块，失败于第 {failed_at_chunk} 个块", file=sys.stderr)
            break

    print("\n" + "=" * 50)
    if start_from > 1 and chunk_count > 0:
        skipped_count = start_from - 1
        print(f"已跳过前 {skipped_count} 个块")
    if max_blocks is not None and processed_count >= max_blocks:
        print(f"已达到最大处理块数限制 ({max_blocks} 个块)")
    if failed_at_chunk:
        print(f"❌ 处理失败于第 {failed_at_chunk} 个块")
        print(f"成功处理: {success_count} 个块")
    else:
        print(f"✓ 所有块已成功添加到记忆库 ({success_count} 个)")
    if chunk_count > 0:
        print(f"总计: 共 {chunk_count} 个块, 处理 {processed_count} 个块, 处理内容共 {total_chars} 个字符")


if __name__ == "__main__":
    asyncio.run(main())
