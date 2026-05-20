# everos should've been installed:
# pip install https://pkg.stainless.com/s/everos-trial-python/ea677a49282be2c1723740b1a7fa943cc01e0d5a/everos-0.0.1-py3-none-any.whl
#
# Migration notes from old v1:
#   - memories.get(filters={"user_id": ...}, memory_type=...)
#     → memory.get(owner_id=..., owner_type=..., memory_type=...)
#   - New memory_type values: "agent_case", "agent_skill" (in addition to "episodic_memory", "profile")
#   - New sort params: sort_by=("timestamp"|"updated_at"), sort_order=("asc"|"desc")
import asyncio
from everos import AsyncEverOS
from pprint import pprint

memory = AsyncEverOS().v1.memory


async def main() -> None:
    # Example 1: Get episodic memories for a user
    print("=== episodic_memory ===")
    response = await memory.get(
        owner_id="user_011",
        owner_type="user",
        memory_type="episodic_memory",
        page_size=5,
        sort_by="timestamp",
        sort_order="desc",
    )
    pprint(response)

    # Example 2: Get user profile
    print("\n=== profile ===")
    response = await memory.get(
        owner_id="user_011",
        owner_type="user",
        memory_type="profile",
    )
    pprint(response)

    # Example 3: Get agent cases (NEW in 0.0.1 — agent-type memory)
    print("\n=== agent_case (owner_type=agent) ===")
    response = await memory.get(
        owner_id="agent_001",
        owner_type="agent",
        memory_type="agent_case",
        page_size=5,
    )
    pprint(response)

    # Example 4: Get agent skills (NEW in 0.0.1)
    print("\n=== agent_skill (owner_type=agent) ===")
    response = await memory.get(
        owner_id="agent_001",
        owner_type="agent",
        memory_type="agent_skill",
        page_size=5,
    )
    pprint(response)


if __name__ == "__main__":
    asyncio.run(main())
