import os
import asyncio
from evermemos import AsyncEverMemOS
from datetime import datetime, timezone

client = AsyncEverMemOS()


async def main() -> None:
    # Batch import historical messages
    # Import conversation metadata and message list, messages will be added to processing queue
    group_id = os.environ.get("EVERMEMOS_GROUP_ID", "group_import_001")
    
    try:
        # Prepare conversation_meta dictionary
        # Note: We'll use extra_body to force-add the version field
        conversation_meta_dict = {
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
        }
        
        import_response = await client.v1.memories.load(
            conversation_meta=conversation_meta_dict,
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
            version="1.0.0",  # Format version parameter (required by SDK)
            # Workaround: Use extra_body to force-merge version into conversation_meta
            # This bypasses SDK's TypedDict validation and ensures version is included
            # in the conversation_meta object sent to the backend
            extra_body={
                "conversation_meta": {
                    **conversation_meta_dict,
                    "version": "1.0.0",  # This version field will be merged into conversation_meta
                }
            },
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
        
        raise


if __name__ == "__main__":
    asyncio.run(main())
