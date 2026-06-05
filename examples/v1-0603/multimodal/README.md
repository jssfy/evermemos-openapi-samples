# 多模态示例（everos_cloud）

演示 `everos_cloud` 的**透明多模态上传**：`client.v1.memories.add()` 被 SDK lib 层重写为
`MemoriesResourceWithMultimodal`，content item 带 `uri` 时自动 sign + upload，再提交 add。

## 文件

| 文件 | 说明 |
|------|------|
| `_common.py` | 共享配置（API_KEY/BASE_URL）+ `make_test_image()` 生成 1x1 测试图 |
| `01_add_multimodal.py` | 多模态 add（text + image 混排，本地文件 uri 自动上传）+ flush 提交 session |
| `02_search_multimodal.py` | add（多模态）→ flush → 等待 → search（自包含）|
| `03_get_multimodal.py` | add（多模态，doc 类型）→ flush → 等待 → get（自包含）|

## 运行

```bash
cd examples/v1-0603/multimodal
python3 01_add_multimodal.py
python3 02_search_multimodal.py
python3 03_get_multimodal.py
```

## 多模态 content item 格式

```python
messages=[{
  "role": "user", "timestamp": <ms>,
  "content": [
    {"type": "text",  "text": "Here's a photo I took."},
    {"type": "image", "uri": "/path/to/local.png"},          # 本地文件 → 自动上传
    {"type": "image", "uri": "https://example.com/pic.jpg"}, # http(s) → 下载后上传
    {"type": "doc",   "uri": "/path/to/report.pdf"},         # doc → file_type=file
  ],
}]
```

- 支持 type：`text` / `image` / `audio` / `doc` / `pdf` / `html` / `email`
- `uri` 自动识别：本地文件路径 / http(s) URL / 已是 object_key（透传）
- 签名上传由 lib 层透明完成，调用方无需手动调 `object.sign`

## 注意

- **多模态价值在 add 端的自动上传**：`type(client.v1.memories).__name__ == "MemoriesResourceWithMultimodal"` 即生效；
  search / get 接口与普通记忆完全一致（多模态内容已在 add 时入库）。
- **search/get 是否返回结果取决于服务端异步记忆提取**（与是否多模态无关）：
  单条短对话 + 数秒等待未必提取出 episode/profile；这与纯文本示例行为一致。
  生产中应轮询 `tasks.retrieve()` 或拉长等待，对话越完整提取越充分。
- 示例用 1x1 PNG 仅为验证「上传链路」；真实图片/文档可被服务端进一步理解。
