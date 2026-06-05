# Cookbook Tests Evaluation

SDK: `everos` (new v1, trial whl)
Gateway: `https://test-gateway.aws.evermind.ai`
Evaluated: 2026-05-20

## Retention Criteria

A cookbook is kept if its use cases are supported **directly by first-class API interfaces** (`memory.add`, `memory.search`, `memory.get`, `memory.feedback`, `tasks.retrieve`, `storage.sign`) without requiring special workarounds or non-obvious modeling conventions.

A cookbook is deprecated if the underlying concept is **not a first-class citizen** in the new API — i.e., it requires workarounds to simulate functionality that used to have a dedicated endpoint.

## Summary

| Cookbook | Cases | Test Result | Disposition | Notes |
|----------|-------|-------------|-------------|-------|
| quickstart | 4 | ✅ 4/4 Pass | ✅ Keep | — |
| personal-assistant | 6 | ✅ 6/6 Pass | ✅ Keep | — |
| customer-support | 8 | ✅ 8/8 Pass | ✅ Keep | — |
| ai-tutor | 11 | ✅ 11/11 Pass | ✅ Keep | — |
| python-integration | 7 | ✅ 7/7 Pass | ✅ Keep | Includes new `memory.feedback()` case |
| batch-processing | 8 | ✅ 8/8 Pass | ✅ Keep | — |
| team-collaboration | 5 | — | ⚠️ Deprecated | See below |

---

## ⚠️ team-collaboration — Deprecated

**Reason:** Group conversation is not a first-class citizen in the new API. `owner_type` only accepts `["user", "agent"]`; there is no `"group"` type. The old SDK had dedicated endpoints (`memories.group.add()`, `memories.group.flush()`); the new API requires a workaround — modeling a group as a user with a shared `owner_id` and embedding `sender_id`/`sender_name` inside messages.

A cookbook built on a workaround rather than a direct API would mislead users into thinking a group interface exists.

**Migration:** The multi-participant pattern is already covered by `batch-processing` Case 4 (Group import). The key pattern to document:

```python
# Group = shared owner_id, owner_type="user", per-message sender fields
memory.add(
    owner_id="group_engineering",
    owner_type="user",
    session_id="group_engineering",
    messages=[
        {"role": "user", "sender_id": "u_alice", "sender_name": "Alice",
         "timestamp": now_ms, "content": "..."},
    ],
)
```

**Disposition:** Directory kept for reference; do not publish as a standalone cookbook entry.

---

## New vs Old SDK — Method Gaps

### ❌ Removed in new SDK

| Old SDK method | Status | New SDK equivalent |
|----------------|--------|--------------------|
| `memories.flush(user_id, session_id)` | ❌ No endpoint | Boundary detection is automatic |
| `memories.group.add(group_id, messages)` | ❌ No group endpoint | `memory.add(owner_id=group_id, owner_type="user", messages=[{sender_id, sender_name}])` |
| `memories.group.flush(group_id)` | ❌ No endpoint | N/A |
| `memories.agent.add(agent_id, messages)` | ❌ No dedicated endpoint | `memory.add(owner_type="agent", owner_id=agent_id, ...)` |
| `task_id` in `add()` response | ❌ Not returned | `AddMemoriesData` only has `message_count` + `status`; no client-side task tracking on add |

### ✅ New in new SDK

| Method | Notes |
|--------|-------|
| `memory.feedback(content, memory_id, memory_type, owner_id, owner_type)` | Submit feedback on a memory item |
| `storage.sign(object_list)` | Pre-sign objects for storage upload |

### 🔄 Signature changes

| Concept | Old SDK | New SDK |
|---------|---------|---------|
| User identifier | `user_id="alice"` | `owner_id="alice", owner_type="user"` |
| Search filters | `filters={"user_id": "alice"}` | `owner_id="alice", owner_type="user"` (direct params) |
| Memory retrieval | `memories.get(filters={...}, memory_type="profile")` | `memory.get(memory_type="profile", owner_id=..., owner_type=...)` |
