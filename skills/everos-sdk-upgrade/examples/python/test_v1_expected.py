"""
Expected v1 (everos) output after migration from test_v0_sample.py.
Covers all 13 migration rules.
"""

import os
from datetime import datetime, timezone

from everos import EverOS, EverOSError
from everos.types.v1 import (
    AddResponse,
    GetMemoriesResponse,
    SearchMemoriesResponse,
    SettingsAPIResponse,
    # MemoryDeleteResponse → v1 delete returns None
    # ConversationMetaCreateResponse → REMOVED, migrated to settings/groups/senders
    # ConversationMetaGetResponse → REMOVED, migrated to settings.retrieve
)

USER_ID = "user-alice"
GROUP_ID = "grp-workspace"


def create_client() -> EverOS:
    return EverOS(
        api_key=os.environ.get("EVEROS_API_KEY"),
        base_url=os.environ.get("EVER_OS_BASE_URL", "https://api.evermind.ai"),
    )


# RULE-011: conversation_meta → settings + senders + groups
def setup_settings(client: EverOS) -> SettingsAPIResponse:
    """Replaces v0 conversation_meta.create.

    Field migrations:
    - llm_custom_setting → settings.update(llm_custom_setting=...)
    - default_timezone → settings.update(timezone=...)
    - scene → DROPPED (implicit via memories.add vs memories.group.add)
    - description, scene_desc, tags, created_at → DROPPED
    - user_details.full_name → senders.create(name=...)
    - user_details.role/custom_role/extra → DROPPED

    WARNING: v0 conversation_meta was per-group; v1 settings is a global singleton.
    """
    response = client.v1.settings.update(
        llm_custom_setting={
            "boundary": {"model": "gpt-4.1-mini", "provider": "openai"},
            "extraction": {"model": "qwen/qwen3-235b-a22b-2507", "provider": "openrouter"},
        },
        timezone="Asia/Shanghai",
    )
    # user_details → senders
    client.v1.senders.create(sender_id=USER_ID, name="Alice")
    return response


# RULE-011: conversation_meta.get → settings.retrieve
def get_settings(client: EverOS) -> SettingsAPIResponse:
    response = client.v1.settings.retrieve()
    if response.data:
        print(f"timezone={response.data.timezone}, extraction_mode={response.data.extraction_mode}")
    return response


# RULE-007: memories.add rewrite
def add_memory(client: EverOS) -> AddResponse:
    now = datetime.now(timezone.utc)
    timestamp_ms = int(now.timestamp() * 1000)
    response = client.v1.memories.add(
        messages=[
            {
                "content": "I prefer dark mode and vim keybindings",
                "role": "user",
                "timestamp": timestamp_ms,
                "sender_id": USER_ID,
            }
        ],
        user_id=USER_ID,
        # NOTE: group_id → use client.v1.memories.group.add() instead
        # NOTE: message_id, sender_name, group_name → no v1 equivalent
    )
    # RULE-007: flush=True → separate flush() call
    client.v1.memories.flush(user_id=USER_ID)

    # RULE-011: group_name → groups.create
    # client.v1.groups.create(group_id=GROUP_ID, name="Dev Team Chat")
    return response


# RULE-010: memories.search rewrite
def search_memories(client: EverOS) -> SearchMemoriesResponse:
    response = client.v1.memories.search(
        filters={"user_id": USER_ID},
        query="dark mode",
    )
    # RULE-013: .result.memories → .data.episodes
    if response.data and response.data.episodes:
        print(f"found {len(response.data.episodes)} episodes")
    return response


# RULE-009: memories.get rewrite
def get_memories(client: EverOS) -> GetMemoriesResponse:
    response = client.v1.memories.get(
        filters={"user_id": USER_ID},
        memory_type="episodic_memory",
    )
    # RULE-013: .result.memories → .data.episodes, .result.total_count → .data.total_count
    if response.data and response.data.episodes:
        print(f"total={response.data.total_count}")
    return response


# RULE-008: memories.delete — memory_id must be used ALONE
def delete_memory(client: EverOS, memory_id: str) -> None:
    client.v1.memories.delete(
        memory_id=memory_id,
        # NOTE: v1 memory_id mode is mutually exclusive — no user_id alongside
    )


# RULE-011: status.request → tasks.retrieve
# WARNING: v0 status.request.get(request_id=...) is REMOVED.
# v1 equivalent: client.v1.tasks.retrieve(task_id=...)
# task_id comes from AddResponse.data.task_id (was MemoryAddResponse.request_id)
# Status values changed: "queued" → "processing"
# def check_task_status(client: EverOS, task_id: str):
#     response = client.v1.tasks.retrieve(task_id=task_id)
#     print(f"status={response.data.status}")
#     return response


def handle_errors():
    client = EverOS()
    try:
        client.v1.memories.add(
            messages=[
                {
                    "content": "test",
                    "role": "user",
                    "timestamp": int(datetime.now(timezone.utc).timestamp() * 1000),
                }
            ],
            user_id="user-1",
        )
    except EverOSError as e:
        print(f"EverOS error: {e}")
