# EverMemOS should've been installed (pip install evermemos -U)
import asyncio
from evermemos import AsyncEverMemOS, NotFoundError

conversation_meta = AsyncEverMemOS().v1.memories.conversation_meta


async def main() -> None:
    # Example 1: Get conversation metadata for a specific group
    # If group_id does not exist, it will fall back to default configuration
    response = await conversation_meta.get(
        extra_query={
            "group_id": "group_project_123",
        }
    )
    print(f"Get result - message: {response.message}")
    print(f"Get result - status: {response.status}")
    if response.result:
        print(f"Metadata ID: {response.result.id}")
        print(f"Conversation name: {response.result.name}")
        print(f"Scene: {response.result.scene}")
        print(f"Group ID: {response.result.group_id}")
        print(f"Is default config: {response.result.is_default}")
        if hasattr(response.result, 'version') and response.result.version:
            print(f"Version: {response.result.version}")
        if response.result.description:
            print(f"Description: {response.result.description}")
        if response.result.default_timezone:
            print(f"Default timezone: {response.result.default_timezone}")
        if response.result.tags:
            print(f"Tags: {response.result.tags}")
        if response.result.user_details:
            print(f"User details: {response.result.user_details}")

    # Example 2: Get default configuration (without providing group_id)
    # Note: If default configuration does not exist, NotFoundError will be raised
    print("\n" + "=" * 50)
    print("Exception test (without group_id):")
    try:
        response = await conversation_meta.get()
        print(f"Get result - message: {response.message}")
        print(f"Get result - status: {response.status}")
        if response.result:
            print(f"Metadata ID: {response.result.id}")
            print(f"Conversation name: {response.result.name}")
            print(f"Scene: {response.result.scene}")
            print(f"Is default config: {response.result.is_default}")
    except NotFoundError as e:
        print(f"Default configuration not found: {e}")
        print("Hint: Need to use create method first to create default configuration (without group_id)")


if __name__ == "__main__":
    asyncio.run(main())
