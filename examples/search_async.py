# EverMemOS should've been installed (pip install evermemos -U)
import asyncio
from evermemos import AsyncEverMemOS
from debug_helpers import print_dict

memories = AsyncEverMemOS().v1.memories


async def main() -> None:
    
    response = await memories.search(
        extra_query={
            # "group_id": "anhua_group_004",
            "user_id": "user_011",
            "memory_types": ["episodic_memory"],
            "top_k": 1,
        },
    )

    print(response)
    # print_dict(response)

if __name__ == "__main__":
    asyncio.run(main())
