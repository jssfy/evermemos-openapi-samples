# everos should've been installed (pip install everos -U)
import asyncio
import time
from everos import AsyncEverOS

memories = AsyncEverOS().v1.memories


async def main() -> None:
    response = await memories.add(
        user_id="user_001",
        messages=[
            {
                "role": "user",
                "timestamp": int(time.time() * 1000),
                "content": "I love basketball & swimming. I am scared of snakes.",
            }
        ],
    )
    print(response)


if __name__ == "__main__":
    asyncio.run(main())
