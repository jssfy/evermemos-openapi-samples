# Migration Rules: evermemos (v0) -> everos (v1)

This file contains every breaking change between the two SDK versions.
Apply rules in the order listed.

## Contents

- RULE-001: Package Dependency (rename evermemos -> everos)
- RULE-002: Environment Variables (EVERMEMOS_API_KEY -> EVEROS_API_KEY)
- RULE-003: Import Statements (module + type renames)
- RULE-004: Client Class (EverMemOS -> EverOS)
- RULE-005: Exception Classes (EverMemOSError -> EverOSError)
- RULE-006: Resource Path (.v0. -> .v1.)
- RULE-007: memories.add() — **COMPLETE REWRITE** (single msg -> batch array)
- RULE-008: memories.delete() (HTTP method + return type change)
- RULE-009: memories.get() — **COMPLETE REWRITE** (no params -> filters DSL)
- RULE-010: memories.search() — **COMPLETE REWRITE** (no params -> filters + query)
- RULE-011: Removed Resources — conversation_meta 逐字段迁移 + status.request → tasks.retrieve
- RULE-012: New v1 Features (informational)
- RULE-013: Response Structure Rewrite (.result->.data, .memories->.episodes, add .request_id->.data.task_id)
- Quick Reference: Search-and-Replace Checklist

---

## RULE-001: Package Dependency

### Change Type: BREAKING - Package Rename

**Before (v0):**
```
# pyproject.toml
dependencies = ["evermemos>=0.3.0"]

# requirements.txt
evermemos>=0.3.0
evermemos==0.3.13
```

**After (v1):**
```
# pyproject.toml
dependencies = ["everos>=0.1.0"]

# requirements.txt
everos>=0.1.0
everos==0.1.1
```

### Search Patterns:
- `evermemos` in pyproject.toml, requirements*.txt, setup.py, setup.cfg, Pipfile

### Steps:
1. FIND: `evermemos` in dependency declarations
2. REPLACE: with `everos`
3. Update version constraints to `>=0.1.0`

---

## RULE-002: Environment Variables

### Change Type: BREAKING - Env Var Rename

**Before (v0):**
```bash
EVERMEMOS_API_KEY=sk-xxx
EVER_MEM_OS_BASE_URL=https://api.evermind.ai
```

**After (v1):**
```bash
EVEROS_API_KEY=sk-xxx
EVER_OS_BASE_URL=https://api.evermind.ai
```

### Search Patterns:
- `EVERMEMOS_API_KEY` -> `EVEROS_API_KEY`
- `EVER_MEM_OS_BASE_URL` -> `EVER_OS_BASE_URL`

### Steps:
1. Search all files: .env, .env.*, docker-compose*.yml, Dockerfile, *.py, *.sh, CI configs
2. FIND: `EVERMEMOS_API_KEY` REPLACE: `EVEROS_API_KEY`
3. FIND: `EVER_MEM_OS_BASE_URL` REPLACE: `EVER_OS_BASE_URL`

---

## RULE-003: Import Statements

### Change Type: BREAKING - Module Rename

**Before (v0):**
```python
import evermemos
from evermemos import EverMemOS, AsyncEverMemOS
from evermemos import EverMemOSError
from evermemos.types.v0 import MemoryAddResponse, MemoryGetResponse, MemorySearchResponse, MemoryDeleteResponse
from evermemos.types.v0 import MemoryType, Metadata
from evermemos.types.v0.memories import (
    ConversationMetaCreateResponse,
    ConversationMetaUpdateResponse,
    ConversationMetaGetResponse,
)
from evermemos.types.v0.status import RequestGetResponse
```

**After (v1):**
```python
import everos
from everos import EverOS, AsyncEverOS
from everos import EverOSError
from everos.types.v1 import AddResponse, GetMemoriesResponse, SearchMemoriesResponse
from everos.types.v1 import (
    ContentItemParam, MessageItemParam, FlushResponse,
    EpisodeItem, ProfileItem, RawMessageDto,
)
# NOTE: ConversationMeta types are REMOVED in v1 - no direct replacement
# NOTE: Status types are REMOVED in v1 - no direct replacement
```

### Search Patterns (regex):
- `^import evermemos` -> `import everos`
- `^from evermemos` -> `from everos`
- `evermemos\.` -> `everos.`
- `\.types\.v0` -> `.types.v1`
- `\.resources\.v0` -> `.resources.v1`

