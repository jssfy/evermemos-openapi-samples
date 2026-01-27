#!/usr/bin/env python3
"""
批量添加记忆到 EverMemOS
读取文件并按句号截断，每超过指定字数输出一次并添加到记忆库
使用生成器方式输出，压缩空行和多个空格为一个空格
仅使用 SDK 方式
"""

import os
import re
import sys
import asyncio
from typing import Generator, Optional
from datetime import datetime, timezone
from evermemos import AsyncEverMemOS

client = AsyncEverMemOS(
    api_key=os.environ.get("EVERMEMOS_API_KEY"),
    base_url=os.environ.get("EVER_MEM_OS_CLIENT_BASE_URL"),
)


def normalize_text(text: str) -> str:
    """
    压缩空行和多个空格为一个空格
    
    Args:
        text: 原始文本
        
    Returns:
        规范化后的文本
    """
    # 将所有空白字符（包括换行、制表符、多个空格）替换为单个空格
    text = re.sub(r'\s+', ' ', text)
    # 去除首尾空格
    text = text.strip()
    return text


def is_chapter_title(text: str) -> bool:
    """
    判断文本是否以"第xxx章"开头
    
    Args:
        text: 要检查的文本
        
    Returns:
        如果是章节标题返回True，否则返回False
    """
    # 匹配"第" + 数字/中文数字 + "章"开头的模式
    pattern = r'^第[一二三四五六七八九十百千万\d]+章'
    return bool(re.match(pattern, text.strip()))


