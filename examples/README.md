# EverOS Python SDK v1 - 示例集

基于 Stainless 生成的 Python SDK（`EverOS-python`），对应 OpenAPI 规范 `openapi.json`（2026-03-30 最新版）。

## 版本记录

| 日期 | Spec 文件 | 测试包安装命令 | `EVER_OS_BASE_URL` 可选值 |
|------|-----------|--------------|-------------------------------|
| 2026-03-30 | `docs/openapi-specs/openapi-0330.json` | `pip install 'https://pkg.stainless.com/s/EverOS-python/57e6f13222c8cadeb2744ed45d3c31c768835ff4/evermemos-0.3.6-py3-none-any.whl'` | `http://localhost:9527` · `https://dev-gateway.aws.evermind.ai` · `https://test-gateway.aws.evermind.ai` · `https://api.evermind.ai` |

SDK 路径：`code/openapi/stainless/evermemos/sdks/EverOS-python`

---

## 对比文档

- evermemos/memsys/v1-apis/api-diff-doc-vs-openapi-2026-03-22.md

## 快速开始

### 1. 安装 SDK

```bash
# 使用本地生成的 SDK（推荐，无需发布 PyPI）
SDK_PATH="$(git rev-parse --show-toplevel)/code/openapi/stainless/evermemos/sdks/EverOS-python"
pip install -e "$SDK_PATH"

# 或从 PyPI 安装发布版（evermemos 0.3.6）
pip install everos
```

### 2. 配置环境变量

```bash
export EVEROS_API_KEY="your_api_key"

# 覆盖接入点（SDK 读取 EVER_OS_BASE_URL，默认 https://api.evermind.ai）
# 可选值（来自 openapi.json servers）：
#   http://localhost:9527                  Local Gateway server
#   https://dev-gateway.aws.evermind.ai   DEV environment
#   https://test-gateway.aws.evermind.ai  TEST environment
#   https://api.evermind.ai               Production（默认）
export EVER_OS_BASE_URL="https://dev-gateway.aws.evermind.ai"
```

> **注意**：环境变量名是 `EVER_OS_BASE_URL`，不是 `EVERMEMOS_BASE_URL`。

### 3. 运行示例

```bash
cd evermemos/backend/samples-on-sdk

# 运行任意示例（需先配置 EVEROS_API_KEY）
python 01_add_sync.py
python 04_search_sync.py
```

### 客户端初始化

```python
from everos import EverOS, AsyncEverOS

client = EverOS()        # api_key 自动从 EVEROS_API_KEY 读取
client = AsyncEverOS()   # 异步版本
```

```python
# 资源入口（均通过 v1 命名空间）
client.v1.memories          # 个人记忆
client.v1.memories.agent    # Agent 轨迹记忆
client.v1.memories.group    # 群组记忆
client.v1.groups            # 群组管理
client.v1.senders           # 发送者管理
client.v1.settings          # 系统设置
client.v1.object            # 文件预签名
client.v1.tasks             # 异步任务状态
```

## 示例文件

| 文件 | 说明 | 调用接口 |
|------|------|---------|
| `01_add_sync.py` | 同步写入个人记忆 | `POST /api/v1/memories` |
| `02_add_async.py` | 异步写入 + task 轮询 | `POST /api/v1/memories`（async_mode=true）<br>`GET /api/v1/tasks/{task_id}` |
| `03_get_sync.py` | 查询记忆（多类型 + 时间范围过滤） | `POST /api/v1/memories/get` |
| `04_search_sync.py` | 语义 / 关键字搜索（hybrid / vector / keyword） | `POST /api/v1/memories/search` |
| `05_delete_sync.py` | 按 ID / 批量删除记忆 | `POST /api/v1/memories/delete` |
| `06_flush_sync.py` | 手动触发会话边界提取 | `POST /api/v1/memories`<br>`POST /api/v1/memories/flush` |
| `07_agent_memories.py` | Agent 轨迹记忆（含 tool_calls） | `POST /api/v1/memories/agent`<br>`POST /api/v1/memories/agent/flush` |
| `08_group_memories.py` | 群组多人对话记忆 | `POST /api/v1/memories/group`<br>`POST /api/v1/memories/group/flush` |
| `09_groups_senders.py` | Groups / Senders / Settings CRUD | `POST /api/v1/groups`<br>`GET /api/v1/groups/{group_id}`<br>`PATCH /api/v1/groups/{group_id}`<br>`POST /api/v1/senders`<br>`GET /api/v1/senders/{sender_id}`<br>`PATCH /api/v1/senders/{sender_id}`<br>`GET /api/v1/settings`<br>`PUT /api/v1/settings` |
| `10_object_sign.py` | 文件批量预签名 | `POST /api/v1/object/sign` |