### Type Rename Mapping:

| v0 Type | v1 Type | Notes |
|---------|---------|-------|
| `MemoryAddResponse` | `AddResponse` | |
| `MemoryGetResponse` | `GetMemoriesResponse` | |
| `MemorySearchResponse` | `SearchMemoriesResponse` | |
| `MemoryDeleteResponse` | *(returns None)* | v1 delete returns None |
| `MemoryType` | *(removed)* | Use Literal types inline |
| `Metadata` | *(removed)* | |
| `ConversationMetaCreateResponse` | **REMOVED** | No v1 equivalent |
| `ConversationMetaUpdateResponse` | **REMOVED** | No v1 equivalent |
| `ConversationMetaGetResponse` | **REMOVED** | No v1 equivalent |
| `RequestGetResponse` | **REMOVED** | Use `GetTaskStatusResponse` for async tasks |

### Steps:
1. FIND all `import evermemos` / `from evermemos` and REPLACE with `everos`
2. FIND `.types.v0` REPLACE `.types.v1`
3. FIND `.resources.v0` REPLACE `.resources.v1`
4. Rename type references per mapping table
5. FLAG any ConversationMeta or Status type usage to user

---

## RULE-004: Client Class

### Change Type: BREAKING - Class Rename

**Before (v0):**
```python
from evermemos import EverMemOS, AsyncEverMemOS

client = EverMemOS(api_key="sk-xxx")
async_client = AsyncEverMemOS(api_key="sk-xxx")

# Or with env var (auto-inferred from EVERMEMOS_API_KEY)
client = EverMemOS()
```

**After (v1):**
```python
from everos import EverOS, AsyncEverOS

client = EverOS(api_key="sk-xxx")
async_client = AsyncEverOS(api_key="sk-xxx")

# Or with env var (auto-inferred from EVEROS_API_KEY)
client = EverOS()
```

### Search Patterns:
- `EverMemOS(` -> `EverOS(`
- `AsyncEverMemOS(` -> `AsyncEverOS(`
- `EverMemOS` (as type hint) -> `EverOS`
- `AsyncEverMemOS` (as type hint) -> `AsyncEverOS`

### Steps:
1. FIND: `EverMemOS` REPLACE: `EverOS` (all occurrences including type hints)
2. FIND: `AsyncEverMemOS` REPLACE: `AsyncEverOS`

---

## RULE-005: Exception Classes

### Change Type: BREAKING - Exception Rename

**Before (v0):**
```python
from evermemos import EverMemOSError
try:
    ...
except EverMemOSError as e:
    ...
```

**After (v1):**
```python
from everos import EverOSError
try:
    ...
except EverOSError as e:
    ...
```

### Search Patterns:
- `EverMemOSError` -> `EverOSError`

---

## RULE-006: Resource Path (v0 -> v1)

### Change Type: BREAKING - Namespace Change

**Before (v0):**
```python
client.v0.memories.add(...)
client.v0.memories.get()
client.v0.memories.search()
client.v0.memories.delete(...)
client.v0.memories.conversation_meta.create(...)
client.v0.status.request.get(...)
```

**After (v1):**
```python
client.v1.memories.add(...)
client.v1.memories.get(...)
client.v1.memories.search(...)
client.v1.memories.delete(...)
# conversation_meta -> REMOVED
# status.request -> REMOVED (use client.v1.tasks.retrieve(task_id) for async tasks)
```

### Search Patterns:
- `\.v0\.` -> `.v1.`
- `client.v0` -> `client.v1`

### Steps:
1. FIND: `.v0.` REPLACE: `.v1.` in all API call chains
2. FLAG any `.conversation_meta.` usage - REMOVED in v1
3. FLAG any `.status.request.` usage - REMOVED in v1

---

## RULE-007: memories.add() - COMPLETE REWRITE

### Change Type: BREAKING - Signature Rewrite

This is the most complex change. v0 accepts single message fields; v1 accepts a
batch messages array with a completely different structure.

**Before (v0):**
```python
response = client.v0.memories.add(
    content="Hello, how are you?",
    create_time="2024-01-15T10:30:00+08:00",
    message_id="msg-001",
    sender="user-123",
    role="user",
    flush=True,
    group_id="grp-001",
    group_name="My Group",
    sender_name="Alice",
    refer_list=["msg-000"],
)
# response: MemoryAddResponse
```

