# EverMemOS should've been installed (pip install evermemos -U)
import asyncio
from evermemos import AsyncEverMemOS, NotFoundError

conversation_meta = AsyncEverMemOS().v0.memories.conversation_meta


async def main() -> None:
    response = await conversation_meta.get(
        extra_query={
            "group_id": "group_project_123",
        }
    )
    print(response)

if __name__ == "__main__":
    asyncio.run(main())
