# everos should've been installed (pip install everos -U)
# Migration notes from v0:
#   - v0 used extra_body={"event_id": ...} as a workaround; v1 exposes memory_id directly
#   - v1 delete has two MUTUALLY EXCLUSIVE modes:
#       Mode A — by ID:      delete(memory_id=...) — no other params allowed
#       Mode B — by filter:  delete(user_id=..., group_id=...) — no memory_id allowed
#   - v1 delete returns None (no response object)
import asyncio
from everos import AsyncEverOS, NotFoundError, UnprocessableEntityError

memories = AsyncEverOS().v1.memories


async def main() -> None:
    # Example 1: Delete memory by memory_id (was event_id in v0 via extra_body workaround)
    memory_id = "6976cbf5c07e8a28d9fb069e"
    print("=" * 50)
    print("Example 1: Delete memory by memory_id")
    print(f"memory_id: {memory_id}")
    try:
        await memories.delete(memory_id=memory_id)
        print("Deleted successfully")
    except (NotFoundError, UnprocessableEntityError) as e:
        print(f"No matching memory found or invalid request: {e}")

    # Example 2: Delete all memories for a specific user
    print("\n" + "=" * 50)
    print("Example 2: Delete all memories for a specific user")
    print("user_id: user_001")
    try:
        await memories.delete(user_id="user_001")
        print("Deleted successfully")
    except (NotFoundError, UnprocessableEntityError) as e:
        print(f"No matching memory found or invalid request: {e}")

    # Example 3: Delete memories for a specific user in a specific group
    print("\n" + "=" * 50)
    print("Example 3: Delete memories for a specific user in a specific group")
    print("user_id: user_001, group_id: group_project_123")
    try:
        await memories.delete(user_id="user_001", group_id="group_project_123")
        print("Deleted successfully")
    except (NotFoundError, UnprocessableEntityError) as e:
        print(f"No matching memory found or invalid request: {e}")


if __name__ == "__main__":
    asyncio.run(main())