**After (v1):**
```python
response = client.v1.memories.add(
    messages=[
        {
            "content": "Hello, how are you?",
            "role": "user",
            "timestamp": 1705285800000,  # unix ms, was ISO 8601 string
            "sender_id": "user-123",     # was "sender"
        }
    ],
    user_id="user-123",                  # explicit, was inferred from "sender"
    session_id=None,                     # new field
    # async_mode=True,                   # optional: async processing
)
# response: AddResponse
#
# For flushing, call separately:
# client.v1.memories.flush(user_id="user-123")
```

### Field Mapping:

| v0 Field | v1 Equivalent | Notes |
|----------|---------------|-------|
| `content` (str) | `messages[].content` (str or list[ContentItemParam]) | Moved into message object. v1 also supports multimodal content. |
| `create_time` (ISO 8601 str) | `messages[].timestamp` (int, unix ms) | **Format change**: ISO string -> unix milliseconds integer |
| `message_id` (str) | *(removed)* | No equivalent in v1 - SDK handles dedup internally |
| `sender` (str) | `messages[].sender_id` (str) + top-level `user_id` (str) | **Split**: sender -> sender_id in message, and explicit user_id at top level |
| `role` (str) | `messages[].role` ("user" \| "assistant") | Moved into message object |
| `flush` (bool) | *(removed)* | Use separate `client.v1.memories.flush(user_id=...)` call |
| `group_id` (str) | *(removed from add)* | Use `client.v1.memories.group.add()` for group memory |
| `group_name` (str) | *(removed)* | Use `client.v1.groups.create(group_id=..., name=...)` |
| `sender_name` (str) | *(removed from add)* | Use `client.v1.senders.create(sender_id=..., name=...)` |
| `refer_list` (list[str]) | *(removed)* | No equivalent in v1 |

### Conversion helper for timestamp:

```python
from datetime import datetime

# v0: ISO 8601 string
v0_time = "2024-01-15T10:30:00+08:00"

# v1: unix milliseconds
v1_timestamp = int(datetime.fromisoformat(v0_time).timestamp() * 1000)
# Result: 1705285800000
```

### Migration Steps:
1. Identify all `client.v0.memories.add(...)` calls
2. Extract the field values from the flat call
3. Restructure into `messages=[{...}]` array format
4. Convert `create_time` ISO string to `timestamp` unix milliseconds
5. Rename `sender` to `sender_id` inside message, add `user_id` at top level
6. If `flush=True` was used, add a separate `client.v1.memories.flush()` call after add
7. If `group_id` was used, switch to `client.v1.memories.group.add()` instead
8. Remove `message_id`, `group_name`, `sender_name`, `refer_list` (no v1 equivalents)

---

## RULE-008: memories.delete()

### Change Type: BREAKING - HTTP Method + Params + Return Type

**Before (v0):**
```python
# HTTP DELETE /api/v0/memories
response = client.v0.memories.delete(
    memory_id="mem-001",
    user_id="user-123",
    group_id="grp-001",
    id="mem-001",          # alias for memory_id
    event_id="mem-001",    # alias for memory_id
)
# response: MemoryDeleteResponse
```

**After (v1):**
```python
# HTTP POST /api/v1/memories/delete
# IMPORTANT: v1 has TWO mutually exclusive delete modes:

# Mode 1 - By ID (memory_id ONLY, no other fields allowed):
client.v1.memories.delete(memory_id="mem-001")

# Mode 2 - By filters (user_id and/or group_id, optional sender_id/session_id):
client.v1.memories.delete(
    user_id="user-123",
    group_id="grp-001",
    sender_id="sender-1",  # optional filter
    session_id="sess-1",   # optional filter
)
# returns None (not a response object)
```

### CRITICAL: Mutually Exclusive Delete Modes

v1 enforces strict separation:
- **By ID**: `memory_id` only — passing `user_id`, `group_id`, `sender_id`, or `session_id` alongside will raise 422
- **By filters**: `user_id` and/or `group_id` required — `memory_id` must NOT be present

v0 allowed mixing `memory_id` with `user_id`; v1 does NOT.

