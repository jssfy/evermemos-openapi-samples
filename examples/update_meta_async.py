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
    # 部分更新对话元数据
    # 只更新提供的字段，未提供的字段保持不变
    # 通过 group_id 定位要更新的对话元数据
    # 如果 group_id 为 null 或不提供，则更新默认配置
    meta_response = await client.v1.memories.conversation_meta.update(
        group_id="group_project_123",  # 可选，如果提供则更新特定群组，否则更新默认配置
        name="更新后的项目讨论组名称",
        description="更新后的描述信息",
        tags=["项目", "协作", "开发", "更新"],
        default_timezone="Asia/Shanghai",
        scene_desc={
            "description": "更新后的场景描述",
            "purpose": "团队协作和项目管理",
        },
        user_details={
            "user_001": {
                "full_name": "张三（已更新）",
                "role": "user",
                "custom_role": "高级开发工程师",
                "extra": {
                    "department": "技术部",
                    "level": "senior",
                },
            },
            "user_003": {
                "full_name": "王五",
                "role": "user",
                "custom_role": "测试工程师",
            },
        },
    )
    print(f"更新结果 - message: {meta_response.message}")
    print(f"更新结果 - status: {meta_response.status}")
    if meta_response.result:
        print(f"元数据 ID: {meta_response.result.id}")
        print(f"群组 ID: {meta_response.result.group_id}")
        if meta_response.result.updated_fields:
            print(f"已更新的字段: {meta_response.result.updated_fields}")
        if meta_response.result.updated_at:
            print(f"更新时间: {meta_response.result.updated_at}")


if __name__ == "__main__":
    asyncio.run(main())
