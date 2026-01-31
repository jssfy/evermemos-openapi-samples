# EverMemOS should've been installed (pip install evermemos -U)
import asyncio
from evermemos import AsyncEverMemOS
from datetime import datetime, timezone

conversation_meta = AsyncEverMemOS().v1.memories.conversation_meta


async def main() -> None:
    response = await conversation_meta.create(
        created_at=datetime.now(timezone.utc).isoformat(),
        name="Project Discussion Group",
        group_id="group_project_123",
        default_timezone="Asia/Shanghai",
        tags=["project", "collaboration", "development"],
        user_details={
            "user_001": {
                "full_name": "Zhang San",
                "role": "user",  # or "assistant"
                "custom_role": "Software Engineer",
                "extra": {
                    "department": "Engineering",
                },
            },
            "user_002": {
                "full_name": "Li Si",
                "role": "user",
                "custom_role": "Product Manager",
            },
        },
    )
    print(response)

if __name__ == "__main__":
    asyncio.run(main())
