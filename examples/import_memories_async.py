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
    # 批量导入历史消息
    # 导入对话元数据和消息列表，消息会被加入处理队列
    group_id = os.environ.get("EVERMEMOS_GROUP_ID", "group_import_001")
    
    # 检查 base_url 配置
    base_url = os.environ.get("EVER_MEM_OS_CLIENT_BASE_URL")
    if not base_url:
        print("⚠️  警告: 未设置 EVER_MEM_OS_CLIENT_BASE_URL 环境变量")
        print("   请确保 base_url 配置正确，且服务器端支持 /api/v1/memories/import 端点")
    else:
        print(f"使用 base_url: {base_url}")
    
    try:
        import_response = await client.v1.memories.load(
        conversation_meta={
            "group_id": group_id,
            "name": "测试导入对话",
            "scene": "group_chat",  # 或 "assistant"
            "scene_desc": {
                "description": "用于测试批量导入功能的对话",
                "purpose": "测试",
            },
            "description": "这是一个测试批量导入功能的对话元数据",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "default_timezone": "Asia/Shanghai",
            "tags": ["测试", "导入"],
            "user_details": {
                "user_001": {
                    "full_name": "用户一",
                    "role": "user",
                    "custom_role": "测试用户",
                },
                "user_002": {
                    "full_name": "用户二",
                    "role": "user",
                    "custom_role": "测试用户",
                },
            },
        },
        conversation_list=[
            {
                "message_id": f"msg_{int(datetime.now(timezone.utc).timestamp() * 1000)}_1",
                "content": "这是第一条测试消息",
                "create_time": datetime.now(timezone.utc).isoformat(),
                "sender": "user_001",
                "sender_name": "用户一",
                "role": "user",
                "type": "text",
            },
            {
                "message_id": f"msg_{int(datetime.now(timezone.utc).timestamp() * 1000)}_2",
                "content": "这是第二条测试消息，用于验证批量导入功能",
                "create_time": datetime.now(timezone.utc).isoformat(),
                "sender": "user_002",
                "sender_name": "用户二",
                "role": "user",
                "type": "text",
            },
            {
                "message_id": f"msg_{int(datetime.now(timezone.utc).timestamp() * 1000)}_3",
                "content": "这是第三条测试消息",
                "create_time": datetime.now(timezone.utc).isoformat(),
                "sender": "user_001",
                "sender_name": "用户一",
                "role": "user",
                "type": "text",
            },
        ],
            version="1.0.0",
        )
        
        print(f"message: {import_response.message}")
        print(f"status: {import_response.status}")
        print(f"imported_meta: {import_response.imported_meta}")
        print(f"total_count: {import_response.total_count}")
        print(f"request_id: {import_response.request_id}")
        
        if import_response.request_id:
            print(f"\n提示: 可以使用以下 request_id 查询处理状态:")
            print(f"  request_id: {import_response.request_id}")
            print(f"\n查询命令示例:")
            print(f"  EVERMEMOS_REQUEST_ID={import_response.request_id} python get_request_status_async.py")
    
    except Exception as e:
        print(f"\n❌ 错误: {type(e).__name__}")
        print(f"   消息: {str(e)}")
        
        # 如果是 404 错误，提供更多帮助信息
        if "404" in str(e) or "Not Found" in str(e):
            print(f"\n💡 可能的解决方案:")
            print(f"   1. 检查 EVER_MEM_OS_CLIENT_BASE_URL 是否正确配置")
            print(f"   2. 确认服务器端是否支持 /api/v1/memories/import 端点")
            print(f"   3. 检查 base_url 是否包含正确的协议 (http:// 或 https://)")
            print(f"   4. 确认 base_url 末尾没有多余的斜杠")
            print(f"\n   当前 base_url: {base_url or '(未设置)'}")
        
        raise


if __name__ == "__main__":
    asyncio.run(main())
