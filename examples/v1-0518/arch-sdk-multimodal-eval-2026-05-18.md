# SDK 多模态能力评估

> 日期：2026-05-18
> 对比：`stainless-helpers/sdks/everos-python`（旧）vs `python-sdk-stainless/sdks/EverOS-python`（新）
> 参考测试文档：`ops-multimodal-mms-2026-05-17.md`

---

## 核心结论

- **新 SDK 具备多模态所需的底层接口**（Content schema、`storage.sign()`、`memory.add()`）
- **完全缺失多模态辅助层**（`lib/` 目录只有 `.keep`）：自动检测、文件上传、S3 POST、URI 替换均需用户手工实现
- **API 参数已对齐新版接口**（`owner_id`/`owner_type`，`/api/v1/memory/add`，`/api/v1/object/sign`）
- `storage.sign()` 字段名为 camelCase（`fileName`/`fileType`/`fileId`），与旧 SDK 及 MMS 文档一致

---

## 一、旧 SDK 的多模态实现

### 完整文件结构

```
src/everos/lib/
├── _multimodal.py   # 编排层，透明覆盖 add()
├── _detect.py       # scan_messages()，自动检测需上传的 content
├── _upload.py       # batch_sign() + s3_post_upload()，含重试
├── _files.py        # FileInput / ResolvedFile，本地/HTTP 文件解析
└── _errors.py       # MultimodalError / FileResolveError / UploadError
```

### 完整处理流程

```
client.v1.memories.add(messages=[...])
    │
    ├─ [1] scan_messages() 扫描 content
    │       ├── type != "text" → 触发检测
    │       ├── uri 为 http(s):// → uri_type="http"（需下载）
    │       ├── uri 为本地路径   → uri_type="local"
    │       └── 其他            → 视为已有 object_key，跳过
    │
    ├─ [2] resolve_file() 解析文件
    │       ├── 本地文件 → 直接读取 MIME/大小
    │       └── HTTP URL → 流式下载到临时文件（限 100MB，60s 超时）
    │
    ├─ [3] batch_sign() 批量预签名（一次 API 调用）
    │       └── POST /api/v1/object/sign，返回 object_key + S3 presigned URL
    │
    ├─ [4] _concurrent_upload() 并发上传
    │       ├── 同步：ThreadPoolExecutor（4 worker）
    │       ├── 异步：asyncio.wait(FIRST_EXCEPTION)
    │       └── s3_post_upload()：3 次重试，5xx/超时重试，4xx 立即失败
    │
    ├─ [5] _replace_uris() 替换消息中的 uri → object_key
    │       └── 自动填充缺失的 name / ext 字段
    │
    ├─ [6] super().add() 发送修改后的消息
    │
    └─ [7] _cleanup() 删除临时文件
```

### content type → MMS fileType 映射

| content[].type | MMS sign fileType | maxSize |
|----------------|-------------------|---------|
| `"image"` | `"image"` | 10 MB |
| `"audio"` | `"file"` | 100 MB |
| `"doc"` / `"pdf"` / `"html"` / `"email"` | `"file"` | 100 MB |
| `"video"` | `"video"` | 100 MB（文档为 500 MB） |

---

## 二、新 SDK 现有多模态能力

### Content schema（完整，已对齐）

```python
# src/everos/types/content.py
class Content(BaseModel):
    type: str                           # 必填
    text: Optional[str] = None
    uri: Optional[str] = None          # object_key 或外部 URL
    base64: Optional[str] = None
    name: Optional[str] = None
    ext: Optional[str] = None
    source: Optional[str] = None
    source_info: Optional[Dict[str, object]] = None
    extras: Optional[Dict[str, object]] = None
```

### storage.sign()

```python
# 路径：/api/v1/object/sign（对应旧版 /api/v1/object/sign，路径一致）
client.storage.sign(
    object_list=[
        {
            "fileName": "photo.jpg",
            "fileType": "image",   # image / file / video
            "fileId": "your-uuid"
        }
    ]
)
# 返回 SignObjectsResponse
# .result.object_list[].objectKey       → S3 对象键
# .result.object_list[].objectSignedInfo.url    → S3 presigned POST URL
# .result.object_list[].objectSignedInfo.fields → S3 POST 表单字段
# .result.object_list[].objectSignedInfo.maxSize
```

### memory.add()（新接口，已对齐）

