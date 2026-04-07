# everos should've been installed (pip install everos -U)
# ⚠️  REMOVED IN v1: conversation_meta resource has been removed from the v1 SDK.
#     There is no direct v1 equivalent for client.v0.memories.conversation_meta.update().
#
# v1 alternatives:
#   - Per-sender update → client.v1.senders.patch(sender_id=..., name=..., ...)
#   - Per-group update  → client.v1.groups.patch(group_id=..., name=..., ...)
#   - Global settings   → client.v1.settings.update(...)
#
# Original v0 file: examples/v0/update_meta_async.py
raise NotImplementedError(
    "conversation_meta.update() is REMOVED in v1. "
    "Use client.v1.senders.patch(), client.v1.groups.patch(), "
    "or client.v1.settings.update() instead."
)
