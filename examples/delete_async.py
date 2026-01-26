import os
import asyncio
from evermemos import AsyncEverMemOS
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
    # 示例1: 先找一个event_id，比如通过 search 获取   
    event_id = "6976cbf5c07e8a28d9fb069e"
    
    # 根据 event_id 删除记忆
    delete_response = await client.v1.memories.delete(
        event_id=event_id,
    )
    print(f"删除结果 - message: {delete_response.message}")
    print(f"删除结果 - status: {delete_response.status}")
    if delete_response.result:
        print(f"删除数量: {delete_response.result.count}")
        if delete_response.result.filters:
            print(f"使用的过滤条件: {delete_response.result.filters}")

    # 示例2: 删除特定用户的所有记忆
    delete_response = await client.v1.memories.delete(
        user_id="user_001",
    )
    print(f"\n删除结果 - message: {delete_response.message}")
    print(f"删除结果 - status: {delete_response.status}")
    if delete_response.result:
        print(f"删除数量: {delete_response.result.count}")

    # 示例3: 删除特定用户在特定组中的记忆
    delete_response = await client.v1.memories.delete(
        user_id="user_001",
        group_id="group_project_123",
    )
    print(f"\n删除结果 - message: {delete_response.message}")
    print(f"删除结果 - status: {delete_response.status}")
    if delete_response.result:
        print(f"删除数量: {delete_response.result.count}")


if __name__ == "__main__":
    asyncio.run(main())
