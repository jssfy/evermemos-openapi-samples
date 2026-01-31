import asyncio
from evermemos import AsyncEverMemOS
from datetime import datetime, timezone

memories = AsyncEverMemOS().v1.memories

async def main() -> None:
    response = await memories.add(
        content="Using isoformat() to generate RFC3339/ISO 8601 formatted time string",
        create_time=datetime.now(timezone.utc).isoformat(),
        message_id=f"msg_{int(datetime.now(timezone.utc).timestamp() * 1000)}",
        sender="user_001",
    )
    print(response)

if __name__ == "__main__":
    asyncio.run(main())
