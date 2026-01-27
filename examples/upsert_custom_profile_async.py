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
    # 创建或更新用户自定义档案
    # 该接口会合并现有数据，重叠字段会被输入覆盖
    user_id = os.environ.get("EVERMEMOS_USER_ID", "user_001")
    
    custom_profile_response = await client.v1.global_user_profile.custom.upsert(
        user_id=user_id,
        custom_profile_data={
            "initial_profile": [
                "用户是一名软件工程师",
                "用户精通 Python 编程",
                "用户对 AI 技术感兴趣",
                "用户喜欢阅读技术文档",
            ],
        },
    )
    
    print(f"message: {custom_profile_response.message}")
    print(f"success: {custom_profile_response.success}")
    
    if custom_profile_response.data:
        print(f"\n档案数据:")
        print(f"  id: {custom_profile_response.data.get('id')}")
        print(f"  user_id: {custom_profile_response.data.get('user_id')}")
        print(f"  confidence: {custom_profile_response.data.get('confidence')}")
        print(f"  memcell_count: {custom_profile_response.data.get('memcell_count')}")
        print(f"  created_at: {custom_profile_response.data.get('created_at')}")
        print(f"  updated_at: {custom_profile_response.data.get('updated_at')}")
        
        custom_profile_data = custom_profile_response.data.get('custom_profile_data')
        if custom_profile_data:
            print(f"  custom_profile_data:")
            initial_profile = custom_profile_data.get('initial_profile', [])
            if initial_profile:
                for idx, profile_item in enumerate(initial_profile, 1):
                    print(f"    {idx}. {profile_item}")
    else:
        print("\n档案数据: (无)")


if __name__ == "__main__":
    asyncio.run(main())
