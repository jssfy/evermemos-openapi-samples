# EverOS Python SDK v1-0518

> 生成日期：2026-05-18
> OpenAPI 规范：`openapi.json`（2026-05-18 版，路径从 `/api/v1/memories/` 改为 `/api/v1/memory/`）
> Stainless build：`bui_0cmpam9rt8000r26s68z5u32ye`
> 状态：测试版本，dev 环境验证通过

---

## 与旧版本的主要变化

| 维度 | v1（旧，`memories` 资源） | v1-0518（新，`memory` 资源） |
|------|--------------------------|------------------------------|
| API 路径 | `/api/v1/memories` `/api/v1/memories/search` 等 | `/api/v1/memory/add` `/api/v1/memory/search` 等 |
| 客户端资源 | `client.v1.memories` | `client.memory` |
| 支持的操作 | add / flush / search / get / delete + agent + group 子资源 | add / search / get / delete（简化，无 flush/agent/group） |
| 其他资源 | `groups` / `settings` / `senders` | 已移除，保留 `tasks` / `storage` |
| 安装包名 | `everos` (旧版) | `everos` (新 SDK，同包名，不同 build) |

---

## 安装 SDK

### 方式一：从 Stainless staging 安装（推荐，无需 PyPI）

```bash
# 从本次 build 的 install_url 安装（whl 文件）
pip install 'https://pkg.stainless.com/s/everos-trial-python/29fcf29579e027805166762a65da8592e94f01ff/everos-0.0.1-py3-none-any.whl'
```

### 方式二：从本地源码安装（离线）

```bash
SDK_PATH="/Users/yeanhua/workspace/tools/markdown/evermemos/python-sdk-stainless/sdks/EverOS-python"
pip install -e "$SDK_PATH"
```

### 方式三：从 staging GitHub 安装

```bash
pip install 'git+ssh://git@github.com/stainless-sdks/everos-trial-python.git@yeanhua/dev'
```

---

## 配置环境

```bash
# Dev 环境 API Key（账号: yeanhua@shanda.com）
export EVEROS_API_KEY="e53843b6-5acf-4e5f-a13e-cf4c6806974f"

# Dev 环境接入点（SDK 读取 EVER_OS_BASE_URL，默认 https://api.evermind.ai）
export EVER_OS_BASE_URL="https://dev-gateway.aws.evermind.ai"
```

| 环境 | 接入点 | API Key 变量 |
|------|--------|-------------|
| dev（当前） | `https://dev-gateway.aws.evermind.ai` | `EVEROS_API_KEY_DEV` |
| test | `https://test-gateway.aws.evermind.ai` | `EVEROS_API_KEY_TEST` |
| prod | `https://api.evermind.ai` | `EVEROS_API_KEY_PROD` |

---

## 客户端初始化

```python
from everos import EverOS

# api_key 自动从 EVEROS_API_KEY 读取，base_url 自动从 EVER_OS_BASE_URL 读取
client = EverOS()

# 或显式指定
client = EverOS(
    api_key="your_api_key",
    base_url="https://dev-gateway.aws.evermind.ai",
)
```

### 资源入口（新 API 结构）

```python
client.memory    # 记忆操作（add / search / get / delete）
client.tasks     # 异步任务状态查询
client.storage   # 文件预签名上传
```

---

## 核心用法

### 添加记忆（add）

```python
response = client.memory.add(
    owner_id="user_123",
    owner_type="user",         # "user" | "agent"
    session_id="session_abc",
    messages=[
        {
            "sender_id": "user_123",
            "role": "user",
            "content": [{"type": "text", "text": "Hello!"}]
        },
        {
            "sender_id": "assistant",
            "role": "assistant",
            "content": [{"type": "text", "text": "Hi there!"}]
        },
    ],
    async_mode=False,    # False=同步提取；True=异步（返回 task_id）
)

print(response.request_id)
print(response.data.status)        # "complete" | "no_memories" | "processing"
print(response.data.message_count) # 处理的消息数量
```

### 搜索记忆（search）

```python
response = client.memory.search(
    owner_id="user_123",
    owner_type="user",
    query="outdoor activities",
    method="keyword",    # "keyword" | "vector" | "hybrid" | "agentic"
    top_k=10,
)

for ep in (response.data.episodes or []):
    print(ep.id, ep.summary, ep.score)
```

### 获取记忆（get）

```python
response = client.memory.get(
    owner_id="user_123",
    owner_type="user",
    memory_type="episodic_memory",  # "episodic_memory" | "profile" | "agent_case" | "agent_skill"
    page=1,
    page_size=20,
    sort_by="timestamp",   # "timestamp" | "updated_at"
    sort_order="desc",
)

print(response.data.total_count)
for ep in (response.data.episodes or []):
    print(ep.id, ep.timestamp, ep.summary)
```

### 删除记忆（delete）

```python
response = client.memory.delete(
    owner_id="user_123",
    owner_type="user",
    memory_id="mem_xxx",    # 按 ID 删除
)
```

### 异步任务查询（tasks）

```python
# async_mode=True 时 add 返回 task_id
add_resp = client.memory.add(..., async_mode=True)
# 此时 add_resp.data.status == "processing"，task_id 在 request_id 中

# 轮询状态（task_id 有效期 1 小时）
task_resp = client.tasks.retrieve(task_id="your_task_id")
print(task_resp.status)    # "processing" | "success" | "failed"
```

---

## 运行测试

### 快速验证（test_sdk.py）

```bash
cd /Users/yeanhua/workspace/tools/markdown/evermemos/python-sdk-stainless

# 配置环境变量
export EVEROS_API_KEY="e53843b6-5acf-4e5f-a13e-cf4c6806974f"
export EVER_OS_BASE_URL="https://dev-gateway.aws.evermind.ai"

# 运行测试（无需 install SDK，直接从 src 路径导入）
python3 examples/v1-0518/test_sdk.py
```

### 预期输出

```
============================================================
EverOS Python SDK 功能测试
============================================================
API 基础 URL: https://dev-gateway.aws.evermind.ai
所有者 ID: test_user_001
会话 ID: test_session_2026-05-18T...

=== 测试 add_memories ===
✅ add_memories 成功
   request_id: 02177907428685600000000000000000000ffff0a1f6b2173659d
   data: AddMemoriesData(message_count=2, status='complete')

=== 测试 search_memories ===
✅ search_memories 成功
   ...

=== 测试 get_memories ===
✅ get_memories 成功
   total_count: 1
   count: 1
   episodes: 1

✅ 全部通过
```

---

## 文件列表

| 文件 | 说明 |
|------|------|
| `README.md` | 本文档：安装、配置、用法 |
| `test_sdk.py` | 功能验证脚本：add / get / search |
