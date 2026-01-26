import os
import asyncio
from evermemos import AsyncEverMemOS
from datetime import datetime, timezone

client = AsyncEverMemOS(
    api_key=os.environ.get(
        "EVERMEMOS_API_KEY",
    ),
    base_url=os.environ.get(
        "EVER_MEM_OS_CLIENT_BASE_URL",
    ),
)


async def main() -> None:
    memory = await client.v1.memories.create(
        content="使用 isoformat() 生成 RFC3339/ISO 8601 格式的时间字符串",
        create_time=datetime.now(timezone.utc).isoformat(),
        message_id=f"msg_{int(datetime.now(timezone.utc).timestamp() * 1000)}",
        sender="user_001",
    )
    print(memory.message)
    print(memory.status)


if __name__ == "__main__":
    asyncio.run(main())
