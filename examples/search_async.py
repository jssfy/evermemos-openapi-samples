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
    # Search memories
    # Problem analysis:
    # 1. curl succeeds: directly sends JSON body, backend directly parses
    # 2. SDK fails: SDK may merge with default parameters when processing extra_body, causing parameter conflicts
    #    Error message shows: user_id and group_id cannot both be MAGIC_ALL
    #    But code only sets user_id="__all__", group_id="0122_series_1"
    #    This suggests SDK may have converted group_id to "__all__" when merging parameters
    #
    # Solutions:
    # - Solution 1: Don't set user_id, only set group_id (recommended)
    # - Solution 2: Use extra_query (verified to work)
    
    search_result = await client.v1.memories.search(
        extra_query={
            "group_id": "0122_series_1",
            "memory_types": ["episodic_memory"],
            "top_k": 20,
        }
    )
    print("✓ Using extra_query succeeded")
    print("Search memory results:")
    print(f"  message: {search_result.message}")
    print(f"  status: {search_result.status}")
    if search_result.result:
        print(f"  total_count: {search_result.result.total_count}")
        print(f"  has_more: {search_result.result.has_more}")
        if search_result.result.memories and search_result.result.total_count > 0:
            print(f"  Found {len(search_result.result.memories)} memory groups")
            # Print detailed information of all memories
            total_memories_count = 0
            for idx, memory_group in enumerate(search_result.result.memories, 1):
                print(f"\n  Memory group {idx}:")
                for group_id, memories in memory_group.items():
                    print(f"    Group ID: {group_id}")
                    print(f"    This group has {len(memories)} memories")
                    # Show all memories (removed [:2] limit)
                    for mem_idx, mem in enumerate(memories, 1):
                        total_memories_count += 1
                        print(f"      Memory {mem_idx}:")
                        print(f"        - user_id: {mem.user_id}")
                        print(f"        - timestamp: {mem.timestamp}")
                        # Print subject field if it exists
                        if hasattr(mem, 'subject') and mem.subject:
                            print(f"        - subject: {mem.subject}")
                        elif hasattr(mem, 'subject'):
                            print(f"        - subject: (empty)")
            print(f"\n  Total displayed {total_memories_count} memories (total_count: {search_result.result.total_count})")
        
        # Print pending messages
        if hasattr(search_result.result, 'pending_messages') and search_result.result.pending_messages:
            print(f"\n  Pending messages ({len(search_result.result.pending_messages)}):")
            for idx, msg in enumerate(search_result.result.pending_messages[:5], 1):  # Show at most 5
                print(f"\n  Message {idx}:")
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
