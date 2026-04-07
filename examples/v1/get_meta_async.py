# everos should've been installed (pip install everos -U)
# ⚠️  REMOVED IN v1: conversation_meta resource has been removed from the v1 SDK.
#     There is no direct v1 equivalent for client.v0.memories.conversation_meta.get().
#
# v1 alternatives:
#   - Per-sender info → client.v1.senders.retrieve(sender_id=...)
#   - Per-group info  → client.v1.groups.retrieve(group_id=...)
#   - Global settings → client.v1.settings.retrieve()
#
# Original v0 file: examples/v0/get_meta_async.py
raise NotImplementedError(
    "conversation_meta.get() is REMOVED in v1. "
    "Use client.v1.senders.retrieve(), client.v1.groups.retrieve(), "
    "or client.v1.settings.retrieve() instead."
)
