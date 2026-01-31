# EverMemOS should've been installed (pip install evermemos -U)
import asyncio
from evermemos import AsyncEverMemOS
from debug_helpers import print_dict

memories = AsyncEverMemOS().v1.memories


async def main() -> None:
    response = await memories.get(
        extra_query={
            "user_id": "user_011",
            "memory_type": "episodic_memory",
        }
    )

    # print(response)
    print_dict(response)


if __name__ == "__main__":
    asyncio.run(main())
