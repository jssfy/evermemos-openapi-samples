#!/usr/bin/env python3
# pip install everos requests
#
# 多模态记忆写入示例：文件上传 + 记忆存储
#
# 完整链路：
#   1. object.sign()  → 获取预签名 URL
#   2. requests.post() → S3 直传上传文件
#   3. memories.add() → 个人多模态记忆（含 image/file content_item）
#   4. memories.group.add() → 群组多模态记忆
#   5. memories.flush() / memories.group.flush() → 触发边界提取
#
# 前提：在本地准备好测试文件（或修改下方路径），并配置 EVEROS_API_KEY 环境变量

import mimetypes
import os
import tempfile
import time
import uuid

import requests
from everos import EverOS

# ============================================================
# 配置
# ============================================================

USER_ID = "sdk_multimodal_demo"
GROUP_ID = "sdk_mm_group_001"
SENDER_ALICE = "alice"
SENDER_BOB = "bob"

# 修改为本地实际存在的文件路径，支持 image / pdf / video
DEMO_FILES = [
    "https://s41.ax1x.com/2026/04/01/peG0uAH.png",
    # "/path/to/photo.png",
    # "/path/to/report.pdf",
]

# ============================================================
# 工具函数
# ============================================================

EXT_TO_FILE_TYPE = {
    ".jpg": "image", ".jpeg": "image", ".png": "image",
    ".gif": "image", ".webp": "image", ".bmp": "image",
    ".mp4": "video", ".mov": "video",
    ".mp3": "audio", ".wav": "audio",
    ".pdf": "file", ".doc": "file", ".docx": "file",
    ".ppt": "file", ".pptx": "file", ".xls": "file", ".xlsx": "file",
}

EXT_TO_CONTENT_TYPE = {
    ".jpg": "image", ".jpeg": "image", ".png": "image",
    ".gif": "image", ".webp": "image", ".bmp": "image",
}


def ts():
    return int(time.time() * 1000)


def file_type(path):
    return EXT_TO_FILE_TYPE.get(os.path.splitext(path)[1].lower(), "file")


def content_type(path):
    return EXT_TO_CONTENT_TYPE.get(os.path.splitext(path)[1].lower(), "file")


# ============================================================
# Step 1: Sign + Upload
# ============================================================

def _resolve_to_local(path: str) -> tuple[str, str, bool]:
    """
    If path is an HTTP URL, download to a temp file.
    Returns (local_path, file_name, is_temp).
    """
    if path.startswith("http://") or path.startswith("https://"):
        file_name = path.split("?")[0].rstrip("/").split("/")[-1] or "download"
        ext = os.path.splitext(file_name)[1]
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=ext)
        print(f"  Downloading: {path}")
        r = requests.get(path, timeout=30)
        r.raise_for_status()
        tmp.write(r.content)
        tmp.close()
        return tmp.name, file_name, True
    return path, os.path.basename(path), False


def upload_file(client: EverOS, path: str) -> str | None:
    """
    Sign the file via SDK, then upload directly to S3.
    Accepts local file path or HTTP URL.
    Returns object_key on success, None on failure.
    """
    local_path, file_name, is_temp = _resolve_to_local(path)
    ftype = file_type(file_name)
    file_id = f"demo-{uuid.uuid4().hex[:8]}"

    print(f"  Signing: {file_name} ({ftype})")
    sign_resp = client.v1.object.sign(
        object_list=[{"file_id": file_id, "file_name": file_name, "file_type": ftype}]
    )

    if not (sign_resp.result and sign_resp.result.data and sign_resp.result.data.object_list):
        print(f"    [FAIL] sign returned no object_list")
        if is_temp:
            os.unlink(local_path)
        return None

    item = sign_resp.result.data.object_list[0]
    object_key = item.object_key
    info = item.object_signed_info

    # S3 direct upload (multipart/form-data)
    ct = (
        info.fields.get("Content-Type")
        or mimetypes.guess_type(file_name)[0]
        or "application/octet-stream"
    )
    try:
        with open(local_path, "rb") as f:
            upload_resp = requests.post(
                info.url,
                data=info.fields,
                files={"file": (file_name, f, ct)},
                timeout=60,
            )
    finally:
        if is_temp:
            os.unlink(local_path)

    if upload_resp.status_code in (200, 201, 204):
        print(f"    [OK] objectKey: {object_key}")
        return object_key
    else:
        print(f"    [FAIL] S3 upload HTTP {upload_resp.status_code}: {upload_resp.text[:200]}")
        return None


# ============================================================
# Step 2: Add personal memory with multimodal content
# ============================================================

