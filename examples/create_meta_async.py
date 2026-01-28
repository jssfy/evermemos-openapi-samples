import asyncio
from evermemos import AsyncEverMemOS
from datetime import datetime, timezone

client = AsyncEverMemOS()


async def main() -> None:
    # Create conversation metadata
    # If group_id exists, it will update the entire record (upsert)
    # If group_id does not exist, it will create a new record
    # If group_id is omitted, it will be saved as the default configuration for the scene
    meta_response = await client.v1.memories.conversation_meta.create(
        created_at=datetime.now(timezone.utc).isoformat(),
        name="Project Discussion Group",
        scene="group_chat",  # or "assistant"
        scene_desc={
            "description": "Group for project collaboration and discussion",
            "purpose": "Team collaboration",
        },
        group_id="group_project_123",  # Optional, if provided, targets a specific group
        description="This is a metadata configuration for a project discussion group",
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
    print(f"Create result - message: {meta_response.message}")
    print(f"Create result - status: {meta_response.status}")
    if meta_response.result:
        print(f"Metadata ID: {meta_response.result.id}")
        print(f"Conversation name: {meta_response.result.name}")
        print(f"Scene: {meta_response.result.scene}")
        print(f"Group ID: {meta_response.result.group_id}")
        print(f"Is default config: {meta_response.result.is_default}")


if __name__ == "__main__":
    asyncio.run(main())
