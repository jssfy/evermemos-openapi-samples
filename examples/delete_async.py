import os
import asyncio
from evermemos import AsyncEverMemOS, NotFoundError
from datetime import datetime, timezone

client = AsyncEverMemOS(
    api_key=os.environ.get(
        "EVERMEMOS_API_KEY",
    ),
    base_url=os.environ.get(
        "EVER_MEM_OS_CLIENT_BASE_URL",
    ),
)


async def main() -> None:
    # 示例1: 根据 event_id 删除记忆
    # 注意: 如果 event_id 不存在或已被删除，会抛出 NotFoundError
    event_id = "6976cbf5c07e8a28d9fb069e"
    print("=" * 50)
    print("示例1: 根据 event_id 删除记忆")
    print(f"event_id: {event_id}")
    try:
        delete_response = await client.v1.memories.delete(
            event_id=event_id,
        )
        print(f"删除结果 - message: {delete_response.message}")
        print(f"删除结果 - status: {delete_response.status}")
        if delete_response.result:
            print(f"删除数量: {delete_response.result.count}")
            if delete_response.result.filters:
                print(f"使用的过滤条件: {delete_response.result.filters}")
    except NotFoundError as e:
        print(f"未找到匹配的记忆: {e}")
        print("提示: 该 event_id 可能不存在或已被删除")

    # 示例2: 删除特定用户的所有记忆
    print("\n" + "=" * 50)
    print("示例2: 删除特定用户的所有记忆")
    print("user_id: user_001")
    try:
        delete_response = await client.v1.memories.delete(
            user_id="user_001",
        )
        print(f"删除结果 - message: {delete_response.message}")
        print(f"删除结果 - status: {delete_response.status}")
        if delete_response.result:
            print(f"删除数量: {delete_response.result.count}")
    except NotFoundError as e:
        print(f"未找到匹配的记忆: {e}")
        print("提示: 该用户可能没有记忆记录")

    # 示例3: 删除特定用户在特定组中的记忆
    print("\n" + "=" * 50)
    print("示例3: 删除特定用户在特定组中的记忆")
    print("user_id: user_001, group_id: group_project_123")
    try:
        delete_response = await client.v1.memories.delete(
            user_id="user_001",
            group_id="group_project_123",
        )
        print(f"删除结果 - message: {delete_response.message}")
        print(f"删除结果 - status: {delete_response.status}")
        if delete_response.result:
            print(f"删除数量: {delete_response.result.count}")
    except NotFoundError as e:
        print(f"未找到匹配的记忆: {e}")
        print("提示: 该用户在指定群组中可能没有记忆记录")


if __name__ == "__main__":
    asyncio.run(main())