```python
client.memory.add(
    owner_id="user_123",     # 新字段（旧版是 user_id）
    owner_type="user",       # 新字段
    session_id="...",
    messages=[...],
    async_mode=False,
)
```

### lib/ 目录现状

```
src/everos/lib/
└── .keep        # 仅占位，无任何实现文件
```

---

## 三、差距分析

### 能力对比

| 能力 | 新 SDK | 旧 SDK |
|------|--------|--------|
| Content schema（type/uri/text/base64 等） | ✅ | ✅ |
| storage.sign() 预签名接口 | ✅ | ✅ |
| memory.add() API | ✅ | ✅ |
| 新接口参数（owner_id/owner_type） | ✅ | ❌（user_id） |
| scan_messages() 自动文件检测 | ❌ | ✅ |
| 本地文件上传 | ❌ | ✅ |
| HTTP URL 下载 + 上传 | ❌ | ✅ |
| batch_sign() 批量签名 | ❌ | ✅ |
| S3 presigned POST（含重试） | ❌ | ✅ |
| 并发上传（4 worker / asyncio） | ❌ | ✅ |
| URI 自动替换（uri → object_key） | ❌ | ✅ |
| name/ext 自动填充 | ❌ | ✅ |
| 异步多模态（AsyncEverOS） | ❌ | ✅ |
| 临时文件自动清理 | ❌ | ✅ |
| 多模态专用异常（FileResolveError 等） | ❌ | ✅ |

### 新 SDK 使用多模态时的手工流程

```python
import httpx, uuid

client = EverOS()

# 1. 获取预签名 URL
sign_resp = client.storage.sign(
    object_list=[{"fileName": "photo.jpg", "fileType": "image", "fileId": str(uuid.uuid4())}]
)
item = sign_resp.result.object_list[0]
object_key = item.object_key
signed = item.object_signed_info

# 2. 上传文件（用户自行实现）
with open("/path/to/photo.jpg", "rb") as f:
    fields = {k: v for k, v in signed.fields.items()}
    httpx.post(signed.url, data=fields, files={"file": f})

# 3. 手动构造 content，uri 填 object_key
client.memory.add(
    owner_id="user_123",
    owner_type="user",
    session_id="session_abc",
    messages=[{
        "sender_id": "user_123",
        "role": "user",
        "content": [
            {"type": "image", "uri": object_key, "name": "photo.jpg", "ext": "jpg"}
        ]
    }]
)
```

---

## 四、与测试文档对照（ops-multimodal-mms-2026-05-17.md）

| 测试文档要点 | 新 SDK 状态 |
|-------------|------------|
| Sign → S3 Upload → memory add 三步流程 | 接口齐全，但需手工串联 |
| `owner_id` / `owner_type` 顶层必填 | ✅ memory.add() 参数已支持 |
| objectKey 直接作为 content[].uri | ✅ Content.uri 字段存在 |
| audio → fileType=`"file"`（非 `"audio"`） | 用户须手动映射，无自动化 |
| image → fileType=`"image"` | 同上 |
| S3 POST `file` 字段必须最后 | 用户自行处理 multipart 顺序 |
| dev ASR/OCR 已启用（2026-05-17 修复后） | 与 SDK 无关，服务端能力 |
| memory get `memory_type` 必填 | ✅ SDK 参数中有 `memory_type` |

---

## 五、建议

### 短期：手工方式（当前可用）

使用 `test_sdk.py` 中的纯文本消息验证 add/get/search，多模态需手工走 Sign → Upload → Add 三步，参考 `ops-multimodal-mms-2026-05-17.md` 中的 curl 步骤。

### 中期：移植 lib 层

将旧 SDK 的 `lib/` 五个文件移植到新 SDK，需调整：

1. **接口适配**：旧版 `user_id` → 新版 `owner_id` / `owner_type`
2. **资源路径**：旧版 `client.v1.memories` → 新版 `client.memory`
3. **sign 接口**：旧版 `client.v1.object.sign()` → 新版 `client.storage.sign()`
4. **字段名**：新版 `storage.sign()` 用 camelCase（`fileName`/`fileType`/`fileId`），与旧版 snake_case 不同

### 优先级判断

若现阶段只需 dev 测试验证多模态服务端能力（ASR/OCR 是否正常），手工三步流程已足够，不需要立即移植 lib 层。若要对外提供 SDK 给业务方使用，lib 层移植是必须项。
