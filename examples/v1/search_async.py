# everos should've been installed (pip install everos -U)
# Migration notes from v0:
#   - v0 group_ids (plural array) → v1 filters support one group_id at a time
#   - v0 calls without a query string have been converted to memories.get()
#     (use memories.search() only when you have a meaningful semantic query)
import asyncio
from everos import AsyncEverOS
from pprint import pprint

memories = AsyncEverOS().v1.memories


async def main() -> None:
    # Search 1: list episodic memories by group (no semantic query → use get())
    # v0: search(extra_query={"group_ids": ["anhua_group_004", "anhua_group_005"], ...})
    for group_id in ["anhua_group_004", "anhua_group_005"]:
        response = await memories.get(
            filters={"group_id": group_id},
            memory_type="episodic_memory",
            page_size=1,
        )
        print(response)

    # Search 2: list episodic memories by user (no semantic query → use get())
    # v0: search(extra_query={"user_id": "user_011", "memory_types": [...], "top_k": 1})
    response = await memories.get(
        filters={"user_id": "user_011"},
        memory_type="episodic_memory",
        page_size=1,
    )
    print(response)


if __name__ == "__main__":
    asyncio.run(main())
