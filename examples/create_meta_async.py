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
    # 创建对话元数据
    # 如果 group_id 存在，会更新整个记录（upsert）
    # 如果 group_id 不存在，会创建新记录
    # 如果 group_id 省略，会保存为场景的默认配置
    meta_response = await client.v1.memories.conversation_meta.create(
        created_at=datetime.now(timezone.utc).isoformat(),
        name="项目讨论组",
        scene="group_chat",  # 或 "assistant"
        scene_desc={
            "description": "用于项目协作和讨论的群组",
            "purpose": "团队协作",
        },
        version="1.0",
        group_id="group_project_123",  # 可选，如果提供则针对特定群组
        description="这是一个项目讨论组的元数据配置",
        default_timezone="Asia/Shanghai",
        tags=["项目", "协作", "开发"],
        user_details={
            "user_001": {
                "full_name": "张三",
                "role": "user",  # 或 "assistant"
                "custom_role": "开发工程师",
                "extra": {
                    "department": "技术部",
                },
            },
            "user_002": {
                "full_name": "李四",
                "role": "user",
                "custom_role": "产品经理",
            },
        },
    )
    print(f"创建结果 - message: {meta_response.message}")
    print(f"创建结果 - status: {meta_response.status}")
    if meta_response.result:
        print(f"元数据 ID: {meta_response.result.id}")
        print(f"对话名称: {meta_response.result.name}")
        print(f"场景: {meta_response.result.scene}")
        print(f"群组 ID: {meta_response.result.group_id}")
        print(f"是否默认配置: {meta_response.result.is_default}")


if __name__ == "__main__":
    asyncio.run(main())
