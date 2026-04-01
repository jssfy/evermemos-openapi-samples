# pip install everos
# 文件上传预签名（批量）—— v1 新 API，支持一次签多个文件
#
# 实际响应结构：resp.result.data.object_list（非 resp.data）
from pprint import pprint
from everos import EverOS

client = EverOS()
obj = client.v1.object

# --- 1. 签名单个图片 ---
print("=== sign single image ===")
resp = obj.sign(
    object_list=[
        {
            "file_id": "file_img_001",
            "file_name": "photo.png",
            "file_type": "image",  # image ≤10MB
        }
    ]
)
pprint(resp)

# --- 2. 批量签名（图片 + 文档 + 视频）---
print("\n=== sign batch (image + file + video) ===")
resp = obj.sign(
    object_list=[
        {
            "file_id": "file_img_001",
            "file_name": "screenshot.jpg",
            "file_type": "image",
        },
        {
            "file_id": "file_doc_002",
            "file_name": "report.pdf",
            "file_type": "file",   # file ≤100MB
        },
        {
            "file_id": "file_vid_003",
            "file_name": "demo.mp4",
            "file_type": "video",  # video ≤500MB
        },
    ]
)
pprint(resp)

# 结果处理：resp.result.data.object_list
if resp.result and resp.result.data and resp.result.data.object_list:
    for item in resp.result.data.object_list:
        print(f"  fileId={item.file_id}  objectKey={item.object_key}")
        print(f"  uploadUrl={item.object_signed_info.url}")

# --- 3. 错误处理 ---
print("\n=== error handling ===")
from everos import BadRequestError, UnprocessableEntityError

try:
    resp = obj.sign(
        object_list=[
            {
                "file_id": "bad_file",
                "file_name": "",       # 无效文件名
                "file_type": "image",
            }
        ]
    )
except UnprocessableEntityError as e:
    print(f"422 Validation error: {e}")
except BadRequestError as e:
    print(f"400 Bad request: {e}")
