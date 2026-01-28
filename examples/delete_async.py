import os
import asyncio
from evermemos import AsyncEverMemOS, NotFoundError
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
    # Example 1: Delete memory by event_id
    # Note: If event_id does not exist or has been deleted, NotFoundError will be raised
    event_id = "6976cbf5c07e8a28d9fb069e"
    print("=" * 50)
    print("Example 1: Delete memory by event_id")
    print(f"event_id: {event_id}")
    try:
        delete_response = await client.v1.memories.delete(
            event_id=event_id,
        )
        print(f"Delete result - message: {delete_response.message}")
        print(f"Delete result - status: {delete_response.status}")
        if delete_response.result:
            print(f"Deleted count: {delete_response.result.count}")
            if delete_response.result.filters:
                print(f"Filters used: {delete_response.result.filters}")
    except NotFoundError as e:
        print(f"No matching memory found: {e}")
        print("Hint: The event_id may not exist or has been deleted")

    # Example 2: Delete all memories for a specific user
    print("\n" + "=" * 50)
    print("Example 2: Delete all memories for a specific user")
    print("user_id: user_001")
    try:
        delete_response = await client.v1.memories.delete(
            user_id="user_001",
        )
        print(f"Delete result - message: {delete_response.message}")
        print(f"Delete result - status: {delete_response.status}")
        if delete_response.result:
            print(f"Deleted count: {delete_response.result.count}")
    except NotFoundError as e:
        print(f"No matching memory found: {e}")
        print("Hint: The user may have no memory records")

    # Example 3: Delete memories for a specific user in a specific group
    print("\n" + "=" * 50)
    print("Example 3: Delete memories for a specific user in a specific group")
    print("user_id: user_001, group_id: group_project_123")
    try:
        delete_response = await client.v1.memories.delete(
            user_id="user_001",
            group_id="group_project_123",
        )
        print(f"Delete result - message: {delete_response.message}")
        print(f"Delete result - status: {delete_response.status}")
        if delete_response.result:
            print(f"Deleted count: {delete_response.result.count}")
    except NotFoundError as e:
        print(f"No matching memory found: {e}")
        print("Hint: The user may have no memory records in the specified group")


if __name__ == "__main__":
    asyncio.run(main())
