# Multimodal 自动上传实现分析

## 核心结论

`client.v1.memories.add()` 透明支持 HTTP URL 和本地文件路径——SDK 内部自动完成"检测 → 下载 → 签名 → 上传 → 替换 URI"的完整流程，调用方无需感知。

**实现方式**：在客户端初始化时将 `MemoriesResource` 替换为 `MemoriesResourceWithMultimodal`，后者重写 `add()` 方法，在真正调用 API 前完成所有上传准备工作。

**五个阶段**：

```
scan_messages → resolve_file → batch_sign → s3_post_upload → _replace_uris → super().add()
    检测           下载/读取      批量签名      并发上传         替换 URI        调用 API
```

---

## 一、入口：客户端注入（`_client.py`）

`EverOS.__init__()` 在 `super().__init__()` 之后执行注入：

```python
# _client.py L94-99
from .resources.v1.v1 import V1Resource as _V1Resource
from .lib._multimodal import MemoriesResourceWithMultimodal as _MemMultimodal
_v1 = _V1Resource(self)
_v1.__dict__["memories"] = _MemMultimodal(self)  # 覆盖原始 MemoriesResource
self.__dict__["v1"] = _v1
```

这使得 `client.v1.memories` 实例为 `MemoriesResourceWithMultimodal`，从而拦截所有 `add()` 调用。`AsyncEverOS` 采用相同模式注入 `AsyncMemoriesResourceWithMultimodal`。

---

## 二、编排层（`lib/_multimodal.py`）

`MemoriesResourceWithMultimodal.add()` 的完整流程：

```python
# _multimodal.py L38-93
def add(self, *, messages, user_id, **kwargs):
    msg_list   = _materialise(messages)          # 规范化为 dict 列表
    tasks      = scan_messages(msg_list)         # 1. 检测
    if not tasks:
        return super().add(...)                  # 无需上传，直接转发

    msg_list   = copy.deepcopy(msg_list)         # 深拷贝，保护原始数据
    resolved   = []
    try:
        _resolve_all(tasks, resolved)            # 2. 下载/读取
        signed  = batch_sign(self._client,
                              tasks, resolved)   # 3. 批量签名
        results = _concurrent_upload(signed,
                                      tasks)     # 4. 并发上传
        _replace_uris(msg_list, tasks, results)  # 5. 替换 URI
        return super().add(messages=msg_list, …) # 6. 调用 API
    finally:
        _cleanup(resolved)                       # 无论成败都清理临时文件
```

**异步版本**（`AsyncMemoriesResourceWithMultimodal`）逻辑相同，各阶段使用 async 对应函数。

---

## 三、阶段详解

### 阶段 1：检测（`lib/_detect.py`）

`scan_messages()` 遍历 messages，对每个 content item 判断：

| `uri` 值 | 判断规则 | 处理 |
|----------|---------|------|
| `http://…` 或 `https://…` | `uri.startswith("http")` | `uri_type="http"` → 下载后上传 |
| 本地文件路径（含 `~/…`） | `os.path.isfile(os.path.expanduser(uri))` | `uri_type="local"` → 直接上传 |
| 其他（如已有 object key） | 以上条件都不满足 | 跳过，直接透传 |
| `type="text"` 或 `uri` 为空 | 无条件跳过 | 跳过 |

返回 `List[UploadTask]`，记录每个需要上传的 item 在 messages 中的 `msg_idx` 和 `content_idx`。

content type 到 sign API `file_type` 的映射：

```python
# _detect.py L29-36
{
    "image": "image",
    "audio": "file",
    "doc":   "file",
    "pdf":   "file",
    "html":  "file",
    "email": "file",
}
```

---

### 阶段 2：文件解析/下载（`lib/_files.py`）

#### 本地文件（`_resolve_from_path()`，L110-120）

直接读取文件元数据，返回 `ResolvedFile(is_temp=False)`。

#### HTTP URL（`_resolve_from_url()`，L123-162）

流式下载到临时文件，边下边检查大小限制：

```python
# _files.py L125-146（简化）
fd, tmp_path = tempfile.mkstemp(prefix="everos_")
with httpx.Client(timeout=60.0) as client:
    with client.stream("GET", url) as resp:
        resp.raise_for_status()
        content_type = resp.headers.get("content-type", "")
        total = 0
        for chunk in resp.iter_bytes(chunk_size=65536):   # 64 KB 分块
            total += len(chunk)
            if total > 100 * 1024 * 1024:                # 超过 100 MB
                os.unlink(tmp_path)
                raise FileResolveError("download exceeds 100 MB limit")
            os.write(fd, chunk)
```

返回 `ResolvedFile(is_temp=True)`，临时文件在 `_cleanup()` 中删除。

**关键常量**：

```python
_DEFAULT_MAX_DOWNLOAD_SIZE = 100 * 1024 * 1024   # 下载上限
_DEFAULT_DOWNLOAD_TIMEOUT  = 60.0                 # 下载超时（秒）
_STREAM_CHUNK_SIZE         = 64 * 1024            # 分块大小
```

---

### 阶段 3：批量签名（`lib/_upload.py`，`batch_sign()`，L56-95）

所有文件**一次** API 调用完成签名，避免多次往返：

