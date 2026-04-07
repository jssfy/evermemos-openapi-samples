# everos should've been installed (pip install everos -U)
# Migration notes from v0:
#   - v0's client.v0.status.request.get(request_id=...) is REMOVED in v1
#   - v1 equivalent: client.v1.tasks.retrieve(task_id=...)
#   - task_id is obtained from add() response: response.data.task_id
#     (v0 used response.request_id; v1 uses response.data.task_id)
#   - env var renamed: EVERMEMOS_REQUEST_ID → EVEROS_TASK_ID
import os
import asyncio
from everos import AsyncEverOS

client = AsyncEverOS()


async def main() -> None:
    task_id = os.environ.get("EVEROS_TASK_ID", "your-task-id-here")

    response = await client.v1.tasks.retrieve(task_id=task_id)
    print(response)


if __name__ == "__main__":
    asyncio.run(main())