### Field Mapping:

| v0 Field | v1 Equivalent | Notes |
|----------|---------------|-------|
| `memory_id` | `memory_id` | Same, but must be used ALONE (no other fields) |
| `user_id` | `user_id` | Same, but must NOT be combined with memory_id |
| `group_id` | `group_id` | Same, but must NOT be combined with memory_id |
| `id` | *(removed)* | Was alias for memory_id, just use memory_id |
| `event_id` | *(removed)* | Was alias for memory_id, just use memory_id |
| *(new)* | `sender_id` | Filter mode only |
| *(new)* | `session_id` | Filter mode only |

### Steps:
1. FIND: `client.v0.memories.delete(` REPLACE: `client.v1.memories.delete(`
2. Remove `id=` and `event_id=` params, use `memory_id=` instead
3. **If `memory_id` is present, REMOVE all other params** (user_id, group_id, etc.)
4. If only filter params (user_id, group_id) were used without memory_id, keep them
5. If return value was used, note that v1 returns None
6. Update any type hints from `MemoryDeleteResponse` to `None`

---

## RULE-009: memories.get() - COMPLETE REWRITE

### Change Type: BREAKING - Signature Rewrite

**Before (v0):**
```python
# GET /api/v0/memories (no parameters)
response = client.v0.memories.get()
# response: MemoryGetResponse
```

**After (v1):**
```python
# POST /api/v1/memories/get (with filters DSL)
response = client.v1.memories.get(
    filters={"user_id": "user-123"},
    memory_type="episodic_memory",  # "episodic_memory" | "profile" | "agent_case" | "agent_skill"
    page=1,
    page_size=20,
    rank_by="timestamp",
    rank_order="desc",
)
# response: GetMemoriesResponse
```

### Note on extra_query pattern:

Some v0 users pass filters via `extra_query` since v0 SDK doesn't expose params:

```python
# v0 with extra_query workaround:
response = client.v0.memories.get(
    extra_query={"user_id": "user-123", "memory_type": "episodic_memory"},
)

# v1 (params are first-class):
response = client.v1.memories.get(
    filters={"user_id": "user-123"},
    memory_type="episodic_memory",
)
```

Extract values from `extra_query` dict and map to v1's named parameters.

### Steps:
1. FIND: `client.v0.memories.get(` (with or without extra_query)
2. If `extra_query` was used, extract `user_id`/`group_id` into `filters` dict and `memory_type` into named param
3. REPLACE: with `client.v1.memories.get(filters={...}, memory_type="episodic_memory")`
4. The user MUST provide `filters` (at minimum `user_id` or `group_id`) and `memory_type`
5. FLAG this to the user if no user_id/group_id can be inferred

---

## RULE-010: memories.search() - COMPLETE REWRITE

### Change Type: BREAKING - Signature Rewrite

**Before (v0):**
```python
# GET /api/v0/memories/search (no parameters in SDK, likely query params)
response = client.v0.memories.search()
# response: MemorySearchResponse
```

**After (v1):**
```python
# POST /api/v1/memories/search
response = client.v1.memories.search(
    filters={"user_id": "user-123"},
    query="what did we discuss yesterday",
    method="hybrid",          # "keyword" | "vector" | "hybrid" | "agentic"
    memory_types=["episodic_memory", "profile"],
    top_k=10,
    radius=0.7,
    include_original_data=False,
)
# response: SearchMemoriesResponse
```

### Note on extra_query pattern:

```python
# v0 with extra_query workaround:
response = client.v0.memories.search(
    extra_query={"user_id": "user-123", "query": "dark mode"},
)

# v1 (params are first-class):
response = client.v1.memories.search(
    filters={"user_id": "user-123"},
    query="dark mode",
)
```

### Steps:
1. FIND: `client.v0.memories.search(` (with or without extra_query)
2. If `extra_query` was used, extract `user_id`/`group_id` into `filters` dict, `query` into named param
3. REPLACE: with `client.v1.memories.search(filters={...}, query="...")`
4. The user MUST provide `filters` and `query` at minimum
5. FLAG this to the user if no filter or query can be inferred

---

## RULE-011: Removed Resources — conversation_meta & status.request

### conversation_meta — field-by-field migration

v0 `conversation_meta.create()` / `.update()` / `.get()` 整体被移除，但其中的字段分别迁移到了不同的 v1 接口。

