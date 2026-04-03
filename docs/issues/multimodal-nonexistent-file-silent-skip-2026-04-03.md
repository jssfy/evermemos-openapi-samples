# Issue: 本地文件路径不存在时 SDK 静默跳过，不抛异常

**日期**：2026-04-03
**状态**：⚠️ 已知行为（设计如此），建议调用方自行防御
**涉及文件**：`everos/lib/_detect.py` → `scan_messages()` / `_is_local_file()`

---

## 核心结论

| 项目 | 说明 |
|------|------|
| **现象** | `uri: "./whiteboard.jpg"` 文件不存在时，SDK 不报错，将原始字符串透传给 API |
| **根因** | `_is_local_file()` 用 `os.path.isfile()` 判断，返回 False 后走 `else: continue`，当作已有 `object_key` 处理 |
| **影响** | SDK 层成功，API 返回 `202 Accepted`；服务端异步处理时因 `object_key` 无效可能静默失败 |
| **建议** | 调用前用 `os.path.isfile()` 断言，或使用 `async_mode=False` 让服务端错误同步暴露 |

---

## 复现场景

```python
response = client.v1.memories.add(
    user_id="user_demo_001",
    messages=[{
        "role": "user",
        "timestamp": now_ms,
        "content": [
            {"type": "image", "uri": "./whiteboard.jpg"},  # ← 文件不存在
        ],
    }],
)
# 不抛异常，返回 status=queued
```

---

## Debug 日志分析（`03.4_save_multi_modal_debug.py` 实测）

### 检测阶段 — `./whiteboard.jpg` 完全不出现

```
DEBUG everos: Multimodal detected: 1 file(s) to upload
DEBUG everos:   [0] messages[1].content[1] type=image uri=https://s41.ax1x.com/... (http)
```

仅检测到 1 个文件（HTTP URL），`./whiteboard.jpg` 没有创建 `UploadTask`，在 `scan_messages()` 内被 `else: continue` 静默跳过。

### 代码执行路径

```python
# _detect.py: scan_messages()
if _is_http_uri(uri):          # "./whiteboard.jpg" → False
    uri_type = "http"
elif _is_local_file(uri):      # os.path.isfile("./whiteboard.jpg") → False（文件不存在）
    uri_type = "local"
else:
    continue                   # ← 走这里，跳过，不创建 UploadTask
```

### 最终发送给 API 的 json_data（关键证据）

```json
{
  "messages": [
    {
      "role": "user",
      "content": [
        {
          "type": "image",
          "uri": "./whiteboard.jpg",    ← 原字符串未经处理，直接透传
          "name": "whiteboard.jpg",
          "ext": "jpg"
        }
      ]
    },
    {
      "role": "user",
      "content": [
        {
          "type": "image",
          "uri": "fee1c04a813880d9/dcd99e91-dd24-46cb-ba6e-0b341c6c1440",  ← HTTP URL 正常替换为 object_key
          "name": "peG0uAH.png",
          "ext": "png"
        }
      ]
    }
  ]
}
```

### API 响应

```
POST /api/v1/memories → HTTP 202 Accepted
status=queued  task_id=02177520764863000000000000000000000ffff0a1f5228c629aa
```

**SDK 层完全无报错**，服务端将任务入队。但 `uri: "./whiteboard.jpg"` 不是合法的 `object_key`，后续异步处理时该内容项会被忽略或导致 task 失败。

---

## 完整处理流程对比（同一次调用中两个 uri 的命运）

```
messages[0].content[1].uri = "./whiteboard.jpg"（不存在的本地路径）
  scan_messages: _is_local_file() → False → continue → 不创建 UploadTask
  → 不下载、不签名、不上传
  → json_data 中 uri 保持 "./whiteboard.jpg"（无效值）
  → 服务端静默失败

messages[1].content[1].uri = "https://s41.ax1x.com/.../peG0uAH.png"（HTTP URL）
  scan_messages: _is_http_uri() → True → 创建 UploadTask(uri_type="http")
  → httpx 下载 → 183108 bytes, image/png → tempfile
  → POST /api/v1/object/sign → object_key: fee1c04a.../dcd99e91-...
  → POST s3.us-west-2.amazonaws.com → HTTP 204 ✅
  → json_data 中 uri 替换为 object_key ✅
  → Cleaned up 1 temp file(s)
```

---

## 建议

### 方案 1：调用前断言（推荐，最简单）

```python
import os

for msg in messages:
    for item in msg.get("content", []):
        uri = item.get("uri", "")
        if uri and not uri.startswith("http") and "://" not in uri:
            assert os.path.isfile(uri), f"File not found: {uri}"
```

### 方案 2：使用同步模式，让服务端错误同步暴露

```python
response = client.v1.memories.add(
    ...,
    async_mode=False,   # HTTP 200 时文件已处理；服务端拒绝时同步报错
)
```

### 方案 3：轮询 task_id 验证最终状态

```python
import time

response = client.v1.memories.add(...)
task_id = response.data.task_id

for _ in range(10):
    result = client.v1.tasks.retrieve(task_id).data
    if result.status == "success":
        print("OK")
        break
    elif result.status == "failed":
        print(f"Task failed: {task_id}")
        break
    time.sleep(1)
# ⚠️ task_id TTL = 1 小时，超时后 404
```

---

## 相关文件

| 文件 | 说明 |
|------|------|
| `everos/lib/_detect.py` | `scan_messages()` / `_is_local_file()` — 静默跳过逻辑所在 |
| `everos/lib/_multimodal.py` | `_resolve_all()` — 仅处理已识别的 UploadTask |
| `examples/getting-started/03.3_save_multi_modal_simple.py` | 触发此问题的示例（`./whiteboard.jpg` 为占位路径） |
| `examples/getting-started/03.4_save_multi_modal_debug.py` | 开启 debug 日志的复现版本 |
