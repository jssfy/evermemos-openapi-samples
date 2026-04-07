# everos should've been installed (pip install everos -U)
import asyncio
from everos import AsyncEverOS
from pprint import pprint

memories = AsyncEverOS().v1.memories


async def main() -> None:
    response = await memories.get(
        filters={"user_id": "user_011"},
        memory_type="episodic_memory",
    )
    pprint(response)


if __name__ == "__main__":
    asyncio.run(main())
