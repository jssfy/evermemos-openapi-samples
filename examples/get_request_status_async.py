import os
import asyncio
from evermemos import AsyncEverMemOS

client = AsyncEverMemOS(
    api_key=os.environ.get(
        "EVERMEMOS_API_KEY",
    ),
    base_url=os.environ.get(
        "EVER_MEM_OS_CLIENT_BASE_URL",
    ),
)


async def main() -> None:
    # 查询请求处理状态
    # 注意：request_id 需要从之前的异步操作（如 load、create 等）的响应中获取
    # 这里使用环境变量或示例 request_id，实际使用时需要替换为真实的 request_id
    request_id = os.environ.get("EVERMEMOS_REQUEST_ID", "02176953239727900000000000000000000ffff0a247c5c592199")
    
    if request_id == "your_request_id_here":
        print("⚠️  警告: 请设置环境变量 EVERMEMOS_REQUEST_ID 或修改代码中的 request_id")
        print("    request_id 通常从 load、create 等异步操作的响应中获取")
        print()
    
    request_status = await client.v1.stats.request.get(
        request_id=request_id,
    )
    
    print(f"message: {request_status.message}")
    print(f"success: {request_status.success}")
    print(f"found: {request_status.found}")
    
    if request_status.data:
        print(f"\n请求状态数据:")
        for key, value in request_status.data.items():
            print(f"  {key}: {value}")
    else:
        print("\n请求状态数据: (无)")


if __name__ == "__main__":
    asyncio.run(main())
