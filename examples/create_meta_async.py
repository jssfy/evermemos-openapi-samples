# EverMemOS should've been installed (pip install evermemos -U)
import asyncio
from evermemos import AsyncEverMemOS
from datetime import datetime, timezone

conversation_meta = AsyncEverMemOS().v0.memories.conversation_meta


async def create_global_config() -> None:
    """Create global config with llm_custom_setting.

    Note: llm_custom_setting is ONLY allowed for global config (group_id=null),
    not allowed for group config (group_id provided).
    """
    response = await conversation_meta.create(
        created_at=datetime.now(timezone.utc).isoformat(),
        scene="group_chat",  # Required for global config
        scene_desc={  # Required for global config
            "description": "Project discussion group chat",
            "type": "project_discussion",
        },
        default_timezone="Asia/Shanghai",
        tags=["project", "collaboration"],
        llm_custom_setting={
            "boundary": {
                "model": "gpt-4o-mini",
                "provider": "openai",
            },
            "extraction": {
                "model": "gpt-4o",
                "provider": "openai",
            },
        },
    )
    print("Global config created:")
    print(response)


async def create_group_config() -> None:
    """Create group config (without llm_custom_setting).

    Note: llm_custom_setting is NOT allowed for group config,
    it inherits from the global config.
    """
    response = await conversation_meta.create(
        created_at=datetime.now(timezone.utc).isoformat(),
        name="Project Discussion Group",  # Required for group config
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
    print("Group config created:")
    print(response)


async def main() -> None:
    # First create global config with llm_custom_setting
    await create_global_config()

    # Then create group config (inherits llm_custom_setting from global)
    await create_group_config()


if __name__ == "__main__":
    asyncio.run(main())
