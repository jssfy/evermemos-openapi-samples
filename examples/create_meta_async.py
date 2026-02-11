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
                "model": "gpt-4.1-mini",
                "provider": "openai",
            },
            "extraction": {
                "model": "qwen/qwen3-235b-a22b-2507",
                "provider": "openrouter",
            },
        },
    )
    print("Global config created:")
    print(response)


async def create_config_with_user_details() -> None:
    """Create config with user details and scene info."""
    response = await conversation_meta.create(
        created_at=datetime.now(timezone.utc).isoformat(),
        scene="group_chat",
        scene_desc={
            "description": "Project discussion group chat",
            "type": "project_discussion",
        },
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
    print("Config with user details created:")
    print(response)


async def main() -> None:
    # Create global config with llm_custom_setting
    await create_global_config()

    # Create config with user details
    await create_config_with_user_details()


if __name__ == "__main__":
    asyncio.run(main())
