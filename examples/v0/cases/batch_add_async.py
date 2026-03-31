#!/usr/bin/env python3
# EverMemOS should've been installed (pip install evermemos -U)
"""
Batch add memories to EverMemOS
Read file and split by periods, output and add to memory library each time exceeding specified character count
Use generator approach, compress empty lines and multiple spaces into a single space
Only use SDK approach
"""

import os
import re
import sys
import asyncio
from typing import Generator, Optional
from datetime import datetime, timezone
from evermemos import AsyncEverMemOS

memories = AsyncEverMemOS().v0.memories


def normalize_text(text: str) -> str:
    """
    Compress empty lines and multiple spaces into a single space
    
    Args:
        text: Original text
        
    Returns:
        Normalized text
    """
    # Replace all whitespace characters (including newlines, tabs, multiple spaces) with a single space
    text = re.sub(r'\s+', ' ', text)
    # Remove leading and trailing spaces
    text = text.strip()
    return text


def is_chapter_title(text: str) -> bool:
    """
    Check if text starts with "Chapter xxx" pattern
    
    Args:
        text: Text to check
        
    Returns:
        True if it's a chapter title, False otherwise
    """
    # Match pattern starting with "第" + number/Chinese number + "章"
    pattern = r'^第[一二三四五六七八九十百千万\d]+章'
    return bool(re.match(pattern, text.strip()))


def read_file_chunks(file_path: str, chunk_size: int = 1000) -> Generator[str, None, None]:
    """
    Read file and split by periods, output each time exceeding specified character count
    If encountering text starting with "Chapter xxx", output separately without merging with previous paragraph
    
    Args:
        file_path: File path
        chunk_size: Minimum character count per chunk (default 1000)
        
    Yields:
        Each text chunk (string)
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"错误: 文件 '{file_path}' 不存在", file=sys.stderr)
        return
    except Exception as e:
        print(f"错误: 读取文件时发生异常: {e}", file=sys.stderr)
        return
    
    # Normalize text: compress empty lines and multiple spaces
    content = normalize_text(content)
    
    # Use regex to find all chapter title positions and insert special markers before them
    # Match text starting with "Chapter xxx"
    chapter_pattern = r'(第[一二三四五六七八九十百千万\d]+章)'
    # Insert special marker before chapter title (using a string unlikely to appear in text)
    marked_content = re.sub(chapter_pattern, r'|||CHAPTER_TITLE|||\1', content)
    
    # Split by special marker
    segments = marked_content.split('|||CHAPTER_TITLE|||')
    
    current_chunk = ""
    
    for idx, segment in enumerate(segments):
        if not segment.strip():
            continue
        
        segment_stripped = segment.strip()
        
        # First segment is text before chapter title, process directly
        # First part of other segments should be chapter title
        if idx == 0:
            # First segment, not a chapter title, process directly
            parts = re.split(r'([。！？])', segment)
        else:
            # Check if current segment starts with chapter title
            if is_chapter_title(segment_stripped):
                # If there's accumulated chunk, output it first
                if current_chunk.strip():
                    yield current_chunk.strip()
                    current_chunk = ""
                # Extract chapter title as start of new chunk
                match = re.match(r'(第[一二三四五六七八九十百千万\d]+章)', segment_stripped)
                if match:
                    chapter_title = match.group(1)
                    # Use chapter title as start of new chunk (ensure space after)
                    current_chunk = chapter_title
                    # If there's content after chapter title, continue processing
                    remaining = segment_stripped[len(chapter_title):].strip()
                    if remaining:
                        # Ensure space between chapter title and following content
                        if not current_chunk.endswith(' '):
                            current_chunk += ' '
                        segment = remaining
                        parts = re.split(r'([。！？])', segment)
                    else:
                        continue
                else:
                    # If match fails, process entire segment directly
                    parts = re.split(r'([。！？])', segment)
            else:
                # Not a chapter title, split text by period, exclamation, question mark (preserve delimiters)
                parts = re.split(r'([。！？])', segment)
        
        # Process text parts (split by periods)
        
        i = 0
        while i < len(parts):
            part = parts[i].strip()
            if not part:
                i += 1
                continue
            
            # If current part is punctuation
            if part in ['。', '！', '？']:
                if current_chunk:
                    current_chunk += part
                    # Check if current chunk reaches or exceeds chunk_size
                    if len(current_chunk) >= chunk_size:
                        yield current_chunk.strip()
                        current_chunk = ""
                i += 1
                continue
            
            # Current part is text content
            # Check if adding this part exceeds chunk_size
            test_chunk = current_chunk + part if current_chunk else part
            
            # If single sentence exceeds chunk_size, output directly
            if len(part) >= chunk_size:
                if current_chunk.strip():
                    yield current_chunk.strip()
                    current_chunk = ""
                yield part
                i += 1
                continue
            
            # Check if adding reaches chunk_size
            if len(test_chunk) >= chunk_size:
                # If there's next punctuation, add it first then output
                if i + 1 < len(parts) and parts[i + 1] in ['。', '！', '？']:
                    test_chunk += parts[i + 1]
                    yield test_chunk.strip()
                    current_chunk = ""
                    i += 2
                else:
                    # No punctuation, output current chunk directly
                    if current_chunk.strip():
                        yield current_chunk.strip()
                    current_chunk = part
                    i += 1
            else:
                # Not reached chunk_size yet, continue accumulating
                current_chunk = test_chunk
                # If there's next punctuation, add it too
                if i + 1 < len(parts) and parts[i + 1] in ['。', '！', '？']:
                    current_chunk += parts[i + 1]
                    i += 2
                else:
                    i += 1
    
    # Output remaining text
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
    Add memory to memory library using SDK approach
    
    Args:
        chunk: Text chunk content
        chunk_count: Chunk number
        group_id: Group ID
        group_name: Group name
        sender: Sender ID
        sender_name: Sender name
        
    Returns:
        True on success, False on failure
    """
    try:
        # Generate message ID, including chunk number
        message_id = f"chunk_{chunk_count}_{int(datetime.now(timezone.utc).timestamp() * 1000)}"
        
        create_time = datetime.now(timezone.utc).isoformat()
        sender_val = sender or "user_001"
        response = await memories.add(
            content=chunk,
            create_time=create_time,
            message_id=message_id,
            sender=sender_val,
            sender_name=sender_name,
            group_id=group_id,
            group_name=group_name,
        )
        print(f"✓ 块 {chunk_count} 已成功添加到记忆库 (长度: {len(chunk)} 字符)")
        print(f"  add 参数: content_len={len(chunk)}, create_time={create_time!r}, message_id={message_id!r}, sender={sender_val!r}, sender_name={sender_name!r}, group_id={group_id!r}, group_name={group_name!r}")
        return True
    except Exception as e:
        print(f"✗ 块 {chunk_count} 添加到记忆库失败: {e}", file=sys.stderr)
        return False


