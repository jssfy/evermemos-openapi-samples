# everos should've been installed (pip install everos -U)
# ⚠️  REMOVED IN v1: conversation_meta resource has been removed from the v1 SDK.
#     There is no direct v1 equivalent for client.v0.memories.conversation_meta.create().
#
# v1 alternatives:
#   - Per-sender metadata → client.v1.senders.create(sender_id=..., name=..., ...)
#   - Per-group metadata  → client.v1.groups.create(group_id=..., name=..., ...)
#   - Global settings     → client.v1.settings.update(...)
#
# Original v0 file: examples/v0/create_meta_async.py
raise NotImplementedError(
    "conversation_meta.create() is REMOVED in v1. "
    "Use client.v1.senders, client.v1.groups, or client.v1.settings instead. "
    "See everos v1 documentation for details."
)
