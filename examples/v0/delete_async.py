# EverMemOS should've been installed (pip install evermemos -U)
import asyncio
from evermemos import AsyncEverMemOS, NotFoundError, UnprocessableEntityError
from datetime import datetime, timezone

memories = AsyncEverMemOS().v0.memories


async def main() -> None:
    # Example 1: Delete memory by event_id
    # Note: Backend API expects 'event_id', but SDK wraps it as 'memory_id'
    # We use extra_body to pass the correct parameter to backend
    event_id = "6976cbf5c07e8a28d9fb069e"
    print("=" * 50)
    print("Example 1: Delete memory by event_id")
    print(f"event_id: {event_id}")
    try:
        response = await memories.delete(
            extra_body={"event_id": event_id},
        )
        print(response)
    except (NotFoundError, UnprocessableEntityError) as e:
        print(f"No matching memory found or invalid request: {e}")

    # Example 2: Delete all memories for a specific user
    print("\n" + "=" * 50)
    print("Example 2: Delete all memories for a specific user")
    print("user_id: user_001")
    try:
        response = await memories.delete(
            user_id="user_001",
        )
        print(response)
    except (NotFoundError, UnprocessableEntityError) as e:
        print(f"No matching memory found or invalid request: {e}")

    # Example 3: Delete memories for a specific user in a specific group
    print("\n" + "=" * 50)
    print("Example 3: Delete memories for a specific user in a specific group")
    print("user_id: user_001, group_id: group_project_123")
    try:
        response = await memories.delete(
            user_id="user_001",
            group_id="group_project_123",
        )
        print(response)
    except (NotFoundError, UnprocessableEntityError) as e:
        print(f"No matching memory found or invalid request: {e}")


if __name__ == "__main__":
    asyncio.run(main())