#### conversation_meta 字段迁移对照表

| v0 conversation_meta 字段 | v1 去向 | 迁移方式 |
|--------------------------|---------|---------|
| `scene` ("group_chat" / "assistant") | **废弃** | v1 通过调用不同 API 隐式区分：个人场景用 `client.v1.memories.add()`，群聊场景用 `client.v1.memories.group.add()` |
| `llm_custom_setting` (boundary/extraction/extra) | **迁移到 settings** | `client.v1.settings.update(llm_custom_setting={...})`，字段结构完全一致（boundary/extraction/extra） |
| `default_timezone` | **迁移到 settings** | `client.v1.settings.update(timezone="Asia/Shanghai")` |
| `description` | **废弃** | v1 无对应字段，删除即可 |
| `scene_desc` | **废弃** | v1 无对应字段，删除即可 |
| `tags` | **废弃** | v1 无对应字段，删除即可 |
| `user_details` | **废弃** | v1 无对应字段，删除即可 |
| `created_at` | **废弃** | v1 settings 自动管理时间戳 |

#### 迁移代码示例

**Before (v0) — conversation_meta.create:**

```python
client.v0.memories.conversation_meta.create(
    created_at="2025-01-15T10:00:00+00:00",
    scene="group_chat",
    default_timezone="Asia/Shanghai",
    llm_custom_setting={
        "boundary": {"model": "gpt-4.1-mini", "provider": "openai"},
        "extraction": {"model": "qwen3-235b", "provider": "openrouter"},
    },
    description="Tech discussion",
    tags=["work", "technical"],
    user_details={
        "user_001": {"full_name": "Alice", "role": "user", "custom_role": "developer"},
    },
)
```

**After (v1) — 拆分到 settings + groups:**

```python
# 1. llm_custom_setting + timezone → settings API（全局配置，一次性设置）
client.v1.settings.update(
    llm_custom_setting={
        "boundary": {"model": "gpt-4.1-mini", "provider": "openai"},
        "extraction": {"model": "qwen3-235b", "provider": "openrouter"},
    },
    timezone="Asia/Shanghai",
)

# 2. scene → 隐式区分（无需显式设置）
#    个人场景: client.v1.memories.add(messages=[...], user_id="...")
#    群聊场景: client.v1.memories.group.add(group_id="...", messages=[...])

# 3. user_details → 部分由 senders 资源替代
#    v0 user_details 包含 full_name, role, custom_role, extra
#    v1 senders 只保留了 sender_id + name（对应 v0 的 sender + full_name）
#    role/custom_role/extra 无 v1 等价物，废弃
#    示例：
#    client.v1.senders.create(sender_id="user_001", name="Alice")

# 4. description, tags, scene_desc, created_at → 废弃，直接删除
```

#### 重要：作用域变更

v0 `conversation_meta` 是**按 group_id 作用域**的配置（每个群聊可以有独立配置，未设置时 fallback 到默认配置）。

v1 `settings` 是**全局单例**（无 group_id 作用域，整个 space 共享一套配置）。

如果用户的 v0 代码为不同 group_id 设置了不同的 `llm_custom_setting`，v1 无法直接迁移——需要统一为一套全局配置。迁移时应 FLAG 此情况给用户。

**Before (v0) — conversation_meta.update:**

```python
client.v0.memories.conversation_meta.update(
    llm_custom_setting={...},
    default_timezone="UTC",
)
```

**After (v1):**

```python
client.v1.settings.update(
    llm_custom_setting={...},
    timezone="UTC",
)
```

**Before (v0) — conversation_meta.get:**

```python
meta = client.v0.memories.conversation_meta.get()
```

**After (v1):**

```python
settings = client.v1.settings.retrieve()
# settings.data 包含 llm_custom_setting, timezone, extraction_mode 等
```

#### Migration Steps:

1. FIND: `conversation_meta.create(` 或 `conversation_meta.update(`
2. 提取 `llm_custom_setting` 和 `default_timezone` 参数
3. REPLACE: 用 `client.v1.settings.update(llm_custom_setting=..., timezone=...)`
4. FIND: `conversation_meta.get()`
5. REPLACE: 用 `client.v1.settings.retrieve()`
6. 删除 `scene`, `description`, `scene_desc`, `tags`, `user_details`, `created_at` 参数
7. 在代码中加注释说明 `scene` 通过 API 选择隐式区分

