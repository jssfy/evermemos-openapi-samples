# EverMemOS should've been installed (pip install evermemos -U)
import os
import asyncio
from evermemos import AsyncEverMemOS

request_stats = AsyncEverMemOS().v0.status.request


async def main() -> None:
    # Query request processing status
    # Note: request_id needs to be obtained from the response of previous async operations (such as load, create, etc.)
    # Here we use environment variable or example request_id, replace with real request_id when actually using
    request_id = os.environ.get("EVERMEMOS_REQUEST_ID", "02176984059750700000000000000000000ffff0a1f5228984d93")

    response = await request_stats.get(
        request_id=request_id,
    )
    print(response)


if __name__ == "__main__":
    asyncio.run(main())