async def main() -> None:
    """Main function"""
    if len(sys.argv) < 2:
        print("用法: python batch_add_async.py <文件路径> [块大小] [起始块号] [最大块数]", file=sys.stderr)
        print("示例: python batch_add_async.py input.txt 1000", file=sys.stderr)
        print("示例: python batch_add_async.py input.txt 1000 5  # 从第5块开始", file=sys.stderr)
        print("示例: python batch_add_async.py input.txt 1000 1 10  # 从第1块开始，处理10个块", file=sys.stderr)
        print("\n环境变量配置（可选，已有默认值）:", file=sys.stderr)
        print("  EVERMEMOS_API_KEY: API密钥（必需）", file=sys.stderr)
        print("  EVER_MEM_OS_CLIENT_BASE_URL: API地址（可选）", file=sys.stderr)
        print("  EVERMEMOS_GROUP_ID: 群组ID（默认: group_123）", file=sys.stderr)
        print("  EVERMEMOS_GROUP_NAME: 群组名称（默认: Project Discussion Group）", file=sys.stderr)
        print("  EVERMEMOS_SENDER: 发送者ID（默认: user_001）", file=sys.stderr)
        print("  EVERMEMOS_SENDER_NAME: 发送者名称（默认: User）", file=sys.stderr)
        sys.exit(1)
    
    file_path = sys.argv[1]
    chunk_size = int(sys.argv[2]) if len(sys.argv) > 2 else 1000
    start_from = int(sys.argv[3]) if len(sys.argv) > 3 else 1
    max_blocks = int(sys.argv[4]) if len(sys.argv) > 4 else None
    
    # Read configuration from environment variables, set default values
    group_id = os.getenv("EVERMEMOS_GROUP_ID", "group_123")
    group_name = os.getenv("EVERMEMOS_GROUP_NAME", "Project Discussion Group")
    sender = os.getenv("EVERMEMOS_SENDER", "user_001")
    sender_name = os.getenv("EVERMEMOS_SENDER_NAME", "User")
    
    print(f"读取文件: {file_path}")
    print(f"块大小: {chunk_size} 字符")
    if start_from > 1:
        print(f"从第 {start_from} 块开始处理")
    if max_blocks is not None:
        print(f"最多处理 {max_blocks} 个块")
    print(f"记忆库: 已配置 (方式: SDK, 群组: {group_id})")
    print("-" * 50)
    
    chunk_count = 0
    total_chars = 0
    processed_count = 0
    success_count = 0
    failed_at_chunk = None
    
    for chunk in read_file_chunks(file_path, chunk_size):
        chunk_count += 1
        
        # Skip previous chunks
        if chunk_count < start_from:
            continue
        
        # Check if reached maximum processing block count
        if max_blocks is not None and processed_count >= max_blocks:
            break
        
        processed_count += 1
        chunk_length = len(chunk)
        total_chars += chunk_length
        
        print(f"\n[块 {chunk_count}] (长度: {chunk_length} 字符)")
        print(f"内容预览: {chunk[:100]}..." if len(chunk) > 100 else f"内容: {chunk}")
        print("-" * 50)
        
        # Call SDK to add memory
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
            # On failure, record progress and stop
            failed_at_chunk = chunk_count
            print(f"\n❌ 处理失败，已停止。成功处理 {success_count} 个块，失败于第 {failed_at_chunk} 个块", file=sys.stderr)
            break
    
    # Output statistics
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
