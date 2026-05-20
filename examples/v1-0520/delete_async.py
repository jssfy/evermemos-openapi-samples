# everos should've been installed:
# pip install https://pkg.stainless.com/s/everos-trial-python/ea677a49282be2c1723740b1a7fa943cc01e0d5a/everos-0.0.1-py3-none-any.whl
#
# Migration notes from old v1:
#   - delete(user_id=..., group_id=...) → delete(owner_id=..., owner_type=..., session_id=...)
#   - All params are optional; at least one filter should be provided
#   - delete() still returns None on success
import asyncio
from everos import AsyncEverOS, NotFoundError, UnprocessableEntityError

memory = AsyncEverOS().v1.memory


async def main() -> None:
    # Example 1: Delete by memory_id (single record)
    print("=" * 50)
    print("Example 1: Delete by memory_id")
    memory_id = "6976cbf5c07e8a28d9fb069e"
    try:
        await memory.delete(memory_id=memory_id)
        print("Deleted successfully")
    except (NotFoundError, UnprocessableEntityError) as e:
        print(f"No matching memory or invalid request: {e}")

    # Example 2: Delete all memories for a specific user (all sessions)
    print("\n" + "=" * 50)
    print("Example 2: Delete all memories for user_001")
    try:
        await memory.delete(owner_id="user_001", owner_type="user")
        print("Deleted successfully")
    except (NotFoundError, UnprocessableEntityError) as e:
        print(f"No matching memory or invalid request: {e}")

    # Example 3: Delete memories for a specific session
    print("\n" + "=" * 50)
    print("Example 3: Delete memories for user_001 / session_001")
    try:
        await memory.delete(owner_id="user_001", owner_type="user", session_id="session_001")
        print("Deleted successfully")
    except (NotFoundError, UnprocessableEntityError) as e:
        print(f"No matching memory or invalid request: {e}")

    # Example 4: Delete all memories for an agent
    print("\n" + "=" * 50)
    print("Example 4: Delete all memories for agent_001")
    try:
        await memory.delete(owner_id="agent_001", owner_type="agent")
        print("Deleted successfully")
    except (NotFoundError, UnprocessableEntityError) as e:
        print(f"No matching memory or invalid request: {e}")


if __name__ == "__main__":
    asyncio.run(main())
