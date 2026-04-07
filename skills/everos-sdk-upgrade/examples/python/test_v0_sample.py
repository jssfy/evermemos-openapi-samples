"""
Sample v0 (evermemos) code for migration testing.
Covers all 13 migration rules. Feed to /everos-sdk-upgrade and verify
output matches test_v1_expected.py.
"""

import os
from datetime import datetime, timezone

from evermemos import EverMemOS, EverMemOSError
from evermemos.types.v0 import (
    MemoryAddResponse,
    MemoryDeleteResponse,
    MemoryGetResponse,
    MemorySearchResponse,
)
from evermemos.types.v0.memories import (
    ConversationMetaCreateResponse,
    ConversationMetaGetResponse,
)

USER_ID = "user-alice"
GROUP_ID = "grp-workspace"


def create_client() -> EverMemOS:
    return EverMemOS(
        api_key=os.environ.get("EVERMEMOS_API_KEY"),
        base_url=os.environ.get("EVER_MEM_OS_BASE_URL", "https://api.evermind.ai"),
    )


# conversation_meta (RULE-011)
def setup_conversation_meta(client: EverMemOS) -> ConversationMetaCreateResponse:
    return client.v0.memories.conversation_meta.create(
        created_at=datetime.now(timezone.utc).isoformat(),
        scene="group_chat",
        default_timezone="Asia/Shanghai",
        llm_custom_setting={
            "boundary": {"model": "gpt-4.1-mini", "provider": "openai"},
            "extraction": {"model": "qwen/qwen3-235b-a22b-2507", "provider": "openrouter"},
        },
        description="Dev team technical discussion",
        scene_desc={"description": "Technical discussion group", "type": "work"},
        tags=["work", "technical"],
        user_details={
            USER_ID: {"full_name": "Alice", "role": "user", "custom_role": "developer"},
        },
    )


def get_conversation_meta(client: EverMemOS) -> ConversationMetaGetResponse:
    response = client.v0.memories.conversation_meta.get()
    if response.result:
        print(f"scene={response.result.scene}, timezone={response.result.default_timezone}")
    return response


# memories.add (RULE-007)
def add_memory(client: EverMemOS) -> MemoryAddResponse:
    return client.v0.memories.add(
        content="I prefer dark mode and vim keybindings",
        create_time=datetime.now(timezone.utc).isoformat(),
        message_id="msg-001",
        sender=USER_ID,
        role="user",
        flush=True,
        group_id=GROUP_ID,
        group_name="Dev Team Chat",
        sender_name="Alice",
    )


# memories.search (RULE-010)
def search_memories(client: EverMemOS) -> MemorySearchResponse:
    response = client.v0.memories.search(
        extra_query={"user_id": USER_ID, "query": "dark mode"},
    )
    if response.result and response.result.memories:
        print(f"found {len(response.result.memories)} memories")
    return response


# memories.get (RULE-009)
def get_memories(client: EverMemOS) -> MemoryGetResponse:
    response = client.v0.memories.get(
        extra_query={"user_id": USER_ID, "memory_type": "episodic_memory"},
    )
    if response.result and response.result.memories:
        print(f"total={response.result.total_count}")
    return response


# memories.delete (RULE-008)
def delete_memory(client: EverMemOS, memory_id: str) -> MemoryDeleteResponse:
    return client.v0.memories.delete(
        memory_id=memory_id,
        user_id=USER_ID,
    )


# status.request (RULE-011)
def check_request_status(client: EverMemOS, request_id: str):
    response = client.v0.status.request.get(request_id=request_id)
    print(f"status={response.status}, found={response.found}")
    return response


def handle_errors():
    client = EverMemOS()
    try:
        client.v0.memories.add(
            content="test",
            create_time=datetime.now(timezone.utc).isoformat(),
            message_id="msg-err",
            sender="user-1",
        )
    except EverMemOSError as e:
        print(f"EverMemOS error: {e}")