def read_file_chunks(file_path: str, chunk_size: int = 1000) -> Generator[str, None, None]:
    """
    读取文件并按句号截断，每超过指定字数输出一次
    如果遇到"第xxx章"开头的文本，会单独输出，不合并到上一段
    
    Args:
        file_path: 文件路径
        chunk_size: 每个块的最小字符数（默认1000）
        
    Yields:
        每个文本块（字符串）
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
    
    # 规范化文本：压缩空行和多个空格
    content = normalize_text(content)
    
    # 使用正则表达式找到所有章节标题的位置，并在前面插入特殊标记
    # 匹配"第xxx章"开头的文本
    chapter_pattern = r'(第[一二三四五六七八九十百千万\d]+章)'
    # 在章节标题前插入特殊标记（使用一个不太可能出现在文本中的字符串）
    marked_content = re.sub(chapter_pattern, r'|||CHAPTER_TITLE|||\1', content)
    
    # 按特殊标记分割
    segments = marked_content.split('|||CHAPTER_TITLE|||')
    
    current_chunk = ""
    
    for idx, segment in enumerate(segments):
        if not segment.strip():
            continue
        
        segment_stripped = segment.strip()
        
        # 第一个segment是章节标题之前的文本，直接处理
        # 其他segment的第一个部分应该是章节标题
        if idx == 0:
            # 第一个segment，不是章节标题，直接处理
            parts = re.split(r'([。！？])', segment)
        else:
            # 检查当前段是否以章节标题开头
            if is_chapter_title(segment_stripped):
                # 如果当前有累积的块，先输出
                if current_chunk.strip():
                    yield current_chunk.strip()
                    current_chunk = ""
                # 提取章节标题，作为新块的开始
                match = re.match(r'(第[一二三四五六七八九十百千万\d]+章)', segment_stripped)
                if match:
                    chapter_title = match.group(1)
                    # 将章节标题作为新块的开始（确保后面有空格）
                    current_chunk = chapter_title
                    # 如果章节标题后面还有内容，继续处理
                    remaining = segment_stripped[len(chapter_title):].strip()
                    if remaining:
                        # 确保章节标题和后续内容之间有空格
                        if not current_chunk.endswith(' '):
                            current_chunk += ' '
                        segment = remaining
                        parts = re.split(r'([。！？])', segment)
                    else:
                        continue
                else:
                    # 如果匹配失败，直接处理整个段
                    parts = re.split(r'([。！？])', segment)
            else:
                # 不是章节标题，按句号、感叹号、问号分割文本（保留分隔符）
                parts = re.split(r'([。！？])', segment)
        
        # 处理文本部分（按句号分割）
        
        i = 0
        while i < len(parts):
            part = parts[i].strip()
            if not part:
                i += 1
                continue
            
            # 如果当前部分是标点符号
            if part in ['。', '！', '？']:
                if current_chunk:
                    current_chunk += part
                    # 检查当前块是否达到或超过chunk_size
                    if len(current_chunk) >= chunk_size:
                        yield current_chunk.strip()
                        current_chunk = ""
                i += 1
                continue
            
            # 当前部分是文本内容
            # 检查添加这个部分后是否超过chunk_size
            test_chunk = current_chunk + part if current_chunk else part
            
            # 如果单个句子就超过chunk_size，直接输出
            if len(part) >= chunk_size:
                if current_chunk.strip():
                    yield current_chunk.strip()
                    current_chunk = ""
                yield part
                i += 1
                continue
            
            # 检查添加后是否达到chunk_size
            if len(test_chunk) >= chunk_size:
                # 如果有下一个标点符号，先加上再输出
                if i + 1 < len(parts) and parts[i + 1] in ['。', '！', '？']:
                    test_chunk += parts[i + 1]
                    yield test_chunk.strip()
                    current_chunk = ""
                    i += 2
                else:
                    # 没有标点符号，直接输出当前块
                    if current_chunk.strip():
                        yield current_chunk.strip()
                    current_chunk = part
                    i += 1
            else:
                # 还没达到chunk_size，继续累积
                current_chunk = test_chunk
                # 如果有下一个标点符号，也加上
                if i + 1 < len(parts) and parts[i + 1] in ['。', '！', '？']:
                    current_chunk += parts[i + 1]
                    i += 2
                else:
                    i += 1
    
    # 输出剩余的文本
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
    使用 SDK 方式添加记忆到记忆库
    
    Args:
        chunk: 文本块内容
        chunk_count: 块编号
        group_id: 群组ID
        group_name: 群组名称
        sender: 发送者ID
        sender_name: 发送者名称
        
    Returns:
        成功返回True，失败返回False
    """
    try:
        # 生成消息ID，包含块编号
        message_id = f"chunk_{chunk_count}_{int(datetime.now(timezone.utc).timestamp() * 1000)}"
        
        memory = await client.v1.memories.create(
            content=chunk,
            create_time=datetime.now(timezone.utc).isoformat(),
            message_id=message_id,
            sender=sender or "user_001",
            sender_name=sender_name,
            group_id=group_id,
            group_name=group_name,
        )
        print(f"✓ 块 {chunk_count} 已成功添加到记忆库 (长度: {len(chunk)} 字符)")
        return True
    except Exception as e:
        print(f"✗ 块 {chunk_count} 添加到记忆库失败: {e}", file=sys.stderr)
        return False


async def main() -> None:
    """主函数"""
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
    
    # 从环境变量读取配置，设置默认值
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
        
        # 跳过前面的块
        if chunk_count < start_from:
            continue
        
        # 检查是否达到最大处理块数
        if max_blocks is not None and processed_count >= max_blocks:
            break
        
        processed_count += 1
        chunk_length = len(chunk)
        total_chars += chunk_length
        
        print(f"\n[块 {chunk_count}] (长度: {chunk_length} 字符)")
        print(f"内容预览: {chunk[:100]}..." if len(chunk) > 100 else f"内容: {chunk}")
        print("-" * 50)
        
        # 调用 SDK 添加记忆
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
            # 失败则记录进度并结束
            failed_at_chunk = chunk_count
            print(f"\n❌ 处理失败，已停止。成功处理 {success_count} 个块，失败于第 {failed_at_chunk} 个块", file=sys.stderr)
            break
    
    # 输出统计信息
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
