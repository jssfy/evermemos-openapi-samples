import asyncio
from evermemos import AsyncEverMemOS

conversation_meta = AsyncEverMemOS().v1.memories.conversation_meta


async def main() -> None:
    # Partially update conversation metadata
    # Only update provided fields, unprovided fields remain unchanged
    # Locate the conversation metadata to update by group_id
    # If group_id is null or not provided, update the default configuration
    response = await conversation_meta.update(
        group_id="group_project_123",  # Optional, if provided, update specific group, otherwise update default config
        name="Updated Project Discussion Group Name",
        tags=["project", "collaboration", "development", "update"],
        default_timezone="Asia/Shanghai",
        scene_desc={
            "description": "Updated scene description",
            "purpose": "Team collaboration and project management",
        },
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
    )
    print(f"Update result - message: {response.message}")
    print(f"Update result - status: {response.status}")
    if response.result:
        print(f"Metadata ID: {response.result.id}")
        print(f"Group ID: {response.result.group_id}")
        if response.result.updated_fields:
            print(f"Updated fields: {response.result.updated_fields}")
        if response.result.updated_at:
            print(f"Updated at: {response.result.updated_at}")


if __name__ == "__main__":
    asyncio.run(main())