def add_personal_memory(client: EverOS, uploaded: list[tuple[str, str]]):
    """
    POST /api/v1/memories — 个人场景
    uploaded: [(file_name, object_key), ...]
    """
    print("\n=== Step 2: Add Personal Memory (multimodal) ===")
    mem = client.v1.memories

    # 构造 content items：text + image/file 引用
    content_items = [{"type": "text", "text": "我上传了几个文件，请帮我分析一下内容："}]
    for file_name, object_key in uploaded:
        ext = os.path.splitext(file_name)[1].lstrip(".")
        item = {
            "type": content_type(file_name),
            "name": file_name,
            "uri": object_key,
        }
        if ext:
            item["ext"] = ext
        content_items.append(item)

    # 主题 1：文件讨论
    resp = mem.add(
        user_id=USER_ID,
        messages=[{"role": "user", "timestamp": ts(), "content": content_items}],
    )
    print(f"  add (multimodal): status={resp.data.status}")

    time.sleep(0.3)
    resp = mem.add(
        user_id=USER_ID,
        messages=[{
            "role": "assistant",
            "timestamp": ts(),
            "content": "好的，我来帮你分析这些文件的内容。",
        }],
    )
    print(f"  add (assistant reply): status={resp.data.status}")

    time.sleep(0.3)
    resp = mem.add(
        user_id=USER_ID,
        messages=[{
            "role": "user",
            "timestamp": ts(),
            "content": "文件里的架构设计有什么亮点？",
        }],
    )
    print(f"  add (follow-up): status={resp.data.status}")

    # 主题 2：话题切换（触发边界检测）
    time.sleep(0.3)
    resp = mem.add(
        user_id=USER_ID,
        messages=[{
            "role": "user",
            "timestamp": ts(),
            "content": "换个话题，下周我想去日本东京旅游，有推荐的地方吗？",
        }],
    )
    print(f"  add (topic switch): status={resp.data.status}")

    return resp


# ============================================================
# Step 3: Add group memory with multimodal content
# ============================================================

def add_group_memory(client: EverOS, uploaded: list[tuple[str, str]]):
    """
    POST /api/v1/memories/group — 群组场景
    uploaded: [(file_name, object_key), ...]
    """
    print("\n=== Step 3: Add Group Memory (multimodal) ===")
    group_mem = client.v1.memories.group

    # Alice 上传文件发到群里
    content_items = [{"type": "text", "text": "大家好，我上传了几个文件供团队参考："}]
    for file_name, object_key in uploaded:
        ext = os.path.splitext(file_name)[1].lstrip(".")
        item = {
            "type": content_type(file_name),
            "name": file_name,
            "uri": object_key,
        }
        if ext:
            item["ext"] = ext
        content_items.append(item)

    resp = group_mem.add(
        group_id=GROUP_ID,
        messages=[{
            "role": "user",
            "sender_id": SENDER_ALICE,
            "sender_name": "Alice",
            "timestamp": ts(),
            "content": content_items,
        }],
    )
    print(f"  group add (multimodal, Alice): status={resp.data.status}")

    time.sleep(0.3)
    # Bob 回复
    resp = group_mem.add(
        group_id=GROUP_ID,
        messages=[{
            "role": "user",
            "sender_id": SENDER_BOB,
            "sender_name": "Bob",
            "timestamp": ts(),
            "content": "收到，我看看这些文件。架构图的分层设计思路很清晰！",
        }],
    )
    print(f"  group add (Bob reply): status={resp.data.status}")

    time.sleep(0.3)
    # 话题切换（触发边界检测）
    resp = group_mem.add(
        group_id=GROUP_ID,
        messages=[{
            "role": "user",
            "sender_id": SENDER_ALICE,
            "sender_name": "Alice",
            "timestamp": ts(),
            "content": "好的，文件先放一边。下周五团建地点定了吗？我推荐那家日料店。",
        }],
    )
    print(f"  group add (topic switch, Alice): status={resp.data.status}")

    return resp


# ============================================================
# Step 4: Flush
# ============================================================

def flush_all(client: EverOS):
    print("\n=== Step 4: Flush ===")

    resp = client.v1.memories.flush(user_id=USER_ID)
    print(f"  personal flush: status={resp.data.status}")

    resp = client.v1.memories.group.flush(group_id=GROUP_ID)
    print(f"  group flush: status={resp.data.status}")


# ============================================================
# Main
# ============================================================

def main():
    client = EverOS()  # reads EVEROS_API_KEY + EVEROS_BASE_URL from env

    # --- Step 1: Upload files ---
    print("=== Step 1: Sign + Upload files ===")
    uploaded: list[tuple[str, str]] = []
    for path in DEMO_FILES:
        is_url = path.startswith("http://") or path.startswith("https://")
        if not is_url and not os.path.isfile(path):
            print(f"  [SKIP] not found: {path}")
            continue
        file_name = path.split("?")[0].rstrip("/").split("/")[-1] if is_url else os.path.basename(path)
        object_key = upload_file(client, path)
        if object_key:
            uploaded.append((file_name, object_key))

    if not uploaded:
        print("  [INFO] No files uploaded — skipping multimodal content items")
        print("         Set DEMO_FILES to local file paths to test full flow.\n")

    # --- Step 2: Personal memory ---
    add_personal_memory(client, uploaded)

    # --- Step 3: Group memory ---
    add_group_memory(client, uploaded)

    # --- Step 4: Flush ---
    flush_all(client)

    print("\nDone.")


if __name__ == "__main__":
    main()