#### 关于 v0 add() 中 group_name 的迁移

v0 `memories.add(group_name="Dev Team Chat")` 在 v1 中需要预先创建 group：

```python
# v1: 先创建/更新 group（group_name → groups.create name）
client.v1.groups.create(group_id="grp-workspace", name="Dev Team Chat")

# 然后用 group.add 写入群聊记忆
client.v1.memories.group.add(group_id="grp-workspace", messages=[...])
```

---

### status.request — 迁移到 tasks.retrieve

**Before (v0):**

```python
response = client.v0.status.request.get(request_id="req-123")
# response: RequestGetResponse(success, data, found, message, request_id, status)
```

**After (v1):**

```python
response = client.v1.tasks.retrieve(task_id="task-123")
# response: GetTaskStatusResponse(data: TaskStatusResult(status, task_id))
# status: "processing" | "success" | "failed"
```

#### 字段映射

| v0 RequestGetResponse | v1 GetTaskStatusResponse | Notes |
|----------------------|-------------------------|-------|
| `request_id` (参数) | `task_id` (参数) | 参数名变更 |
| `status` ("queued"/"success"/...) | `data.status` ("processing"/"success"/"failed") | 值域变更: "queued" → "processing" |
| `success` (bool) | *(removed)* | 通过 status 判断 |
| `found` (bool) | *(removed)* | 未找到会抛异常 |
| `data` (dict) | *(removed)* | v1 不返回详细执行数据 |
| `message` (str) | *(removed)* | v1 不返回消息文本 |

#### 注意: task_id 来源变更

v0 的 `request_id` 来自 `MemoryAddResponse.request_id`。
v1 的 `task_id` 来自 `AddResponse.data.task_id`（需要 `async_mode=True` 才会返回）。

```python
# v1: 使用 async_mode 获取 task_id
response = client.v1.memories.add(messages=[...], user_id="...", async_mode=True)
task_id = response.data.task_id

# 然后轮询
status = client.v1.tasks.retrieve(task_id=task_id)
```

#### Migration Steps:

1. FIND: `client.v0.status.request.get(request_id=`
2. REPLACE: `client.v1.tasks.retrieve(task_id=`
3. 更新响应字段访问：`response.status` → `response.data.status`
4. 更新状态值判断：`"queued"` → `"processing"`
5. 如果代码依赖 `response.success` / `response.found` / `response.message`，改为通过 `response.data.status` 判断

---

## RULE-012: New v1 Features (informational, do NOT auto-add)

These resources are new in v1. Do NOT add them during migration unless the user
explicitly asks. List them in the migration summary for awareness:

| Resource | Purpose |
|----------|---------|
| `client.v1.memories.flush()` | Trigger boundary detection (replaces v0 `flush=True` param) |
| `client.v1.memories.agent.add()` / `.flush()` | Agent trajectory memory |
| `client.v1.memories.group.add()` / `.flush()` | Group memory (replaces v0 group_id in add) |
| `client.v1.groups.create/retrieve/patch()` | Group CRUD |
| `client.v1.senders.create/retrieve/patch()` | Sender CRUD |
| `client.v1.settings.retrieve/update()` | Global settings |
| `client.v1.tasks.retrieve()` | Async task status |
| `client.v1.object.sign()` | Multimodal pre-signed upload |
| Multimodal content in messages | `content` can be `list[ContentItemParam]` with image/audio/doc/pdf types |

---

## RULE-013: Response Structure Rewrite

### Change Type: BREAKING - Response Wrapper + Field Renames

Two changes: (1) top-level accessor `.result` → `.data`, and (2) field names
inside the response are renamed.

**Before (v0):**
```python
# get response (MemoryGetResponse)
response = client.v0.memories.get()
memories = response.result.memories      # list of memory objects
total = response.result.total_count
count = response.result.count

# search response (MemorySearchResponse)
response = client.v0.memories.search()
memories = response.result.memories      # list of memory objects
profiles = response.result.profiles
```

