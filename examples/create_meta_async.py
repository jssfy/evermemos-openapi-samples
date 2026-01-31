# EverMemOS should've been installed (pip install evermemos -U)
import asyncio
from evermemos import AsyncEverMemOS
from datetime import datetime, timezone

conversation_meta = AsyncEverMemOS().v1.memories.conversation_meta


async def main() -> None:
    # Create conversation metadata
    # If group_id exists, it will update the entire record (upsert)
    # If group_id does not exist, it will create a new record
    # If group_id is omitted, it will be saved as the default configuration for the scene
    response = await conversation_meta.create(
        created_at=datetime.now(timezone.utc).isoformat(),
        name="Project Discussion Group",
        # Do not pass scene_desc when group_id is set - scene is inherited from global config
        group_id="group_project_123",  # Optional, if provided, targets a specific group
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
    print(f"Create result - message: {response.message}")
    print(f"Create result - status: {response.status}")
    if response.result:
        print(f"Metadata ID: {response.result.id}")
        print(f"Conversation name: {response.result.name}")
        print(f"Scene: {response.result.scene}")
        print(f"Group ID: {response.result.group_id}")
        print(f"Is default config: {response.result.is_default}")


if __name__ == "__main__":
    asyncio.run(main())
