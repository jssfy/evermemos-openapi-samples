# everos should've been installed:
# pip install https://pkg.stainless.com/s/everos-trial-python/ea677a49282be2c1723740b1a7fa943cc01e0d5a/everos-0.0.1-py3-none-any.whl
#
# Migration notes from old v1:
#   - client.v1.memories  → client.v1.memory  (singular)
#   - user_id             → owner_id + owner_type="user"
#   - session_id is now REQUIRED
import asyncio
import time
from everos import AsyncEverOS

memory = AsyncEverOS().v1.memory


async def main() -> None:
    response = await memory.add(
        owner_id="user_001",
        owner_type="user",
        session_id="session_001",
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
