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
    # Batch import historical messages
    # Import conversation metadata and message list, messages will be added to processing queue
    group_id = os.environ.get("EVERMEMOS_GROUP_ID", "group_import_001")
    
    # Check base_url configuration
    base_url = os.environ.get("EVER_MEM_OS_CLIENT_BASE_URL")
    if not base_url:
        print("⚠️  Warning: EVER_MEM_OS_CLIENT_BASE_URL environment variable not set")
        print("   Please ensure base_url is configured correctly and the server supports /api/v1/memories/import endpoint")
    else:
        print(f"Using base_url: {base_url}")
    
    try:
        import_response = await client.v1.memories.load(
            conversation_meta={
                "group_id": group_id,
                "name": "Test Import Conversation",
                "scene": "group_chat",  # or "assistant"
                "scene_desc": {
                    "description": "Conversation for testing batch import functionality",
                    "purpose": "Testing",
                },
                "description": "This is a conversation metadata for testing batch import functionality",
                "created_at": datetime.now(timezone.utc).isoformat(),
                "default_timezone": "Asia/Shanghai",
                "tags": ["test", "import"],
                "user_details": {
                    "user_001": {
                        "full_name": "User One",
                        "role": "user",
                        "custom_role": "Test User",
                    },
                    "user_002": {
                        "full_name": "User Two",
                        "role": "user",
                        "custom_role": "Test User",
                    },
                },
            },
            conversation_list=[
                {
                    "message_id": f"msg_{int(datetime.now(timezone.utc).timestamp() * 1000)}_1",
                    "content": "This is the first test message",
                    "create_time": datetime.now(timezone.utc).isoformat(),
                    "sender": "user_001",
                    "sender_name": "User One",
                    "role": "user",
                    "type": "text",
                },
                {
                    "message_id": f"msg_{int(datetime.now(timezone.utc).timestamp() * 1000)}_2",
                    "content": "This is the second test message for verifying batch import functionality",
                    "create_time": datetime.now(timezone.utc).isoformat(),
                    "sender": "user_002",
                    "sender_name": "User Two",
                    "role": "user",
                    "type": "text",
                },
                {
                    "message_id": f"msg_{int(datetime.now(timezone.utc).timestamp() * 1000)}_3",
                    "content": "This is the third test message",
                    "create_time": datetime.now(timezone.utc).isoformat(),
                    "sender": "user_001",
                    "sender_name": "User One",
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
            print(f"\nHint: You can use the following request_id to query processing status:")
            print(f"  request_id: {import_response.request_id}")
            print(f"\nExample query command:")
            print(f"  EVERMEMOS_REQUEST_ID={import_response.request_id} python get_request_status_async.py")
    
    except Exception as e:
        print(f"\n❌ Error: {type(e).__name__}")
        print(f"   Message: {str(e)}")
        
        # Print detailed error information returned by server
        if hasattr(e, 'response'):
            print(f"\n📋 Server response details:")
            print(f"   Status code: {e.response.status_code}")
            print(f"   Request URL: {e.response.request.url}")
            print(f"   Request method: {e.response.request.method}")
            
            # Print response headers
            if e.response.headers:
                print(f"\n   Response headers:")
                for key, value in e.response.headers.items():
                    print(f"     {key}: {value}")
        
        # Print response body
        if hasattr(e, 'body'):
            print(f"\n📄 Server response body:")
            import json
            if isinstance(e.body, dict):
                print(f"   {json.dumps(e.body, indent=2, ensure_ascii=False)}")
            elif isinstance(e.body, str):
                print(f"   {e.body}")
            else:
                print(f"   {repr(e.body)}")
        
        # If it's a 404 error, provide more help information
        if "404" in str(e) or "Not Found" in str(e) or (hasattr(e, 'status_code') and e.status_code == 404):
            print(f"\n💡 Possible solutions:")
            print(f"   1. Check if EVER_MEM_OS_CLIENT_BASE_URL is configured correctly")
            print(f"   2. Confirm if the server supports /api/v1/memories/import endpoint")
            print(f"      - This endpoint may not be available in some environments")
            print(f"      - If the endpoint does not exist, consider using create() method to create memories one by one")
            print(f"   3. Check if base_url contains the correct protocol (http:// or https://)")
            print(f"   4. Confirm there is no trailing slash at the end of base_url")
            print(f"\n   Current base_url: {base_url or '(not set)'}")
            print(f"\n   Alternative solutions:")
            print(f"   - If /api/v1/memories/import endpoint is not available, you can use add_async.py or batch_add_async.py")
            print(f"   - First use create_meta_async.py to create conversation metadata")
            print(f"   - Then use add_async.py to add messages one by one")
        
        raise


if __name__ == "__main__":
    asyncio.run(main())
