import os
import asyncio
from evermemos import AsyncEverMemOS, NotFoundError

client = AsyncEverMemOS(
    api_key=os.environ.get(
        "EVERMEMOS_API_KEY",
    ),
    base_url=os.environ.get(
        "EVER_MEM_OS_CLIENT_BASE_URL",
    ),
)


async def main() -> None:
    # 示例1: 获取特定群组的对话元数据
    # 如果 group_id 不存在，会回退到默认配置
    meta_response = await client.v1.memories.conversation_meta.get(
        extra_query={
            "group_id": "group_project_123",
        }
    )
    print(f"获取结果 - message: {meta_response.message}")
    print(f"获取结果 - status: {meta_response.status}")
    if meta_response.result:
        print(f"元数据 ID: {meta_response.result.id}")
        print(f"对话名称: {meta_response.result.name}")
        print(f"场景: {meta_response.result.scene}")
        print(f"版本: {meta_response.result.version}")
        print(f"群组 ID: {meta_response.result.group_id}")
        print(f"是否默认配置: {meta_response.result.is_default}")
        if meta_response.result.description:
            print(f"描述: {meta_response.result.description}")
        if meta_response.result.default_timezone:
            print(f"默认时区: {meta_response.result.default_timezone}")
        if meta_response.result.tags:
            print(f"标签: {meta_response.result.tags}")
        if meta_response.result.user_details:
            print(f"用户详情: {meta_response.result.user_details}")

    # 示例2: 获取默认配置（不提供 group_id）
    # 注意：如果默认配置不存在，会抛出 NotFoundError
    print("\n" + "=" * 50)
    print("获取默认配置:")
    try:
        default_meta = await client.v1.memories.conversation_meta.get()
        print(f"获取结果 - message: {default_meta.message}")
        print(f"获取结果 - status: {default_meta.status}")
        if default_meta.result:
            print(f"元数据 ID: {default_meta.result.id}")
            print(f"对话名称: {default_meta.result.name}")
            print(f"场景: {default_meta.result.scene}")
            print(f"是否默认配置: {default_meta.result.is_default}")
    except NotFoundError as e:
        print(f"未找到默认配置: {e}")
        print("提示: 需要先使用 create 方法创建默认配置（不提供 group_id）")


if __name__ == "__main__":
    asyncio.run(main())
