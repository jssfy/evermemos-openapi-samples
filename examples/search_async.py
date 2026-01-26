import os
import asyncio
from evermemos import AsyncEverMemOS

client = AsyncEverMemOS(
    api_key=os.environ.get(
        "EVERMEMOS_API_KEY",
    ),
    base_url=os.environ.get(
        "EVER_MEM_OS_CLIENT_BASE_URL",
    ),
)


async def main() -> None:
    # 搜索记忆
    # 问题分析：
    # 1. curl 成功：直接发送 JSON body，后端直接解析
    # 2. SDK 失败：SDK 在处理 extra_body 时，可能与默认参数合并，导致参数冲突
    #    错误信息显示：user_id 和 group_id 不能同时为 MAGIC_ALL
    #    但代码中只设置了 user_id="__all__"，group_id="0122_series_1"
    #    说明 SDK 可能在合并参数时，将 group_id 也转换成了 "__all__"
    #
    # 解决方案：
    # - 方案1：不设置 user_id，只设置 group_id（推荐）
    # - 方案2：使用 extra_query（已验证可用）
    
    search_result = await client.v1.memories.search(
        extra_query={
            "group_id": "0122_series_1",
            "memory_types": ["episodic_memory"],
            "top_k": 20,
        }
    )
    print("✓ 使用 extra_query 成功")
    print("搜索记忆结果:")
    print(f"  message: {search_result.message}")
    print(f"  status: {search_result.status}")
    if search_result.result:
        print(f"  total_count: {search_result.result.total_count}")
        print(f"  has_more: {search_result.result.has_more}")
        if search_result.result.memories and search_result.result.total_count > 0:
            print(f"  找到 {len(search_result.result.memories)} 组记忆")
            # 打印所有记忆的详细信息
            total_memories_count = 0
            for idx, memory_group in enumerate(search_result.result.memories, 1):
                print(f"\n  记忆组 {idx}:")
                for group_id, memories in memory_group.items():
                    print(f"    群组ID: {group_id}")
                    print(f"    该组共有 {len(memories)} 条记忆")
                    # 显示所有记忆（移除 [:2] 限制）
                    for mem_idx, mem in enumerate(memories, 1):
                        total_memories_count += 1
                        print(f"      记忆 {mem_idx}:")
                        print(f"        - user_id: {mem.user_id}")
                        print(f"        - timestamp: {mem.timestamp}")
                        # 打印 subject 字段（如果存在）
                        if hasattr(mem, 'subject') and mem.subject:
                            print(f"        - subject: {mem.subject}")
                        elif hasattr(mem, 'subject'):
                            print(f"        - subject: (空)")
            print(f"\n  总计显示 {total_memories_count} 条记忆（total_count: {search_result.result.total_count}）")
        
        # 打印待处理消息
        if hasattr(search_result.result, 'pending_messages') and search_result.result.pending_messages:
            print(f"\n  待处理消息 ({len(search_result.result.pending_messages)} 条):")
            for idx, msg in enumerate(search_result.result.pending_messages[:5], 1):  # 最多显示5条
                print(f"\n  消息 {idx}:")
                print(f"    id: {msg.id}")
                print(f"    message_id: {msg.message_id}")
                print(f"    group_id: {msg.group_id}")
                print(f"    user_id: {msg.user_id}")
                print(f"    sender: {msg.sender}")
                if hasattr(msg, 'sender_name') and msg.sender_name:
                    print(f"    sender_name: {msg.sender_name}")
                if hasattr(msg, 'group_name') and msg.group_name:
                    print(f"    group_name: {msg.group_name}")
                print(f"    content: {msg.content}")
                if hasattr(msg, 'refer_list') and msg.refer_list:
                    print(f"    refer_list: {msg.refer_list}")
                if hasattr(msg, 'message_create_time') and msg.message_create_time:
                    print(f"    message_create_time: {msg.message_create_time}")
                if hasattr(msg, 'created_at') and msg.created_at:
                    print(f"    created_at: {msg.created_at}")


if __name__ == "__main__":
    asyncio.run(main())
