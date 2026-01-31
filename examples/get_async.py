# EverMemOS should've been installed (pip install evermemos -U)
import asyncio
from evermemos import AsyncEverMemOS
from debug_helpers import print_dict

memories = AsyncEverMemOS().v1.memories


async def main() -> None:
    response = await memories.get(
        extra_query={
            "user_id": "anhua_004",
            # "memory_type": "profile",
        }
    )

    # print(response)
    print_dict(response)


if __name__ == "__main__":
    asyncio.run(main())