```python
# _upload.py L62-72
object_list = [
    {
        "file_id":   f"sdk-{uuid.uuid4().hex}",   # 本地生成，用于关联
        "file_name": resolved.filename,
        "file_type": task.file_type,              # "image" 或 "file"
    }
    for task, resolved in zip(upload_tasks, resolved_files)
]
sign_resp = client.v1.object.sign(object_list=object_list)
```

响应包含每个文件的：
- `object_key`：最终替换到 `uri` 的值
- `object_signed_info.url`：S3 预签名上传 URL
- `object_signed_info.fields`：S3 multipart/form-data 字段（含签名）

---

### 阶段 4：并发上传（`lib/_upload.py`，`s3_post_upload()`）

#### 上传请求

```python
# _upload.py L109-115
with resolved.open() as fh:          # 流式打开，不加载进内存
    resp = httpx.post(
        signed.upload_url,
        data=signed.upload_fields,   # 签名字段
        files={"file": (filename, fh, content_type)},
        timeout=120.0,
    )
```

S3 返回 200/201/204 视为成功。

#### 重试策略

```python
# _upload.py L103-149
for attempt in range(3):
    try:
        resp = httpx.post(...)
        if resp.status_code in (200, 201, 204):
            return UploadResult(...)
        elif resp.status_code < 500:
            raise UploadError(...)       # 4xx：不重试，直接抛出
        # 5xx：记录错误，继续重试
    except httpx.TimeoutException:
        pass                             # 超时：继续重试
    time.sleep(1.0)                      # 重试间隔 1 秒
raise UploadError("failed after 3 attempts")
```

#### 并发执行（同步）

```python
# _multimodal.py L221-249
with ThreadPoolExecutor(max_workers=4) as executor:
    futures = [executor.submit(s3_post_upload, sf) for sf in signed_files]
    for fut in as_completed(futures):
        if fut.exception():
            # 第一个失败立即取消其余任务
            for other in futures:
                other.cancel()
            raise MultimodalError(...) from fut.exception()
```

**异步版本**（`_async_concurrent_upload()`）使用 `asyncio.wait(return_when=FIRST_EXCEPTION)`，逻辑相同。

---

### 阶段 5：URI 替换（`_replace_uris()`，L311-331）

```python
# _multimodal.py L311-331
for result, task in zip(results, upload_tasks):
    item = msg_list[task.msg_idx]["content"][task.content_idx]
    item["uri"] = result.object_key          # 替换为 object key
    if not item.get("name"):
        item["name"] = result.filename       # 补全文件名
    if not item.get("ext"):
        item["ext"] = result.filename.rsplit(".", 1)[-1]  # 补全扩展名
```

修改的是 `deepcopy` 的副本，不影响用户传入的原始数据。

---

## 四、完整调用链（HTTP URL 场景）

```
用户传入:  uri = "https://s41.ax1x.com/2026/04/01/peG0uAH.png"

scan_messages()                               [_detect.py:72]
  → UploadTask(uri_type="http", file_type="image")

_resolve_from_url()                           [_files.py:123]
  → GET https://s41.ax1x.com/2026/04/01/peG0uAH.png  (流式，64KB块)
  → /tmp/everos_xxxxxx  (临时文件, is_temp=True)
  → ResolvedFile(filename="peG0uAH.png", content_type="image/png")

batch_sign()                                  [_upload.py:56]
  → POST /api/v1/object/sign  {file_type="image", file_name="peG0uAH.png"}
  → SignedFile(object_key="memory/2026/...", upload_url="https://s3...")

s3_post_upload()                              [_upload.py:98]
  → POST https://s3...  multipart/form-data  (流式上传)
  → HTTP 204 ✓
  → UploadResult(object_key="memory/2026/...")

_replace_uris()                               [_multimodal.py:311]
  → content[0]["uri"] = "memory/2026/..."    ← 替换完成

super().add(messages=[...已替换URI...])       [生成的 MemoriesResource]
  → POST /api/v1/memories/add

_cleanup()                                    [_multimodal.py:334]
  → 删除 /tmp/everos_xxxxxx
```

---

## 五、错误类型

```
MultimodalError            # 基类
├── FileResolveError       # 检测/下载阶段
│   ├─ HTTP 4xx/5xx
│   ├─ 下载超过 100 MB
│   ├─ 下载超时
│   └─ 本地路径不存在或非文件
└── UploadError            # 签名/上传阶段
    ├─ object.sign() 返回错误
    ├─ S3 4xx
    └─ S3 5xx 重试 3 次后仍失败
```

所有异常链保留原始 cause（`__cause__`），临时文件在 `finally` 块中保证清理。

---

## 六、关键设计决策

| 设计点 | 实现 |
|--------|------|
| 流式处理 | 文件始终流式读写，不全量加载到内存 |
| 批量签名 | 所有文件一次 `object.sign()` 调用 |
| 并发上传 | 同步 4 线程 / 异步 asyncio Task |
| 失败快速停止 | 第一个上传失败立即取消其余任务 |
| 重试范围 | 仅 S3 上传重试（5xx/超时），下载和签名不重试 |
| 大小限制 | 100 MB 下载上限，超限边下边抛出异常 |
| 原始数据保护 | `deepcopy` 后再修改，不污染调用方数据 |
| 临时文件保证 | `finally` 块无条件清理 |
| object key 透传 | 非 http/本地文件的 uri 直接透传，不重复上传 |
