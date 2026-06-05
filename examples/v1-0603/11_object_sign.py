#!/usr/bin/env python3
"""
11_object_sign.py — 获取对象存储预签名上传 URL

client.v1.object.sign() 返回 S3 presigned POST 信息，
可供前端/客户端直接上传文件，无需经过后端转发。

注：dev 环境部分 MIME 类型可能返回 1002（文件类型不支持），
    以实际业务允许的类型为准。
"""
import asyncio, os
from everos_cloud import AsyncEverOS
from pprint import pprint

API_KEY  = os.getenv("EVEROS_API_KEY",  "ddcf3ffb-df31-4c9c-9d30-fb2ee67aed26")
BASE_URL = os.getenv("EVER_OS_BASE_URL", "https://dev-gateway.aws.evermind.ai")

client = AsyncEverOS(api_key=API_KEY, base_url=BASE_URL)


async def main() -> None:
    resp = await client.v1.object.sign(
        object_list=[
            {"fileId": "f001", "fileName": "document.pdf",  "fileType": "application/pdf"},
            {"fileId": "f002", "fileName": "photo.jpg",     "fileType": "image/jpeg"},
            {"fileId": "f003", "fileName": "audio.mp3",     "fileType": "audio/mpeg"},
        ]
    )
    pprint(resp)

    # 解析结果
    items = getattr(getattr(resp, "data", None), "object_list", None) or []
    for item in items:
        print(f"\nfileId: {getattr(item, 'file_id', None)}")
        print(f"objectKey: {getattr(item, 'object_key', None)}")
        signed = getattr(item, "object_signed_info", None)
        if signed:
            print(f"uploadUrl: {signed.url}")


if __name__ == "__main__":
    asyncio.run(main())
