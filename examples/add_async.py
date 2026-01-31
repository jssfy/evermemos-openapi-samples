import asyncio
from evermemos import AsyncEverMemOS
from datetime import datetime, timezone

client = AsyncEverMemOS()


async def main() -> None:
    memory = await client.v1.memories.add(
        content="Using isoformat() to generate RFC3339/ISO 8601 formatted time string",
        create_time=datetime.now(timezone.utc).isoformat(),
        message_id=f"msg_{int(datetime.now(timezone.utc).timestamp() * 1000)}",
        sender="user_001",
    )
    print(memory.message)
    print(memory.status)


if __name__ == "__main__":
    asyncio.run(main())
