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
    # 获取记忆
    memory_result = await client.v1.memories.list(
        extra_query={
            "user_id": "天下霸唱",
            "memory_type": "profile",
        }
    )
    print(f"message: {memory_result.message}")
    print(f"status: {memory_result.status}")
    if memory_result.result:
        print(f"total_count: {memory_result.result.total_count}")
        if memory_result.result.memories:
            print(f"找到 {len(memory_result.result.memories)} 条记忆")
            for idx, memory in enumerate(memory_result.result.memories[:5], 1):  # 最多显示5条
                print(f"\n记忆 {idx}:")
                # 所有记忆类型都有 id
                if hasattr(memory, 'id') and memory.id:
                    print(f"  id: {memory.id}")
                # 所有记忆类型都有 user_id
                if hasattr(memory, 'user_id') and memory.user_id:
                    print(f"  user_id: {memory.user_id}")
                # Profile 类型特有属性
                if hasattr(memory, 'profile_data') and memory.profile_data:
                    print(f"  profile_data: {memory.profile_data}")
                if hasattr(memory, 'scenario') and memory.scenario:
                    print(f"  scenario: {memory.scenario}")
                if hasattr(memory, 'confidence') and memory.confidence is not None:
                    print(f"  confidence: {memory.confidence}")
                # EpisodicMemory 类型特有属性
                if hasattr(memory, 'episode_id') and memory.episode_id:
                    print(f"  episode_id: {memory.episode_id}")
                if hasattr(memory, 'title') and memory.title:
                    print(f"  title: {memory.title}")
                if hasattr(memory, 'summary') and memory.summary:
                    print(f"  summary: {memory.summary}")
                # EventLog 类型特有属性
                if hasattr(memory, 'atomic_fact') and memory.atomic_fact:
                    print(f"  atomic_fact: {memory.atomic_fact}")
                if hasattr(memory, 'event_type') and memory.event_type:
                    print(f"  event_type: {memory.event_type}")
                # Foresight 类型特有属性
                if hasattr(memory, 'content') and memory.content:
                    print(f"  content: {memory.content}")
                # 通用属性
                if hasattr(memory, 'group_id') and memory.group_id:
                    print(f"  group_id: {memory.group_id}")
                if hasattr(memory, 'group_name') and memory.group_name:
                    print(f"  group_name: {memory.group_name}")
                if hasattr(memory, 'timestamp') and memory.timestamp:
                    print(f"  timestamp: {memory.timestamp}")
                if hasattr(memory, 'created_at') and memory.created_at:
                    print(f"  created_at: {memory.created_at}")
                if hasattr(memory, 'updated_at') and memory.updated_at:
                    print(f"  updated_at: {memory.updated_at}")


if __name__ == "__main__":
    asyncio.run(main())
