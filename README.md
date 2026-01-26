# EverMemOS Python SDK 示例代码

本目录包含 EverMemOS Python SDK 的使用示例，展示了如何使用异步和同步客户端进行各种操作。

## 项目链接

- [PyPI链接](https://pypi.org/project/evermemos/)
- [github链接](https://github.com/evermemos/evermemos-python)

## 环境变量配置

运行示例前，需要设置以下环境变量：

```bash
export EVERMEMOS_API_KEY="your_api_key"
export EVER_MEM_OS_CLIENT_BASE_URL="https://api.evermind.ai"
```

## 记忆（Memories）操作

### 创建记忆

#### `add_async.py` - 异步创建记忆
- **用途**: 使用异步客户端创建单条记忆
- **功能**: 演示如何创建记忆，包括设置内容、创建时间、消息ID和发送者
- **特点**: 使用 `AsyncEverMemOS` 客户端，适合异步应用场景
- **运行**: `python add_async.py`

#### `add_sync.py` - 同步创建记忆
- **用途**: 使用同步客户端创建单条记忆
- **功能**: 演示同步方式创建记忆的基本用法
- **特点**: 使用 `EverMemOS` 客户端，适合同步应用场景
- **运行**: `python add_sync.py`

### 获取记忆

#### `get_async.py` - 异步获取/列出记忆
- **用途**: 使用异步客户端查询和列出记忆
- **功能**: 
  - 通过 `user_id` 和 `memory_type` 过滤查询记忆
  - 展示如何访问不同类型的记忆属性（Profile、EpisodicMemory、EventLog、Foresight）
  - 打印记忆的详细信息
- **特点**: 支持多种记忆类型的查询和展示
- **运行**: `python get_async.py`

### 搜索记忆

#### `search_async.py` - 异步搜索记忆
- **用途**: 使用异步客户端进行语义搜索记忆
- **功能**:
  - 通过 `group_id` 和 `memory_types` 搜索记忆
  - 展示搜索结果的分组结构
  - 显示待处理消息（pending_messages）
- **特点**: 
  - 使用 `extra_query` 参数传递搜索条件（推荐方式）
  - 支持按群组分组显示搜索结果
- **运行**: `python search_async.py`

### 删除记忆

#### `delete_async.py` - 异步删除记忆
- **用途**: 使用异步客户端删除记忆
- **功能**: 演示三种删除方式：
  1. 根据 `event_id` 删除特定记忆
  2. 根据 `user_id` 删除用户的所有记忆
  3. 根据 `user_id` 和 `group_id` 组合删除特定群组的记忆
- **特点**: 支持多种删除条件组合
- **运行**: `python delete_async.py`

## 对话元数据（Conversation Meta）操作

### 创建对话元数据

#### `create_meta_async.py` - 异步创建对话元数据
- **用途**: 使用异步客户端创建或更新对话元数据
- **功能**:
  - 创建对话元数据，包括场景、参与者、标签等信息
  - 支持创建特定群组的元数据或默认配置
  - 如果 `group_id` 存在则更新（upsert），不存在则创建
  - 如果省略 `group_id` 则保存为场景的默认配置
- **参数说明**:
  - `scene`: 场景类型（`group_chat` 或 `assistant`）
  - `user_details`: 参与者详情，包括用户ID、姓名、角色等
- **运行**: `python create_meta_async.py`

### 获取对话元数据

#### `get_meta_async.py` - 异步获取对话元数据
- **用途**: 使用异步客户端获取对话元数据
- **功能**:
  1. 获取特定群组的对话元数据（通过 `extra_query` 传递 `group_id`）
  2. 获取默认配置（不提供 `group_id`）
  3. 包含错误处理，当默认配置不存在时显示友好提示
- **特点**: 
  - 如果群组配置不存在，会自动回退到默认配置
  - 包含 `NotFoundError` 异常处理
- **运行**: `python get_meta_async.py`

### 更新对话元数据

#### `update_meta_async.py` - 异步更新对话元数据
- **用途**: 使用异步客户端部分更新对话元数据
- **功能**:
  - 只更新提供的字段，未提供的字段保持不变
  - 支持更新名称、描述、标签、时区、场景描述、用户详情等
  - 通过 `group_id` 定位要更新的元数据，不提供则更新默认配置
- **特点**: 部分更新，不会覆盖未提供的字段
- **运行**: `python update_meta_async.py`

## 文件分类

### 异步示例（推荐）
- `add_async.py`
- `get_async.py`
- `search_async.py`
- `delete_async.py`
- `create_meta_async.py`
- `get_meta_async.py`
- `update_meta_async.py`

### 同步示例
- `add_sync.py`

## 使用建议

1. **异步 vs 同步**: 对于生产环境，推荐使用异步客户端（`AsyncEverMemOS`），性能更好
2. **错误处理**: 参考 `get_meta_async.py` 中的错误处理方式，使用 `try-except` 捕获 `NotFoundError` 等异常
3. **参数传递**: 
   - 对于查询参数，使用 `extra_query` 传递（如 `search_async.py`）
   - 对于必需参数，直接作为方法参数传递
4. **时间格式**: 使用 ISO 8601 格式的时间字符串（如 `datetime.now(timezone.utc).isoformat()`）

## 注意事项

- 所有示例都需要先配置环境变量 `EVERMEMOS_API_KEY` 和 `EVER_MEM_OS_CLIENT_BASE_URL`
- 删除操作不可逆，请谨慎使用
- 创建默认配置时，需要不提供 `group_id` 参数
- 搜索功能使用 `extra_query` 传递参数，避免参数冲突
