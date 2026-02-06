# EverMemOS should've been installed (pip install evermemos -U)
import asyncio
from evermemos import AsyncEverMemOS
from datetime import datetime, timezone

memories = AsyncEverMemOS().v0.memories

async def main() -> None:
    response = await memories.add(
        content="I love basketball & swimming. I am scared of snakes.",
        create_time=datetime.now(timezone.utc).isoformat(),
        message_id=f"msg_{int(datetime.now(timezone.utc).timestamp() * 1000)}",
        sender="user_001",
    )
    print(response)

if __name__ == "__main__":
    asyncio.run(main())
