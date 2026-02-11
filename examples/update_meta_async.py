# EverMemOS should've been installed (pip install evermemos -U)
import asyncio
from evermemos import AsyncEverMemOS

conversation_meta = AsyncEverMemOS().v0.memories.conversation_meta


async def main() -> None:
    response = await conversation_meta.update(
        tags=["project", "collaboration", "development", "update"],
        default_timezone="Asia/Shanghai",
        user_details={
            "user_001": {
                "full_name": "Zhang San (Updated)",
                "role": "user",
                "custom_role": "Senior Software Engineer",
                "extra": {
                    "department": "Engineering",
                    "level": "senior",
                },
            },
            "user_003": {
                "full_name": "Wang Wu",
                "role": "user",
                "custom_role": "Test Engineer",
            },
        },
        extra_body={
            "group_id": "group_project_123",  # Optional, if provided, update specific group, otherwise update default config
            "name": "Updated Project Discussion Group Name",
        },
    )
    print(response)


if __name__ == "__main__":
    asyncio.run(main())
