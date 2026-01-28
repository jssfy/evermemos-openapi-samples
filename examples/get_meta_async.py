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
    # Example 1: Get conversation metadata for a specific group
    # If group_id does not exist, it will fall back to default configuration
    meta_response = await client.v1.memories.conversation_meta.get(
        extra_query={
            "group_id": "group_project_123",
        }
    )
    print(f"Get result - message: {meta_response.message}")
    print(f"Get result - status: {meta_response.status}")
    if meta_response.result:
        print(f"Metadata ID: {meta_response.result.id}")
        print(f"Conversation name: {meta_response.result.name}")
        print(f"Scene: {meta_response.result.scene}")
        print(f"Group ID: {meta_response.result.group_id}")
        print(f"Is default config: {meta_response.result.is_default}")
        if hasattr(meta_response.result, 'version') and meta_response.result.version:
            print(f"Version: {meta_response.result.version}")
        if meta_response.result.description:
            print(f"Description: {meta_response.result.description}")
        if meta_response.result.default_timezone:
            print(f"Default timezone: {meta_response.result.default_timezone}")
        if meta_response.result.tags:
            print(f"Tags: {meta_response.result.tags}")
        if meta_response.result.user_details:
            print(f"User details: {meta_response.result.user_details}")

    # Example 2: Get default configuration (without providing group_id)
    # Note: If default configuration does not exist, NotFoundError will be raised
    print("\n" + "=" * 50)
    print("Exception test (without group_id):")
    try:
        default_meta = await client.v1.memories.conversation_meta.get()
        print(f"Get result - message: {default_meta.message}")
        print(f"Get result - status: {default_meta.status}")
        if default_meta.result:
            print(f"Metadata ID: {default_meta.result.id}")
            print(f"Conversation name: {default_meta.result.name}")
            print(f"Scene: {default_meta.result.scene}")
            print(f"Is default config: {default_meta.result.is_default}")
    except NotFoundError as e:
        print(f"Default configuration not found: {e}")
        print("Hint: Need to use create method first to create default configuration (without group_id)")


if __name__ == "__main__":
    asyncio.run(main())