**After (v1):**
```python
# get response (GetMemoriesResponse -> GetMemResponse)
response = client.v1.memories.get(filters={...}, memory_type="episodic_memory")
episodes = response.data.episodes        # was .memories, now .episodes
profiles = response.data.profiles        # was nested in .memories, now top-level
agent_cases = response.data.agent_cases  # new field
agent_skills = response.data.agent_skills  # new field
total = response.data.total_count
count = response.data.count

# search response (SearchMemoriesResponse -> SearchMemoriesResponseData)
response = client.v1.memories.search(filters={...}, query="...")
episodes = response.data.episodes        # was .memories, now .episodes
profiles = response.data.profiles        # top-level, not nested
agent_memory = response.data.agent_memory  # new field
raw_messages = response.data.raw_messages  # new field
```

### Field Rename Mapping:

| v0 field | v1 field | Notes |
|----------|----------|-------|
| `.result` | `.data` | Top-level wrapper rename |
| `.result.memories` | `.data.episodes` | **Renamed**: memories → episodes |
| `.result.profiles` | `.data.profiles` | Kept, but now top-level in search response |
| `.result.total_count` | `.data.total_count` | Same for **get** only. **search** response has no total_count in v1 |
| `.result.count` | `.data.count` | Same for **get** only |
| *(new)* | `.data.agent_cases` | New in v1 get |
| *(new)* | `.data.agent_skills` | New in v1 get |
| *(new)* | `.data.agent_memory` | New in v1 search |
| *(new)* | `.data.raw_messages` | New in v1 search (replaces v0 `.result.pending_messages`) |
| `.result.pending_messages` | `.data.raw_messages` | **Renamed**: pending_messages → raw_messages |
| `.result.query_metadata` | `.data.query` | **Renamed + restructured**: QueryMetadata → Query |
| `.result.metadata` | *(removed)* | v0 Metadata object not present in v1 responses |

### Add response field changes:

```python
# v0 add response (MemoryAddResponse)
response.request_id   # str
response.message      # str
response.status       # str

# v1 add response (AddResponse -> AddResult)
response.data.task_id        # str (was request_id)
response.data.message        # str
response.data.status         # "accumulated" | "extracted" (was free-form str)
response.data.message_count  # int (new)
```

### Search Patterns:
- `.result.` → `.data.` (in SDK response contexts)
- `.result.memories` or `.data.memories` → `.data.episodes`
- `.result.profiles` → `.data.profiles`
- `.result.pending_messages` → `.data.raw_messages`
- `.result.query_metadata` → `.data.query`
- `.request_id` (on add response) → `.data.task_id`

### Steps:
1. FIND: `.result.` REPLACE: `.data.` (in SDK response access chains)
2. FIND: `.memories` (on response data objects) REPLACE: `.episodes`
3. FIND: `.data.total_count` — keep as-is (unchanged)
4. Be careful not to replace `.result` or `.memories` in non-SDK contexts

---

## Quick Reference: Search-and-Replace Checklist

For simple renames, these can be applied project-wide:

| Find | Replace | Scope |
|------|---------|-------|
| `evermemos` | `everos` | All files |
| `EverMemOS` | `EverOS` | *.py |
| `AsyncEverMemOS` | `AsyncEverOS` | *.py |
| `EverMemOSError` | `EverOSError` | *.py |
| `EVERMEMOS_API_KEY` | `EVEROS_API_KEY` | All files |
| `EVER_MEM_OS_BASE_URL` | `EVER_OS_BASE_URL` | All files |
| `.v0.` | `.v1.` | *.py (in API call chains) |
| `.types.v0` | `.types.v1` | *.py |
| `.resources.v0` | `.resources.v1` | *.py |
| `MemoryAddResponse` | `AddResponse` | *.py |
| `MemoryGetResponse` | `GetMemoriesResponse` | *.py |
| `MemorySearchResponse` | `SearchMemoriesResponse` | *.py |
| `MemoryDeleteResponse` | `None` | *.py (type hints only) |
| `.result.` | `.data.` | *.py (response access) |
| `.data.memories` | `.data.episodes` | *.py (response field rename) |

**These are NOT simple renames** (require manual restructuring):
- `memories.add()` parameters -> see RULE-007
- `memories.get()` parameters -> see RULE-009
- `memories.search()` parameters -> see RULE-010
- `conversation_meta.*` calls -> REMOVED, see RULE-011
- `status.request.*` calls -> REMOVED, see RULE-011
