# EverMemOS should've been installed (pip install evermemos -U)
import asyncio
from evermemos import AsyncEverMemOS
from pprint import pprint

memories = AsyncEverMemOS().v0.memories


async def main() -> None:
    response = await memories.get(
        extra_query={
            "user_id": "user_011",
            "memory_type": "episodic_memory",
        }
    )

    # print(response)
    pprint(response)


if __name__ == "__main__":
    asyncio.run(main())
