import os
import asyncio
from evermemos import AsyncEverMemOS

request_stats = AsyncEverMemOS().v1.stats.request


async def main() -> None:
    # Query request processing status
    # Note: request_id needs to be obtained from the response of previous async operations (such as load, create, etc.)
    # Here we use environment variable or example request_id, replace with real request_id when actually using
    request_id = os.environ.get("EVERMEMOS_REQUEST_ID", "02176953239727900000000000000000000ffff0a247c5c592199")
    
    if request_id == "your_request_id_here":
        print("⚠️  Warning: Please set environment variable EVERMEMOS_REQUEST_ID or modify request_id in code")
        print("    request_id is usually obtained from responses of async operations like load, create, etc.")
        print()
    
    response = await request_stats.get(
        request_id=request_id,
    )
    
    print(f"message: {response.message}")
    print(f"success: {response.success}")
    print(f"found: {response.found}")
    
    if response.data:
        print(f"\nRequest status data:")
        for key, value in response.data.items():
            print(f"  {key}: {value}")
    else:
        print("\nRequest status data: (none)")


if __name__ == "__main__":
    asyncio.run(main())
