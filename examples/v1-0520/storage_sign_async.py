# everos should've been installed:
# pip install https://pkg.stainless.com/s/everos-trial-python/ea677a49282be2c1723740b1a7fa943cc01e0d5a/everos-0.0.1-py3-none-any.whl
#
# NEW in 0.0.1: client.v1.storage.sign() — get pre-signed upload URLs for object storage
#   Returned signed_info.url + fields can be used for direct browser/client upload (S3 form POST).
#
# NOTE: dev environment returns status=1002 ("文件类型不支持") for all MIME types tested.
#       This feature may require specific file type configuration or a different environment.
import asyncio
from everos import AsyncEverOS
from pprint import pprint

client = AsyncEverOS()
storage = client.v1.storage


async def main() -> None:
    # Request pre-signed URLs for one or more files
    response = await storage.sign(
        object_list=[
            {
                "fileId": "file_001",
                "fileName": "document.pdf",
                "fileType": "application/pdf",
            },
            {
                "fileId": "file_002",
                "fileName": "image.png",
                "fileType": "image/png",
            },
        ]
    )
    pprint(response)

    # Access signed results
    if response.result and response.result.data and response.result.data.object_list:
        for obj in response.result.data.object_list:
            print(f"\nfileId: {obj.file_id}")
            print(f"objectKey: {obj.object_key}")
            if obj.object_signed_info:
                print(f"uploadUrl: {obj.object_signed_info.url}")
                print(f"fields: {obj.object_signed_info.fields}")


if __name__ == "__main__":
    asyncio.run(main())