## 关键调用模式速查

### 写入记忆

```python
# 个人记忆（同步）
client.v1.memories.add(
    user_id="user_010",
    messages=[
        {"role": "user", "timestamp": int(time.time() * 1000), "content": "..."},
        {"role": "assistant", "timestamp": int(time.time() * 1000) + 500, "content": "..."},
    ],
)

# 群组记忆（每条 message 必须有 sender_id）
client.v1.memories.group.add(
    group_id="group_001",
    messages=[
        {"role": "user", "sender_id": "alice", "timestamp": ..., "content": "..."},
    ],
)

# 异步模式（返回 task_id，用 tasks.retrieve() 轮询）
resp = client.v1.memories.add(user_id=..., messages=[...], async_mode=True)
task_id = resp.data.task_id
status_resp = client.v1.tasks.retrieve(task_id)
```

### 查询 / 搜索记忆

```python
# 按类型查询（filters DSL 支持 eq/in/gt/gte/lt/lte/AND/OR）
client.v1.memories.get(
    filters={"user_id": "user_010", "timestamp": {"gte": start_ms}},
    memory_type="episodic_memory",   # episodic_memory | profile | agent_case | agent_skill
)

# 语义搜索
client.v1.memories.search(
    filters={"user_id": "user_010"},
    query="outdoor activities",
    method="hybrid",                 # hybrid | vector | keyword | agentic
    top_k=5,
)
```

### 触发记忆提取（flush）

```python
client.v1.memories.flush(user_id="user_010", session_id="session_abc")
```

### 文件批量预签名

```python
resp = client.v1.object.sign(
    object_list=[
        {"file_id": "f1", "file_name": "photo.png", "file_type": "image"},
        {"file_id": "f2", "file_name": "doc.pdf",   "file_type": "file"},
    ]
)
```

### 错误处理

```python
from everos import BadRequestError, UnprocessableEntityError, AuthenticationError

try:
    client.v1.memories.add(...)
except UnprocessableEntityError as e:   # 422 参数校验失败（v1 新错误码）
    print(e.status_code, e.message)
except AuthenticationError:             # 401 API Key 无效
    ...
```

---

## FAQ

### Q: 传入不存在的本地文件路径，为什么 SDK 不报错？

`scan_messages()` 用 `os.path.isfile()` 判断 `uri` 是否为本地文件。若文件不存在，URI 会被当作**已有的 `object_key`** 原样透传给 API，SDK 层不抛异常。

```
uri 判断逻辑（_detect.py）
├── http:// 或 https:// 开头     → 下载后上传
├── os.path.isfile() == True     → 直接上传
└── 其他（含不存在的路径）        → 视为 object_key，原样透传 ← 静默跳过
```

**结果**：API 收到一个无效的 `object_key`，同步模式（`async_mode=False`）可能返回错误，异步模式（`async_mode=True`，默认）则 `add()` 返回 `202 queued`，实际任务处理时 `task_id` 对应的 `status` 最终为 `"failed"`。

**最佳实践**：传入本地路径前确保文件真实存在，或用 `async_mode=False` + 任务轮询检测失败。

---

### Q: HTTP URL 返回 404 / 非 2xx 时会怎样？

SDK 会立即抛出 `FileResolveError`，`add()` 调用中断，**不会**调用 API。这是符合预期的行为。

实测日志（URL 末尾加了无效后缀 `pngxxx`）：

```
DEBUG everos: Multimodal detected: 1 file(s) to upload
DEBUG everos:   [0] messages[1].content[1] type=image uri=https://s41.ax1x.com/.../peG0uAH.pngxxx (http)
INFO  httpx: HTTP Request: GET https://s41.ax1x.com/.../peG0uAH.pngxxx "HTTP/1.1 404 Not Found"
# ↑ 下载失败，resp.raise_for_status() 抛出 HTTPStatusError
# ↑ _resolve_from_url 捕获后包装为 FileResolveError

everos.lib._errors.FileResolveError: Failed to download https://.../peG0uAH.pngxxx:
  Client error '404 Not Found' for url '...'
```

与本地不存在路径的处理对比：

| 情况 | SDK 行为 | API 是否被调用 |
|------|---------|--------------|
| 本地路径不存在 | 静默跳过，原样透传 uri | ✅ 是（带无效 uri） |
| HTTP URL 返回 4xx/5xx | 立即抛 `FileResolveError` | ❌ 否，调用中断 |
| HTTP URL 返回 200 | 正常下载 → sign → 上传 | ✅ 是（带有效 object_key） |

捕获方式：

```python
from everos.lib import FileResolveError

try:
    response = memories.add(...)
except FileResolveError as e:
    print(f"文件解析失败: {e}")  # HTTP 下载失败或本地路径校验失败
```

---

### Q: 本地文件 vs HTTP URL，上传流程有什么区别？

| 来源 | 流程 | 临时文件 |
|------|------|---------|
| 本地路径 | 直接 sign → S3 POST | 无 |
| HTTP URL | 先下载到 tempfile（最大 100 MB）→ sign → S3 POST | 有（`finally` 中自动清理） |

HTTP 下载限制：超过 100 MB 抛 `FileResolveError`，需改用低层 `client.v1.object.sign()` 手动上传。

---

### Q: `object.sign` 响应如何判断成功？

响应字段 `status` 的成功值为 `0`（**不是** `200`，OpenAPI 文档有误，以 SDK 实现为准）：

```python
# 有效的 sign 响应需同时满足：
sign_resp.status == 0          # MMS 业务码，0 = 成功
sign_resp.error == "OK"        # 文字描述
len(sign_resp.result.data.object_list) == len(upload_tasks)  # 数量匹配
# 每项：object_key 非空 且 object_signed_info.url 非空
```

---

### Q: S3 上传失败会重试吗？

会，规则如下：

| 情况 | 处理 |
|------|------|
| HTTP 5xx / 超时 | 最多重试 3 次，间隔 1 秒 |
| HTTP 4xx | 立即抛 `UploadError`，不重试 |
| 3 次均失败 | 抛 `UploadError` |

---

### Q: `add()` 返回后如何确认文件被处理？

```python
# 同步模式（async_mode=False）——返回时文件已处理
response = memories.add(..., async_mode=False)
print(response.data.status)   # "accumulated" | "extracted"

# 异步模式（默认）——需轮询 task_id
response = memories.add(...)
task_id = response.data.task_id
status = client.v1.tasks.retrieve(task_id).data.status
# "processing" | "success" | "failed"
# ⚠️ task_id 在 Redis 中 TTL = 1 小时
```

---

## v0 → v1 主要变化

| 维度 | v0 (旧 SDK) | v1 (新 SDK) |
|------|-------------|-------------|
| 客户端入口 | `client.v0.memories` | `client.v1.memories` |
| 消息格式 | 单条扁平参数（content/sender） | `messages[]` 数组，每条含 role/timestamp/sender_id |
| 搜索参数 | `extra_query={}` | `filters={...}` + `query=` 类型化参数 |
| 过滤 DSL | 无结构 | `{user_id: X, timestamp: {gte: T}}` |
| 异步任务 | `client.v0.status.request.get()` | `client.v1.tasks.retrieve(task_id)` |
| 文件签名 | 单文件字段 | `object_list=[{file_id, file_name, file_type}]` |
| 搜索方法 | keyword / vector / hybrid / rrf / agentic | keyword / vector / hybrid / agentic（rrf 已移除） |
| 验证错误码 | 400 | 422 |
